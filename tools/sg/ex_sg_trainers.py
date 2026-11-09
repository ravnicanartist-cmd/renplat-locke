"""PChal Sacred Gold Trainer_Battles.xlsx -> trainers per split (same template as the BB2 Redux / Renegade Platinum workbooks)."""
import json, collections, importlib.util
_spec = importlib.util.spec_from_file_location("bb2_ex_trainers", "/home/claude/bb2/ex_trainers.py")
X = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(X)
X.FILES = {"sg": "/mnt/user-data/uploads/e8cb29ec-Trainer_Battles.xlsx"}
X.SPLITS = ["Falkner", "Bugsy", "Whitney", "Morty", "Chuck", "Jasmine", "Pryce", "Clair", "Champion"]
if __name__ == "__main__":
    T = X.parse("sg")
    print(len(T), collections.Counter(t["fill"] for t in T), collections.Counter(t["split"] for t in T))
    json.dump(T, open("/home/claude/sg/trainers_sg.json", "w"), ensure_ascii=False)
    for t in [t for t in T if t["name"].startswith(("Leader", "Elite", "Champion", "Rival", "Executive", "Pkmn", "PKMN"))][:40]:
        print(t["split"], "|", t["loc"], "|", t["name"], t["mand"], t["notes"][:2], [(m["s"], m["l"]) for m in t["team"]])
