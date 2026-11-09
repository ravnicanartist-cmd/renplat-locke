"""Sacred Gold (PChal QoL, HeartGold base): story order, and when areas, TMs, items and gifts open up.

Stage n = everything you can reach while preparing for the n-th split's leader (0 = Falkner ... 8 = Elite Four / Lance,
9 = Kanto postgame). A gym's TM reward therefore opens at the next stage.
Sources: PChal's Trainer_Battles "Raw Notes" (which trainers / places belong to which split), Pokemon_Locations,
Important_Item_Locations, and the original HeartGold locations for TMs the docs list as "No change"."""
import re

SPLITS = ["Falkner", "Bugsy", "Whitney", "Morty", "Chuck", "Jasmine", "Pryce", "Clair", "Champion", "Kanto"]
F, BU, WH, MO, CH, JA, PR, CL, E4, KA = range(10)

AREA = {
    "New Bark Town": F, "Route 29": F, "Route 46": F, "Cherrygrove City": F, "Route 30": F, "Route 31": F,
    "Dark Cave (Violet City Side)": F, "Violet City": F, "Sprout Tower": F,
    "Route 32": BU, "Ruins of Alph": BU, "Union Cave": BU, "Route 33": BU, "Slowpoke Well": BU, "Azalea Town": BU,
    "Ilex Forest": WH, "Route 34": WH, "Goldenrod City": WH, "Route 35": WH, "National Park": WH, "Route 36": WH,
    "Route 37": MO, "Ecruteak City": MO, "Burned Tower": MO,
    "Route 38": CH, "Route 39": CH, "Olivine City": CH, "Route 40": CH, "Route 41": CH, "Cianwood City": CH,
    "Route 47": JA, "Cliff Cave": JA, "Route 48": JA,
    "Route 42": PR, "Mt. Mortar": PR, "Route 43": PR, "Lake of Rage": PR, "Mahogany Town": PR,
    "Whirl Islands": CL, "Route 44": CL, "Ice Path": CL, "Blackthorn City": CL, "Route 45": CL, "Dark Cave (Blackthorn Side)": CL,
    "Bell Tower": E4, "Dragon's Den": E4, "Tohjo Falls": E4, "Route 27": E4, "Route 26": E4, "Victory Road": E4,
}
SURF = CH          # HM03 from Morty's town after his badge
ROD = {"old": F, "good": CH, "super": CL}   # Old Rod: Cherrygrove; Good Rod: Olivine diner; Super Rod: Blackthorn
ROCKSMASH = BU     # HM06 on Route 36, usable with the Zephyr Badge
RADIO = CL         # Hoenn / Sinnoh Sound: Expansion Card after the Radio Tower
REMINDER = CL      # Move Reminder in Blackthorn City

def gate_text(t):
    """stage at which a location in the item docs can be reached"""
    t = t.lower()
    if re.search(r"indigo plateau|victory road|route 2[67]|tohjo|dragon's den|bell tower|bellchime", t): return E4 if "bellchime" not in t else MO
    if re.search(r"celadon|saffron|vermilion|cerulean|pewter|viridian|lavender|fuchsia|cinnabar|route (1[0-9]|[1-9])\b|rock tunnel|power plant|kanto|silph|diglett|seafoam|pallet", t): return KA
    for k, v in sorted(AREA.items(), key=lambda kv: -len(kv[0])):
        if k.lower() in t: return v
    if "olivine" in t or "lighthouse" in t: return CH
    if "safari zone" in t or "battle frontier" in t: return PR
    if "radio tower" in t or "team rocket's hideout" in t or "rocket hq" in t or "hideout" in t: return PR
    if "sprout tower" in t: return F
    return None

# (TM, move, where, stage). Docs text first; "No change" ones use the original HeartGold location.
TMS_RAW = [
    (1, "Focus Punch", "Chuck's reward", JA), (2, "Dragon Claw", "Goldenrod lottery only", 99), (3, "Water Pulse", "Fisherman in Route 32's Pokémon Center", BU),
    (4, "Calm Mind", "Goldenrod Pokémon Center", WH), (5, "Roar", "Route 32 (Cut)", WH), (6, "Toxic", "After Petrel in Cliff Cave", JA),
    (7, "Hail", "Mahogany shop; Pryce's reward", PR), (8, "Bulk Up", "Goldenrod Pokémon Center", WH), (9, "Bullet Seed", "Route 32", BU),
    (10, "Hidden Power", "Ruins of Alph (7 Unown types)", 99), (11, "Sunny Day", "Mahogany shop", PR), (12, "Taunt", "—", WH),
    (13, "Ice Beam", "Goldenrod Game Corner (4,000 coins); Ice Path", WH), (14, "Blizzard", "Goldenrod Dept. Store", WH), (15, "Hyper Beam", "Goldenrod Dept. Store", WH),
    (16, "Reflect", "—", WH), (17, "Protect", "—", WH), (18, "Rain Dance", "Mahogany shop", PR), (19, "Giga Drain", "Route 39", CH), (20, "Safeguard", "—", WH),
    (21, "Frustration", "Goldenrod Dept. Store (Sundays)", WH), (22, "Solar Beam", "Goldenrod Dept. Store", WH), (23, "Iron Tail", "Jasmine's reward", PR),
    (24, "Thunderbolt", "Goldenrod Game Corner (4,000 coins); Olivine shore", WH), (25, "Thunder", "Goldenrod Dept. Store", WH), (26, "Earthquake", "Celadon City", KA),
    (27, "Return", "Goldenrod Dept. Store (Sundays)", WH), (28, "Dig", "Goldenrod City", WH), (29, "Psychic", "Ruins of Alph", BU), (30, "Shadow Ball", "Morty's reward", CH),
    (31, "Brick Break", "Man on Route 36", MO), (32, "Double Team", "—", WH), (33, "Light Screen", "—", WH), (34, "Shock Wave", "Azalea Pokémon Center", BU),
    (35, "Flamethrower", "Goldenrod Game Corner (4,000 coins); Bellchime Trail", WH), (36, "Sludge Bomb", "Route 43 gate after the Rocket Hideout", PR), (37, "Sandstorm", "Mahogany shop", PR),
    (38, "Fire Blast", "Goldenrod Dept. Store", WH), (39, "Rock Tomb", "Union Cave B1F", BU), (40, "Aerial Ace", "Route 34", WH), (41, "Torment", "—", KA), (42, "Facade", "Goldenrod lottery", 99),
    (43, "Secret Power", "Lake of Rage (Surf)", PR), (44, "Rest", "—", WH), (45, "Attract", "Whitney's reward", MO), (46, "Thief", "Man in Azalea Town", BU), (47, "Steel Wing", "Olivine Lighthouse", CH),
    (48, "Skill Swap", "Mahogany shop", PR), (49, "Snatch", "—", PR), (50, "Overheat", "Burned Tower basement", MO), (51, "Roost", "Falkner's reward", BU), (52, "Focus Blast", "Goldenrod Dept. Store", WH),
    (53, "Energy Ball", "Girl on Route 39", CH), (54, "False Swipe", "Goldenrod Dept. Store", WH), (55, "Brine", "Goldenrod Dept. Store", WH), (56, "Fling", "Rock Tunnel", KA), (57, "Charge Beam", "Lottery / Power Plant", KA),
    (58, "Endure", "—", WH), (59, "Dragon Pulse", "Clair's reward", E4), (60, "Drain Punch", "Goldenrod lottery", 99), (61, "Will-O-Wisp", "Fantina in Ecruteak", MO), (62, "Silver Wind", "Route 39", CH),
    (63, "Embargo", "Route 40", CH), (64, "Explosion", "Kanto Underground", KA), (65, "Shadow Claw", "Ecruteak City", MO), (66, "Payback", "Route 35", WH), (67, "Recycle", "—", KA),
    (68, "Giga Impact", "Celadon Game Corner", KA), (69, "Rock Polish", "Route 10", KA), (70, "Flash", "Route 10 Pokémon Center", KA), (71, "Stone Edge", "Man in Indigo Plateau", E4),
    (72, "Avalanche", "Ice Path B2F", CL), (73, "Thunder Wave", "Volkner in Olivine Lighthouse", CH), (74, "Gyro Ball", "Celadon Game Corner", KA), (75, "Swords Dance", "—", WH),
    (76, "Stealth Rock", "Mt. Mortar", PR), (77, "Psych Up", "—", WH), (78, "Captivate", "—", KA), (79, "Dark Pulse", "Victory Road 3F", E4), (80, "Rock Slide", "Mt. Mortar", PR),
    (81, "X-Scissor", "Bug Catcher in Ilex Forest", WH), (82, "Sleep Talk", "—", WH), (83, "Natural Gift", "—", 99), (84, "Poison Jab", "After Ariana on Route 47", JA), (85, "Dream Eater", "Viridian City", KA),
    (86, "Grass Knot", "Gardenia in Ilex Forest; Goldenrod Dept. Store", WH), (87, "Swagger", "—", WH), (88, "Pluck", "Route 40", CH), (89, "U-turn", "Bugsy's reward", WH), (90, "Substitute", "—", WH),
    (91, "Flash Cannon", "Route 9 / lottery", KA), (92, "Trick Room", "Clown in Ecruteak City", MO),
]
HMS = [("HM01", "Cut", "Ilex Forest", WH), ("HM02", "Fly", "Cianwood City", JA), ("HM03", "Surf", "Ecruteak Dance Theater", CH), ("HM04", "Strength", "Olivine City", CH),
       ("HM05", "Whirlpool", "Rocket Hideout", CL), ("HM06", "Rock Smash", "Route 36", BU), ("HM07", "Waterfall", "Ice Path (Rising Badge to use)", E4), ("HM08", "Rock Climb", "Kanto, 16 badges", 99)]
TMS = [(f"TM{n:02d}", mv, loc, g) for n, mv, loc, g in TMS_RAW] + HMS
KEYF = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
TM_BY_MOVE = {}
for tm, mv, loc, g in TMS: TM_BY_MOVE[KEYF(mv)] = min(g, TM_BY_MOVE.get(KEYF(mv), 99))

# evolution items: earliest stage you can hold one. The Sprout Tower Elder gives ONE of the starred items (your choice).
EVO_ITEM = {
    "Fire Stone": F, "Thunder Stone": F, "Water Stone": F, "Woodland Ore": F, "Serenade Orb": F, "Aubade Orb": F, "Chilled Ore": F,   # Elder Li's choice
    "Leaf Stone": WH, "Dawn Stone": WH, "Oval Stone": WH, "Covenant Orb": BU, "Moon Stone": CH, "Sun Stone": CH, "Metal Coat": CH,
    "Razor Claw": CH, "Razor Fang": CH, "Deep Sea Scale": JA, "Deep Sea Tooth": JA, "Up-Grade": JA, "Dusk Stone": PR, "Voltaic Ore": PR,
    "King's Rock": PR, "Dubious Disc": PR, "Shiny Stone": PR, "Electirizer": CL, "Magmarizer": CL, "Reaper Cloth": CL, "Dragon Scale": CL, "Protector": E4,
}
EVO_ITEM_K = {KEYF(k): v for k, v in EVO_ITEM.items()}

LEGENDARY = {"Raikou", "Entei", "Suicune", "Lugia", "Ho-Oh", "Celebi", "Mewtwo", "Mew", "Articuno", "Zapdos", "Moltres", "Kyogre", "Groudon", "Rayquaza",
             "Latias", "Latios", "Dialga", "Palkia", "Giratina", "Arceus", "Regirock", "Regice", "Registeel", "Regigigas", "Heatran", "Cresselia",
             "Darkrai", "Shaymin", "Manaphy", "Phione", "Jirachi", "Deoxys", "Uxie", "Mesprit", "Azelf"}

# (species or [choices], where, how, stage, nuzlocke area)
GIFTS = [
    ("Eevee", "Route 30 (Mr. Pokémon's house)", "gift", F, "Route 30"),
    (["Bulbasaur", "Charmander", "Squirtle"], "Violet City Pokémon Center (Juggler's quiz)", "gift", F, "Violet City"),
    ("Togepi", "Violet City Pokémon Center (Egg, Zephyr Badge)", "egg", BU, "Violet City"),
    (["Treecko", "Torchic", "Mudkip"], "Azalea Town Pokémon Center (Juggler's quiz)", "gift", BU, "Azalea Town"),
    ("Beldum", "Azalea Town (trade for Gible)", "trade", BU, "Azalea Town"),
    ("Gligar", "Violet City (trade for Rhyhorn)", "trade", BU, "Violet City"),
    (["Turtwig", "Chimchar", "Piplup"], "Goldenrod City Pokémon Center (Juggler's quiz)", "gift", WH, "Goldenrod City"),
    (["Smeargle", "Tangela", "Porygon"], "Goldenrod Game Corner (coins)", "gift", WH, "Goldenrod City"),
    ("Torkoal", "Goldenrod Dept. Store (trade for Noctowl)", "trade", WH, "Goldenrod City"),
    ("Spearow", "Route 35 gate", "gift", WH, "Route 35"),
    ("Spiritomb", "Slowpoke Well entrance (Odd Keystone)", "static", WH, "Slowpoke Well"),
    ("Rotom", "New Bark Town, home TV (Plain Badge)", "static", MO, "New Bark Town"),
    ("Sudowoodo", "Route 36 (Squirt Bottle)", "static", MO, "Route 36"),
    ("Castform", "Goldenrod City, Bill's house", "gift", MO, "Goldenrod City"),
    ("Smoochum", "Ecruteak City (trade for Mime Jr.)", "trade", MO, "Ecruteak City"),
    ("Lapras", "Union Cave (Fridays, Surf)", "static", CH, "Union Cave"),
    ("Skarmory", "Olivine City (trade for Electabuzz)", "trade", CH, "Olivine City"),
    ("Steelix", "Olivine City (trade)", "trade", CH, "Olivine City"),
    ("Shuckle", "Cianwood City", "gift", CH, "Cianwood City"),
    ("Pikachu", "Cianwood City (max friendship)", "gift", CH, "Cianwood City"),
    ("Tyrogue", "Mt. Mortar B1F (Black Belt Kiyo)", "gift", PR, "Mt. Mortar"),
    ("Riolu", "Mahogany Town (Egg)", "egg", PR, "Mahogany Town"),
    ("Gyarados", "Lake of Rage (red Gyarados)", "static", PR, "Lake of Rage"),
]
NOT_IN_GAME = {"Volbeat", "Lunatone"}    # Storm Silver swarms; this is Sacred Gold (HeartGold base)

def boss_key(t):
    n = t["name"]
    if n.startswith("Leader "): return n.split()[1].lower()
    if n.startswith("Elite Four "): return n.split()[-1].lower()
    if n.startswith("Champion "): return "lance"
    if n.startswith("Executive "): return n.split()[-1].lower()
    return None

def label(t, k):
    n = t["name"]
    for p in ("Leader ", "Elite Four ", "Champion ", "Executive "):
        if n.startswith(p): n = n[len(p):]
    if t["name"].startswith("Executive"):
        return f"{n} ({t['loc']})"
    if t["name"].startswith("Champion"): return f"{n} (Champion)"
    return n

NOTE = {}
KANTO = [(255, "surge", "Lt. Surge", "Vermilion City Gym"), (258, "sabrina", "Sabrina", "Saffron City Gym"), (254, "misty", "Misty", "Cerulean City Gym"),
         (256, "erika", "Erika", "Celadon City Gym"), (257, "janine", "Janine", "Fuchsia City Gym"), (253, "brock", "Brock", "Pewter City Gym"),
         (259, "blaine", "Blaine", "Seafoam Islands Gym"), (261, "blue", "Blue", "Viridian City Gym"), (260, "red", "Red", "Mt. Silver")]
