"""Per-game move numbers (accuracy, PP) and the hack's own move-change notes -> /home/claude/text/src_<game>.json"""
import json, re, sys, os, openpyxl
os.chdir("/home/claude/build"); sys.path.insert(0, "/home/claude/build")
import build as B
clean = lambda v: re.sub(r"[᠎᠋\s]+", " ", str(v or "")).strip()
KEY = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
# ---- Renegade Platinum: ROM numbers + the documentation's MOVE MODIFICATIONS / replacements
meta = json.load(open("/home/claude/hub/renplat/data/meta.json"))
rp = {"moves": {}, "notes": {}, "general": [
    "Move numbers (power, accuracy, PP, effect chance, priority) follow Ultra Sun / Ultra Moon.",
    "Curse is Ghost type; Charm, Moonlight and Sweet Kiss are Fairy type."]}
for n, v in B.MOVES.items():
    c = B.mcanon(n)
    rp["moves"][c] = {"acc": v["acc"] or None, "pp": v["pp"]}
wb = openpyxl.load_workbook("/mnt/user-data/uploads/62793feb-Pokemon_Renegade_Platinum_-_Documentation.xlsx", read_only=True)
rows = list(wb["MOVES"].iter_rows(values_only=True))
for r in rows[6:31]:
    j = clean(r[9]) if len(r) > 9 else ""
    if "//" in j:
        name, *ch = [x.strip() for x in j.split("//")]
        rp["notes"][B.mcanon(name.rstrip(":"))] = "; ".join(ch).replace(">>", "→")
    old, new = clean(r[1]), clean(r[3]) if len(r) > 3 else ""
    if old and new and old not in ("Old Move",) and len(old) < 20 and not old.startswith(("-", "MOVE", "The ", "Moves")):
        k = B.mcanon(new)
        rp["notes"][k] = (rp["notes"].get(k, "") + "; " if k in rp["notes"] else "") + f"Replaces {old} in this hack"
json.dump(rp, open("/home/claude/text/src_rp.json", "w"), ensure_ascii=False, indent=0)
print("rp", len(rp["moves"]), rp["notes"])
# ---- Blaze Black 2 Redux: hzla's data + the Move Changes sheet
t = open("/home/claude/ref/dec/backups/bb2redux1-4.js").read()
J = json.loads(t[t.index("{"):t.rindex("}") + 1])
bb = {"moves": {}, "notes": {}, "general": []}
for n, v in J["moves"].items():
    bb["moves"][n] = {"acc": v.get("accuracy"), "pp": v.get("pp"), "pri": v.get("priority", 0)}
mk = {KEY(n): n for n in J["moves"]}
wb = openpyxl.load_workbook("/mnt/user-data/uploads/d210b055-Base_Stats_and_Learnsets.xlsx", read_only=True)
for r in list(wb["Move Changes"].iter_rows(values_only=True))[3:]:
    a, b = clean(r[0]), str(r[1] or "").strip()
    if a and b:
        k = mk.get(KEY(a.replace("Armour", "Armor")), a)
        bb["notes"][k] = "; ".join(x.strip(" -") for x in b.split("\n") if x.strip(" -")).replace("->", "→")
    if len(r) > 3 and r[2] and r[3]:
        k = mk.get(KEY(clean(r[3])), clean(r[3]))
        bb["notes"][k] = (bb["notes"][k] + "; " if k in bb["notes"] else "") + f"Replaces {clean(r[2])} in this hack"
json.dump(bb, open("/home/claude/text/src_bb2r.json", "w"), ensure_ascii=False, indent=0)
print("bb2r", len(bb["moves"]), len(bb["notes"]), list(bb["notes"].items())[:5])
