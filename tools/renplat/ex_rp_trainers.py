"""PChal Renegade Platinum Trainer_Battles.xlsx -> trainers per split (same template as the BB2 Redux workbooks)."""
import sys, json, collections, importlib.util
_spec = importlib.util.spec_from_file_location("bb2_ex_trainers", "/home/claude/bb2/ex_trainers.py")
X = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(X)
X.FILES = {"rp": "/mnt/user-data/uploads/6f9de92f-Trainer_Battles.xlsx"}
X.SPLITS = ["Roark", "Gardenia", "Fantina", "Maylene", "Wake", "Byron", "Candice", "Volkner", "Champion"]
if __name__ == "__main__":
    T = X.parse("rp")
    print(len(T), collections.Counter(t["fill"] for t in T), collections.Counter(t["split"] for t in T))
    json.dump(T, open("/home/claude/rp2/trainers_rp.json", "w"), ensure_ascii=False)
    for t in T[:6] + [t for t in T if "Leader" in t["name"]][:3]: print(t["split"], t["loc"], t["name"], t["mand"], t["notes"][:2], [(m["s"], m["l"], m["a"], m["m"]) for m in t["team"]][:2])
