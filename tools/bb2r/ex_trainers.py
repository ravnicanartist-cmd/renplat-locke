"""BB2/VW2 Redux trainer docs (Normal and Challenge Mode) -> list of trainers per split, in document order."""
import re, json, sys, collections
import openpyxl

FILES = {"normal": "/mnt/user-data/uploads/38fddbec-Trainer_Battles_-_Normal_Mode.xlsx",
         "challenge": "/mnt/user-data/uploads/32292d1e-Trainer_Battles_-_Challenge_Mode.xlsx"}
SPLITS = ["Cheren", "Roxie", "Burgh", "Elesa", "Clay", "Skyla", "Drayden", "Marlon", "Ghetsis", "Champion"]

def s(v):
    if v is None: return ""
    v = str(v)
    if v.startswith("="): return ""
    return re.sub(r"\s+", " ", v.replace("\\n", " ")).strip()

def fillrgb(c):
    try:
        return c.fill.fgColor.rgb if isinstance(c.fill.fgColor.rgb, str) else ""
    except Exception:
        return ""

def parse(mode):
    wb = openpyxl.load_workbook(FILES[mode], data_only=False)
    out = []
    for sp in SPLITS:
        ws = wb[f"{sp} Split"]
        loc = None
        rows = ws.max_row
        r = 14
        while r <= rows:
            a = ws.cell(r, 1)
            av = s(a.value)
            fl = fillrgb(a)
            if av and fl == "FF191919":
                loc = av; r += 1; continue
            c3 = s(ws.cell(r, 3).value)
            lvl = s(ws.cell(r + 1, 3).value)
            if av and c3 and lvl.lower().startswith("level"):
                team = []
                for col in range(3, 9):
                    nm = s(ws.cell(r, col).value)
                    if not nm or nm.lower().startswith("pokemon name"): continue
                    lv = re.search(r"(\d+)", s(ws.cell(r + 1, col).value))
                    nat = s(ws.cell(r + 2, col).value).split(" ")[0]
                    mv = [s(ws.cell(r + 5 + k, col).value) for k in range(4)]
                    team.append({"s": nm, "l": int(lv.group(1)) if lv else None, "n": nat,
                                 "a": s(ws.cell(r + 3, col).value), "i": "" if s(ws.cell(r + 4, col).value) in ("No Item", "-", "") else s(ws.cell(r + 4, col).value),
                                 "m": [x for x in mv if x and x not in ("-", "--", "-----")]})
                notes = []
                k = r + 1
                while k < r + 9:
                    t = s(ws.cell(k, 1).value)
                    if t: notes.append(t)
                    k += 1
                out.append({"split": sp, "loc": loc, "name": av, "mand": fl in ("FFEA9999", "FFE06666", "FFF4CCCC", "FFCC0000"),
                            "fill": fl, "notes": notes, "team": team, "row": r})
                r += 9; continue
            r += 1
    return out

if __name__ == "__main__":
    for mode in FILES:
        T = parse(mode)
        print(mode, len(T), collections.Counter(t["fill"] for t in T))
        json.dump(T, open(f"/home/claude/bb2/trainers_{mode}.json", "w"), ensure_ascii=False)
    T = json.load(open("/home/claude/bb2/trainers_challenge.json"))
    for t in T:
        if any(x in t["name"] for x in ["Leader", "Elite", "Champion", "Rival", "Colress", "Ghetsis", "Zinzolin", "Shadow", "N ", "Hugh", "Cheren", "Bianca", "Plasma"]) and "Grunt" not in t["name"]:
            print(t["split"], "|", t["loc"], "|", t["name"], t["mand"], [m["s"] + str(m["l"]) for m in t["team"]], t["notes"][:2])
