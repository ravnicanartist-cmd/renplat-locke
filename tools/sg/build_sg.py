"""Sacred Gold (PChal QoL build, HeartGold base) -> data files for the hub site (sg/data).

Sources: the patched ROM (species, learnsets, TM compatibility, evolutions, moves, every trainer's levels / items / moves / IVs),
PChal's workbooks (trainer teams with natures and abilities, must-fight flags, encounters, gifts, items), hzla's calc data
(set ids for calc links), and story_sg.py (story order and when each area / TM / item opens up)."""
import json, re, sys, os, collections
sys.path.insert(0, "/home/claude/build"); sys.path.insert(0, "/home/claude/sg")
import model as MD
import story_sg as S
import rom_sg as R
from common import dump

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/hub/sg/data"
SRC = "/home/claude/sg/src"
KEY = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower().replace("♀", "f").replace("♂", "m"))
AP = lambda s: str(s).replace("’", "'")

# ------------------------------------------------------------------ species and moves (ROM)
MONS = {}
for n, d in R.mons().items():
    MONS[AP(n)] = dict(d, ha="", evos=[dict(e, to=AP(e["to"])) for e in d["evos"]])
BYKEY = {KEY(n): n for n in MONS}
ALIAS = {"nidoranm": "Nidoran-M", "nidoranf": "Nidoran-F", "farfetchd": "Farfetch'd", "mrmime": "Mr. Mime", "mimejr": "Mime Jr.", "flaffy": "Flaaffy", "golden": "Goldeen", "migthyena": "Mightyena"}
def canon(n):
    k = KEY(re.sub(r"\(.*?\)", "", str(n)))
    return ALIAS.get(k) or BYKEY.get(k) or n
MOVES = {n: {"t": m["t"], "c": m["c"], "bp": m["bp"]} for n, m in R.moves().items()}
ROMMOVES = R.moves()
MKEY = {KEY(m): m for m in MOVES}
MKEY.update({"vicegrip": "Vise Grip", "hijumpkick": "High Jump Kick", "faintattack": "Feint Attack", "smellingsalt": "Smelling Salts",
             "sandattack": "Sand Attack", "softboiled": "Soft-Boiled", "selfdestruct": "Self-Destruct", "doubleedge": "Double-Edge"})
def mcanon(m): return MKEY.get(KEY(m), m)
MULTI = {"Double Slap": 3, "Comet Punch": 3, "Fury Attack": 3, "Pin Missile": 3, "Spike Cannon": 3, "Barrage": 3, "Fury Swipes": 3,
         "Bone Rush": 3, "Arm Thrust": 3, "Bullet Seed": 3, "Icicle Spear": 3, "Rock Blast": 3, "Double Kick": 2, "Bonemerang": 2,
         "Twineedle": 2, "Double Hit": 2, "Triple Kick": 3}
MULTI = {k: v for k, v in MULTI.items() if k in MOVES}
# Generation 4 type chart: no Fairy type in Sacred Gold, and Steel still resists Ghost and Dark
CHART = json.loads(json.dumps(MD.CHART))
CHART.pop("Fairy", None)
for a in CHART: CHART[a].pop("Fairy", None)
CHART["Ghost"]["Steel"] = 0.5; CHART["Dark"]["Steel"] = 0.5
MD.MONS, MD.MOVES, MD.MULTI, MD.CHART = MONS, MOVES, MULTI, CHART

PRE = {}
for n, d in MONS.items():
    for e in d["evos"]:
        if e["to"] in MONS: PRE.setdefault(e["to"], n)
def root(n):
    while n in PRE: n = PRE[n]
    return n
for n in MONS: MONS[n]["fam"] = root(n)

# ------------------------------------------------------------------ trainers: docs + ROM + calc set ids
LV = {n: d["lv"] for n, d in MONS.items()}
ROMT = []
for tid in range(min(len(R.TD), len(R.TP))):
    t = R.trainer(tid, LV)
    for m in t["team"]: m["s"] = AP(m["s"])
    ROMT.append(t)
t = open("/home/claude/hub/calc/backups/sgss.js", encoding="utf-8").read()
J = json.loads(t[t.index("{"):t.rindex("}") + 1])
SETS = collections.defaultdict(list)
for sp, d in J["formatted_sets"].items():
    for nm, v in d.items(): SETS[KEY(sp)].append((sp, nm, v))
STOP = ("team", "rocket", "leader", "pkmn", "trainer", "elite", "four", "champion", "executive")
def toks(name): return [w[:4] for w in re.findall(r"[a-z]+", name.lower()) if len(w) >= 3 and w not in STOP]
def name_hit(tname, nm):
    tk, words = toks(tname), re.findall(r"[a-z]+", nm.lower())
    return bool(tk) and all(any(x.startswith(t) for x in words) for t in tk)
def match_set(m, tname=""):
    best, bs = None, -1
    want = {KEY(x) for x in m["m"]}
    for sp, nm, v in SETS.get(KEY(m["s"]), []):
        sc = len(want & {KEY(x) for x in v["moves"]}) * 10 - abs((v["level"] or 0) - (m["l"] or 0)) + (60 if tname and name_hit(tname, nm) else 0)
        if sc > bs: best, bs = (sp, nm, v), sc
    return best if bs >= 25 else None
def rom_match(name, team):
    sig = sorted(KEY(canon(m["s"])) for m in team)
    tk = toks(name)
    hits = [r for r in ROMT if sorted(KEY(m["s"]) for m in r["team"]) == sig]
    named = [r for r in hits if tk and all(any(KEY(r["name"]).startswith(x) or x in KEY(r["name"]) for x in tk[-1:]) for _ in [0])]
    pick = named or (hits if len(hits) == 1 else [])
    if not pick: return None
    lv = [m["l"] for m in team]
    pick.sort(key=lambda r: sum(abs(a["l"] - b) for a, b in zip(r["team"], lv)))
    if sum(abs(a["l"] - b) for a, b in zip(pick[0]["team"], lv)) > 3 * len(lv): return None   # same species, different fight
    return pick[0]

TR = json.load(open("/home/claude/sg/trainers_sg.json"))
ABK = {KEY(a): a for v in MONS.values() for a in v["ab"]}
def fix_shift(m):
    a = m["a"]
    if not a or KEY(a) in ABK: return dict(m, a=ABK.get(KEY(a), a))
    m = dict(m, shifted=True)
    if "(+" in a: m["n"], m["a"], m["i"], m["m"] = a.split(" ")[0], m["i"], (m["m"] or [""])[0], m["m"][1:]
    elif KEY(m["i"]) in MKEY: m["i"], m["m"], m["a"] = ("" if a in ("No Item", "-") else a), [m["i"]] + m["m"], ""
    else: m["i"], m["a"] = a, ""
    if m["i"] in ("No Item", "-"): m["i"] = ""
    m["a"] = ABK.get(KEY(m["a"]), "") if m["a"] else ""
    return m
romfix = collections.Counter()
def team_of(t):
    """the doc team with levels, items, moves and IVs from the ROM where the trainer can be matched"""
    team = [fix_shift(dict(m, s=canon(m["s"]))) for m in t["team"]]
    r = rom_match(t["name"], team)
    out = []
    order = list(r["team"]) if r else []
    for m in team:
        rm = None
        for k, x in enumerate(order):
            if KEY(x["s"]) == KEY(m["s"]): rm = order.pop(k); break
        s2 = m["s"]
        ab = m["a"] if m["a"] in MONS.get(s2, {}).get("ab", []) else (MONS.get(s2, {}).get("ab") or [""])[0]
        e = {"s": s2, "l": m["l"], "n": m["n"] if m["n"] in MD.NATURES else "Hardy", "a": ab, "i": "" if m["i"] in ("No Item", "-") else m["i"],
             "m": [mcanon(x) for x in m["m"] if x and x != "-"], "iv": 31}
        if rm:
            new = {"l": rm["l"], "i": rm["i"], "m": [mcanon(x) for x in rm["m"]], "iv": rm["iv"]}
            if any(e[k] != v for k, v in new.items() if k != "iv"): romfix["fixed from ROM"] += 1
            e.update(new)
        hit = match_set(e, t["name"])
        if hit: e["calc"] = f"{hit[0]} ({hit[1]})"
        out.append(e)
    romfix["matched" if r else "doc only"] += 1
    return out, (r["id"] if r else None)
def rom_boss(tid, tname):
    r = ROMT[tid]
    out = []
    for m in r["team"]:
        e = {"s": m["s"], "l": m["l"], "n": "Hardy", "a": (MONS[m["s"]]["ab"])[min((m["abg"] >> 4) & 1, len(MONS[m["s"]]["ab"]) - 1)],
             "i": m["i"], "m": [mcanon(x) for x in m["m"]], "iv": m["iv"]}
        hit = match_set(e, tname)
        if hit:
            e["calc"] = f"{hit[0]} ({hit[1]})"
            v = hit[2]
            if v.get("nature") in MD.NATURES: e["n"] = v["nature"]
            if v.get("ability") in MONS[m["s"]]["ab"]: e["a"] = v["ability"]
        out.append(e)
    return out

# ------------------------------------------------------------------ encounters
def rows(p):
    r = [l.rstrip("\n").split("\t") for l in open(p, encoding="utf-8")]
    w = max(len(x) for x in r)
    return [x + [""] * (w - len(x)) for x in r]
E = rows(f"{SRC}/Pokemon_Locations/Encounter_Table.tsv")
def basearea(a):
    a = a.split("\\n")[0].strip()
    a = re.split(r"\s+-\s+", a)[0].strip()
    return a
def method(label):
    l = label.lower().replace("\\n", " ")
    if "surf" in l: return "surf", S.SURF
    if "old rod" in l: return "fishing", S.ROD["old"]
    if "good rod" in l: return "fishing", S.ROD["good"]
    if "super rod" in l: return "fishing", S.ROD["super"]
    if "rock smash" in l: return "rock smash", S.ROCKSMASH
    if "sound" in l: return "radio", S.RADIO
    if "night" in l: return "walking (night)", 0
    if "day" in l: return "walking (day)", 0
    return "walking (morning)", 0
RATE = {}
SOURCES, missing, unknown = [], set(), set()
blocks = []
cur = None
for i in range(3, len(E)):
    if E[i][0].strip(): cur = E[i][0]
    blocks.append((i, cur))
for j in range(1, len(E[0])):
    an = E[0][j].strip()
    if not an or E[2][j].strip() != "Pokemon": continue
    loc = basearea(an)
    if loc not in S.AREA: missing.add(loc); continue
    lvl = None; last = None
    for i, lab in blocks:
        if lab is None: continue
        if lab != last: lvl, last = None, lab
        sp = E[i][j].strip()
        lv = [int(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", E[i][j + 2])] if j + 2 < len(E[i]) else []
        if lv: lvl = min(lv)
        if not sp: continue
        if sp.lower().startswith("same as"):          # e.g. Day = "Same as Morning": copy that time's list
            src = "walking (" + sp.split()[-1].lower() + ")"
            how, g = method(lab)
            for x in [x for x in SOURCES if x[1] == an.replace("\\n", " ") and x[2] == src]:
                SOURCES.append((x[0], x[1], how, x[3], x[4], x[5]))
                if (x[0], x[1], src) in RATE: RATE[(x[0], x[1], how)] = RATE[(x[0], x[1], src)]
            continue
        s2 = canon(sp)
        if s2 not in MONS:
            if re.match(r"^[A-Z][a-z]", sp) and len(sp) < 14 and "(" not in sp: unknown.add(sp)
            continue
        how, g = method(lab)
        SOURCES.append((s2, an.replace("\\n", " "), how, max(S.AREA[loc], g), lvl or 0, loc))
        try: RATE[(s2, an.replace("\\n", " "), how)] = (max if how == "fishing" else lambda a, b: a + b)(RATE.get((s2, an.replace("\\n", " "), how), 0), float(E[i][j + 1] or 0) * 100)
        except ValueError: pass
st = rows(f"{SRC}/Pokemon_Locations/Static_Encounters_Gifts_Trade.tsv")
for r in st[2:]:
    sp, where = r[13].strip(), r[14].replace("\\n", " ").strip() if len(r) > 14 else ""
    if not sp: continue
    if "(Storm Silver)" in sp.replace("\\n", " "): continue
    s2 = canon(sp.split("\\n")[0])
    loc = basearea(where.split("(")[0].strip())
    fish = "fishing" in where.lower()
    if s2 in MONS and loc in S.AREA:
        SOURCES.append((s2, f"{where} (swarm)", "swarm", max(S.AREA[loc], S.ROD["good"] if fish else 0), 0, loc))
for sp, an, how, gate, loc in S.GIFTS:
    for s2 in (sp if isinstance(sp, list) else [sp]):
        SOURCES.append((canon(s2), an, how, gate, 0, loc))
if missing: print("UNMAPPED AREAS", missing)
if unknown: print("UNKNOWN SPECIES", sorted(unknown))
SOURCES = [s for s in SOURCES if s[0] in MONS and s[0] not in S.LEGENDARY and s[0] not in S.NOT_IN_GAME]

# ------------------------------------------------------------------ pools
def evo_ok(e, n, stage, cap):
    k = e["kind"]
    if k == "level": return isinstance(e["p"], int) and e["p"] <= cap
    if k == "friendship": return True
    if k in ("item", "helditem"): return S.EVO_ITEM_K.get(KEY(e["p"]), 99) <= stage
    if k == "move": return any(l <= cap and KEY(x) == KEY(e["p"]) for l, x in MONS[n]["lv"])
    if k == "teammate": return True
    if k == "shedinja": return False
    return False
def evolve(b, stage, cap):
    out = []
    def go(n, path):
        nxt = []
        for e in MONS[n]["evos"]:
            if e["to"] in MONS and e["to"] not in nxt and evo_ok(e, n, stage, cap): nxt.append(e["to"])
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
    remind = stage >= S.REMINDER
    for k, sp in enumerate(path):
        top = cap
        if k + 1 < len(path):
            el = evo_level(sp, path[k + 1]); top = min(cap, el) if el else cap
        for l, m in MONS[sp]["lv"]:
            if l <= top and (l > 1 or remind): mv.add(m)
    for m in MONS[n]["tm"]:
        g = S.TM_BY_MOVE.get(KEY(m))
        if g is not None and g <= stage: mv.add(mcanon(m))
    mv.discard("Frustration")      # friendship-based: weak on a Pokemon that likes you
    return mv
def damaging(m):
    d = MOVES.get(m)
    return d is not None and (m in MD.FIXED or (d["c"] != "Status" and d["bp"] > 1))
def pool(stage, cap):
    base, locs = {}, {}
    for sp, an, how, gate, mlv, loc in SOURCES:
        if gate <= stage and mlv <= cap:
            base.setdefault(sp, []).append(f"{an} ({how})")
            if how not in ("gift", "egg", "trade", "static"): locs.setdefault(sp, set()).add(loc)
    rows_ = {}
    for b, where in base.items():
        for fin, path in evolve(b, stage, cap):
            r = rows_.setdefault(fin, {"s": fin, "from": [], "where": [], "path": path, "areas": set()})
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
def bossmon(m): return MD.mon(m["s"], m["l"], m["iv"], m["n"], m["a"], m["i"], m["m"])

def main():
    os.makedirs(f"{OUT}/fights", exist_ok=True)
    # trainers page (+ the ROM id of each documented trainer)
    trainers, docid = [], {}
    caps = {}
    for t in TR:
        if t["name"].startswith("Leader") and "Gym" in (t["loc"] or ""): caps[t["split"]] = max(m["l"] for m in t["team"])
        if t["name"].startswith("Champion"): caps[t["split"]] = max(m["l"] for m in t["team"])
    for sp in S.SPLITS[:9]:
        tl = []
        for t in TR:
            if t["split"] != sp: continue
            team, tid = team_of(t)
            docid[id(t)] = (team, tid)
            tl.append({"name": t["name"], "loc": t["loc"], "mand": t["mand"], "partner": t["fill"] == "FFB6D7A8", "notes": t["notes"], "team": team,
                       "ai": ROMT[tid]["ai"] if tid is not None else None})
        trainers.append({"split": sp, "cap": caps.get(sp), "trainers": tl})
    # boss fights
    fights, seen = [], collections.Counter()
    for t in TR:
        key = S.boss_key(t)
        if not key: continue
        seen[key] += 1
        fights.append((key if seen[key] == 1 else f"{key}{seen[key]}", t["split"], t["name"], t["loc"], docid[id(t)][0], t["notes"], S.label(t, key), docid[id(t)][1]))
    for tid, key, nm, loc in S.KANTO:
        team = rom_boss(tid, nm)
        fights.append((key, "Kanto", ("Leader " if key != "red" else "Pkmn Trainer ") + nm, loc, team, [], nm, tid))
    idx, tabs = [], {"G": [], "V": [], "A": []}
    prev = {"G": None, "V": None, "A": None}; prevst = {"G": -1, "V": -1, "A": -1}
    cells = 0
    for k, split, name, loc, team, notes, label, tid in fights:
        stage = S.SPLITS.index(split)
        cap = caps.get(split) or max(m["l"] for m in team)
        if split == "Kanto": cap = max(m["l"] for m in team)
        team = [m for m in team if m["s"] in MONS]
        P = pool(stage, cap)
        bms = [bossmon(m) for m in team]
        grid = [[MD.matchup(MD.mon(r["s"], cap, 15, "Hardy", r["ab"], "", r["moves"]), b) for b in bms] for r in P]
        cells += len(P) * len(bms)
        tab = "V" if name.startswith("Executive") else "G"
        new, since = {}, {}
        for tb in (tab, "A"):
            pp = prev[tb]
            new[tb] = [i for i, r in enumerate(P) if pp is not None and r["s"] not in pp]
            lo = prevst[tb]
            since[tb] = {"tm": [f"{tm} {mv} — {where}" for tm, mv, where, g in S.TMS if lo < g <= stage and (lo < g or prev[tb] is None)],
                         "items": sorted(i for i, g in S.EVO_ITEM.items() if lo < g <= stage), "rods": [],
                         "other": [x for x, g in (("Surf", S.SURF), ("Old Rod", S.ROD["old"]), ("Good Rod", S.ROD["good"]), ("Super Rod", S.ROD["super"]),
                                                  ("Rock Smash", S.ROCKSMASH), ("Move reminder (Blackthorn)", S.REMINDER)) if lo < g <= stage]}
            prev[tb] = {r["s"] for r in P}; prevst[tb] = stage
        dump(f"{OUT}/fights/{k}.json", {"key": k, "label": label, "cap": cap, "team": team,
             "variants": [{"v": {}, "cols": list(range(len(team)))}], "pool": P, "grid": grid, "new": new, "since": since})
        note = "Kanto: the docs don't cover Kanto's wild Pokémon, so your options are the Johto ones (plus Kanto TMs)." if split == "Kanto" else ""
        idx.append({"key": k, "label": label, "cap": cap, "split": split, "loc": loc, "kind": None, "notes": notes[:3], "note": note,
                    "names": [name], "ids": [tid] if tid is not None else [], "vars": [{}], "n": len(P)})
        tabs[tab].append(k); tabs["A"].append(k)
    caps["Kanto"] = max(f["cap"] for f in idx if f["split"] == "Kanto")
    areas = collections.OrderedDict()
    for sp, an, how, gate, mlv, loc in sorted(SOURCES, key=lambda s: s[3]):
        a = areas.setdefault(loc, {"name": loc, "gate": gate, "split": S.SPLITS[min(gate, 9)], "mons": []})
        a["gate"] = min(a["gate"], gate)
        a["mons"].append([sp, an, how, gate, mlv] + ([round(RATE[(sp, an, how)])] if RATE.get((sp, an, how)) else []))
    for a in areas.values(): a["split"] = S.SPLITS[a["gate"]]
    meta = {"game": "sg", "mons": {n: {"no": d["no"], "t": d["t"], "bs": d["bs"], "ab": d["ab"], "fam": d["fam"]} for n, d in MONS.items()},
            "moves": {m: [d["t"], d["c"], d["bp"]] for m, d in MOVES.items()}, "chart": CHART,
            "natures": {k: v for k, v in MD.NATURES.items() if v}, "boost": MD.BOOST, "immune": MD.IMMUNE, "multi": MULTI, "fixed": MD.FIXED,
            "evos": {n: [{"to": e["to"], "kind": e["kind"], "p": e["p"]} for e in d["evos"]] for n, d in MONS.items() if d["evos"]},
            "fights": idx, "tabs": tabs, "order": {f["key"]: i for i, f in enumerate(idx)}, "caps": caps,
            "areas": list(areas.values()), "splits": S.SPLITS, "tm": {tm: [mv, where, g] for tm, mv, where, g in S.TMS}}
    dump(f"{OUT}/meta.json", meta)
    dump(f"{OUT}/trainers.json", {"all": [dict(x, label=x["split"]) for x in trainers]})
    json.dump({n: {"acc": m["acc"], "pp": m["pp"]} for n, m in ROMMOVES.items()}, open("/home/claude/sg/moves_rom.json", "w"))
    print(len(idx), "fights", cells, "cells", len(areas), "areas", dict(romfix), "caps", caps)

if __name__ == "__main__":
    main()
