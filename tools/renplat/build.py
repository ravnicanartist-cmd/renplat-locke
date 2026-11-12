"""Build every JSON file the site loads.

Sources, in this order:
  1. The PChal Renegade Platinum ROM the player uses (species stats/types/abilities, learnsets, TM compatibility,
     evolutions, move data, trainer teams).  It was cross-checked against the documentation: it matches the
     "Complete" patch except for a handful of listed differences, which are reported by verify.py.
  2. The Renegade Platinum documentation workbook (trainer natures and abilities, wild areas, gifts, TM locations,
     move tutors).
  3. story.py (hand-written story order and when things become obtainable).
"""
import json, math, re, struct, sys
from collections import OrderedDict
from common import clean, grid, dump, mon_name
from rom import narc, messages, msgfile
import story as S
from ex_trainers import all_trainers
from ex_enc import blocks, method_kind

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/site/data"
MSG = messages()
SPN, MVN, ITN, ABN = (msgfile(MSG[i]) for i in (412, 647, 392, 610))
GT = ['Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel', 'Fairy', 'Fire', 'Water',
      'Grass', 'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark']
GROWTH = ["Medium Fast", "Erratic", "Fluctuating", "Medium Slow", "Fast", "Slow"]
KEY = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("♀", "f").replace("♂", "m"))

def sname(i):
    return SPN[i].replace("♀", "-F").replace("♂", "-M").replace("’", "'")
FORMS = {496: "Deoxys-Attack", 497: "Deoxys-Defense", 498: "Deoxys-Speed", 499: "Wormadam-Sandy", 500: "Wormadam-Trash",
         501: "Giratina-Origin", 502: "Shaymin-Sky", 503: "Rotom-Heat", 504: "Rotom-Wash", 505: "Rotom-Frost",
         506: "Rotom-Fan", 507: "Rotom-Mow"}
FORM_OF = {("Rotom", 1): "Rotom-Heat", ("Rotom", 2): "Rotom-Wash", ("Rotom", 3): "Rotom-Frost", ("Rotom", 4): "Rotom-Fan",
           ("Rotom", 5): "Rotom-Mow", ("Wormadam", 1): "Wormadam-Sandy", ("Wormadam", 2): "Wormadam-Trash",
           ("Giratina", 1): "Giratina-Origin", ("Shaymin", 1): "Shaymin-Sky", ("Deoxys", 1): "Deoxys-Attack",
           ("Deoxys", 2): "Deoxys-Defense", ("Deoxys", 3): "Deoxys-Speed"}
ROTOM_MOVE = {"Rotom-Heat": "Overheat", "Rotom-Wash": "Hydro Pump", "Rotom-Frost": "Blizzard", "Rotom-Fan": "Air Slash",
              "Rotom-Mow": "Leaf Storm"}
DOCNAME = {"Wormadam (P)": "Wormadam", "Wormadam (S)": "Wormadam-Sandy", "Wormadam (T)": "Wormadam-Trash",
           "Wormadam (Plant)": "Wormadam", "Wormadam (Sandy)": "Wormadam-Sandy", "Wormadam (Trash)": "Wormadam-Trash",
           "Rotom (Heat)": "Rotom-Heat", "Rotom (Wash)": "Rotom-Wash", "Rotom (Frost)": "Rotom-Frost",
           "Rotom (Spin)": "Rotom-Fan", "Rotom (Cut)": "Rotom-Mow", "Giratina (Origin)": "Giratina-Origin",
           "Giratina (Altered)": "Giratina", "Shaymin (Land)": "Shaymin", "Shaymin (Sky)": "Shaymin-Sky",
           "Deoxys (Normal)": "Deoxys", "Deoxys (Attack)": "Deoxys-Attack", "Deoxys (Defense)": "Deoxys-Defense",
           "Deoxys (Speed)": "Deoxys-Speed", "Giratina": "Giratina", "Shaymin": "Shaymin"}

# ------------------------------------------------------------------ species, learnsets, moves (ROM)
PB = narc('poketool/personal/pl_personal.narc')
WO = narc('poketool/personal/wotbl.narc')
EV = narc('poketool/personal/evo.narc')
WZ = narc('poketool/waza/pl_waza_tbl.narc')
IDX = {}            # name -> personal index
MONS = OrderedDict()
for i in list(range(1, 494)) + list(FORMS):
    b = PB[i]
    n = FORMS.get(i) or sname(i)
    t = [GT[b[6]]] + ([GT[b[7]]] if b[7] != b[6] else [])
    ab = [ABN[b[0x16]]] + ([ABN[b[0x17]]] if b[0x17] and b[0x17] != b[0x16] else [])
    bs = [b[0], b[1], b[2], b[4], b[5], b[3]]       # hp at df sa sd sp
    no = i if i < 494 else {496: 386, 497: 386, 498: 386, 499: 413, 500: 413, 501: 487, 502: 492}.get(i, 479)
    MONS[n] = {"no": no, "t": t, "bs": bs, "ab": ab, "gr": b[0x13]}
    IDX[n] = i
BYKEY = {KEY(n): n for n in MONS}
def canon(n):
    n = DOCNAME.get(n, n)
    return BYKEY.get(KEY(n), n)

CAT = ["Physical", "Special", "Status"]
MOVES = {}
for i in range(1, 468):
    b = WZ[i]
    MOVES[MVN[i]] = {"t": GT[b[4]], "c": CAT[b[2]], "bp": b[3], "acc": b[5], "pp": b[6], "id": i}
MKEY = {KEY(m): m for m in MOVES}
MKEY.update({"visegrip": "Vice Grip", "drllrun": "Drill Run", "twinneedle": "Twineedle", "hijumpkick": MKEY.get("highjumpkick", "Hi Jump Kick")})
def mcanon(m):
    return MKEY.get(KEY(m), m)

LV = {}
for n, i in IDX.items():
    b, l = WO[i], []
    for k in range(0, len(b) - 1, 2):
        v = struct.unpack_from('<H', b, k)[0]
        if v == 0xFFFF: break
        l.append([v >> 9, MVN[v & 0x1FF]])
    LV[n] = l
for n in list(LV):           # forms without their own learnset use the base form's
    if not LV[n] and "-" in n and n.split("-")[0] in LV: LV[n] = LV[n.split("-")[0]]

# TM list (number -> move) and locations, from the documentation
TMLIST, TMLOC = {}, {}
g = grid("iTEMSTMs")
for r in g:
    for b in (26, 35, 44):
        c = clean(r[b])
        m = re.match(r"(TM|HM)(\d+)\s+(.+)$", c)
        if m:
            k = f"{m.group(1)}{int(m.group(2)):02d}"
            TMLIST[k] = mcanon(m.group(3)); TMLOC[k] = f"{clean(r[b + 5])} ({clean(r[b + 6]).lower()})"
TMORDER = [f"TM{i:02d}" for i in range(1, 93)] + [f"HM{i:02d}" for i in range(1, 9)]
TMS = {}
for n, i in IDX.items():
    bits = int.from_bytes(PB[i][0x1C:0x1C + 13], "little")
    TMS[n] = [TMORDER[k] for k in range(100) if bits >> k & 1]

# Move tutors (documentation; PChal puts every tutor in the PC after Maylene).  Special tutors are left out.
TUT = {}
g = grid("LEARNSETS")
sec = {clean(r[0]).upper().split(" ")[0]: i for i, r in enumerate(g) if clean(r[0])}
tu0 = next(i for i, r in enumerate(g) if clean(r[0]).upper().startswith("MOVE TUTOR"))
for j, h in enumerate(g[0]):
    if not clean(h).startswith("#"): continue
    n = canon(mon_name(h))
    if n not in MONS: continue
    lst = []
    for i in range(tu0 + 1, len(g)):
        c = clean(g[i][j])
        if c.lower().startswith("special tutor"): break
        if c and c not in ("N", "-", "ALL") and not c.lower().startswith("move tutor"):
            lst.append(mcanon(c))
    TUT[n] = lst
TUT["Rotom"] = TUT.get("Rotom", [])
for f in ROTOM_MOVE: TUT[f] = TUT["Rotom"]

# Evolutions (ROM)
EVM = {1: 'friendship', 2: 'friendship', 3: 'friendship', 4: 'level', 5: 'trade', 6: 'tradeitem', 7: 'item', 8: 'level',
       9: 'level', 10: 'level', 11: 'level', 12: 'level', 13: 'level', 14: 'shedinja', 15: 'beauty', 16: 'item',
       17: 'item', 18: 'helditem', 19: 'helditem', 20: 'move', 21: 'teammate', 22: 'level', 23: 'level', 24: 'place',
       25: 'place', 26: 'place'}
EVOS = {}
for n, i in IDX.items():
    if i >= 494: continue
    b = EV[i]
    for k in range(0, len(b) - 5, 6):
        m, p, t = struct.unpack_from('<HHH', b, k)
        if m == 0: continue
        kind = EVM.get(m, "?")
        to = sname(t)
        if n == "Burmy" and m == 23: to = "Wormadam"
        par = p if kind in ("level", "beauty", "shedinja") else ITN[p] if kind in ("item", "helditem", "tradeitem") else MVN[p] if kind == "move" else sname(p) if kind == "teammate" else p
        EVOS.setdefault(n, []).append({"to": to, "kind": kind, "p": par})
EVOS.setdefault("Burmy", []).extend([{"to": "Wormadam-Sandy", "kind": "level", "p": 20}, {"to": "Wormadam-Trash", "kind": "level", "p": 20}])
PRE = {}
for a, l in EVOS.items():
    for e in l:
        PRE.setdefault(e["to"], a)
def root(n):
    n = n.split("-")[0] if n.startswith(("Rotom-", "Wormadam-")) else n
    while n in PRE: n = PRE[n]
    return n
for n in MONS: MONS[n]["fam"] = root(n)

# ------------------------------------------------------------------ story order
ORDER = {}
FIGHTS, TR = [], {t["id"]: t for t in all_trainers()[::-1]}   # first listing wins
TRALL = all_trainers()
TP = narc('poketool/trainer/trpoke.narc'); TD = narc('poketool/trainer/trdata.narc')
def rom_team(tid):
    d, p = TD[tid], TP[tid]
    flags, n = d[0], d[3]
    hasm, hasi = flags & 1, flags & 2
    sz = 6 + (2 if hasi else 0) + (8 if hasm else 0) + 2
    out = []
    for k in range(n):
        o = k * sz
        diff, abg, lv, spf = struct.unpack_from('<BBHH', p, o); q = o + 6
        item = ""
        if hasi:
            item = ITN[struct.unpack_from('<H', p, q)[0]]; q += 2
            if item in ("None", "-"): item = ""
        mv = []
        if hasm:
            mv = [MVN[x] for x in struct.unpack_from('<4H', p, q) if x]; q += 8
        base = sname(spf & 0x3FF)
        sp = FORM_OF.get((base, spf >> 10), base)
        if not mv:   # default moves: the last four level-up moves at or below its level
            seen = []
            for l, m in LV[sp]:
                if l <= lv and m not in seen: seen.append(m)
            mv = seen[-4:]
        out.append({"s": sp, "l": lv, "i": item, "m": mv, "iv": diff * 31 // 255})
    return out

_RP = None
def calc_sets():
    global _RP
    if _RP is None:
        t = open("/home/claude/repo/calc/backups/rp.js", encoding="utf-8").read()
        j = json.loads(t[t.index("{"):t.rindex("}") + 1])
        _RP = {}
        for sp, d in j["formatted_sets"].items():
            for n, v in d.items():
                _RP.setdefault(v.get("tr_id"), []).append((sp, n))
    return _RP

def boss_team(tid):
    team = rom_team(tid)
    sets = list(calc_sets().get(tid, []))
    for m in team:
        k = KEY(m["s"])
        hit = next((x for x in sets if KEY(x[0].replace("-Glitched", "")) == k), None)
        if hit:
            m["calc"] = f"{hit[0]} ({hit[1]})"; sets.remove(hit)
    doc = next((t for t in TRALL if t["id"] == tid and t["team"]), None)
    for k, m in enumerate(team):
        d = doc["team"][k] if doc and k < len(doc["team"]) else None
        if d and canon(d["s"]).split("-")[0] == m["s"].split("-")[0]:
            m["n"] = d["n"] if d["n"] in NATURES else "Hardy"
            m["a"] = d["a"] if d["a"] else MONS[m["s"]]["ab"][0]
            if None not in d["bs"] and d["bs"] != MONS[m["s"]]["bs"]:
                m["bs"] = d["bs"]          # the documented in-game stats (Volkner's Rotoms bug)
        else:
            m["n"] = "Hardy"; m["a"] = MONS[m["s"]]["ab"][0]
        m["a"] = {"Compoundeyes": "Compound Eyes"}.get(m["a"], m["a"])
    return team

NATURES = OrderedDict([("Hardy", None), ("Lonely", ["at", "df"]), ("Brave", ["at", "sp"]), ("Adamant", ["at", "sa"]),
    ("Naughty", ["at", "sd"]), ("Bold", ["df", "at"]), ("Docile", None), ("Relaxed", ["df", "sp"]), ("Impish", ["df", "sa"]),
    ("Lax", ["df", "sd"]), ("Timid", ["sp", "at"]), ("Hasty", ["sp", "df"]), ("Serious", None), ("Jolly", ["sp", "sa"]),
    ("Naive", ["sp", "sd"]), ("Modest", ["sa", "at"]), ("Mild", ["sa", "df"]), ("Quiet", ["sa", "sp"]), ("Bashful", None),
    ("Rash", ["sa", "sd"]), ("Calm", ["sd", "at"]), ("Gentle", ["sd", "df"]), ("Sassy", ["sd", "sp"]),
    ("Careful", ["sd", "sa"]), ("Quirky", None)])

STARTERS = ["Turtwig", "Chimchar", "Piplup"]
def variant_of(tid):
    t = TR.get(tid, {"notes": [], "name": "", "var": ""})
    txt = " ".join(t["notes"]).upper()
    v = {}
    m = re.search(r"IF YOU CHOSE (TURTWIG|CHIMCHAR|PIPLUP)", txt)
    if m: v["starter"] = m.group(1).title()
    if "Dawn" in t["name"]: v["gender"] = "M"
    if "Lucas" in t["name"]: v["gender"] = "F"
    if t["var"]: v["team"] = int(float(t["var"]))
    return v

for idx, (key, tabs, ids, kind) in enumerate(S.FIGHTS):
    ORDER[key] = idx
for idx, (key, tabs, ids, kind) in enumerate(S.FIGHTS):
    first = TR[ids[0]]
    split = first["split"]
    cap = S.CAPS[split]
    if key == "byron": cap = 53
    if kind in ("multi", "gauntlet"):
        variants = [{"v": {}, "ids": ids}]
    else:
        variants = [{"v": variant_of(i), "ids": [i]} for i in ids]
    names = sorted({TR[i]["name"] for i in ids})
    label = S.LABELS.get(key) or (" + ".join(n.replace("Gym Leader ", "").replace("Elite Four ", "").replace("Champion ", "")
                                             .replace("Galactic Boss ", "").replace("Commander ", "") for n in names[:2]))
    if kind is None and len(ids) == 1 and "Grunt" in first["name"]:
        label = f"Galactic Grunt ({first['loc']})"
    FIGHTS.append({"key": key, "tabs": tabs, "label": label, "cap": cap, "split": split, "loc": first["loc"],
                   "kind": kind, "variants": variants, "names": names,
                   "notes": [n for i in ids[:1] for n in TR[i]["notes"] if not n.startswith("(")][:4],
                   "note": S.NOTE.get(key, "")})

def unlocked(k, fi):
    if k is None or k == "post": return False
    return k == "" or ORDER[k] < fi

# ------------------------------------------------------------------ what the player can obtain
B = blocks()
AREAS = []          # display names
def areaname(b):
    a = (b["sub"] or b["area"]).title().replace("Mt.", "Mt.").replace("Pokemon", "Pokémon")
    return re.sub(r"\bR(\d+)\b", r"R\1", a)
missing = set()
RATE = {}
SOURCES = []        # (species, area display, method label, gate list)
for b in B:
    kind = method_kind(b["method"])
    ak = b["sub"] if b["sub"] in S.AREA else b["area"]
    if ak not in S.AREA:
        missing.add(ak); continue
    gate = S.AREA[ak]
    an = areaname(b)
    LOCN = {"Area 1 And 2": "Great Marsh", "Area 3 And 4": "Great Marsh", "Area 5 And 6": "Great Marsh"}
    loc = re.sub(r"\s*\(.*\)$", "", b["area"]).title().replace("Pokemon", "Pokémon")
    loc = LOCN.get(loc, loc)
    mlv = re.search(r"\((\d+)", b["method"])
    mlv = int(mlv.group(1)) if mlv and kind in ("grass", "cave", "ground", "other", "surf", "honey tree") else 0
    for m in b["mons"]:
        sp = canon(m["s"])
        if sp not in MONS or sp in S.LEGENDARY or m["s"] in S.LEGENDARY: continue
        def pc(i):
            try: return float(m["v"][i] or 0)
            except (ValueError, IndexError): return 0.0
        if kind in ("grass", "cave", "ground", "other"):
            rr = RATE.setdefault((sp, an, kind), [0, 0, 0])
            for i in range(3): rr[i] += pc(i + 1)
        elif kind in ("surf", "honey tree"):
            rr = RATE.setdefault((sp, an, kind), [0]); rr[0] += pc(1)
        elif kind == "rods":
            for col, rod in ((1, "Old Rod"), (2, "Good Rod"), (3, "Super Rod")):
                rr = RATE.setdefault((sp, an, rod), [0]); rr[0] += pc(col)
        if f"{m['s']}@{b['area']}" in S.REMOVED: continue
        v = m["v"]
        if kind in ("grass", "cave", "ground", "other"):
            SOURCES.append((sp, an, kind, [gate], mlv, loc))
        elif kind == "surf":
            SOURCES.append((sp, an, "surf", [gate, S.SURF], mlv, loc))
        elif kind == "rods":
            for col, rod in ((1, "O"), (2, "G"), (3, "S")):
                try: ok = float(v[col] or 0) > 0
                except ValueError: ok = False
                if ok: SOURCES.append((sp, an, {"O": "Old Rod", "G": "Good Rod", "S": "Super Rod"}[rod], [gate, S.RODS[rod]], 0, loc))
        elif kind == "honey tree":
            SOURCES.append((sp, an, "honey tree", [gate, S.HONEY], mlv, loc))
        elif kind == "poké radar":
            continue
        elif kind == "trade":
            if "get" in (v[1] or ""): SOURCES.append((sp, an, "trade", [gate], 0, loc))
        else:   # gift / static / egg / revive
            if m["s"] in S.SPECIAL or sp in S.SPECIAL:
                g2 = S.SPECIAL.get(m["s"], S.SPECIAL.get(sp))
                SOURCES.append((sp, an, {"static": "static", "egg": "egg", "revive": "fossil"}.get(kind, "gift"), [g2], 0, loc))
if missing: print("UNMAPPED AREAS", missing)

BASESET = set()
def evo_ok(e, n, fi, cap):
    k, p = e["kind"], e["p"]
    if k in ("level", "shedinja"): return p <= cap
    if k == "friendship": return True                              # PChal: friendship evolutions are instant
    if k in ("item", "helditem", "tradeitem"):
        return unlocked(S.EVO_ITEM.get(p, None), fi)
    if k == "move":
        return any(l <= cap for l, m in LV[n] if m == p) or any(TMLIST.get(t) == p and unlocked(S.TM.get(t), fi) for t in TMS[n])
    if k == "teammate": return p in BASESET
    if k == "place": return unlocked(S.EVO_ITEM["Mt. Coronet"], fi)
    return False

def chain(n):
    c = [n]
    while c[-1] in PRE: c.append(PRE[c[-1]])
    return c[::-1]

def evolve(base, fi, cap):
    """All final forms reachable from base by the cap; returns [(species, [path])]"""
    out = []
    def go(n, path):
        nxt = [e for e in EVOS.get(n, []) if evo_ok(e, n, fi, cap) and e["to"] in MONS]
        seen = set()
        nxt = [e for e in nxt if not (e["to"] in seen or seen.add(e["to"]))]
        if not nxt: out.append((n, path))
        for e in nxt: go(e["to"], path + [e["to"]])
    go(base, [base])
    return out

def evo_level(a, b):
    for e in EVOS.get(a, []):
        if e["to"] == b and e["kind"] in ("level", "shedinja"): return e["p"]
    return None

def learnable(n, path, fi, cap):
    mv = set()
    remind = unlocked(S.MOVE_REMINDER, fi)
    for k, sp in enumerate(path):
        top = cap
        if k + 1 < len(path):
            el = evo_level(sp, path[k + 1])
            top = min(cap, el) if el else cap
        for l, m in LV.get(sp, []):
            if l <= top and (l > 1 or remind): mv.add(m)
    for t in TMS.get(n, []):
        if unlocked(S.TM.get(t), fi) and t in TMLIST: mv.add(TMLIST[t])
    if unlocked(S.TUTORS, fi):
        mv.update(TUT.get(n, []))
    if n in ROTOM_MOVE: mv.add(ROTOM_MOVE[n])
    return mv

FIXED = {"Seismic Toss": "level", "Night Shade": "level", "Dragon Rage": 40, "Sonic Boom": 20}
MULTI = {"Fury Attack": 3, "Twineedle": 2, "Pin Missile": 3, "Double Kick": 2, "Bullet Seed": 3, "Icicle Spear": 3,
         "Rock Blast": 3, "Arm Thrust": 3, "Fury Swipes": 3, "Double Hit": 2, "Bonemerang": 2, "Double Slap": 3,
         "Comet Punch": 3, "Bone Rush": 3, "Spike Cannon": 3, "Triple Kick": 3}
def damaging(m):
    d = MOVES.get(m)
    return d is not None and (m in FIXED or (d["c"] != "Status" and d["bp"] > 1))

def pool(fi, cap):
    base = {}
    locs = {}
    for sp, an, how, gates, mlv, loc in SOURCES:
        if mlv <= cap and all(unlocked(g, fi) for g in gates):
            base.setdefault(sp, []).append(f"{an} ({how})")
            if how not in ("gift", "egg", "fossil", "trade", "static"): locs.setdefault(sp, set()).add(loc)
    BASESET.clear(); BASESET.update(base)
    rows = {}
    for b, where in base.items():
        for fin, path in evolve(b, fi, cap):
            r = rows.setdefault(fin, {"s": fin, "from": [], "where": [], "path": path, "areas": set()})
            r["areas"] |= locs.get(b, set())
            if b not in r["from"]: r["from"].append(b)
            for w in where:
                if w not in r["where"]: r["where"].append(w)
            if len(path) > len(r["path"]): r["path"] = path
    if "Rotom" in rows and unlocked("jupiter_eterna", fi):       # Secret Key: Rotom's forms
        for f in ROTOM_MOVE:
            rows[f] = {"s": f, "from": ["Rotom"], "where": rows["Rotom"]["where"] + ["Rotom room (Secret Key)"], "path": ["Rotom", f], "areas": rows["Rotom"]["areas"]}
    out = []
    for n in sorted(rows):
        r = rows[n]
        mv = sorted(m for m in learnable(n, r["path"], fi, cap) if damaging(m))
        out.append({"s": n, "from": r["from"], "where": r["where"][:6], "moves": mv, "ab": MONS[n]["ab"][0], "areas": sorted(r["areas"])})
    return out

# ------------------------------------------------------------------ the 1-on-1 model (JavaScript copy in model.js)
CHART = {}
def se(a, ds, v):
    for d in ds.split(): CHART.setdefault(a, {})[d] = v
for a, s2, h, z in [
    ("Normal", "", "Rock Steel", "Ghost"), ("Fire", "Grass Ice Bug Steel", "Fire Water Rock Dragon", ""),
    ("Water", "Fire Ground Rock", "Water Grass Dragon", ""), ("Electric", "Water Flying", "Electric Grass Dragon", "Ground"),
    ("Grass", "Water Ground Rock", "Fire Grass Poison Flying Bug Dragon Steel", ""),
    ("Ice", "Grass Ground Flying Dragon", "Fire Water Ice Steel", ""),
    ("Fighting", "Normal Ice Rock Dark Steel", "Poison Flying Psychic Bug Fairy", "Ghost"),
    ("Poison", "Grass Fairy", "Poison Ground Rock Ghost", "Steel"), ("Ground", "Fire Electric Poison Rock Steel", "Grass Bug", "Flying"),
    ("Flying", "Grass Fighting Bug", "Electric Rock Steel", ""), ("Psychic", "Fighting Poison", "Psychic Steel", "Dark"),
    ("Bug", "Grass Psychic Dark", "Fire Fighting Poison Flying Ghost Steel Fairy", ""),
    ("Rock", "Fire Ice Flying Bug", "Fighting Ground Steel", ""), ("Ghost", "Psychic Ghost", "Dark", "Normal"),
    ("Dragon", "Dragon", "Steel", "Fairy"), ("Dark", "Psychic Ghost", "Fighting Dark Fairy", ""),
    ("Steel", "Ice Rock Fairy", "Fire Water Electric Steel", ""), ("Fairy", "Fighting Dragon Dark", "Fire Poison Steel", "")]:
    se(a, s2, 2); se(a, h, 0.5); se(a, z, 0)
BOOST = {"Charcoal": "Fire", "Mystic Water": "Water", "Magnet": "Electric", "Miracle Seed": "Grass", "NeverMeltIce": "Ice",
         "Never-Melt Ice": "Ice", "Black Belt": "Fighting", "Poison Barb": "Poison", "Soft Sand": "Ground", "Sharp Beak": "Flying",
         "TwistedSpoon": "Psychic", "Twisted Spoon": "Psychic", "SilverPowder": "Bug", "Silver Powder": "Bug", "Hard Stone": "Rock",
         "Spell Tag": "Ghost", "Dragon Fang": "Dragon", "BlackGlasses": "Dark", "Black Glasses": "Dark", "Metal Coat": "Steel",
         "Silk Scarf": "Normal", "Flame Plate": "Fire", "Splash Plate": "Water", "Zap Plate": "Electric", "Meadow Plate": "Grass",
         "Icicle Plate": "Ice", "Fist Plate": "Fighting", "Toxic Plate": "Poison", "Earth Plate": "Ground", "Sky Plate": "Flying",
         "Mind Plate": "Psychic", "Insect Plate": "Bug", "Stone Plate": "Rock", "Spooky Plate": "Ghost", "Draco Plate": "Dragon",
         "Dread Plate": "Dark", "Iron Plate": "Steel", "Sea Incense": "Water", "Wave Incense": "Water", "Odd Incense": "Psychic",
         "Rock Incense": "Rock", "Rose Incense": "Grass"}
IMMUNE = {"Levitate": "Ground", "Flash Fire": "Fire", "Water Absorb": "Water", "Storm Drain": "Water", "Dry Skin": "Water",
          "Volt Absorb": "Electric", "Lightning Rod": "Electric", "Motor Drive": "Electric", "Sap Sipper": "Grass"}
KEYS6 = ["hp", "at", "df", "sa", "sd", "sp"]

def stats(bs, lv, iv, nature):
    nat = NATURES.get(nature) or [None, None]
    st = {}
    for i, k in enumerate(KEYS6):
        b = bs[i]
        if k == "hp": st[k] = (2 * b + iv) * lv // 100 + lv + 10
        else: st[k] = math.floor(((2 * b + iv) * lv // 100 + 5) * (1.1 if k == nat[0] else 0.9 if k == nat[1] else 1))
    return st

def mon(name, lv, iv=15, nature="Hardy", ab=None, item="", moves=(), bs=None):
    d = MONS[name]
    return {"name": name, "lv": lv, "t": d["t"], "ab": ab or d["ab"][0], "item": item, "moves": list(moves),
            "st": stats(bs or d["bs"], lv, iv, nature)}

def eff(mt, types):
    x = 1
    for t in types: x = x * CHART.get(mt, {}).get(t, 1)
    return x

def damage(a, d, move, intim):
    m = MOVES.get(move)
    if not m: return 0
    mt, cat, bp = m["t"], m["c"], m["bp"]
    if move in FIXED:
        return 0 if eff(mt, d["t"]) == 0 else (a["lv"] if FIXED[move] == "level" else FIXED[move])
    if not bp or bp <= 1 or cat == "Status": return 0
    phys = cat == "Physical"
    A = a["st"]["at" if phys else "sa"]; D = d["st"]["df" if phys else "sd"]
    if phys and a["ab"] in ("Huge Power", "Pure Power"): A *= 2
    if phys and intim: A = A * 2 // 3
    if a["ab"] == "Technician" and bp <= 60: bp *= 1.5
    base = math.floor(math.floor(math.floor(2 * a["lv"] / 5 + 2) * bp * A / D) / 50) + 2
    stab = (2 if a["ab"] == "Adaptability" else 1.5) if mt in a["t"] else 1
    item = 1.2 if BOOST.get(a["item"]) == mt else 1.3 if a["item"] == "Life Orb" else 1.5 if ((a["item"] == "Choice Band" and phys) or (a["item"] == "Choice Specs" and not phys)) else 1
    e = eff(mt, d["t"])
    if IMMUNE.get(d["ab"]) == mt: e = 0
    if d["ab"] == "Thick Fat" and mt in ("Fire", "Ice"): e *= 0.5
    return base * 0.925 * stab * e * item * MULTI.get(move, 1)

def best(a, d, intim):
    if not a["moves"]: return (0, "")
    return max((damage(a, d, m, intim), m) for m in a["moves"])

def matchup(p, b):
    pd, pm = best(p, b, b["ab"] == "Intimidate")
    bd, bm = best(b, p, p["ab"] == "Intimidate")
    first = p["st"]["sp"] >= b["st"]["sp"]
    win = False
    if pd > 0:
        ph = math.ceil(b["st"]["hp"] / pd); bh = math.ceil(p["st"]["hp"] / bd) if bd > 0 else 99
        win = ph <= bh if first else ph < bh
    return [1 if win else 0, pm, round(pd / b["st"]["hp"] * 100 * .85 / .925), round(pd / b["st"]["hp"] * 100 / .925), bm,
            round(bd / p["st"]["hp"] * 100 * .85 / .925), round(bd / p["st"]["hp"] * 100 / .925), 1 if first else 0]

def bossmon(m):
    return mon(m["s"], m["l"], m["iv"], m["n"], m["a"], m["i"], m["m"], m.get("bs"))

# ------------------------------------------------------------------ write
def main():
    import os
    os.makedirs(OUT + "/fights", exist_ok=True)
    index = []
    tabs = {"G": [], "V": [], "R": [], "A": []}
    prevpool = {t: None for t in "GVRA"}
    prevfi = {t: -1 for t in "GVRA"}
    cells = 0
    for fi, F in enumerate(FIGHTS):
        cols, colkey = [], {}
        for v in F["variants"]:
            v["cols"] = []
            for tid in v["ids"]:
                for m in boss_team(tid):
                    k = json.dumps(m, sort_keys=True)
                    if k not in colkey:
                        colkey[k] = len(cols); cols.append(m)
                    v["cols"].append(colkey[k])
        P = pool(fi, F["cap"])
        bms = [bossmon(m) for m in cols]
        grid_ = []
        for r in P:
            pm = mon(r["s"], F["cap"], 15, "Hardy", r["ab"], "", r["moves"])
            grid_.append([matchup(pm, b) for b in bms]); cells += len(bms)
        mytabs = [t for t in F["tabs"]] + ["A"]
        new = {}
        for t in mytabs:
            pp = prevpool[t]
            new[t] = [i for i, r in enumerate(P) if pp is not None and r["s"] not in pp]
            # TMs / evolution items that became obtainable since the previous fight in this tab
            lo = prevfi[t]
            F.setdefault("since", {})[t] = {
                "tm": [f"{k} {TMLIST[k]} — {TMLOC.get(k, '')}" for k in TMORDER if k in TMLIST and S.TM.get(k) not in (None, "post") and (S.TM[k] == "" or lo < ORDER[S.TM[k]] < fi)],
                "items": sorted(k for k, g2 in S.EVO_ITEM.items() if g2 and lo < ORDER[g2] < fi and k != "Mt. Coronet"),
                "rods": [{"O": "Old Rod", "G": "Good Rod", "S": "Super Rod"}[r] for r, g2 in S.RODS.items() if lo < ORDER[g2] < fi],
                "other": ([s for s, g2 in (("Surf", S.SURF), ("Move reminder (Lv 1 moves)", S.MOVE_REMINDER), ("Move tutors in the PC", S.TUTORS)) if lo < ORDER[g2] < fi])}
            prevpool[t] = {r["s"] for r in P}; prevfi[t] = fi
        data = {"key": F["key"], "label": F["label"], "cap": F["cap"], "team": cols,
                "variants": [{"v": v["v"], "cols": v["cols"]} for v in F["variants"]],
                "pool": P, "grid": grid_, "new": new, "since": F["since"]}
        dump(f"{OUT}/fights/{F['key']}.json", data)
        ent = {k: F[k] for k in ("key", "label", "cap", "split", "loc", "kind", "notes", "note", "names")}
        ent["ids"] = sorted({i for v in F["variants"] for i in v["ids"]})
        ent["vars"] = [v["v"] for v in F["variants"]]
        ent["n"] = len(P)
        if F["key"] in S.PARTNERS: ent["partner"] = S.PARTNERS[F["key"]]
        index.append(ent)
        for t in mytabs: tabs[t].append(F["key"])
    meta = {"mons": {n: {"no": d["no"], "t": d["t"], "bs": d["bs"], "ab": d["ab"], "fam": d["fam"], "gr": d["gr"]} for n, d in MONS.items()},
            "moves": {m: [d["t"], d["c"], d["bp"]] for m, d in MOVES.items()},
            "chart": CHART, "natures": {k: v for k, v in NATURES.items() if v}, "boost": BOOST, "immune": IMMUNE,
            "multi": MULTI, "fixed": FIXED, "evos": EVOS, "tabs": tabs, "fights": index,
            "tm": {k: [TMLIST[k], TMLOC.get(k, ""), S.TM.get(k)] for k in TMORDER if k in TMLIST},
            "order": {k: v for k, v in ORDER.items()}}
    # Nuzlocke areas (in-game location names), in story order, with what can be found there
    areas = OrderedDict()
    for sp, an, how, gates, mlv, loc in SOURCES:
        a = areas.setdefault(loc, {"name": loc, "gate": None, "mons": []})
        g0 = max((ORDER.get(g, -1) if g not in (None, "post") else 999 for g in gates), default=-1)
        if g0 < 999 and (a["gate"] is None or g0 < a["gate"]): a["gate"] = g0
        rr = [round(x) for x in RATE.get((sp, an, how), [])]
        a["mons"].append([sp, an, how, g0, mlv] + ([rr[0] if len(set(rr)) == 1 else rr] if any(rr) else []))
    AL = [a for a in areas.values()]
    AL.sort(key=lambda a: (a["gate"] if a["gate"] is not None else 999))
    meta["areas"] = AL
    dump(f"{OUT}/meta.json", meta)
    # save-reader id tables (ROM text)
    ids = {"species": [sname(i) for i in range(494)], "moves": MVN[:468], "items": ITN, "abilities": ABN,
           "natures": list(NATURES), "g4": "".join(c if c else "\u0000" for c in __import__("rom").G4TAB), "loc": msgfile(MSG[433]), "growth": {n: MONS[n]["gr"] for n in MONS}, "tflag": 1360}
    dump(f"{OUT}/ids.json", ids)
    print(len(FIGHTS), "fights", cells, "cells")
    return meta

if __name__ == "__main__":
    main()
