"""Species (Complete version), learnsets, moves, evolutions from the Renegade Platinum documentation."""
import re
from common import *

def species():
    g = grid("STATS")
    mons, bynum = {}, {}
    for r in g[3:]:
        if not clean(r[1]).startswith("#"):
            continue
        name, no = mon_name(r[1]), dexno(r[1])
        bs = [int(num(r[i])) for i in range(4, 10)]
        types = []
        for i in range(12, 17):
            t = tname(r[i])
            if t and t not in types:
                types.append(t)
        abil = [clean(r[i]) for i in (17, 18, 19) if clean(r[i]) not in ("", "-")]
        evo = clean(r[43])
        mons[name] = {"no": no, "t": types, "bs": bs, "ab": abil[:2], "evraw": evo,
                      "growth": clean(r[31]), "gender": clean(r[37])}
        bynum.setdefault(no, name)
    # evolutions: each row says how it evolved FROM its pre-evolution
    for name, d in mons.items():
        raw = d.pop("evraw")
        m = re.match(r"#0*(\d+)\s+(.*?)(?:\s*-\s*Can evolve into.*)?$", raw)
        if not m or raw.startswith("Can evolve") or raw in ("N", ""):
            continue
        pre = bynum.get(int(m.group(1)) if int(m.group(1)) < 1000 else int(str(m.group(1))[1:]))
        meth = m.group(2).strip()
        if pre is None:
            continue
        d["from"] = [pre, meth]
    return mons, bynum

def learnsets(mons):
    g = grid("LEARNSETS")
    head = g[0]
    sec = {}
    for i, r in enumerate(g):
        t = clean(r[0]).upper()
        if t.startswith("LEVEL UP"): sec["lv"] = i
        elif t.startswith("TMS"): sec["tm"] = i
        elif t.startswith("MOVE TUTOR"): sec["tu"] = i
    alias = {"Giratina (O)": "Giratina (Origin)", "Giratina": "Giratina (Altered)", "Shaymin": "Shaymin (Land)",
             "Shaymin (S)": "Shaymin (Sky)", "Deoxys (N)": "Deoxys (Normal)", "Deoxys (A)": "Deoxys (Attack)",
             "Deoxys (D)": "Deoxys (Defense)", "Deoxys (S)": "Deoxys (Speed)", "Wormadam (P)": "Wormadam (Plant)",
             "Wormadam (S)": "Wormadam (Sandy)", "Wormadam (T)": "Wormadam (Trash)"}
    out, miss = {}, []
    for j, h in enumerate(head):
        if not clean(h).startswith("#"):
            continue
        n = mon_name(h)
        n = alias.get(n, n)
        if n not in mons:
            miss.append(n); continue
        lv, tm, tu = [], [], []
        for i in range(sec["lv"] + 1, sec["tm"]):
            c = clean(g[i][j])
            m = re.match(r"(\d+)\s*-\s*(.+)$", c)
            if m: lv.append([int(m.group(1)), m.group(2).strip()])
        for i in range(sec["tm"] + 1, sec["tu"]):
            c = clean(g[i][j])
            m = re.match(r"(TM|HM)(\d+)\s+(.+)$", c)
            if m: tm.append(f"{m.group(1)}{m.group(2)}")
        for i in range(sec["tu"] + 1, len(g)):
            c = clean(g[i][j])
            if c and c not in ("N", "-") and not c.lower().startswith("move tutor"):
                tu.append(c)
        out[n] = {"lv": lv, "tm": tm, "tu": tu}
    return out, miss

def moves():
    g = grid("MOVES")
    hi = next(i for i, r in enumerate(g) if clean(r[1]) == "NAME")
    out = {}
    for r in g[hi + 1:]:
        n = clean(r[1])
        if not n: continue
        cat = clean(r[6]).title()
        bp = num(r[8]); acc = num(r[9])
        out[n] = {"t": tname(r[3]) or "Normal", "c": cat, "bp": int(bp) if bp else 0,
                  "acc": acc, "pp": clean(r[10]), "e": clean(r[12])[:200]}
    return out

if __name__ == "__main__":
    mons, bynum = species()
    ls, miss = learnsets(mons)
    mv = moves()
    print(len(mons), "species;", len(ls), "learnsets; missing", miss, ";", len(mv), "moves")
    nols = [n for n in mons if n not in ls]; print("no learnset:", nols)
    meths = sorted({d["from"][1] for d in mons.values() if "from" in d})
    print([m for m in meths if not m.startswith("Lv.")])
    unk = sorted({m for l in ls.values() for _, m in l["lv"] if m not in mv})
    print("unknown lv moves", unk[:40])
    tus = sorted({m for l in ls.values() for m in l["tu"]}); print(len(tus), "tutor moves", [m for m in tus if m not in mv])
    print(mons["Charizard"], ls["Charizard"]["tm"][:5], ls["Charizard"]["tu"][:5])
    print({k: v for k, v in mv.items() if v["bp"] == 0 and v["c"] != "Status"})
