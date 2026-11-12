"""Reachability analysis of the SoulGold world from the game source (maps, tiles, objects).

Walks the map grid like the player would (collision, elevation, ledges, directional walls, warps, map connections) from New Bark Town
with a given set of field abilities, and reports for every map: can you stand on an encounter tile, reach water (surf / fish),
reach a breakable rock, and which item balls you can pick up.  Story gates (NPCs with a hide flag, hidden until/after an event)
are treated as walls when `block_flagged` is set, so the difference between the two runs shows what depends on story events."""
import json, re, os, struct, sys, collections
SRC = "/home/claude/soulgold/site"
PRIM = 1024
ML = 7      # ELEVATION_MULTI_LEVEL in this build (bridges)

# ---- metatile behaviours
MB = {}
i = 0
for line in open(f"{SRC}/include/constants/metatile_behaviors.h"):
    m = re.match(r"\s*(MB_\w+)\s*(?:=\s*(\w+))?\s*,", line)
    if m:
        if m.group(2) and m.group(2).isdigit(): i = int(m.group(2))
        MB[m.group(1)] = i; i += 1
N = {v: k for k, v in MB.items()}
SURF_B = {MB[k] for k in ("MB_POND_WATER", "MB_INTERIOR_DEEP_WATER", "MB_DEEP_WATER", "MB_WATERFALL", "MB_SOOTOPOLIS_DEEP_WATER", "MB_OCEAN_WATER",
                          "MB_NO_SURFACING", "MB_SEAWEED", "MB_SEAWEED_NO_SURFACING", "MB_EASTWARD_CURRENT", "MB_WESTWARD_CURRENT",
                          "MB_NORTHWARD_CURRENT", "MB_SOUTHWARD_CURRENT", "MB_WATER_DOOR", "MB_WATER_SOUTH_ARROW_WARP")}
ENC_B = {MB[k] for k in ("MB_TALL_GRASS", "MB_LONG_GRASS", "MB_DEEP_SAND", "MB_CAVE", "MB_INDOOR_ENCOUNTER", "MB_ASHGRASS", "MB_FOOTPRINTS") if k in MB}
for k in MB:
    if "GRASS" in k and "SHORT" not in k and "EDGE" not in k: ENC_B.add(MB[k])
DIRS = {"E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1)}
OPP = {"E": "W", "W": "E", "N": "S", "S": "N"}
BLOCK = {"E": {"MB_IMPASSABLE_EAST", "MB_IMPASSABLE_NORTHEAST", "MB_IMPASSABLE_SOUTHEAST"}, "W": {"MB_IMPASSABLE_WEST", "MB_IMPASSABLE_NORTHWEST", "MB_IMPASSABLE_SOUTHWEST"},
         "N": {"MB_IMPASSABLE_NORTH", "MB_IMPASSABLE_NORTHEAST", "MB_IMPASSABLE_NORTHWEST"}, "S": {"MB_IMPASSABLE_SOUTH", "MB_IMPASSABLE_SOUTHEAST", "MB_IMPASSABLE_SOUTHWEST"}}
BLOCK = {d: {MB[k] for k in v} for d, v in BLOCK.items()}
JUMP = {"E": MB["MB_JUMP_EAST"], "W": MB["MB_JUMP_WEST"], "N": MB["MB_JUMP_NORTH"], "S": MB["MB_JUMP_SOUTH"]}
WATERFALL = MB["MB_WATERFALL"]; ROCKCLIMB = MB.get("MB_ROCK_CLIMB", -1)

# ---- tilesets
hdr = open(f"{SRC}/src/data/tilesets/headers.h").read()
mt = open(f"{SRC}/src/data/tilesets/metatiles.h").read()
ATTR_PATH = dict(re.findall(r"(gMetatileAttributes_\w+)\[\]\s*=\s*INCBIN_U16\(\"([^\"]+)\"\)", mt))
TS = {}
for m in re.finditer(r"const struct Tileset (gTileset_\w+)\s*=\s*\{(.*?)\};", hdr, re.S):
    a = re.search(r"\.metatileAttributes\s*=\s*(\w+)", m.group(2))
    if a and a.group(1) in ATTR_PATH:
        p = f"{SRC}/{ATTR_PATH[a.group(1)]}"
        if os.path.exists(p):
            b = open(p, "rb").read(); TS[m.group(1)] = [x & 0xFF for x in struct.unpack(f"<{len(b)//2}H", b[:len(b)//2*2])]

# ---- layouts and maps
LAY = {l["id"]: l for l in json.load(open(f"{SRC}/data/layouts/layouts.json"))["layouts"] if "id" in l}
MAPS = {}
for d in os.listdir(f"{SRC}/data/maps"):
    f = f"{SRC}/data/maps/{d}/map.json"
    if os.path.exists(f):
        j = json.load(open(f)); j["dir"] = d; MAPS[j["id"]] = j
GRID = {}
def grid(mid):
    if mid in GRID: return GRID[mid]
    j = MAPS.get(mid); l = LAY.get(j["layout"]) if j else None
    if not l: GRID[mid] = None; return None
    b = open(f"{SRC}/{l['blockdata_filepath']}", "rb").read()
    w, h = l["width"], l["height"]
    v = struct.unpack(f"<{w*h}H", b[:w*h*2])
    p, s = TS.get(l["primary_tileset"], []), TS.get(l["secondary_tileset"], [])
    def beh(t):
        t &= 0x7FF
        if t < PRIM: return p[t] if t < len(p) else 0
        return s[t - PRIM] if t - PRIM < len(s) else 0
    g = {"w": w, "h": h, "col": [(x >> 11) & 1 for x in v], "el": [x >> 12 for x in v], "b": [beh(x) for x in v]}
    # objects
    g["obj"] = {}
    for k, o in enumerate(j.get("object_events") or []):
        gfx = o.get("graphics_id", "")
        kind = ("cut" if "CUTTABLE_TREE" in gfx else "rock" if "BREAKABLE_ROCK" in gfx else "boulder" if "PUSHABLE_BOULDER" in gfx
                else "whirl" if "WHIRLPOOL" in gfx else "item" if gfx in ("OBJ_EVENT_GFX_ITEM_BALL", "OBJ_EVENT_GFX_TMBALL", "OBJ_EVENT_GFX_POKE_BALL") and o.get("trainer_type") == "TRAINER_TYPE_NONE" and "Item" in (o.get("script") or "")
                else "npc")
        sc = o.get("script") or ""
        kind = {"EventScript_Whirlpool": "whirl", "EventScript_CutTree": "cut", "EventScript_RockSmash": "rock", "EventScript_StrengthBoulder": "boulder"}.get(sc, kind)
        if (o.get("script") or "") == "Common_EventScript_FindItem" or (kind == "npc" and gfx in ("OBJ_EVENT_GFX_ITEM_BALL", "OBJ_EVENT_GFX_TMBALL")): kind = "item"
        g["obj"].setdefault((o["x"], o["y"]), []).append({"kind": kind, "flag": o.get("flag", "0"), "script": o.get("script"), "gfx": gfx, "item": o.get("trainer_sight_or_berry_tree_id"),
                                                         "move": o.get("movement_type", ""), "trainer": o.get("trainer_type")})
    g["warp"] = {}
    for wv in j.get("warp_events") or []: g["warp"].setdefault((wv["x"], wv["y"]), wv)
    g["conn"] = j.get("connections") or []
    GRID[mid] = g
    return g

def warp_dest(wv):
    dm = wv["dest_map"]
    if dm in ("MAP_DYNAMIC", "MAP_NONE") or dm not in MAPS: return None
    ws = MAPS[dm].get("warp_events") or []
    try: k = int(wv["dest_warp_id"])
    except ValueError: return None
    if k >= len(ws): return None
    return dm, ws[k]["x"], ws[k]["y"]

def run(caps, block_flagged=False, start=("MAP_NEW_BARK_TOWN", None), open_flags=(), closed=(), opened=()):
    """caps: set of 'surf','cut','rock','strength','whirl','waterfall','rockclimb'.  Returns dict map -> info."""
    g0 = grid(start[0])
    if start[1] is None:
        wv = next(iter(g0["warp"].values())); sx, sy = wv["x"], wv["y"] + 1
    else: sx, sy = start[1]
    st0 = (start[0], sx, sy, g0["el"][sy * g0["w"] + sx], False)
    seen = {st0}; q = collections.deque([st0]); par = {}; run.par = par
    info = collections.defaultdict(lambda: {"land": False, "enc": False, "water": False, "fish": False, "rock": False, "items": set(), "tiles": 0, "gates": set()})
    def passable_obj(g, x, y, el, mid):
        if (mid, x, y) in closed: return False
        for o in g["obj"].get((x, y), []):
            k = o["kind"]
            if k == "item": continue
            if k == "cut":
                if "cut" not in caps: return False
            elif k == "rock":
                if "rock" not in caps: return False
            elif k == "boulder":
                if "strength" not in caps: return False
            elif k == "whirl":
                if "whirl" not in caps: return False
            else:
                if o["flag"] in ("0", 0) and (mid, x, y) not in opened and not any(t in o["move"] for t in ("WANDER", "WALK", "COPY", "ROTATE")) and o["trainer"] in (None, "TRAINER_TYPE_NONE", "0") and "SPECIES" not in o["gfx"] and "LIGHT_SPRITE" not in o["gfx"]:
                    return False
                if block_flagged and o["flag"] not in ("0", 0) and o["flag"] not in open_flags and "WANDER" not in o["move"] and "WALK" not in o["move"]:
                    info[mid]["gates"].add((x, y, o["flag"], o["script"])); return False
        return True
    while q:
        mid, x, y, el, surf = q.popleft()
        g = grid(mid); w, h = g["w"], g["h"]; I = info[mid]
        bh = g["b"][y * w + x]
        I["tiles"] += 1
        if surf: I["water"] = True; I["fish"] = True
        else:
            I["land"] = True
            if bh in ENC_B: I["enc"] = True
        # things next to me
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if g["b"][ny * w + nx] in SURF_B and not surf: I["fish"] = True
                for o in g["obj"].get((nx, ny), []):
                    if o["kind"] == "item": I["items"].add(o["item"] if str(o["item"]).startswith("ITEM_") else o["script"])
                    if o["kind"] == "rock" and "rock" in caps: I["rock"] = True
        # warp
        nxt = []
        wv = g["warp"].get((x, y))
        if wv:
            dst = warp_dest(wv)
            if dst:
                g2 = grid(dst[0])
                if g2 and 0 <= dst[1] < g2["w"] and 0 <= dst[2] < g2["h"]:
                    b2 = g2["b"][dst[2] * g2["w"] + dst[1]]
                    nxt.append((dst[0], dst[1], dst[2], g2["el"][dst[2] * g2["w"] + dst[1]], b2 in SURF_B))
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy; nm, ng = mid, g
            if not (0 <= nx < w and 0 <= ny < h):
                hit = None
                for c in g["conn"]:
                    cd = c["direction"]; off = c["offset"]; g2 = grid(c["map"])
                    if not g2: continue
                    if cd == "up" and ny < 0 and 0 <= nx - off < g2["w"]: hit = (c["map"], nx - off, g2["h"] + ny)
                    if cd == "down" and ny >= h and 0 <= nx - off < g2["w"]: hit = (c["map"], nx - off, ny - h)
                    if cd == "left" and nx < 0 and 0 <= ny - off < g2["h"]: hit = (c["map"], g2["w"] + nx, ny - off)
                    if cd == "right" and nx >= w and 0 <= ny - off < g2["h"]: hit = (c["map"], nx - w, ny - off)
                if not hit: continue
                nm, nx, ny = hit; ng = grid(nm)
            k = ny * ng["w"] + nx
            nb, ncol, nel = ng["b"][k], ng["col"][k], ng["el"][k]
            if bh in BLOCK[d] or nb in BLOCK[OPP[d]]: continue
            # ledge
            if not surf and nb == JUMP[d]:
                jx, jy = nx + dx, ny + dy
                if 0 <= jx < ng["w"] and 0 <= jy < ng["h"] and not ng["col"][jy * ng["w"] + jx]:
                    nxt.append((nm, jx, jy, ng["el"][jy * ng["w"] + jx], False))
                continue
            if (nb == ROCKCLIMB or bh == ROCKCLIMB) and "rockclimb" in caps and (nb == ROCKCLIMB or not ncol):
                nxt.append((nm, nx, ny, nel if nb != ROCKCLIMB and nel != ML else 0, surf and nb in SURF_B))
                if ncol: continue
            wv2 = ng["warp"].get((nx, ny))
            if wv2 and ncol and any(t in N.get(nb, "") for t in ("DOOR", "LADDER", "ESCALATOR", "WARP", "STAIRS")):
                dst = warp_dest(wv2)
                if dst:
                    g2 = grid(dst[0])
                    if g2 and 0 <= dst[1] < g2["w"] and 0 <= dst[2] < g2["h"]:
                        nxt.append((dst[0], dst[1], dst[2], g2["el"][dst[2] * g2["w"] + dst[1]], False))
                continue
            if ncol: continue
            if not passable_obj(ng, nx, ny, el, nm): continue
            water = nb in SURF_B
            mism = not (el == 0 or nel in (0, ML) or nel == el)
            if surf:
                if water:
                    if nb == WATERFALL and d == "N" and "waterfall" not in caps: continue
                    nxt.append((nm, nx, ny, el, True))
                elif nel == 3 or not mism: nxt.append((nm, nx, ny, nel if nel != ML else 3, False))
            else:
                if water:
                    if "surf" in caps: nxt.append((nm, nx, ny, nel if nel != ML else 1, True))
                elif not mism: nxt.append((nm, nx, ny, el if nel == ML else nel, False))
        for s in nxt:
            if s not in seen: seen.add(s); q.append(s); par[s] = (mid, x, y, el, surf)
    run.seen = seen
    return info

if __name__ == "__main__":
    caps = set(sys.argv[1].split(",")) if len(sys.argv) > 1 and sys.argv[1] else set()
    r = run(caps, block_flagged=len(sys.argv) > 2)
    for m in sorted(r):
        i = r[m]
        print(m, "enc" if i["enc"] else "", "water" if i["water"] else "fish" if i["fish"] else "", "rock" if i["rock"] else "", len(i["items"]), sorted(i["gates"])[:4])

def path_to(mapid, pred=None):
    """Map-level route of the last run() to the first reached state in mapid (optionally matching pred)."""
    t = next((s for s in run.seen if s[0] == mapid and (pred is None or pred(s))), None)
    if not t: return None
    out = []
    while t in run.par:
        p = run.par[t]
        if p[0] != t[0] or abs(p[1] - t[1]) + abs(p[2] - t[2]) > 2: out.append(f"{p[0][4:]}({p[1]},{p[2]})->{t[0][4:]}({t[1]},{t[2]})")
        t = p
    return out[::-1]
