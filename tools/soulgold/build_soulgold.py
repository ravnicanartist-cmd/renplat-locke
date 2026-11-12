"""SoulGold v1.2.1 (eemeliri, pokeemerald-expansion Johto hack) -> data files for the hub site (hub/soulgold/data).

Sources: the hack's own documentation data (docs/data/*.json in github.com/eemeliri/soulgold: species, learnsets, TMs, moves,
abilities, every trainer in Normal and Hard, wild encounters, items) plus the game source for things the docs don't carry
(map -> met-location sections, growth rates, item ids, trainer AI flags)."""
import json, re, os, sys, collections
sys.path.insert(0, "/home/claude/build")
import model as MD
from common import dump

SRC = "/home/claude/soulgold/site"
D = f"{SRC}/docs/data"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/hub/soulgold/data"
J = lambda p: json.load(open(f"{D}/{p}", encoding="utf-8"))
TITLE = lambda c: c.split("_", 1)[1].title() if c else ""          # TYPE_FIRE -> Fire
CAT = {"DAMAGE_CATEGORY_PHYSICAL": "Physical", "DAMAGE_CATEGORY_SPECIAL": "Special", "DAMAGE_CATEGORY_STATUS": "Status"}

# ------------------------------------------------------------------ species
SPEC = J("species.json")
def slugn(n): return n.lower().replace(" ", "-").replace(".", "").replace("’", "").replace("'", "").replace(":", "")
have_plain = {slugn(s["name"]) for s in SPEC if slugn(s["name"]) == s["slug"]}
NAME, used = {}, set()
for s in SPEC:
    n = s["name"]
    if slugn(n) != s["slug"]:
        base = slugn(n)
        if base not in have_plain and n not in used:
            pass                                             # the only form of this species: keep the plain name
        else:
            suf = s["slug"][len(base) + 1:] if s["slug"].startswith(base + "-") else s["slug"]
            n = n + "-" + "-".join(w.capitalize() for w in suf.split("-"))
    if n in used: n = n + "-" + s["slug"]
    n = {"Nidoran F": "Nidoran-F", "Nidoran M": "Nidoran-M"}.get(n, n)
    used.add(n); NAME[s["constant"]] = n
SPR = set(f[:-4] for f in os.listdir("/home/claude/hub/rupture/img/pokesprite"))
def rslug(n): return n.lower().replace(" ", "-", 1).replace(".", "").replace(".", "").replace("’", "").replace(":", "-")
ABN = {k: v["name"] for k, v in J("abilities.json").items()}
MOVESJ = J("moves.json")
MVN = {k: v["name"] for k, v in MOVESJ.items()}
MONS, BYID = {}, {}
for s in SPEC:
    n = NAME[s["constant"]]
    try: det = json.load(open(f"{D}/species-details/{s['slug']}.json"))
    except FileNotFoundError: det = {"levelUp": [], "tmhm": [], "evolutions": [], "tutors": []}
    reg = [ABN.get(a, a) for a in s["regularAbilities"] if a != "ABILITY_NONE"]
    hid = [ABN.get(a, a) for a in s["hiddenAbilities"] if a != "ABILITY_NONE"]
    ab = list(dict.fromkeys(reg + hid)) or ["-"]
    st = s["stats"]
    sp = s["slug"] if s["slug"] in SPR else (rslug(n) if rslug(n) in SPR else s["slug"].split("-")[0])
    MONS[n] = {"id": s["id"], "no": s["dex"], "t": list(dict.fromkeys(TITLE(t) for t in s["types"])), "bs": [st["hp"], st["atk"], st["def"], st["spa"], st["spd"], st["spe"]],
               "ab": ab, "abs": [reg[0] if reg else ab[0], reg[1] if len(reg) > 1 else (reg[0] if reg else ab[0]), hid[0] if hid else (reg[0] if reg else ab[0])],
               "lv": [(x["level"], MVN.get(x["move"], x["move"])) for x in det["levelUp"]], "tm": [MVN.get(m, m) for m in det["tmhm"]],
               "evos": [], "cat": s["categories"], "sp": sp, "const": s["constant"], "rawevo": det["evolutions"]}
    BYID[s["id"]] = n
for n, d in MONS.items():
    for e in d.pop("rawevo"):
        to = NAME.get(e["target"])
        if not to: continue
        m, p = e["method"], e["param"]
        if m.startswith("EVO_LEVEL"): d["evos"].append({"to": to, "kind": "level", "p": int(p) if str(p).isdigit() else 1})
        elif m == "EVO_ITEM": d["evos"].append({"to": to, "kind": "item", "p": e.get("itemName") or p})
        elif m == "EVO_SPLIT_FROM_EVO": d["evos"].append({"to": to, "kind": "shedinja", "p": None})
        else: d["evos"].append({"to": to, "kind": "other", "p": e.get("label")})
PRE = {}
for n, d in MONS.items():
    for e in d["evos"]: PRE.setdefault(e["to"], n)
def root(n):
    seen = set()
    while n in PRE and n not in seen: seen.add(n); n = PRE[n]
    return n
for n in MONS: MONS[n]["fam"] = root(n)
LEGEND = {n for n, d in MONS.items() if set(d["cat"]) & {"legendary", "mythical", "paradox"}}

# ------------------------------------------------------------------ moves
MOVES = {}
for k, m in MOVESJ.items():
    if k == "MOVE_NONE": continue
    MOVES[m["name"]] = {"t": TITLE(m["type"]), "c": CAT.get(m["category"], "Status"), "bp": m["power"] or 0}
MULTI = {"Double Slap": 3, "Comet Punch": 3, "Fury Attack": 3, "Pin Missile": 3, "Spike Cannon": 3, "Barrage": 3, "Fury Swipes": 3,
         "Bone Rush": 3, "Arm Thrust": 3, "Bullet Seed": 3, "Icicle Spear": 3, "Rock Blast": 3, "Tail Slap": 3, "Scale Shot": 3, "Water Shuriken": 3,
         "Double Kick": 2, "Bonemerang": 2, "Twineedle": 2, "Double Hit": 2, "Dual Chop": 2, "Gear Grind": 2, "Double Iron Bash": 2,
         "Dragon Darts": 2, "Dual Wingbeat": 2, "Tachyon Cutter": 2, "Triple Kick": 3, "Triple Axel": 3, "Surging Strikes": 3, "Population Bomb": 4}
MULTI = {k: v for k, v in MULTI.items() if k in MOVES}
MD.MONS, MD.MOVES, MD.MULTI = MONS, MOVES, MULTI
KEY = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())
MKEY = {KEY(m): m for m in MOVES}; MKEY["hijumpkick"] = "High Jump Kick"
ABKEY = {KEY(a): a for a in ABN.values()}

# ------------------------------------------------------------------ story: splits and when each place opens up
SPLITS = ["Falkner", "Bugsy", "Whitney", "Morty", "Gym 5", "Gym 6", "Gym 7", "Rocket takeover", "Clair", "Ho-Oh / Lugia", "Elite Four", "Post-game"]
CAPS = [12, 19, 26, 34, 42, 45, 48, 55, 58, 62, 70, 100]
POST = 11
# Field moves need a badge in SoulGold (src/field_move.c): Rock Smash 1 (HM on Route 36), Cut 2, Strength 3 (HM in Olivine), Surf 4,
# Whirlpool 7, Waterfall / Rock Climb 8.  Rods: Old = Route 32 Pokémon Center, Good = Olivine (walkable before Morty), Super = Blackthorn.
SURF, ROCKSMASH, OLD, GOOD, SUPER = 4, 1, 1, 3, 8
GYMDONE = [(r"Violet City Gym", 1), (r"Azalea Town Gym", 2), (r"Goldenrod City Gym", 3), (r"Ecruteak City Gym", 4),
           (r"(Olivine City|Cianwood|Mahogany Town) Gym", 7), (r"Blackthorn City Gym", 9)]
LOCS = [
    (r"^(Goldenrod City Radio Tower|Goldenrod City Underground Switches|Goldenrod City Underground Storage|Rocket Hideout|Rocket Arcade)", 7),
    (r"^(Dark Cave North|Dragon|Route 45|Route 46 Upper|Kitakami|Tin Tower|Bellchime)", 9),
    (r"^(Union Cave B2F)", 4),
    (r"^Safari Zone Top Right", 8), (r"^Safari Zone Low Right", 10),
    (r"^(New Bark|Route 29|Cherrygrove|Route 30|Route 31|Route 46|Dark Cave|Violet|Sprout Tower|Mr\.? Pokemon)", 0),
    (r"^(Route 32|Ruins of Alph|Union Cave|Route 33|Azalea|Slowpoke Well|Kurt)", 1),
    (r"^(Ilex|Route 34|Goldenrod|Foggy Shore|Battle Factory|Battle Arcade|Day.?care)", 2),
    (r"^Route 36", 0),
    (r"^(Route 35|National Park|Bug Catching|Route 37|Ecruteak|Burned Tower)", 3),
    (r"^(Route 38|Route 39|Olivine|Route 40|Route 41|Cianwood|Whirl|Route 42|Mt\.? Mortar|Mahogany|Route 43|Lake of Rage|Cliff|Route 47|Route 48|"
     r"Safari Zone|Route 49|Railway|Vajra Desert West|Vajra Desert$|Snowtop|South Shore|Lost Woods|Foggy Forest|Rinto|South Johto Sea)", 4),
    (r"^(Route 44|Ice Path|Blackthorn)", 8),
    (r"^(Route 27|Route 26|Tohjo|Victory Road|Indigo|Pokemon League|Pokémon League)", 10),
]
# Reachability from the game's own maps (tools/reach.py walks the map grid; tools/stages.py adds the story gates read from the scripts):
# earliest stage you can stand in each map / reach its grass, water, rocks and item balls.
import stages as STG
FIRST, ITEMST = STG.staged()
def to_split(s): return 99 if s is None else POST if s >= 11 else s
NORM = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())
MAPID = {}
for mid, j in STG.R.MAPS.items(): MAPID.setdefault(NORM(j["name"]), mid)
for e in J("encounters.json"): MAPID[NORM(e["name"])] = e["map"]
ITEMCONST = {i["name"]: i["constant"] for i in J("items.json")}
def reach(loc, kind="land"):
    mid = MAPID.get(NORM(loc))
    return to_split(FIRST.get((mid, kind))) if mid else None
def loc_stage(loc, src="", item=None):
    s = f"{loc} {src}"
    if re.search(r"postgame|post-game|achievement|trophy|Hidden Grotto|Wild held|Battle Cafe|Title Defense|BP shop|Password|puzzles", s, re.I): return 99
    if re.search(r"New Bark Town Lab Gift", s): return 1      # Elm gives the Shiny Stone once the Togepi egg hatches (Carlos got it with 1 badge)
    if re.search(r"New Bark Town House 3", s): return 99       # Dive: post-game
    if re.search(r"After Rocket Hideout|^Rocket Hideout", s, re.I): return 7       # the Mahogany hideout (entered through a script)
    if re.search(r"^Goldenrod City Underground (Storage|Switches)", s): return 8   # only open during the Radio Tower takeover
    if re.search(r"^Kitakami Well", s): return 9
    if re.search(r"After Jasmine", s, re.I): return 7
    if re.search(r"Bug Catching Contest|place choice", s): return 3
    if re.search(r"Game Corner", s): return 2
    for pat, g in GYMDONE:
        if re.search(pat, loc): return g
    m = re.match(r"Gate (?:Goldenrod City )?(Route \d+)", loc)
    mid = MAPID.get(NORM(loc)) or (MAPID.get(NORM(m.group(1))) if m else None)
    g = None
    if mid:
        if src in ("Item ball",) and item:
            g = to_split(ITEMST.get((mid, item)))            # a ball you can't walk to (yet) stays out
        else:
            g = to_split(FIRST.get((mid, "land")))
    else:
        for pat, gg in LOCS:
            if re.search(pat, loc, re.I): g = gg; break
        if g is None: g = 99
    if re.search(r"after 4 badges|after 4th badge", s, re.I): g = max(g, 4)
    if re.search(r"After beating Whitney", s, re.I): g = max(g, 3)
    return g

# ------------------------------------------------------------------ items / TMs
EVO_ITEMS = {e["p"] for d in MONS.values() for e in d["evos"] if e["kind"] == "item"}
ITEMS = J("items.json")
EVO_ITEM = {}
for it in ITEMS:
    if it["name"] in EVO_ITEMS:
        g = min([loc_stage(l["map"], l["source"], it["constant"]) for l in it["locations"]] or [99])
        EVO_ITEM[it["name"]] = g
for i in EVO_ITEMS: EVO_ITEM.setdefault(i, 99)
TMS = []
for t in J("machines.json"):
    g = min([loc_stage(l["map"], l["source"], t["item"]) for l in t["locations"]] or [99])
    TMS.append((t["label"], t["moveName"], t.get("location") or "", g))
TM_BY_MOVE = {}
for tm, mv, w, g in TMS: TM_BY_MOVE[mv] = min(g, TM_BY_MOVE.get(mv, 99))

# ------------------------------------------------------------------ encounters -> Nuzlocke areas (met-location sections)
MAPSEC = {}
for d in os.listdir(f"{SRC}/data/maps"):
    f = f"{SRC}/data/maps/{d}/map.json"
    if os.path.exists(f):
        j = json.load(open(f)); MAPSEC[j["id"]] = j.get("region_map_section")
SECS = json.load(open(f"{SRC}/src/data/region_map/region_map_sections.json"))["map_sections"]
SECNAME = {x["id"]: x.get("name", x["id"]) for x in SECS}
AREA_FIX = {"Mt Mortar": "Mt. Mortar"}
def fixarea(a): return AREA_FIX.get(a, a)
SOURCES = []   # (species, where, how, gate for Boss Prep, min level, area, gate for the Nuzlocke area)
ENC = collections.OrderedDict()
KIND = {"Land": "enc", "Water": "water", "Fishing": "fish", "Rock": "rock"}
# places you get into through a script (no door to walk through), and the Safari Zone's later areas (FAQ: 2nd area opens
# before the Ice Path, 3rd after Tohjo Falls)
ENC_FIX = {"MAP_ROCKET_HIDEOUT_B1F": 4, "MAP_NATIONAL_PARK_BUG_CONTEST": 2, "MAP_KITAKAMI_WELL_B1F": 9,
           "MAP_SAFARI_ZONE_TOP_RIGHT": 8, "MAP_SAFARI_ZONE_LOW_RIGHT": 10}
DROPPED = []
def level_gate(g, lv):
    """Level caps: a wild Pokémon above the cap can't be used, so it counts from the first split whose cap reaches its lowest level."""
    while g < POST and CAPS[g] < lv: g += 1
    return g
for e in J("encounters.json"):
    area = fixarea(SECNAME.get(MAPSEC.get(e["map"]), e["name"]))
    for v in e["variants"]:
        tm = (v.get("time") or "").lower()
        for m in v["methods"]:
            meth = m["method"]; kind = KIND.get(meth.split()[0], "enc")
            st = to_split(FIRST.get((e["map"], kind)))
            if e["map"] in ENC_FIX: st = max(ENC_FIX[e["map"]], st if st < 99 else 0)
            elif st == 99 and (e["map"], "land") not in FIRST and not any((e["map"], k) in FIRST for k in ("water", "fish")):
                st = POST                                   # never reached on foot: post-game places (Dive, Faraway Island, the Pyramid)
            elif st == 99:
                DROPPED.append((e["name"], meth)); continue  # the table exists but there's no such tile to stand on (e.g. fishing on Route 38)
            for k, x in enumerate(m["mons"]):
                if not x.get("hasSpecies", True): continue
                n = NAME.get(x["species"])
                if not n: continue
                if meth.startswith("Land"): how, g = "grass", st
                elif meth.startswith("Water"): how, g = "surf", max(st, SURF)
                elif meth.startswith("Rock"): how, g = "rock smash", max(st, ROCKSMASH)
                elif meth.startswith("Fishing"):
                    rod = "old" if k < 2 else "good" if k < 5 else "super"
                    how, g = f"{rod} rod", max(st, {"old": OLD, "good": GOOD, "super": SUPER}[rod])
                else: how, g = meth.lower(), st
                r = ENC.setdefault((n, e["name"], how), {"g": g, "lv": x["minLevel"], "area": area, "t": set()})
                r["lv"] = min(r["lv"], x["minLevel"]); r["t"].add(tm); r["g"] = min(r["g"], g)
for (n, where, how), r in ENC.items():
    if how == "grass" and len(r["t"]) == 1 and next(iter(r["t"])): how = f"grass ({next(iter(r['t']))})"
    SOURCES.append((n, where, how, level_gate(r["g"], r["lv"]), r["lv"], r["area"], r["g"]))
GIFTS = [(["Togepi"], "Togepi egg from Elm's aide (Violet City), after the 1st gym", "egg", 1, "Violet City"),
         (["Rattata-Alola", "Zigzagoon-Galar"], "Cherrygrove City (choose one)", "gift", 0, "Cherrygrove City"),
         (["Pawmi"], "Violet City trade (for Cottonee)", "trade", 0, "Violet City"),
         (["Slowpoke-Galar"], "Azalea Town trade (for Slowpoke)", "trade", 1, "Azalea Town"),
         (["Bagon", "Gible", "Feebas", "Riolu", "Jangmo-o", "Zorua-Hisui", "Goomy"], "Odd Egg on Route 34: prize for beating Crystal/Gold, or from the Day Care son (one per game)", "egg", 2, "Route 34"),
         (["Kabuto", "Aerodactyl", "Lileep", "Archen", "Tyrunt", "Amaura"], "Fossil from a Ruins of Alph rock, revived at the lab (Carlos's rule: one per run)", "revive", 1, "Fossil revival (1 per run)"),
         (["Honedge"], "Goldenrod Dept. Store trade (for Clefairy)", "trade", 2, "Goldenrod City"),
         (["Eevee-Starter", "Pikachu-Starter"], "Bill in Ecruteak (choose one)", "gift", 3, "Ecruteak City"),
         (["Gimmighoul"], "Cianwood City house", "gift", 4, "Cianwood City"),
         (["Tyrogue"], "Mt. Mortar Karate King", "gift", 4, "Mt. Mortar"),
         (["Rotom"], "Route 39 / 49 gatehouse trade (for Zorua)", "trade", 3, "Route 39"),
         (["Voltorb-Hisui"], "Olivine City trade (for Mareanie)", "trade", 3, "Olivine City"),
         (["Gabite"], "Blackthorn City trade (for Dragonair)", "trade", 8, "Blackthorn City"),
         (["Dratini"], "Dragon's Den shrine (after Clair)", "gift", 9, "Dragon's Den"),
         (["Beldum"], "Steven in Kitakami", "gift", 9, "Kitakami Village")]
for sp, where, how, g, area in GIFTS:
    for s in sp:
        n = s if s in MONS else next((x for x in MONS if x.lower() == s.lower()), None)
        if n: SOURCES.append((n, where, how, g, 0, area, g))
        else: print("gift not found", s)
SOURCES = [s for s in SOURCES if s[0] not in LEGEND]

# ------------------------------------------------------------------ pools (same rules as the other games)
def evo_ok(e, n, stage, cap):
    k = e["kind"]
    if k == "level": return e["p"] <= cap
    if k == "item": return EVO_ITEM.get(e["p"], 99) <= stage
    return False
def evolve(b, stage, cap):
    out = []
    def go(n, path):
        nxt = [e["to"] for e in MONS[n]["evos"] if e["to"] in MONS and e["to"] not in path and e["to"] not in LEGEND and evo_ok(e, n, stage, cap)]
        nxt = list(dict.fromkeys(nxt))
        if not nxt: out.append((n, path))
        for t2 in nxt: go(t2, path + [t2])
    go(b, [b])
    return out
def evo_level(a, b):
    for e in MONS[a]["evos"]:
        if e["to"] == b and e["kind"] == "level": return e["p"]
    return None
def learnable(n, path, stage, cap):
    mv = set()
    for k, sp in enumerate(path):
        top = cap
        if k + 1 < len(path):
            el = evo_level(sp, path[k + 1]); top = min(cap, el) if el else cap
        for l, m in MONS[sp]["lv"]:
            if l <= top: mv.add(m)
    for l, m in MONS[n]["lv"]:
        if l <= cap: mv.add(m)
    for m in MONS[n]["tm"]:
        if TM_BY_MOVE.get(m, 99) <= stage: mv.add(m)
    mv.discard("Frustration"); mv -= MD.NOUSE   # NOUSE: recharge moves, Last Resort, moves that faint the user
    return mv
def damaging(m):
    d = MOVES.get(m)
    return d is not None and (m in MD.FIXED or (d["c"] != "Status" and d["bp"] > 1))
def pool(stage, cap):
    base, locs = {}, {}
    for sp, an, how, gate, mlv, loc, rg in SOURCES:
        if gate <= stage:
            base.setdefault(sp, []).append(f"{an} ({how})")
            if how not in ("gift", "egg", "trade", "fossil", "static"): locs.setdefault(sp, set()).add(loc)
    rows_ = {}
    for b, where in base.items():
        for fin, path in evolve(b, stage, cap):
            r = rows_.setdefault(fin, {"from": [], "where": [], "path": path, "areas": set()})
            if b not in r["from"]: r["from"].append(b)
            for w in where:
                if w not in r["where"]: r["where"].append(w)
            r["areas"] |= locs.get(b, set())
            if len(path) > len(r["path"]): r["path"] = path
    out = []
    for n in sorted(rows_):
        r = rows_[n]
        out.append({"s": n, "from": r["from"], "where": r["where"][:6], "ab": MONS[n]["ab"][0],
                    "moves": sorted(m for m in learnable(n, r["path"], stage, cap) if damaging(m)), "areas": sorted(r["areas"])})
    return out

# ------------------------------------------------------------------ trainers (Normal and Hard)
AIF = {}
cur = None
for line in open(f"{SRC}/src/data/trainers.party", encoding="utf-8"):
    m = re.match(r"=== (TRAINER_\w+) ===", line)
    if m: cur = {"c": m.group(1), "diff": "Normal", "ai": "", "dbl": False}; continue
    if cur is None: continue
    if line.startswith("AI:"): cur["ai"] = line[3:].strip()
    elif line.startswith("Double Battle:"): cur["dbl"] = "Yes" in line
    elif line.startswith("Difficulty:"): cur["diff"] = line.split(":")[1].strip()
    elif not line.strip() and cur.get("ai") is not None:
        AIF[(cur["c"], cur["diff"])] = cur
def ai_of(c, diff):
    x = AIF.get((c, diff)) or AIF.get((c, "Normal"))
    if not x: return None
    v = 6 if "Smart" in x["ai"] else 2 if x["ai"] else 0
    return v | (128 if x["dbl"] else 0)
TR = J("trainers.json")
BYMODE = {"normal": {}, "hard": {}}
for t in TR:
    if t["difficulty"] == "Normal": BYMODE["normal"][t["constant"]] = t; BYMODE["hard"].setdefault(t["constant"], t)
for t in TR:
    if t["difficulty"] == "Hard": BYMODE["hard"][t["constant"]] = t
ORDER = [t["constant"] for t in TR if t["difficulty"] == "Normal"]
NATS = set(MD.NATURES)
def default_moves(n, lv):
    learned = []
    for l, m in MONS[n]["lv"]:
        if l <= lv and m not in learned: learned.append(m)
    return learned[-4:]
def boss(m):
    n = NAME.get(m["constant"]) or m["name"]
    mv = [MKEY.get(KEY(x), x) for x in m["moves"] if x and x not in ("-", "None")] or default_moves(n, m["level"])
    iv = m.get("ivs") or {}
    ivv = round(sum(iv.values()) / len(iv)) if iv else 0
    ab = ABKEY.get(KEY(m["ability"]), m["ability"]) if m["ability"] else MONS[n]["ab"][0]
    return {"s": n, "l": m["level"], "n": m["nature"] if m["nature"] in NATS else "", "a": ab, "i": m.get("itemName") or m.get("item") or "",
            "m": mv, "iv": ivv, **({"dm": 1} if not m["moves"] else {})}
def lvl_stage(lv):
    for i, c in enumerate(CAPS[:-1]):
        if lv <= c: return i
    return POST

# boss fights: (key, label, stage, tab, [(variant, constant)], location)
GYM57 = [("Chuck", "TRAINER_CHUCK_1", "Cianwood Gym"), ("Jasmine", "TRAINER_JASMINE_1", "Olivine City Gym"), ("Pryce", "TRAINER_PRYCE_1", "Mahogany Town Gym")]
SIL = lambda k: [({"starter": "Grass starter"}, f"TRAINER_RIVAL_CYNDAQUIL_{k}"), ({"starter": "Fire starter"}, f"TRAINER_RIVAL_TOTODILE_{k}"),
                 ({"starter": "Water starter"}, f"TRAINER_RIVAL_CHIKORITA_{k}")]
FIGHTS = [
    ("silver1", "Silver (Cherrygrove)", 0, "V", SIL(1)),
    ("falkner", "Falkner", 0, "G", [({}, "TRAINER_FALKNER_1")]),
    ("proton1", "Proton (Slowpoke Well)", 1, "V", [({}, "TRAINER_PROTON_1")]),
    ("bugsy", "Bugsy", 1, "G", [({}, "TRAINER_BUGSY_1")]),
    ("silver2", "Silver (Azalea)", 2, "V", SIL(2)),
    ("friend2", "Crystal / Gold (Route 34)", 2, "V", [({"gender": "M"}, "TRAINER_RIVALCRYSTAL2"), ({"gender": "F"}, "TRAINER_RIVALGOLD2")]),
    ("whitney", "Whitney", 2, "G", [({}, "TRAINER_WHITNEY_1")]),
    ("silver3", "Silver (Burned Tower)", 3, "V", SIL(3)),
    ("morty", "Morty", 3, "G", [({}, "TRAINER_MORTY_1")]),
    ("gym5", "Gym 5: Chuck / Jasmine / Pryce", 4, "G", [({"leader": a}, c) for a, c, _ in GYM57]),
    ("gym6", "Gym 6: Chuck / Jasmine / Pryce", 5, "G", [({"leader": a}, c + "_2") for a, c, _ in GYM57]),
    # The Mahogany hideout has to be cleared before Pryce will fight you; its bosses are built for the 7th-gym cap (48)
    ("petrel1", "Petrel (Rocket Hideout)", 6, "V", [({}, "TRAINER_PETREL_1")]),
    ("ariana1", "Ariana (Rocket Hideout)", 6, "V", [({}, "TRAINER_ARIANA_1")]),
    ("gym7", "Gym 7: Chuck / Jasmine / Pryce", 6, "G", [({"leader": a}, c + "_3") for a, c, _ in GYM57]),
    ("petrel2", "Petrel (Radio Tower)", 7, "V", [({}, "TRAINER_PETREL_2")]),
    ("silver4", "Silver (Goldenrod Underground)", 7, "V", SIL(4)),
    ("proton2", "Proton (Radio Tower)", 7, "V", [({}, "TRAINER_PROTON_2")]),
    ("ariana2", "Ariana (Radio Tower)", 7, "V", [({}, "TRAINER_ARIANA_2")]),
    ("archer", "Archer (Radio Tower)", 7, "V", [({}, "TRAINER_ARCHER")]),
    ("friend3", "Crystal / Gold (Ice Path)", 8, "V", [({"gender": "M"}, "TRAINER_RIVAL_CRYSTAL_ICEPATH"), ({"gender": "F"}, "TRAINER_RIVAL_GOLD_ICEPATH")]),
    ("clair", "Clair", 8, "G", [({}, "TRAINER_CLAIR_1")]),
    ("silver5", "Silver (Victory Road)", 10, "V", SIL(5)),
    ("will", "Elite Four Will", 10, "G", [({}, "TRAINER_WILL_1")]),
    ("koga", "Elite Four Koga", 10, "G", [({}, "TRAINER_KOGA_1")]),
    ("bruno", "Elite Four Bruno", 10, "G", [({}, "TRAINER_BRUNO_1")]),
    ("karen", "Elite Four Karen", 10, "G", [({}, "TRAINER_KAREN_1")]),
    ("lance", "Champion Lance", 10, "G", [({}, "TRAINER_LANCE_1")]),
]
MAND = {c for f in FIGHTS for _, c in f[4]}
CLASSNAME = {"Falkner": "Leader", "Bugsy": "Leader", "Whitney": "Leader", "Morty": "Leader", "Chuck": "Leader", "Jasmine": "Leader", "Pryce": "Leader",
             "Clair": "Leader", "Will": "Elite Four", "Koga": "Elite Four", "Bruno": "Elite Four", "Karen": "Elite Four", "Lance": "Champion",
             "Petrel": "Executive", "Ariana": "Executive", "Proton": "Executive", "Archer": "Executive", "Silver": "Rival"}

# ------------------------------------------------------------------ damage calc data (the Dynamic Calc copy under rupture/, customPoks mode)
SETID = {}
def calc_backup(mode):
    T = BYMODE[mode]
    sets = collections.defaultdict(dict)
    for tid, c in enumerate(ORDER):
        t = T[c]
        tname = "Silver" if t["name"] == "Passerby" else t["name"]
        cls = CLASSNAME.get(tname, "")
        loc = (t.get("locations") or [""])[0]
        for k, m in enumerate(t["party"]):
            n = NAME.get(m["constant"])
            if n not in MONS: continue
            b = boss(m)
            nm = f"Lvl {b['l']} {loc}: {(cls + ' ' if cls else '') + tname}"
            base, i = nm, 2
            while nm in sets[n]: nm = f"{base} ({i})"; i += 1
            iv = m.get("ivs") or {}
            sets[n][nm] = {"sublevel": "0", "level": b["l"], "nature": b["n"] or "Hardy", "sub_index": k, "tr_id": tid, "moves": b["m"], "item": b["i"],
                           "ivs": {"hp": iv.get("hp", 0), "at": iv.get("atk", 0), "df": iv.get("def", 0), "sa": iv.get("spa", 0), "sd": iv.get("spd", 0), "sp": iv.get("spe", 0)},
                           "ability": b["a"]}
            SETID[(mode, c, k)] = f"{n} ({nm})"
    poks = {n: {"bs": dict(zip(["hp", "at", "df", "sa", "sd", "sp"], [str(x) for x in d["bs"]])), "types": d["t"], "abilities": d["ab"],
                "learnset_info": {"tms": d["tm"], "learnset": [[l, m] for l, m in d["lv"]]}} for n, d in MONS.items()}
    moves = {k: {"basePower": v["bp"], "type": v["t"], "category": v["c"], "priority": MOVESJ_BY_NAME[k].get("priority", 0)} for k, v in MOVES.items()}
    return {"poks": poks, "moves": moves, "formatted_sets": sets}
MOVESJ_BY_NAME = {m["name"]: m for m in MOVESJ.values()}

def main():
    os.makedirs(OUT, exist_ok=True)
    for mode in ("normal", "hard"):
        bk = calc_backup(mode)
        with open(f"/home/claude/hub/rupture/backups/soulgold{'' if mode == 'normal' else '-hard'}.js", "w", encoding="utf-8") as f:
            f.write("backup_data = " + json.dumps(bk, ensure_ascii=False, separators=(",", ":")))
    trainers, index, cells = {}, {}, 0
    for mode in ("normal", "hard"):
        T = BYMODE[mode]
        # ---- trainers page, split by split
        rows = []
        for c in ORDER:
            t = T[c]
            team = [dict(boss(m), calc=SETID.get((mode, c, k))) for k, m in enumerate(t["party"]) if (NAME.get(m["constant"]) or "") in MONS]
            if not team: continue
            lv = max(m["l"] for m in team)
            locs = t.get("locations") or [""]
            ls = reach(locs[0])                              # where the trainer stands: the split you can first walk there
            if ls is None: ls = next((g for pat, g in LOCS if re.search(pat, locs[0], re.I)), 99)
            if re.search(r"Title Defense|Battle Cafe", locs[0]): ls = 99
            st = lvl_stage(lv)
            if ls < 99: st = max(st, ls) if ls < POST else POST
            if re.search(r"Rocket Hideout", locs[0]): st = 6                                  # before Pryce (see the Petrel / Ariana note)
            if re.search(r"Goldenrod City (Radio Tower|Underground (Storage|Switches))", locs[0]): st = 7   # the takeover
            if lv > 70: st = POST
            fnote = next((f for f in FIGHTS for v, cc in f[4] if cc == c), None)
            if fnote: st = fnote[2]
            notes = []
            if fnote and fnote[0].startswith("silver"): notes.append({"Grass starter": "If you chose Grass (a Grass-type starter)", "Fire starter": "If you chose Fire (a Fire-type starter)", "Water starter": "If you chose Water (a Water-type starter)"}[next(v for v, cc in fnote[4] if cc == c)["starter"]])
            if fnote and fnote[0].startswith("friend"): notes.append("If you play as a " + ("boy" if "CRYSTAL" in c else "girl"))
            if fnote and fnote[0] in ("gym5", "gym6", "gym7"): notes.append({"gym5": "If this is your 5th gym", "gym6": "If this is your 6th gym", "gym7": "If this is your 7th gym"}[fnote[0]])
            if any(m.get("dm") for m in team): notes.append("No set moves: shown with its latest level-up moves" + (" (Hard mode gives these trainers smarter picks)" if mode == "hard" else ""))
            ai = ai_of(c, "Hard" if mode == "hard" and t["difficulty"] == "Hard" else "Normal")
            if mode == "hard" and fnote and fnote[3] == "G" and fnote[0] not in ("will", "koga", "bruno", "karen", "lance") and ai is not None: ai |= 128
            cls = CLASSNAME.get(t["name"], "")
            tname = "Silver" if t["name"] == "Passerby" else t["name"]
            rows.append((st, ls if ls < 99 else st, sum(m["l"] for m in team) / len(team), {
                "name": (cls + " " if cls else "") + tname, "loc": locs[0], "mand": c in MAND, "partner": False, "notes": notes,
                "team": [{k: v for k, v in m.items() if k != "dm"} for m in team], "ai": ai}))
        rows.sort(key=lambda r: (r[0], r[1], r[2]))
        trainers[mode] = [{"split": SPLITS[i], "cap": CAPS[i] if i < POST else "—", "trainers": [r[3] for r in rows if r[0] == i]} for i in range(len(SPLITS))]
        trainers[mode] = [x for x in trainers[mode] if x["trainers"]]
        # ---- boss fights
        os.makedirs(f"{OUT}/fights/{mode}", exist_ok=True)
        idx, tabs = [], {"G": [], "V": [], "A": []}
        prev = {"G": None, "V": None, "A": None}; prevst = {"G": -1, "V": -1, "A": -1}
        for key, label, stage, tab, variants, in FIGHTS:
            team, vars_, cols, names, locs = [], [], [], [], []
            for v, c in variants:
                t = T.get(c)
                if not t: print("missing", mode, c); continue
                mons = [dict(boss(m), calc=SETID.get((mode, c, k))) for k, m in enumerate(t["party"]) if (NAME.get(m["constant"]) or "") in MONS]
                cols.append(list(range(len(team), len(team) + len(mons))))
                team += mons; vars_.append(v); names.append("Silver" if t["name"] == "Passerby" else t["name"]); locs.append((t.get("locations") or [""])[0])
            cap = CAPS[stage]
            P = pool(stage, cap)
            grid = [[MD.matchup(MD.mon(r["s"], cap, 15, "Hardy", r["ab"], "", r["moves"]), MD.mon(m["s"], m["l"], m["iv"], m["n"] or "Hardy", m["a"], m["i"], m["m"])) for m in team] for r in P]
            cells += len(P) * len(team)
            new, since = {}, {}
            for tb in (tab, "A"):
                pp = prev[tb]
                new[tb] = [i for i, r in enumerate(P) if pp is not None and r["s"] not in pp]
                lo = prevst[tb]
                since[tb] = {"tm": [f"{tm} {mv} — {w}" for tm, mv, w, g in TMS if lo < g <= stage],
                             "items": sorted(i for i, g in EVO_ITEM.items() if lo < g <= stage), "rods": [],
                             "other": [x for x, g in (("Surf", SURF), ("Old Rod", OLD), ("Good Rod", GOOD), ("Super Rod", SUPER), ("Rock Smash", ROCKSMASH)) if lo < g <= stage]}
                prev[tb] = {r["s"] for r in P}; prevst[tb] = stage
            dbl = mode == "hard" and tab == "G" and key not in ("will", "koga", "bruno", "karen", "lance")
            note = "Hard mode: this gym is a double battle; matchups are still 1-on-1." if dbl else ""
            if key in ("petrel1", "ariana1"): note = "The Mahogany hideout must be cleared before Pryce's gym opens (it needs Surf, so 4 badges). This team is built for the 7th-gym cap (48), which fits doing Chuck and Jasmine first; if you go earlier you'll be under-levelled by your cap."
            if key in ("gym5", "gym6", "gym7"): note = ("Chuck, Jasmine and Pryce can be done in any order and their teams scale with it: pick the leader you're facing. " + note).strip()
            dump(f"{OUT}/fights/{mode}/{key}.json", {"key": key, "label": label, "cap": cap, "team": team,
                 "variants": [{"v": v, "cols": c} for v, c in zip(vars_, cols)], "pool": P, "grid": grid, "new": new, "since": since})
            idx.append({"key": key, "label": label, "cap": cap, "split": SPLITS[stage], "loc": locs[0] if len(set(locs)) == 1 else " / ".join(dict.fromkeys(locs)),
                        "kind": None, "notes": [], "note": note, "names": list(dict.fromkeys(names)), "ids": [], "vars": vars_, "n": len(P)})
            tabs[tab].append(key); tabs["A"].append(key)
        index[mode] = {"fights": idx, "tabs": tabs, "order": {f["key"]: i for i, f in enumerate(idx)}, "caps": {s: c for s, c in zip(SPLITS, CAPS)}}
    # ---- Nuzlocke areas
    areas = collections.OrderedDict()
    for sp, an, how, gate, mlv, loc, rg in sorted(SOURCES, key=lambda s: (s[6], s[3])):
        a = areas.setdefault(loc, {"name": loc, "gate": rg, "split": SPLITS[min(rg, POST)], "mons": [], **({"met": "Ruins of Alph"} if loc.startswith("Fossil revival") else {})})
        a["gate"] = min(a["gate"], rg)
        a["mons"].append([sp, an, how, gate, mlv])
    for a in areas.values(): a["split"] = SPLITS[min(a["gate"], POST)]
    meta = {"game": "soulgold",
            "mons": {n: {"no": d["no"], "t": d["t"], "bs": d["bs"], "ab": d["ab"], "fam": d["fam"], **({"sp": d["sp"]} if d["sp"] != rslug(n) else {})} for n, d in MONS.items()},
            "moves": {m: [d["t"], d["c"], d["bp"]] for m, d in MOVES.items()}, "chart": MD.CHART,
            "natures": {k: v for k, v in MD.NATURES.items() if v}, "boost": MD.BOOST, "immune": MD.IMMUNE, "multi": MULTI, "fixed": MD.FIXED,
            "evos": {n: [{"to": e["to"], "kind": e["kind"], "p": e["p"]} for e in d["evos"]] for n, d in MONS.items() if d["evos"]},
            "modes": index, "areas": list(areas.values()), "splits": SPLITS, "tm": {tm: [mv, w, g] for tm, mv, w, g in TMS}}
    dump(f"{OUT}/meta.json", meta)
    dump(f"{OUT}/trainers.json", trainers)
    # ---- tooltips: the hack's own move and ability text
    ab = {v["name"]: v["description"] for v in J("abilities.json").values() if v["name"] and v["name"] != "-------"}
    mv = {m["name"]: [m["accuracy"] or "—", m["pp"], m["description"], ("Priority " + ("+" if m["priority"] > 0 else "") + str(m["priority"])) if m["priority"] else ""]
          for k, m in MOVESJ.items() if k != "MOVE_NONE"}
    dump(f"{OUT}/text.json", {"ab": ab, "mv": mv})
    # ---- ids for the save reader
    items = {}
    val = -1
    for line in open(f"{SRC}/include/constants/items.h"):
        m = re.match(r"\s*(ITEM_\w+)\s*(?:=\s*(\w+))?\s*,", line)
        if not m or m.group(1) in ("ITEMS_COUNT",): continue
        if m.group(2) is not None:
            if m.group(2).isdigit(): val = int(m.group(2))
            else: continue
        else: val += 1
        items.setdefault(val, m.group(1))
    names = {}
    txt = open(f"{SRC}/src/data/items.h", encoding="utf-8").read()
    for m in re.finditer(r"\[(ITEM_\w+)\]\s*=\s*\{\s*\.name\s*=\s*(?:ITEM_NAME|_|COMPOUND_STRING)\(\"([^\"]*)\"\)", txt): names[m.group(1)] = m.group(2)
    IT = [""] * (max(items) + 1)
    for i, c in items.items(): IT[i] = names.get(c) or c[5:].replace("_", " ").title()
    IT[0] = ""
    nmax = max(BYID)
    gr = {}
    for f in os.listdir(f"{SRC}/src/data/pokemon/species_info"):
        t = open(f"{SRC}/src/data/pokemon/species_info/{f}", encoding="utf-8").read()
        for m in re.finditer(r"\[(SPECIES_\w+)\]\s*=\s*\{(.*?)\n    \}", t, re.S):
            g = re.search(r"\.growthRate\s*=\s*(GROWTH_\w+)", m.group(2))
            if g: gr[m.group(1)] = g.group(1)
    GRN = ["GROWTH_MEDIUM_FAST", "GROWTH_ERRATIC", "GROWTH_FLUCTUATING", "GROWTH_MEDIUM_SLOW", "GROWTH_FAST", "GROWTH_SLOW"]
    sp = [""] * (nmax + 1); grl = [0] * (nmax + 1); abl = [None] * (nmax + 1); dex = {}
    for n, d in MONS.items():
        sp[d["id"]] = n; grl[d["id"]] = GRN.index(gr[d["const"]]) if gr.get(d["const"]) in GRN else 0; abl[d["id"]] = d["abs"]
        if d["no"] and (d["no"] not in dex or d["id"] < MONS[dex[d["no"]]]["id"]): dex[d["no"]] = n
    nmv = max(m["id"] for m in MOVESJ.values())
    mvl = [""] * (nmv + 1)
    for m in MOVESJ.values(): mvl[m["id"]] = m["name"] if m["id"] else ""
    dump(f"{OUT}/ids.json", {"species": sp, "gr": grl, "abil": abl, "moves": mvl, "items": IT, "loc": [fixarea(SECNAME.get(x["id"], "")) for x in SECS],
                             "natures": list(MD.NATURES)})
    print(sum(len(v["fights"]) for v in index.values()), "fights", cells, "cells", len(areas), "areas",
          {m: sum(len(s["trainers"]) for s in trainers[m]) for m in trainers})

if __name__ == "__main__":
    main()
