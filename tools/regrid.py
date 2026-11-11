"""Recompute every Boss Prep grid on the hub with the current model (after a rule change), without rebuilding the data."""
import json, glob, os, sys
sys.path.insert(0, "/home/claude/build")
import model as MD
HUB = "/home/claude/hub"
for g in ["renplat", "bb2r", "sg", "soulgold"]:
    meta = json.load(open(f"{HUB}/{g}/data/meta.json"))
    MD.MONS = meta["mons"]; MD.MOVES = {k: {"t": v[0], "c": v[1], "bp": v[2]} for k, v in meta["moves"].items()}
    MD.CHART = meta["chart"]; MD.MULTI = meta.get("multi", {})
    for k in ("fixed", "boost", "immune"):
        if k in meta: setattr(MD, k.upper(), meta[k])
    n = 0
    for f in glob.glob(f"{HUB}/{g}/data/fights/**/*.json", recursive=True):
        d = json.load(open(f))
        for r in d["pool"]: r["moves"] = [m for m in r["moves"] if m not in MD.NOUSE]
        d["grid"] = [[MD.matchup(MD.mon(r["s"], d["cap"], 15, "Hardy", r["ab"], "", r["moves"]), MD.bossmon(m)) for m in d["team"]] for r in d["pool"]]
        n += len(d["pool"]) * len(d["team"])
        json.dump(d, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
    print(g, n)
