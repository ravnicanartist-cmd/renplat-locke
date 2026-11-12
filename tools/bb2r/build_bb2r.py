"""Blaze Black 2 / Volt White 2 Redux (PChal QoL build) -> data files for the hub site.

Sources: hzla's Dynamic Calc data for this build (extracted from the ROM: species, learnsets, TMs, evolutions, moves,
trainer IVs), the Redux documentation workbooks (trainer teams in Normal and Challenge Mode, encounters, gifts, items),
and story_bb2r.py (story order and when each area / TM / item opens up)."""
import json, re, sys, os, collections
sys.path.insert(0, "/home/claude/build"); sys.path.insert(0, "/home/claude/bb2")
import model as MD
import story_bb2r as S
from common import dump

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/hub/bb2r/data"
SRC = "/home/claude/bb2/src"
KEY = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower().replace("♀", "f").replace("♂", "m"))

t = open("/home/claude/ref/dec/backups/bb2redux1-4.js", encoding="utf-8").read()
J = json.loads(t[t.index("{"):t.rindex("}") + 1])
P = J["poks"]
MONS = {}
for n, p in P.items():
    if not isinstance(p, dict) or "bs" not in p: continue
    name = n.replace("’", "'")
    b = p["bs"]
    abs_ = [a for a in p.get("abs", []) if a and a != "None"]
    MONS[name] = {"no": p.get("num"), "t": p["types"], "bs": [b["hp"], b["at"], b["df"], b["sa"], b["sd"], b["sp"]],
                  "ab": abs_[:2] if len(abs_) >= 2 and abs_[0] != abs_[1] else abs_[:1], "ha": abs_[2] if len(abs_) > 2 else "",
                  "lv": p.get("learnset_info", {}).get("learnset", []), "tm": p.get("learnset_info", {}).get("tms", []),
                  "tu": p.get("learnset_info", {}).get("tutors", []) if isinstance(p.get("learnset_info", {}).get("tutors", []), list) else [],
                  "evos": list(zip(p.get("evos", []), p.get("evoMethods", []), p.get("evoParams", [])))}
BYKEY = {KEY(n): n for n in MONS}
ALIAS = {"nidoranm": "Nidoran-M", "nidoranf": "Nidoran-F", "cinchou": "Chinchou", "gudurr": "Gurdurr", "reuiniclus": "Reuniclus", "sesimitoad": "Seismitoad"}
def canon(n):
    k = KEY(n)
    return ALIAS.get(k) or BYKEY.get(k) or n
MOVES = {}
for n, m in J["moves"].items():
    MOVES[n] = {"t": m["type"], "c": m["category"], "bp": m.get("basePower", 0) or 0}
MKEY = {KEY(m): m for m in MOVES}
def mcanon(m): return MKEY.get(KEY(m), m)
MULTI = {n: (3 if m.get("multihit") == [2, 5] else m["multihit"] if isinstance(m.get("multihit"), int) else 2 if m.get("multihit") else 1)
         for n, m in J["moves"].items() if m.get("multihit")}
MD.MONS, MD.MOVES, MD.MULTI = MONS, MOVES, MULTI

# evolutions
PRE = {}
for n, d in MONS.items():
    for to, meth, par in d["evos"]:
        to = to.replace("’", "'")
        if to in MONS: PRE.setdefault(to, n)
def root(n):
    while n in PRE: n = PRE[n]
    return n
for n in MONS: MONS[n]["fam"] = root(n)

# ------------------------------------------------------------------ trainers (docs) + IVs / calc ids (hzla)
SETS = collections.defaultdict(list)
for sp, d in J["formatted_sets"].items():
    for nm, v in d.items():
        SETS[KEY(sp)].append((sp, nm, v))
def name_hit(tname, nm):
    # the docs and hzla's data spell some names differently (Terrel / Terrell), so compare the first 4 letters of each word
    who = nm.split(" - ")[0].lower()
    toks = [w[:4] for w in re.findall(r"[a-z]+", tname.lower()) if len(w) >= 3 and w not in ("team", "plasma", "leader", "pkmn", "trainer")]
    return bool(toks) and all(any(x.startswith(t) for x in re.findall(r"[a-z]+", who)) for t in toks)
def match_set(m, tname=""):
    best, bs = None, -1
    want = {KEY(x) for x in m["m"]}
    for sp, nm, v in SETS.get(KEY(m["s"]), []):
        sc = len(want & {KEY(x) for x in v["moves"]}) * 10 - abs((v["level"] or 0) - (m["l"] or 0)) + (60 if tname and name_hit(tname, nm) else 0)
        if sc > bs: best, bs = (sp, nm, v), sc
    return best if bs >= 25 else None

TR = {mode: json.load(open(f"/home/claude/bb2/trainers_{mode}.json")) for mode in ("normal", "challenge")}
ABK = {KEY(a): a for v in MONS.values() for a in (v.get("ab") or [])}
def fix_shift(m):
    """a few rows of the docs are shifted by one cell (a nature or item sits in the ability box): put them back"""
    a = m["a"]
    if not a or KEY(a) in ABK: return dict(m, a=ABK.get(KEY(a), a))
    m = dict(m, shifted=True)
    if "(+" in a:                            # nature | ability | item | 3 moves
        m["n"], m["a"], m["i"], m["m"] = a.split(" ")[0], m["i"], (m["m"] or [""])[0], m["m"][1:]
    elif KEY(m["i"]) in {KEY(x) for x in MOVES}:   # item | move | 3 moves
        m["i"], m["m"], m["a"] = ("" if a in ("No Item", "-") else a), [m["i"]] + m["m"], ""
    else:                                    # two items: keep the first, the calc data settles it below
        m["i"], m["a"], m["broken"] = a, "", True
    if m["i"] in ("No Item", "-"): m["i"] = ""
    m["a"] = ABK.get(KEY(m["a"]), "") if m["a"] else ""
    return m
def boss(m, tname=""):
    m = fix_shift(m)
    s2 = canon(m["s"])
    hit = match_set(m, tname)
    if hit and (not m["a"] or m["a"] not in (MONS.get(s2, {}).get("ab") or [m["a"]])):
        m = dict(m, a=hit[2].get("ability") or m["a"])           # the docs' ability doesn't fit the species: trust hzla's ROM data
    if hit and m.get("broken") and hit[2].get("item") not in (None, "", "-"): m["i"] = hit[2]["item"]
    if hit and m.get("shifted") and len(m["m"]) < len(hit[2].get("moves") or []): m = dict(m, m=list(hit[2]["moves"]))
    iv = 31
    out = {"s": s2, "l": m["l"], "n": m["n"] if m["n"] in MD.NATURES else "Hardy", "a": m["a"] or (MONS.get(s2, {}).get("ab") or [""])[0],
           "i": m["i"], "m": [mcanon(x) for x in m["m"]], "iv": iv}
    if hit:
        sp, nm, v = hit
        out["iv"] = (v.get("ivs") or {}).get("hp", 31)
        out["calc"] = f"{sp} ({nm})"
        out["ai"] = v.get("ai")
    return out
def tr_ai(team):
    a = [m.pop("ai") for m in team if m.get("ai") is not None]
    return max(a, key=a.count) if a else None

def ace_caps(mode):
    caps = {}
    for t in TR[mode]:
        if t["name"].startswith("Leader") and "Gym" in (t["loc"] or ""):
            caps[t["split"]] = max(m["l"] for m in t["team"])
        if t["name"].startswith("Champion") or t["name"] == "Team Plasma Ghetsis":
            caps[t["split"]] = max(m["l"] for m in t["team"])
    return caps

# ------------------------------------------------------------------ encounters
def rows(p):
    r = [l.rstrip("\n").split("\t") for l in open(p, encoding="utf-8")]
    w = max(len(x) for x in r)
    return [x + [""] * (w - len(x)) for x in r]
E = rows(f"{SRC}/Pokemon_Locations/Encounter_Table.tsv")
METH = []
for i, r in enumerate(E):
    if i >= 3 and r[0].strip(): METH.append((i, r[0].replace("\\n", " ").strip()))
def meth_at(i):
    m = None
    for k, n in METH:
        if k <= i: m = n
    return m
def mkind(m):
    m = m.lower()
    return "surf" if "surf" in m else "fishing" if "fish" in m else "dark grass" if "doubles" in m else "shaking" if "shaking" in m else "grass"
RATE = {}
SOURCES = []    # (species, area display, how, split gate, min level, nuzlocke area)
def basearea(a):
    a = a.split("\\n")[0].strip()
    a = re.sub(r"\s*\(.*?\)\s*$", "", a)
    a = re.split(r"\s*-\s+", a)[0].strip()
    return {"Abdundant Shrine": "Abundant Shrine", "Giant Chasm-": "Giant Chasm"}.get(a, a)
missing = set()
for j in range(1, len(E[0]) - 2):
    an = E[0][j].strip()
    if not an or E[2][j].strip() != "Pokemon": continue
    loc = basearea(an)
    if loc not in S.AREA:
        missing.add(loc); continue
    for i in range(3, len(E)):
        sp = E[i][j].strip()
        if not sp: continue
        lv = [int(x) for x in re.findall(r"\d+", E[i][j + 2])]
        how = mkind(meth_at(i))
        gate = max(S.AREA[loc], S.SURF if how == "surf" else 0, S.FISH if how == "fishing" else 0)
        SOURCES.append((canon(sp), an.replace("\\n", " "), how, gate, min(lv) if lv else 0, loc))
        try: RATE[(canon(sp), an.replace("\\n", " "), how)] = (max if how == "fishing" else lambda a, b: a + b)(RATE.get((canon(sp), an.replace("\\n", " "), how), 0), float(E[i][j + 1] or 0) * 100)
        except ValueError: pass
if missing: print("UNMAPPED", missing)
for sp, an, how, gate, loc in S.GIFTS:
    for s2 in (sp if isinstance(sp, list) else [sp]):
        SOURCES.append((canon(s2), an, how, gate, 0, loc))
eg = rows(f"{SRC}/Pokemon_Locations/Mystery_Eggs.tsv")
for r in eg[3:]:
    if r[0].strip(): SOURCES.append((canon(r[0].strip()), "Floccesy Ranch (Mystery Egg)", "egg", 0, 0, "Floccesy Ranch"))
    if r[3].strip(): SOURCES.append((canon(r[3].strip()), "Castelia City (Mystery Egg)", "egg", 2, 0, "Castelia City"))
bad = sorted({s[0] for s in SOURCES if s[0] not in MONS})
if bad: print("UNKNOWN SPECIES", bad)
SOURCES = [s for s in SOURCES if s[0] in MONS and s[0] not in S.LEGENDARY]

# ------------------------------------------------------------------ pools
def evo_ok(meth, par, n, stage, cap, base):
    m = meth.lower()
    if m.startswith("level requirement"): return isinstance(par, int) and par <= cap
    if "friendship" in m or "happiness" in m: return True
    if m.startswith("item use") or "hold" in m: return S.EVO_ITEM_K.get(KEY(par), 99) <= stage
    if "specific move" in m: return any(l <= cap and KEY(x) == KEY(par) for l, x in MONS[n]["lv"])
    if "party member" in m: return True
    return False
def evolve(b, stage, cap, base):
    out = []
    def go(n, path):
        nxt = []
        for to, meth, par in MONS[n]["evos"]:
            to = to.replace("’", "'")
            if to in MONS and to not in [x for x in nxt] and evo_ok(meth, par, n, stage, cap, base): nxt.append(to)
        if not nxt: out.append((n, path))
        for t2 in nxt: go(t2, path + [t2])
    go(b, [b])
    return out
def evo_level(a, b):
    for to, meth, par in MONS[a]["evos"]:
        if to.replace("’", "'") == b and meth.startswith("Level Requirement") and isinstance(par, int): return par
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
    mv.discard("Frustration")   # friendship-based again (VW2 QoL 1.2.2): ~1 BP on a Pokemon that likes you; bosses keep 102
    return mv
def damaging(m):
    d = MOVES.get(m)
    return d is not None and (m in MD.FIXED or (d["c"] != "Status" and d["bp"] > 1))
def pool(stage, cap, mode):
    base, locs = {}, {}
    for sp, an, how, gate, mlv, loc in SOURCES:
        if gate <= stage and mlv <= cap and not (mode == "challenge" and sp in S.NOT_IN_CHALLENGE):
            base.setdefault(sp, []).append(f"{an} ({how})")
            if how not in ("gift", "egg", "trade", "static", "fossil"): locs.setdefault(sp, set()).add(loc)
    rows_ = {}
    for b, where in base.items():
        for fin, path in evolve(b, stage, cap, base):
            r = rows_.setdefault(fin, {"s": fin, "from": [], "where": [], "path": path, "areas": set()})
            if b not in r["from"]: r["from"].append(b)
            for w in where:
                if w not in r["where"]: r["where"].append(w)
            r["areas"] |= locs.get(b, set())
            if len(path) > len(r["path"]): r["path"] = path
    out = []
    for n in sorted(rows_):
        r = rows_[n]
        out.append({"s": n, "from": r["from"], "where": r["where"][:6], "ab": MONS[n]["ab"][0] if MONS[n]["ab"] else "",
                    "moves": sorted(m for m in learnable(n, r["path"], stage, cap) if damaging(m)), "areas": sorted(r["areas"])})
    return out

def bossmon(m):
    return MD.mon(m["s"], m["l"], m["iv"], m["n"], m["a"], m["i"], m["m"], m.get("bs"))

def main():
    os.makedirs(OUT, exist_ok=True)
    index, cells = {}, 0
    trainers = {}
    for mode in ("normal", "challenge"):
        caps = ace_caps(mode)
        T = TR[mode]
        # trainers page
        trainers[mode] = [{"split": sp, "cap": caps.get(sp), "trainers": [
            {"name": t["name"], "loc": t["loc"], "mand": t["mand"], "partner": t["fill"] == "FFB6D7A8", "notes": t["notes"],
             "team": tm, "ai": tr_ai(tm)} for t in T if t["split"] == sp for tm in [[boss(m, t["name"]) for m in t["team"]]]]} for sp in S.SPLITS]
        fights, seen = [], collections.Counter()
        for t in T:
            key = S.boss_key(t)
            if not key: continue
            seen[key] += 1
            k2 = key if seen[key] == 1 else f"{key}{seen[key]}"
            fights.append((k2, t))
        tabs = {"G": [], "V": [], "A": []}
        idx = []
        os.makedirs(f"{OUT}/fights/{mode}", exist_ok=True)
        prev = {"G": None, "V": None, "A": None}
        prevst = {"G": -1, "V": -1, "A": -1}
        for k, t in fights:
            stage = S.SPLITS.index(t["split"])
            cap = caps[t["split"]]
            team = [boss(m, t["name"]) for m in t["team"] if canon(m["s"]) in MONS]
            if not team: continue
            P = pool(stage, cap, mode)
            bms = [bossmon(m) for m in team]
            grid = [[MD.matchup(MD.mon(r["s"], cap, 15, "Hardy", r["ab"], "", r["moves"]), b) for b in bms] for r in P]
            cells += len(P) * len(bms)
            tab = "G" if t["name"].startswith(("Leader", "Elite", "Champion")) else "V"
            new, since = {}, {}
            for tb in (tab, "A"):
                pp = prev[tb]
                new[tb] = [i for i, r in enumerate(P) if pp is not None and r["s"] not in pp]
                lo = prevst[tb]
                since[tb] = {"tm": [f"{tm} {mv} — {loc}" for tm, mv, loc, g in S.TMS if lo < g <= stage and (lo < g or prev[tb] is None)],
                             "items": sorted(i for i, g in S.EVO_ITEM.items() if lo < g <= stage), "rods": [],
                             "other": [x for x, g in (("Surf", S.SURF), ("Move reminder", S.REMINDER)) if lo < g <= stage]}
                prev[tb] = {r["s"] for r in P}; prevst[tb] = stage
            label = S.label(t, k)
            dump(f"{OUT}/fights/{mode}/{k}.json", {"key": k, "label": label, "cap": cap, "team": team,
                 "variants": [{"v": {}, "cols": list(range(len(team)))}], "pool": P, "grid": grid, "new": new, "since": since})
            idx.append({"key": k, "label": label, "cap": cap, "split": t["split"], "loc": t["loc"], "kind": None,
                        "notes": t["notes"][:3], "note": S.NOTE.get(k, ""), "names": [t["name"]], "ids": [], "vars": [{}], "n": len(P)})
            tabs[tab].append(k); tabs["A"].append(k)
        index[mode] = {"fights": idx, "tabs": tabs, "order": {f["key"]: i for i, f in enumerate(idx)}, "caps": caps}
    # nuzlocke areas
    areas = collections.OrderedDict()
    for sp, an, how, gate, mlv, loc in sorted(SOURCES, key=lambda s: s[3]):
        a = areas.setdefault(loc, {"name": loc, "gate": gate, "split": S.SPLITS[min(gate, 9)], "mons": []})
        a["gate"] = min(a["gate"], gate)
        a["mons"].append([sp, an, how, gate, mlv] + ([round(RATE[(sp, an, how)])] if RATE.get((sp, an, how)) else []))
    meta = {"game": "bb2r", "mons": {n: {"no": d["no"], "t": d["t"], "bs": d["bs"], "ab": d["ab"] + ([d["ha"]] if d["ha"] else []), "fam": d["fam"]} for n, d in MONS.items()},
            "moves": {m: [d["t"], d["c"], d["bp"]] for m, d in MOVES.items()}, "chart": MD.CHART,
            "natures": {k: v for k, v in MD.NATURES.items() if v}, "boost": MD.BOOST, "immune": MD.IMMUNE, "multi": MULTI,
            "fixed": MD.FIXED, "evos": {n: [{"to": a, "kind": b, "p": c} for a, b, c in d["evos"]] for n, d in MONS.items() if d["evos"]},
            "modes": index, "areas": list(areas.values()), "splits": S.SPLITS,
            "tm": {tm: [mv, loc, g] for tm, mv, loc, g in S.TMS}}
    dump(f"{OUT}/meta.json", meta)
    dump(f"{OUT}/trainers.json", trainers)
    print(sum(len(v["fights"]) for v in index.values()), "fights", cells, "cells", len(areas), "areas")

if __name__ == "__main__":
    main()
