"""Earliest story stage at which each wild area / method / item ball is reachable (reach.py + hand-read story gates)."""
import reach as R, json, sys, collections
def coords(mapid, *scripts):
    return {(mapid, c["x"], c["y"]) for c in R.MAPS[mapid].get("coord_events") or [] if c.get("script") in scripts}
def objs(mapid, *scripts_or_flags):
    return {(mapid, o["x"], o["y"]) for o in R.MAPS[mapid].get("object_events") or [] if o.get("script") in scripts_or_flags or o.get("flag") in scripts_or_flags}
B32 = coords("MAP_ROUTE32", "Route32_EventScript_BaldingManTriggerLeft", "Route32_EventScript_BaldingManTriggerMid", "Route32_EventScript_BaldingManTriggerRight")
SUDO = objs("MAP_ROUTE36", "FLAG_HIDE_SUDOWOODO")
MAHO = coords("MAP_MAHOGANYTOWN", "MahoganyTown_EventScript_MerchantTrigger")
RECEP = coords("MAP_RECEPTION_GATE", "ReceptionGate_Trigger")
POST = coords("MAP_RINTO_VILLAGE", "Rinto_TriggerEastGuard") | coords("MAP_SOUTHERN_PASSAGE", "BlockSouthJohtoAccess") | objs("MAP_RINTO_VILLAGE", "Rinto_EastGuard")
DEN = coords("MAP_BLACKTHORN_CITY", "BlackThornCity_Trigger_Sage")       # Dragon's Den opens once Clair is beaten
# flag-less NPCs that a script moves aside later, and other gates read from the scripts: stage they open at -> tiles
GATES = [
    (12, objs("MAP_LAKE_OF_RAGE", "LakeOfRagePostgamePoliceman")),                  # Route 50 / Vajra East: FLAG_IS_CHAMPION
    (12, objs("MAP_ROUTE28", "Route28Guard")),                                     # Mt. Silver: after becoming Champion
    (8, objs("MAP_MAHOGANYTOWN", "MahoganyTown_EventScript_Merchant")),          # Rage Candy Bar man: gone once the Radio Tower is freed
    (9, objs("MAP_ECRUTEAK_CITY_SAGE_OFFICE1", "EcruteakCity_SageOffice2_EventScript_SageA")),   # Tin Tower: needs the Clear Bell (Kimono Girls, after Clair)
    (12, objs("MAP_SPROUT_TOWER_1F", "FLAG_HIDE_SPROUT_BASEMENT_GUARD")),        # Sprout Tower basement: after Elder Li's late rematch (his Lv 61 team)
]
# stage -> (caps, closed tiles)
def plan(extra=None):
    ex = list(GATES) + list(extra or [])
    S = []
    for s in range(13):
        caps = set()
        if s >= 1: caps |= {"rock"}
        if s >= 2: caps |= {"cut"}
        if s >= 3: caps |= {"strength"}
        if s >= 4: caps |= {"surf"}
        if s >= 7: caps |= {"whirl"}
        if s >= 9: caps |= {"waterfall"}
        if s >= 10: caps |= {"rockclimb"}
        closed = set()
        if s < 1: closed |= B32
        if s < 3: closed |= SUDO
        if s < 8: closed |= MAHO
        if s < 10: closed |= RECEP
        if s < 9: closed |= DEN
        if s < 12: closed |= POST
        opened = set()
        for until, tiles in ex:
            if s < until: closed |= tiles
            else: opened |= tiles
        S.append((caps, closed, opened))
    return S
def staged(extra=None):
    first = {}
    items = {}
    for s, (caps, closed, opened) in enumerate(plan(extra)):
        r = R.run(caps, closed=closed, opened=opened)
        for m, i in r.items():
            for k in ("enc", "water", "fish", "rock", "land"):
                if i[k]: first.setdefault((m, k), s)
            for it in i["items"]: items.setdefault((m, it), s)
    return first, items
if __name__ == "__main__":
    first, items = staged()
    json.dump({"first": {f"{m}|{k}": s for (m, k), s in first.items()}, "items": {f"{m}|{k}": s for (m, k), s in items.items()}}, open("/tmp/stages.json", "w"))
    E = json.load(open(R.SRC + "/docs/data/encounters.json"))
    for e in E:
        m = e["map"]
        meths = {mm["method"].split()[0] for v in e["variants"] for mm in v["methods"]}
        print(f"{e['name']:30}", {k: first.get((m, {"Land": "enc", "Water": "water", "Fishing": "fish", "Rock": "rock"}[k]), "NEVER") for k in sorted(meths)}, "" if (m, "land") in first else "MAP NEVER REACHED")
