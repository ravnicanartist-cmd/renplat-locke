"""Hand-written story order for Blaze Black 2 Redux (PChal QoL). Gates are split numbers: 0 = Cheren split (from the
start), 1 = Roxie split, ... 9 = Champion split. Something with gate g can be used in every fight of split g or later.
Areas count as reachable for every fight in their split, so a mid-split villain fight is slightly generous."""
import re
SPLITS = ["Cheren", "Roxie", "Burgh", "Elesa", "Clay", "Skyla", "Drayden", "Marlon", "Ghetsis", "Champion"]
KEY = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())

AREA = {"Aspertia City": 0, "Route 19": 0, "Route 20": 0, "Floccesy Ranch": 0, "Floccesy Town": 0,
        "Virbank City": 1, "Virbank Complex": 1,
        "Castelia City": 2, "Castelia Sewers": 2, "Relic Passage": 2, "Route 4": 2,
        "Desert Resort": 3, "Relic Castle": 3, "Route 5": 3, "Route 16": 3, "Lostlorn Forest": 3, "Nimbasa City": 3,
        "Driftveil Drawbridge": 4, "Driftveil City": 4, "Route 6": 4, "Clay Tunnel": 4, "Anville Town": 4,
        "Mistralton Cave": 5, "Chargestone Cave": 5, "Route 7": 5, "Celestial Tower": 5, "Mistralton City": 5,
        "Reversal Mountain": 6, "Strange House": 6, "Undella Town": 6, "Undella Bay": 6, "Route 14": 6,
        "Abundant Shrine": 6, "Route 13": 6, "Route 12": 6, "Village Bridge": 6, "Route 11": 6, "Route 9": 6,
        "Shopping Mall Nine": 6, "Lentimas Town": 6, "Lacunosa Town": 6,
        "Seaside Cave": 7, "Route 21": 7, "Humilau City": 7, "Route 22": 7,
        "Giant Chasm": 8, "Route 23": 9, "Victory Road": 9}
SURF = 5        # HM03 Surf is handed over after the Plasma Frigate leaves Driftveil (start of the Skyla split)
FISH = 0        # Super Rod: Route 20 (Redux gives it early)
REMINDER = 5    # Move reminder in Mistralton City; PChal's PC reminder opens after you talk to him

_TMLOC = [("defeat cheren", 1), ("defeat roxie", 2), ("defeat burgh", 3), ("defeat elesa", 4), ("defeat clay", 5),
          ("defeat skyla", 6), ("defeat drayden", 7), ("defeat marlon", 8),
          ("relic passage", 4), ("pwt", 5), ("marine tube", 7), ("plasma frigate", 8), ("castelia gardens", 2)]
def tm_gate(loc):
    l = loc.lower()
    for k, g in _TMLOC:
        if k in l: return g
    best = None
    for a, g in AREA.items():
        if a.lower() in l: best = g if best is None else min(best, g)
    return best if best is not None else 9

def _load_tms():
    rows = [l.rstrip("\n").split("\t") for l in open("/home/claude/bb2/src/Important_Item_Locations/Technical_Machines.tsv", encoding="utf-8")]
    out = []
    for r in rows[3:]:
        if len(r) > 2 and r[0].startswith(("TM", "HM")):
            loc = r[2].replace("\\n", " / ")
            out.append((r[0], r[1], loc, tm_gate(loc)))
    return out
TMS = _load_tms()
TM_BY_MOVE = {KEY(mv): g for tm, mv, loc, g in TMS}
TM_BY_MOVE.update({KEY("Surf"): SURF, KEY("Cut"): 1, KEY("Strength"): 4, KEY("Fly"): 6, KEY("Waterfall"): 8, KEY("Dive"): 8})

EVO_ITEM = {"Water Stone": 0, "Fire Stone": 2, "Thunder Stone": 2, "Leaf Stone": 2, "Moon Stone": 2, "Sun Stone": 2,
            "Ice Stone": 2, "Prism Scale": 2, "Up-Grade": 2, "Dawn Stone": 3, "Shiny Stone": 4, "Link Cable": 4,
            "King's Rock": 4, "Metal Coat": 4, "Reaper Cloth": 4, "Dragon Scale": 5, "Dusk Stone": 6, "Dubious Disc": 6,
            "Electirizer": 6, "Magmarizer": 6, "Razor Fang": 6, "Razor Claw": 8, "Protector": 9}
# Castelia City gives ONE stone of your choice; any of them counts from the Burgh split.
EVO_ITEM_K = {KEY(k): v for k, v in EVO_ITEM.items()}
EVO_ITEM_K.update({KEY("Dubious Disk"): 6, KEY("Upgrade"): 2})

GIFTS = [(["Pansage", "Panpour", "Pansear"], "Floccesy Town (gift, depends on your starter)", "gift", 0, "Floccesy Town"),
         (["Bulbasaur", "Charmander", "Squirtle"], "Virbank City (Kanto starter, pick one)", "gift", 1, "Virbank City"),
         ("Meditite", "Virbank City (egg from Brawly)", "gift", 1, "Virbank City"),
         ("Eevee", "Castelia City (Amanita; Easy/Normal only)", "gift", 2, "Castelia City"),
         (["Chikorita", "Cyndaquil", "Totodile"], "Castelia City (Johto starter, pick one)", "gift", 2, "Castelia City"),
         (["Omanyte", "Kabuto", "Lileep", "Anorith", "Cranidos", "Shieldon", "Tirtouga", "Archen"], "Relic Castle / Desert Resort (random fossil)", "fossil", 3, "Relic Castle"),
         (["Treecko", "Torchic", "Mudkip"], "Anville Town (Hoenn starter, pick one)", "gift", 4, "Anville Town"),
         (["Turtwig", "Chimchar", "Piplup"], "Driftveil City (Sinnoh starter, pick one)", "gift", 4, "Driftveil City"),
         ("Zorua", "Driftveil City (after Rood)", "gift", 4, "Driftveil City"),
         ("Corsola", "Route 6 (Season Research Lab)", "gift", 4, "Route 6"),
         ("Stantler", "Route 5 (Hidden Grotto)", "static", 3, "Route 5"),
         ("Mandibuzz", "Route 4 (Thursdays, BB2)", "static", 2, "Route 4"),
         ("Volcarona", "Relic Castle (Volcarona room)", "static", 3, "Relic Castle"),
         ("Jellicent", "Undella Bay (Mondays, BB2)", "static", 6, "Undella Bay"),
         ("Lapras", "Village Bridge (Surf)", "static", 6, "Village Bridge"),
         ("Rotom", "Shopping Mall Nine", "static", 6, "Shopping Mall Nine"),
         ("Crustle", "Seaside Cave (Colress Machine)", "static", 7, "Seaside Cave"),
         ("Togepi", "Route 4 (trade for Meowth)", "trade", 2, "Route 4"),
         ("Ditto", "Route 7 (trade for Feebas)", "trade", 5, "Route 7")]
NOT_IN_CHALLENGE = {"Eevee"}
LEGENDARY = {"Cobalion", "Virizion", "Terrakion", "Reshiram", "Zekrom", "Kyurem", "Phione", "Latias", "Latios", "Genesect",
             "Keldeo", "Meloetta", "Tornadus", "Thundurus", "Landorus", "Heatran", "Regirock", "Regice", "Registeel",
             "Regigigas", "Uxie", "Mesprit", "Azelf", "Cresselia", "Darkrai", "Mew", "Mewtwo", "Celebi", "Jirachi"}

def boss_key(t):
    n, loc = t["name"], t["loc"] or ""
    if n.startswith("Leader ") and "Gym" in loc: return n.split(" ")[1].lower()
    if n.startswith("Elite Four "): return n.split(" ")[2].lower()
    if n.startswith("Champion "): return n.split(" ")[1].lower()
    if n == "PKMN Trainer Colress" and "Twist Mountain" not in loc: return "colress"
    if n.startswith("Team Plasma ") and "Grunt" not in n: return n.split(" ")[2].lower()
    return None
def label(t, k):
    n, loc = t["name"], t["loc"] or ""
    if n.startswith("Leader "): return n.split(" ")[1]
    if n.startswith("Elite Four "): return n.split(" ")[2]
    if n.startswith("Champion "): return n.split(" ")[1] + " (Champion)"
    who = n.split(" ")[-1]
    return f"{who} ({loc.replace('Plasma Frigate - ', 'Frigate: ')})"
NOTE = {"colress": "PKMN Trainer Colress on Route 4."}
