"""Hand-authored story order for Renegade Platinum (PChal QoL build): which fights exist, which tab they sit in,
and after which fight each area, method, TM and evolution item becomes obtainable.  Keys refer to FIGHTS."""

# (key, tabs, trainer ids, kind)   kind: None = one trainer; "multi" = the ids fight together; "gauntlet" = back to back
# Variants (starter / gender / random E4 team) are worked out from the documentation notes of each id.
FIGHTS = [
    # ---- Roark split (cap 16)
    ("barry_201", "R", [850, 851, 852], None),
    ("dawn_202", "R", [929, 930, 928, 932, 933, 931], None),
    ("barry_203", "R", [247, 248, 249], None),
    ("roark", "G", [246], None),
    # ---- Gardenia split (cap 26)
    ("grunts_jubilife", "R", [414, 415], "multi"),
    ("grunt_843", "", [843], None),
    ("grunts_meadow", "", [296, 297], "multi"),
    ("grunt_298", "", [298], None),
    ("grunt_299", "", [299], None),
    ("mars_windworks", "V", [295], None),
    ("cheryl", "R", [1064], None),
    ("gardenia", "G", [315], None),
    # ---- Fantina split (cap 33)
    ("grunt_939", "", [939], None),
    ("grunt_421", "", [421], None),
    ("grunt_410", "", [410], None),
    ("grunt_412", "", [412], None),
    ("grunt_422", "", [422], None),
    ("grunt_423", "", [423], None),
    ("jupiter_eterna", "V", [406], None),
    ("mira", "R", [1065], None),
    ("dawn_207", "R", [940, 941, 942, 943, 944, 945], None),
    ("aaron_gate", "R", [946], None),
    ("fantina", "G", [318], None),
    # ---- Maylene split (cap 39)
    ("barry_hearthome", "R", [470, 471, 472], None),
    ("grunt_947", "", [947], None),
    ("grunt_949", "", [949], None),
    ("grunt_948", "", [948], None),
    ("grunts_mansion_gate", "", [951, 950], "multi"),
    ("grunt_957", "", [957], None),
    ("grunt_956", "", [956], None),
    ("grunt_955", "", [955], None),
    ("mansion_gauntlet", "", [952, 953, 954], "gauntlet"),
    ("grunt_958", "", [958], None),
    ("saturn_mansion", "V", [959, 960], "multi"),
    ("maylene", "G", [317], None),
    # ---- Wake split (cap 44)
    ("grunts_veilstone", "R", [849, 848], "multi"),
    ("wake", "G", [316], None),
    # ---- Byron split (cap 53)
    ("grunt_valor", "R", [847], None),
    ("dawn_210", "R", [963, 964, 965, 966, 967, 968], None),
    ("grunt_celestic", "", [416], None),
    ("cyrus_celestic", "V", [913], None),
    ("barry_canalave", "R", [476, 477, 478], None),
    ("riley", "R", [970], None),
    ("grunts_iron", "R", [836, 835], "multi"),
    ("byron", "G", [250], None),
    # ---- Candice split (cap 56)
    ("grunt_425", "", [425], None),
    ("grunt_417", "", [417], None),
    ("grunt_418", "", [418], None),
    ("saturn_valor", "V", [408], None),
    ("grunts_verity", "", [426, 419], "multi"),
    ("grunt_427", "", [427], None),
    ("grunt_420", "", [420], None),
    ("mars_verity", "V", [405], None),
    ("candice", "G", [319], None),
    # ---- Volkner split (cap 62)
    ("grunt_507", "", [507], None), ("grunt_508", "", [508], None), ("grunt_428", "", [428], None),
    ("grunt_510", "", [510], None), ("grunt_509", "", [509], None), ("grunt_512", "", [512], None),
    ("grunt_513", "", [513], None), ("grunt_430", "", [430], None), ("grunt_514", "", [514], None),
    ("grunt_522", "", [522], None),
    ("cyrus_hq", "V", [403], None),
    ("saturn_hq", "V", [409], None),
    ("grunt_523", "", [523], None), ("grunt_515", "", [515], None), ("grunt_516", "", [516], None),
    ("grunt_517", "", [517], None), ("grunt_519", "", [519], None), ("grunt_524", "", [524], None),
    ("grunt_518", "", [518], None), ("grunt_525", "", [525], None), ("grunt_520", "", [520], None),
    ("grunt_526", "", [526], None),
    ("grunts_spear", "", [521, 527], "multi"),
    ("mars_jupiter", "V", [528, 407], "multi"),
    ("cyrus_dp", "V", [972], None),
    ("cyrus_dw", "V", [404], None),
    ("volkner", "G", [320], None),
    # ---- Champion split (cap 78)
    ("marley", "R", [974], None),
    ("dawn_224", "R", [975, 976, 977, 978, 979, 980], None),
    ("barry_league", "R", [479, 480, 481], None),
    ("aaron", "G", [261, 981, 982, 983], None),
    ("bertha", "G", [262, 984, 985, 986], None),
    ("flint", "G", [263, 987, 988, 989], None),
    ("lucian", "G", [264, 990, 991, 992], None),
    ("cynthia", "G", [267, 993, 994, 995], None),
]
PARTNERS = {"grunts_jubilife": [613, 614, 615, 616, 617, 618], "grunts_veilstone": [621, 622, 623, 624, 625, 626],
            "saturn_mansion": [470, 471, 472], "mars_jupiter": [607, 619, 620], "grunts_iron": [609]}
LABELS = {"barry_201": "Barry (Route 201)", "dawn_202": "Dawn / Lucas (Route 202)", "barry_203": "Barry (Route 203)",
          "grunts_jubilife": "Galactic Grunts (Jubilife, with Dawn/Lucas)", "cheryl": "Cheryl (Eterna Forest)",
          "mira": "Mira (Wayward Cave, optional)", "dawn_207": "Dawn / Lucas (Route 207)", "aaron_gate": "Aaron (Hearthome west gate)",
          "barry_hearthome": "Barry (Hearthome east gate)", "grunts_veilstone": "Galactic Grunts (Veilstone, with Dawn/Lucas)",
          "grunt_valor": "Galactic Grunt (Valor Lakefront)", "dawn_210": "Dawn / Lucas (Route 210)", "barry_canalave": "Barry (Canalave)",
          "riley": "Riley (Iron Island)", "grunts_iron": "Galactic Grunts (Iron Island, with Riley)", "marley": "Marley (Victory Road)",
          "dawn_224": "Dawn / Lucas (Route 224)", "barry_league": "Barry (Pokémon League)",
          "mars_windworks": "Mars (Valley Windworks)", "jupiter_eterna": "Jupiter (Eterna Galactic Building)",
          "saturn_mansion": "Saturn + Backlot (Pokémon Mansion, with Barry)", "cyrus_celestic": "Cyrus (Celestic Ruins)",
          "saturn_valor": "Saturn (Lake Valor)", "mars_verity": "Mars (Lake Verity)", "cyrus_hq": "Cyrus (Galactic HQ)",
          "saturn_hq": "Saturn (Galactic HQ)", "mars_jupiter": "Mars + Jupiter (Spear Pillar, with Barry)",
          "cyrus_dp": "Cyrus: Dialga + Palkia (Distortion World)", "cyrus_dw": "Cyrus (Distortion World)",
          "grunts_meadow": "Galactic Grunts (Floaroma Meadow)", "grunts_mansion_gate": "Galactic Grunts (Mansion gate)",
          "mansion_gauntlet": "Galactic Grunts (Mansion gauntlet)", "grunts_verity": "Galactic Grunts (Lake Verity)",
          "grunts_spear": "Galactic Grunts (Spear Pillar)"}
NOTE = {"dawn_224": "The documentation lists this fight before the League. Route 224 opens after the Elite Four in the base game.",
        "mira": "Wayward Cave is optional.", "cyrus_dp": "Double battle against Dialga and Palkia at level 70.",
        "volkner": "Known game bug from the docs: Volkner's Rotoms use plain Rotom stats, not their appliance stats. The model uses what the game does."}
CAPS = {"ROARK": 16, "GARDENIA": 26, "FANTINA": 33, "MAYLENE": 39, "WAKE": 44, "BYRON": 53, "CANDICE": 56, "VOLKNER": 62, "CHAMPION": 78}

# Areas from the ENCOUNTERS sheet -> the fight after which you can first reach them ("" = from the start).
# Grass/cave/ground slots follow the area; Surf, rods, honey trees and the Poké Radar have their own gates below.
AREA = {
    "ROUTE 201": "", "TWINLEAF TOWN": "", "LAKE VERITY": "", "ROUTE 202": "", "SANDGEM TOWN": "barry_201",
    "JUBILIFE CITY": "dawn_202", "TRAINER SCHOOL": "dawn_202", "ROUTE 218": "dawn_202", "ROUTE 219": "dawn_202",
    "ROUTE 204 (SOUTH)": "dawn_202", "ROUTE 203": "dawn_202",
    "OREBURGH GATE": "barry_203", "OREBURGH GATE (1F)": "barry_203", "OREBURGH GATE (B1F)": "roark",
    "OREBURGH CITY": "barry_203", "ROUTE 207": "barry_203", "OREBURGH MINE": "barry_203",
    "RAVAGED PATH": "roark", "ROUTE 204 (NORTH)": "roark", "FLOAROMA TOWN": "roark", "FLOAROMA MEADOW": "roark",
    "VALLEY WINDWORKS": "roark", "ROUTE 205 (SOUTH)": "roark", "ETERNA FOREST": "roark",
    "OLD CHATEAU": "gardenia", "ROUTE 205 (NORTH)": "cheryl", "ETERNA CITY": "cheryl",
    "ROUTE 211 (WEST)": "gardenia", "MT. CORONET": "gardenia", "MT. CORONET (R211 ENTRY)": "gardenia",
    "ROUTE 211 (EAST)": "gardenia", "MT. CORONET (B1F)": "gardenia", "MINING MUSEUM": "gardenia",
    "GALACTIC BUILDING": "jupiter_eterna", "ROUTE 206": "jupiter_eterna", "WAYWARD CAVE (BOTH)": "jupiter_eterna",
    "MT. CORONET (R207 ENTRY)": "jupiter_eterna", "ROUTE 208": "jupiter_eterna",
    "ROUTE 212 (NORTH)": "fantina", "TROPHY GARDEN": "fantina", "POKEMON MANSION": "saturn_mansion",
    "ROUTE 209": "barry_hearthome", "SOLACEON RUINS": "barry_hearthome", "LOST TOWER": "barry_hearthome",
    "ROUTE 210 (SOUTH)": "barry_hearthome", "ROUTE 215": "barry_hearthome",
    "MANIAC TUNNEL": "maylene", "ROUTE 214": "maylene", "VALOR LAKEFRONT": "maylene", "ROUTE 213": "maylene",
    "PASTORIA CITY": "maylene", "AREA 1 AND 2": "maylene", "AREA 3 AND 4": "maylene", "AREA 5 AND 6": "maylene",
    "ROUTE 212 (SOUTH)": "maylene",
    "ROUTE 210 (NORTH)": "grunt_valor", "CELESTIC TOWN": "dawn_210", "FUEGO IRONWORKS": "cyrus_celestic",
    "ROUTE 220": "cyrus_celestic", "ROUTE 221": "cyrus_celestic", "CANALAVE CITY": "cyrus_celestic",
    "IRON ISLAND": "barry_canalave",
    "LAKE VALOR": "saturn_valor", "MT. CORONET (R216 ENTRY)": "mars_verity", "ROUTE 216": "mars_verity",
    "ROUTE 217": "mars_verity", "ACUITY LAKEFRONT": "mars_verity", "LAKE ACUITY": "candice",
    "MT. CORONET (2F, 3F)": "saturn_hq", "MT. CORONET (4F)": "saturn_hq", "MT. CORONET (SNOW AREA)": "saturn_hq",
    "MT. CORONET (SUMMIT)": "saturn_hq", "MT. CORONET (5F, 6F, 7F)": "saturn_hq", "DISTORTION WORLD": "post",
    "SENDOFF SPRING": "cyrus_dw", "ROUTE 222": "cyrus_dw", "SUNYSHORE CITY": "cyrus_dw",
    "ROUTE 223": "volkner", "VICTORY ROAD": "volkner", "VICTORY ROAD (2F)": "volkner", "VICTORY ROAD (B1F)": "volkner",
    "POKEMON LEAGUE": "volkner",
    # after the Elite Four
    "TURNBACK CAVE": "post", "SNOWPOINT TEMPLE": "post", "ROUTE 224": "post", "FLOWER PARADISE": "post",
    "ROUTE 225": "post", "ROUTE 226": "post", "ROUTE 227": "post", "ROUTE 228": "post", "ROUTE 229": "post",
    "RESORT AREA": "post", "ROUTE 230": "post", "STARK MOUNTAIN": "post", "STARK MOUNTAIN (OUTSIDE)": "post",
    "STARK MOUNTAIN (INSIDE)": "post",
}
# Methods with their own gate (fight after which the method is available)
SURF = "cyrus_celestic"          # HM03 Surf from the Celestic elder; the Fen Badge (Wake) lets you use it outside battle
RODS = {"O": "dawn_202",         # Old Rod: fisherman on Route 218, next to Jubilife
        "G": "barry_hearthome",  # Good Rod: Route 209
        "S": "mars_verity"}      # Super Rod: Snowpoint City
HONEY = "roark"                  # honey trees need Honey (Floaroma)
RADAR = "post"                   # Poké Radar needs the National Dex
MOVE_REMINDER = "maylene"        # Move reminder in Pastoria; PChal's PC reminder opens after you talk to him
TUTORS = "maylene"               # PChal: every move tutor is in the PC once Maylene is beaten

# Gifts / statics / trades / eggs: species -> fight after which you can get it (None = not obtainable in this build)
SPECIAL = {
    "Turtwig": "", "Chimchar": "", "Piplup": "",            # starter, and Rowan's suitcase gives one of the other two
    "Eevee": "", "Bulbasaur": "dawn_202", "Charmander": "dawn_202", "Squirtle": "dawn_202",
    "Treecko": "barry_203", "Torchic": "barry_203", "Mudkip": "barry_203",
    "Chikorita": "roark", "Cyndaquil": "roark", "Totodile": "roark",
    "Spheal": "barry_203", "Skorupi": "roark", "Chatot": "cheryl", "Porygon": "jupiter_eterna", "Togepi": "jupiter_eterna",
    "Drifloon": "roark", "Rotom": "gardenia", "Gengar": "gardenia", "Spiritomb": "barry_hearthome",
    "Omanyte": "gardenia", "Kabuto": "gardenia", "Aerodactyl": "gardenia", "Lileep": "gardenia", "Anorith": "gardenia",
    "Cranidos": "gardenia", "Shieldon": "gardenia",
    # Trainer School egg (one of these at random); PChal removed Happiny and Togepi from it
    "Pichu": "dawn_202", "Cleffa": "dawn_202", "Igglybuff": "dawn_202", "Tyrogue": "dawn_202", "Smoochum": "dawn_202",
    "Elekid": "dawn_202", "Magby": "dawn_202", "Azurill": "dawn_202", "Wynaut": "dawn_202", "Budew": "dawn_202",
    "Chingling": "dawn_202", "Bonsly": "dawn_202", "Mime Jr.": "dawn_202", "Munchlax": "dawn_202", "Riolu": "dawn_202",
    "Mantyke": "dawn_202",
}
REMOVED = {"Beldum@OREBURGH CITY": "PChal removed Steven's Beldum", "Lapras@PASTORIA CITY": "PChal removed the Pastoria Lapras",
           "Gabite@WAYWARD CAVE (BOTH)": "PChal removed the Wayward Cave Gabite", "Happiny@TRAINER SCHOOL": "removed from the egg",
           "Togepi@TRAINER SCHOOL": "removed from the egg"}
LEGENDARY = {"Mew", "Zapdos", "Moltres", "Articuno", "Celebi", "Entei", "Raikou", "Suicune", "Jirachi", "Regigigas",
             "Giratina (Altered)", "Giratina (Origin)", "Giratina", "Shaymin (Land)", "Shaymin", "Dialga", "Palkia",
             "Uxie", "Mesprit", "Azelf", "Heatran", "Cresselia", "Manaphy", "Phione", "Darkrai", "Arceus",
             "Regice", "Regirock", "Registeel", "Mewtwo", "Lugia", "Ho-Oh", "Kyogre", "Groudon", "Rayquaza",
             "Latias", "Latios", "Deoxys (Normal)", "Magikarp (GER)"}

# Evolution items -> fight after which you can get one (from the item locations sheet)
EVO_ITEM = {"Fire Stone": "barry_203", "Water Stone": "barry_203", "Thunderstone": "barry_203", "Thunder Stone": "barry_203",
            "Leaf Stone": "barry_203", "Moon Stone": "barry_203", "Sun Stone": "barry_203", "Ice Stone": "barry_203",
            "Oval Stone": "barry_203",                                   # all in Oreburgh Mine / Oreburgh City
            "Shiny Stone": "aaron_gate", "Up-Grade": "aaron_gate",       # Hearthome City
            "Dusk Stone": "jupiter_eterna", "King's Rock": "jupiter_eterna", "Dawn Stone": "jupiter_eterna",
            "Metal Coat": "jupiter_eterna",                              # Wayward Cave, Eterna bike shop, Route 207
            "Reaper Cloth": "barry_hearthome", "Razor Claw": "barry_hearthome",   # Lost Tower, Route 215
            "Dragon Scale": "saturn_mansion", "Dubious Disc": "saturn_mansion",   # Veilstone City
            "Electrizer": "maylene", "Electirizer": "maylene", "Magmarizer": "maylene",  # Hotel Grand Lake, Route 213
            "Protector": "barry_canalave",                               # Iron Island
            "Prism Scale": "gardenia",                                   # Mt. Coronet
            "Deep Sea Scale": "roark", "Deep Sea Tooth": "roark",        # Floaroma Town
            "Mt. Coronet": "gardenia"}                                   # "level up at Mt. Coronet"
# Razor Fang has no location in the docs, so Gligar -> Gliscor is skipped.

# TMs / HMs -> fight after which you can get them (no Poké Mart sells TMs in Renegade Platinum)
TM = {
    "TM01": "roark", "TM02": SURF, "TM03": SURF, "TM04": "barry_hearthome", "TM05": "maylene", "TM06": "maylene",
    "TM07": "mars_verity", "TM08": "roark", "TM09": "roark", "TM10": "dawn_202", "TM11": SURF, "TM12": "gardenia",
    "TM13": "mars_verity", "TM14": "candice", "TM15": "cyrus_dw", "TM16": "gardenia", "TM17": "maylene", "TM18": "volkner",
    "TM19": "barry_hearthome", "TM20": "fantina", "TM21": "candice", "TM22": "grunt_valor", "TM23": "barry_canalave",
    "TM24": SURF, "TM25": "saturn_valor", "TM26": "saturn_mansion", "TM27": "cheryl", "TM28": "cheryl", "TM29": "barry_hearthome",
    "TM30": "fantina", "TM31": "roark", "TM32": "jupiter_eterna", "TM33": "gardenia", "TM34": "roark", "TM35": SURF,
    "TM36": "maylene", "TM37": "post", "TM38": SURF, "TM39": "roark", "TM40": "roark", "TM41": "maylene", "TM42": "dawn_202",
    "TM43": "aaron_gate", "TM44": "aaron_gate", "TM45": "aaron_gate", "TM46": "cheryl", "TM47": "barry_hearthome",
    "TM48": "cyrus_celestic", "TM49": "candice", "TM50": "cyrus_dw", "TM51": "barry_hearthome", "TM52": "mars_verity",
    "TM53": "maylene", "TM54": "cheryl", "TM55": "aaron_gate", "TM56": "cyrus_dw", "TM57": "volkner", "TM58": "dawn_202",
    "TM59": "maylene", "TM60": "maylene", "TM61": "barry_hearthome", "TM62": "maylene", "TM63": "saturn_mansion",
    "TM64": "saturn_mansion", "TM65": "gardenia", "TM66": "barry_hearthome", "TM67": "cheryl", "TM68": "volkner",
    "TM69": "jupiter_eterna", "TM70": "roark", "TM71": "roark", "TM72": "candice", "TM73": "gardenia", "TM74": "jupiter_eterna",
    "TM75": "jupiter_eterna", "TM76": "roark", "TM77": "gardenia", "TM78": "roark", "TM79": "saturn_mansion",
    "TM80": "cheryl", "TM81": "aaron_gate", "TM82": "gardenia", "TM83": "barry_hearthome", "TM84": "maylene",
    "TM85": "mira", "TM86": "gardenia", "TM87": "saturn_mansion", "TM88": "grunt_valor", "TM89": "cyrus_celestic",
    "TM90": None, "TM91": "byron", "TM92": "maylene",
    "HM01": "gardenia", "HM02": "grunts_veilstone", "HM03": "cyrus_celestic", "HM04": "grunts_iron", "HM05": "barry_hearthome",
    "HM06": "barry_203", "HM07": "wake", "HM08": "candice",
}
