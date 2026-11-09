"""Wild encounters, gifts, statics and trades from the ENCOUNTERS sheet (blocks 7 columns wide, story order)."""
import re
from common import *

METHOD = re.compile(r"^(Grass|Cave|Ground|Surf|Rods|Poké Radar|Honey Tree|Cave Every Floor|Surf and Rods|Lost Tower|Static|Gift|Inside|Get the|Egg|Trade|Revive|Mr\. Backlot|Static \(haha\)|Remember|Grass \()", re.I)

def blocks():
    g = grid("ENCOUNTERS")
    W = len(g[0])
    out = []   # list of dicts {area, sub, method, note, mons:[{s, lv, rates}]}
    heads = {}
    for c in range(4, W - 6, 7):
        area = sub = None
        heads[c] = []
        cur = None
        for i in range(1, len(g)):
            c0 = clean(g[i][c]); c1 = clean(g[i][c + 1])
            if c0 and not c1.startswith("#"):
                if c0.isupper() and not METHOD.match(c0) and not c0.startswith("("):
                    if area and c0.startswith(area.split(" (")[0]) and "(" in c0 and c0 != area:
                        sub = c0
                        heads[c].append((i, area, sub))
                    else:
                        area, sub = c0, None
                    heads[c].append((i, area, sub))
                    cur = None
                    continue
                if METHOD.match(c0) or c0.lower().startswith(("gift", "static", "trade", "egg", "inside", "get the", "revive", "mr. backlot", "lost tower", "cave", "surf", "rods", "grass", "ground", "honey")):
                    a2, s2 = area, sub
                    if a2 is None:
                        for (hr, ha, hs) in heads.get(c - 7, []):
                            if hr <= i: a2, s2 = ha, hs
                    cur = {"area": a2, "sub": s2, "method": c0, "notes": [], "mons": [], "col": c, "row": i}
                    out.append(cur)
                    # a rods header has O/G/S columns
                    continue
                if cur is not None:
                    cur["notes"].append(c0)
                continue
            if c1.startswith("#") and cur is not None:
                vals = [clean(g[i][c + k]) for k in range(2, 6)]
                cur["mons"].append({"s": mon_name(c1), "v": vals})
            elif c1 and cur is not None:
                cur["notes"].append(c1)
    return out

def method_kind(m):
    m = m.lower()
    for k in ["grass", "cave", "ground", "surf and rods", "surf", "rods", "poké radar", "honey tree", "static", "gift", "egg", "trade", "revive", "inside rowan", "get the", "mr. backlot", "lost tower"]:
        if m.startswith(k):
            return {"inside rowan": "gift", "get the": "gift", "mr. backlot": "egg", "lost tower": "ground", "surf and rods": "surf"}.get(k, k)
    return "other"

if __name__ == "__main__":
    B = blocks()
    print(len(B), "blocks")
    import collections
    print(collections.Counter(method_kind(b["method"]) for b in B))
    seen = []
    for b in B:
        key = (b["area"], b["sub"])
        if key not in seen: seen.append(key)
    for a, s in seen: print(a, "|", s)
