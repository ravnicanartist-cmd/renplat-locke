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
    MD.EVOS = set(meta.get("evos", {})); MD.STURDY = g in ("bb2r", "soulgold")
    if MD.STURDY and not meta.get("sturdy"):
        meta["sturdy"] = True; json.dump(meta, open(f"{HUB}/{g}/data/meta.json", "w"), ensure_ascii=False, separators=(",", ":"))
    n = 0
    for f in glob.glob(f"{HUB}/{g}/data/fights/**/*.json", recursive=True):
        d = json.load(open(f))
        for r in d["pool"]: r["moves"] = [m for m in r["moves"] if m not in MD.NOUSE]
        bt = [None] * len(d["team"])              # weather is worked out per variant: each one has its own lead
        for v in d.get("variants") or [{"cols": list(range(len(d["team"])))}]:
            for c, b in zip(v["cols"], MD.bossteam([d["team"][c] for c in v["cols"]])):
                if bt[c] is not None and bt[c].get("w") != b.get("w"): print("  weather differs between variants", g, d["key"], c)
                bt[c] = b
        for c in range(len(bt)):
            if bt[c] is None: bt[c] = MD.bossteam([d["team"][c]])[0]
        d["grid"] = [[MD.matchup(MD.mon(r["s"], d["cap"], 15, "Hardy", r["ab"], "", r["moves"]), b) for b in bt] for r in d["pool"]]
        n += len(d["pool"]) * len(d["team"])
        json.dump(d, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
    print(g, n)
