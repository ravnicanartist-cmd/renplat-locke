"""Every trainer in the ... SPLiT sheets (base Renegade Platinum documentation)."""
import re
from common import *

SPLITS = ["ROARK", "GARDENiA", "FANTINA", "MAYLENE", "WAKE", "BYRON", "CANDICE", "VOLKNER", "CHAMPiON"]
TYPESET = {t.upper() for t in TYPES}

def is_loc(r):
    cs = [(j, clean(c)) for j, c in enumerate(r) if clean(c)]
    if len(cs) != 1 or cs[0][0] != 1:
        return None
    c = cs[0][1]
    if c in TYPESET or c.startswith("(") or "[" in c or len(c) < 4 or c.upper() != c:
        return None
    if re.match(r"(IF YOU|CAN USE|ONCE)", c):
        return None
    return c.title()

def parse_split(sp):
    g = grid(f"{sp}_SPLiT")
    cap = None
    m = re.search(r"LVL CAP\s*:\s*(\d+)", " ".join(g[1]))
    if m: cap = int(m.group(1))
    out, loc = [], None
    for i, r in enumerate(g):
        L = is_loc(r)
        if L:
            loc = L
            continue
        h = clean(r[1])
        m = re.search(r"^(.*?)\s*\[(\d+)\]\s*$", h)
        if not m or i < 2:
            continue
        name = re.sub(r"^SINNOH POKEMON LEAGUE\s*", "", m.group(1)).strip()
        tid = int(m.group(2))
        variant = clean(r[2])
        mons = []
        sprow = g[i - 2]
        for k in range(6):
            b = 4 + 8 * k
            sname = clean(sprow[b + 1]) if b + 1 < len(sprow) else ""
            if not sname.startswith("#"):
                continue
            lv = re.search(r"(\d+)", clean(sprow[b + 6]))
            bs = [num(g[i + 1][b + x]) for x in range(6)]
            nat = clean(g[i + 3][b]).split(" ")[0]
            iv = re.search(r"(\d+)\s*IV", clean(g[i + 3][b + 6]))
            mv = [clean(g[i + 4 + x][b]) for x in range(4)]
            mv = [x for x in mv if x and x not in ("-", "--")]
            item = clean(g[i + 2][b + 1])
            mons.append({"s": mon_name(sname), "l": int(lv.group(1)) if lv else None,
                         "a": clean(g[i + 2][b + 4]), "i": "" if item in ("No Item", "-", "") else item,
                         "n": nat, "iv": int(iv.group(1)) if iv else None, "m": mv,
                         "bs": [int(x) if x is not None else None for x in bs]})
        notes = [clean(g[i + x][1]) for x in range(1, 9) if i + x < len(g) and clean(g[i + x][1])]
        out.append({"split": sp.upper(), "cap": cap, "loc": loc, "name": name.title(), "id": tid,
                    "var": variant, "notes": notes, "team": mons, "row": i})
    return out

def all_trainers():
    res = []
    for sp in SPLITS:
        res += parse_split(sp)
    return res

if __name__ == "__main__":
    from ex_species import species
    mons, _ = species()
    T = all_trainers()
    print(len(T), "trainers")
    bad = set()
    for t in T:
        for m in t["team"]:
            if m["s"] not in mons: bad.add(("name", m["s"]))
            elif None not in m["bs"] and m["bs"] != mons[m["s"]]["bs"]: bad.add(("bs", m["s"], tuple(m["bs"]), tuple(mons[m["s"]]["bs"])))
            if m["iv"] is None: bad.add(("iv", t["name"], t["id"]))
    print(sorted(bad)[:30], len(bad))
    for t in T:
        if any(x in t["name"] for x in ["Leader", "Commander", "Boss", "Rival", "Elite", "Champion", "Lucas", "Dawn"]) :
            print(t["split"], t["loc"], t["name"], t["id"], t["var"], [m["s"] + str(m["l"]) for m in t["team"]], t["notes"][:2])
