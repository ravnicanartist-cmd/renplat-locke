"""Renegade Platinum Trainers page: PChal's Trainer_Battles.xlsx (teams, mandatory / optional / partner) -> renplat/data/trainers.json.
Names are matched to the site's species and move names; calc links come from hzla's rp.js sets (species + moves + trainer name)."""
import json, re, sys, collections
sys.path.insert(0, "/home/claude/rp2"); sys.path.insert(0, "/home/claude/build")
from ex_rp_trainers import X
import story as S
HUB = "/home/claude/hub"
KEY = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower().replace("♀", "f").replace("♂", "m"))
meta = json.load(open(f"{HUB}/renplat/data/meta.json"))
MK = {KEY(n): n for n in meta["mons"]}; VK = {KEY(n): n for n in meta["moves"]}
AK = {KEY(a): a for v in meta["mons"].values() for a in v["ab"]}
def ability(a, sp, alt=None):
    r = AK.get(KEY({"Initmidate": "Intimidate"}.get(a, a))) or AK.get(KEY(alt or ""))
    if not r: miss["ability " + a] += 1; r = meta["mons"].get(sp, {}).get("ab", [""])[0]
    return r
ALIAS = {"drllrun": "Drill Run", "doubleedge": "Double-Edge", "nidoranf": "Nidoran-F", "nidoranm": "Nidoran-M", "capitvate": "Captivate",
         "seisimictoss": "Seismic Toss", "acurpressure": "Acupressure", "hornrill": "Drill Run"}
import os; os.chdir("/home/claude/build"); import build as B      # the ROM: teams are checked against it
BASE = collections.defaultdict(list)
for t in B.TRALL: BASE[t["split"]].append(t)
romfix = collections.Counter()
def rom_match(split, name, team):
    """the base-doc trainer (and so the ROM trainer id) with exactly this species line-up and a similar name"""
    sig = [KEY(re.sub(r"-.*", "", m["s"])) for m in team]
    toks = {w[:4] for w in re.findall(r"[a-z]+", name.lower()) if len(w) >= 3}
    best = None
    for b in BASE[split]:
        if [KEY(re.sub(r"-.*", "", B.canon(m["s"]))) for m in b["team"]] != sig: continue
        sc = len(toks & {w[:4] for w in re.findall(r"[a-z]+", b["name"].lower()) if len(w) >= 3})
        if sc and (best is None or sc > best[0]): best = (sc, b["id"])
    return best[1] if best else None
miss = collections.Counter()
def mon(n):
    k = KEY(re.sub(r"\(.*?\)", "", n))
    r = MK.get(k) or ALIAS.get(k)
    if not r:
        r = next((v for kk, v in MK.items() if kk.startswith(k) or k.startswith(kk)), None)
    if not r: miss["mon " + n] += 1
    return r or n
def move(n):
    k = KEY(n.replace("(!!!)", ""))
    r = VK.get(k) or ALIAS.get(k)
    if not r: miss["move " + n] += 1
    return r or n

t = open(f"{HUB}/calc/backups/rp.js", encoding="utf-8").read()
J = json.loads(t[t.index("{"):t.rindex("}") + 1])
SETS = collections.defaultdict(list)
for sp, d in J["formatted_sets"].items():
    for nm, v in d.items(): SETS[KEY(sp)].append((sp, nm, v))
def name_hit(tname, nm):
    toks = [w[:4] for w in re.findall(r"[a-z]+", tname.lower()) if len(w) >= 3 and w not in ("pkmn", "trainer", "leader", "elite", "four", "team", "galactic")]
    words = re.findall(r"[a-z]+", nm.lower())
    return bool(toks) and all(any(x.startswith(t) for x in words) for t in toks)
def calc_id(m, tname):
    best, bs = None, -1
    want = {KEY(x) for x in m["m"]}
    for sp, nm, v in SETS.get(KEY(m["s"]), []):
        sc = len(want & {KEY(x) for x in v["moves"]}) * 10 - abs((v["level"] or 0) - (m["l"] or 0)) + (60 if name_hit(tname, nm) else 0)
        if sc > bs: best, bs = f"{sp} ({nm})", sc
    return best if bs >= 25 else None

T = X.parse("rp")
out = []
for sp in X.SPLITS:
    key = sp.upper()
    tr = []
    for x in T:
        if x["split"] != sp: continue
        team = []
        for m in x["team"]:
            team.append({"s": mon(m["s"]), "l": m["l"], "n": m["n"], "a": m["a"], "i": m["i"], "m": [move(v) for v in m["m"]]})
        tid = rom_match(key, x["name"], team)
        if tid is not None:                      # levels, items and moves from the ROM (the docs have a few typos)
            rom = B.rom_team(tid)
            for mm, r in zip(team, rom):
                new = {"l": r["l"], "i": r["i"], "m": [move(v) for v in r["m"]]}
                if any(mm[k] != v for k, v in new.items()): romfix["fixed from ROM"] += 1
                mm.update(new)
            basedoc = next(b for b in BASE[key] if b["id"] == tid)["team"]
            for mm, bd in zip(team, basedoc): mm["a"] = ability(mm["a"], mm["s"], bd.get("a"))
            romfix["matched"] += 1
        else:
            romfix["doc only"] += 1
            for mm in team: mm["a"] = ability(mm["a"], mm["s"])
        for mm in team:
            c = calc_id(mm, x["name"])
            if c: mm["calc"] = c
        tr.append({"name": x["name"], "loc": x["loc"], "mand": x["mand"], "partner": x["fill"] == "FFB6D7A8", "notes": x["notes"], "team": team})
    out.append({"split": key, "label": sp, "cap": S.CAPS[key], "trainers": tr})
json.dump({"all": out}, open(f"{HUB}/renplat/data/trainers.json", "w"), ensure_ascii=False, separators=(",", ":"))
n = sum(len(s["trainers"]) for s in out); nm = sum(len(t["team"]) for s in out for t in s["trainers"])
nc = sum(1 for s in out for t in s["trainers"] for m in t["team"] if "calc" in m)
print(n, "trainers", nm, "pokemon", nc, "with calc sets", romfix); print(miss.most_common(40))
