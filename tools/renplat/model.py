"""The 1-on-1 model shared by every game. The caller sets MONS, MOVES (name -> {t, c, bp}), NATURES, FIXED, MULTI."""
import math
from collections import OrderedDict
MONS, MOVES = {}, {}
# Moves left out on the player's side (Carlos never uses them): must recharge, Last Resort, and moves that faint the user
NOUSE = {"Hyper Beam", "Giga Impact", "Blast Burn", "Frenzy Plant", "Hydro Cannon", "Rock Wrecker", "Roar of Time", "Prismatic Laser",
         "Eternabeam", "Meteor Assault", "Last Resort", "Explosion", "Self-Destruct", "Selfdestruct", "Misty Explosion", "Final Gambit", "Memento",
         # only work in special situations (target asleep, first turn, hits two turns later, ...)
         "Dream Eater", "Future Sight", "Doom Desire", "Focus Punch", "Fake Out", "First Impression", "Belch", "Snore"}
FIXED = {"Seismic Toss": "level", "Night Shade": "level", "Dragon Rage": 40, "Sonic Boom": 20}
MULTI = {}
NATURES = OrderedDict([("Hardy", None), ("Lonely", ["at", "df"]), ("Brave", ["at", "sp"]), ("Adamant", ["at", "sa"]),
    ("Naughty", ["at", "sd"]), ("Bold", ["df", "at"]), ("Docile", None), ("Relaxed", ["df", "sp"]), ("Impish", ["df", "sa"]),
    ("Lax", ["df", "sd"]), ("Timid", ["sp", "at"]), ("Hasty", ["sp", "df"]), ("Serious", None), ("Jolly", ["sp", "sa"]),
    ("Naive", ["sp", "sd"]), ("Modest", ["sa", "at"]), ("Mild", ["sa", "df"]), ("Quiet", ["sa", "sp"]), ("Bashful", None),
    ("Rash", ["sa", "sd"]), ("Calm", ["sd", "at"]), ("Gentle", ["sd", "df"]), ("Sassy", ["sd", "sp"]),
    ("Careful", ["sd", "sa"]), ("Quirky", None)])
# ------------------------------------------------------------------ the 1-on-1 model (JavaScript copy in model.js)
CHART = {}
def se(a, ds, v):
    for d in ds.split(): CHART.setdefault(a, {})[d] = v
for a, s2, h, z in [
    ("Normal", "", "Rock Steel", "Ghost"), ("Fire", "Grass Ice Bug Steel", "Fire Water Rock Dragon", ""),
    ("Water", "Fire Ground Rock", "Water Grass Dragon", ""), ("Electric", "Water Flying", "Electric Grass Dragon", "Ground"),
    ("Grass", "Water Ground Rock", "Fire Grass Poison Flying Bug Dragon Steel", ""),
    ("Ice", "Grass Ground Flying Dragon", "Fire Water Ice Steel", ""),
    ("Fighting", "Normal Ice Rock Dark Steel", "Poison Flying Psychic Bug Fairy", "Ghost"),
    ("Poison", "Grass Fairy", "Poison Ground Rock Ghost", "Steel"), ("Ground", "Fire Electric Poison Rock Steel", "Grass Bug", "Flying"),
    ("Flying", "Grass Fighting Bug", "Electric Rock Steel", ""), ("Psychic", "Fighting Poison", "Psychic Steel", "Dark"),
    ("Bug", "Grass Psychic Dark", "Fire Fighting Poison Flying Ghost Steel Fairy", ""),
    ("Rock", "Fire Ice Flying Bug", "Fighting Ground Steel", ""), ("Ghost", "Psychic Ghost", "Dark", "Normal"),
    ("Dragon", "Dragon", "Steel", "Fairy"), ("Dark", "Psychic Ghost", "Fighting Dark Fairy", ""),
    ("Steel", "Ice Rock Fairy", "Fire Water Electric Steel", ""), ("Fairy", "Fighting Dragon Dark", "Fire Poison Steel", "")]:
    se(a, s2, 2); se(a, h, 0.5); se(a, z, 0)
BOOST = {"Charcoal": "Fire", "Mystic Water": "Water", "Magnet": "Electric", "Miracle Seed": "Grass", "NeverMeltIce": "Ice",
         "Never-Melt Ice": "Ice", "Black Belt": "Fighting", "Poison Barb": "Poison", "Soft Sand": "Ground", "Sharp Beak": "Flying",
         "TwistedSpoon": "Psychic", "Twisted Spoon": "Psychic", "SilverPowder": "Bug", "Silver Powder": "Bug", "Hard Stone": "Rock",
         "Spell Tag": "Ghost", "Dragon Fang": "Dragon", "BlackGlasses": "Dark", "Black Glasses": "Dark", "Metal Coat": "Steel",
         "Silk Scarf": "Normal", "Flame Plate": "Fire", "Splash Plate": "Water", "Zap Plate": "Electric", "Meadow Plate": "Grass",
         "Icicle Plate": "Ice", "Fist Plate": "Fighting", "Toxic Plate": "Poison", "Earth Plate": "Ground", "Sky Plate": "Flying",
         "Mind Plate": "Psychic", "Insect Plate": "Bug", "Stone Plate": "Rock", "Spooky Plate": "Ghost", "Draco Plate": "Dragon",
         "Dread Plate": "Dark", "Iron Plate": "Steel", "Sea Incense": "Water", "Wave Incense": "Water", "Odd Incense": "Psychic",
         "Rock Incense": "Rock", "Rose Incense": "Grass"}
IMMUNE = {"Levitate": "Ground", "Flash Fire": "Fire", "Water Absorb": "Water", "Storm Drain": "Water", "Dry Skin": "Water",
          "Volt Absorb": "Electric", "Lightning Rod": "Electric", "Motor Drive": "Electric", "Sap Sipper": "Grass"}
KEYS6 = ["hp", "at", "df", "sa", "sd", "sp"]

def stats(bs, lv, iv, nature):
    nat = NATURES.get(nature) or [None, None]
    st = {}
    for i, k in enumerate(KEYS6):
        b = bs[i]
        if k == "hp": st[k] = (2 * b + iv) * lv // 100 + lv + 10
        else: st[k] = math.floor(((2 * b + iv) * lv // 100 + 5) * (1.1 if k == nat[0] else 0.9 if k == nat[1] else 1))
    return st

def mon(name, lv, iv=15, nature="Hardy", ab=None, item="", moves=(), bs=None):
    d = MONS[name]
    return {"name": name, "lv": lv, "t": d["t"], "ab": ab or d["ab"][0], "item": item, "moves": list(moves),
            "st": stats(bs or d["bs"], lv, iv, nature)}

def eff(mt, types):
    x = 1
    for t in types: x = x * CHART.get(mt, {}).get(t, 1)
    return x

EVOS, STURDY = set(), False      # species that can still evolve (Eviolite); Sturdy survives a KO from full HP (Gen 5 on)
WAB = {"Drizzle": "rain", "Drought": "sun", "Sand Stream": "sand", "Snow Warning": "hail", "Primordial Sea": "rain", "Desolate Land": "sun"}
WMOVE = {"Rain Dance": "rain", "Sunny Day": "sun", "Sandstorm": "sand", "Hail": "hail", "Snowscape": "hail", "Chilly Reception": "hail"}
WBALL = {"rain": "Water", "sun": "Fire", "sand": "Rock", "hail": "Ice"}
WSPEED = {"Swift Swim": "rain", "Chlorophyll": "sun", "Sand Rush": "sand", "Slush Rush": "hail"}
RESIST = {"Occa Berry": "Fire", "Passho Berry": "Water", "Wacan Berry": "Electric", "Rindo Berry": "Grass", "Yache Berry": "Ice",
          "Chople Berry": "Fighting", "Kebia Berry": "Poison", "Shuca Berry": "Ground", "Coba Berry": "Flying", "Payapa Berry": "Psychic",
          "Tanga Berry": "Bug", "Charti Berry": "Rock", "Kasib Berry": "Ghost", "Haban Berry": "Dragon", "Colbur Berry": "Dark",
          "Babiri Berry": "Steel", "Roseli Berry": "Fairy"}
BREAK = ("Mold Breaker", "Teravolt", "Turboblaze")

def mtype(move, w):
    return WBALL[w] if move == "Weather Ball" and w else MOVES[move]["t"]

def effd(a, d, mt):
    """Type effectiveness with the abilities and items that change it."""
    e = eff(mt, [t for t in d["t"] if t != "Ghost"] if a["ab"] == "Scrappy" and mt in ("Normal", "Fighting") else d["t"])
    if a["ab"] not in BREAK:
        if IMMUNE.get(d["ab"]) == mt: e = 0
        if d["ab"] == "Thick Fat" and mt in ("Fire", "Ice"): e *= 0.5
        if d["ab"] == "Heatproof" and mt == "Fire": e *= 0.5
        if d["ab"] == "Wonder Guard" and e <= 1: e = 0
        if d["ab"] in ("Filter", "Solid Rock", "Prism Armor") and e > 1: e *= 0.75
    if d["item"] == "Air Balloon" and mt == "Ground": e = 0
    if a["ab"] == "Tinted Lens" and 0 < e < 1: e *= 2
    return e

def damage(a, d, move, intim, w=""):
    m = MOVES.get(move)
    if not m: return 0
    mt, cat, bp = mtype(move, w), m["c"], m["bp"]
    if move in FIXED:
        return 0 if eff(mt, d["t"]) == 0 else (a["lv"] if FIXED[move] == "level" else FIXED[move])
    if not bp or bp <= 1 or cat == "Status": return 0
    if move == "Synchronoise" and not set(a["t"]) & set(d["t"]): return 0      # only hits targets that share a type with the user
    if move == "Weather Ball" and w: bp *= 2
    if move == "Acrobatics" and a["item"] in ("", "Flying Gem"): bp *= 2
    phys = cat == "Physical"
    A = a["st"]["at" if phys else "sa"]; D = d["st"]["df" if phys else "sd"]
    if phys and a["ab"] in ("Huge Power", "Pure Power"): A *= 2
    if (a["item"] == "Light Ball" and a["name"] == "Pikachu") or (phys and a["item"] == "Thick Club" and a["name"] in ("Cubone", "Marowak")): A *= 2
    if phys and a["ab"] == "Hustle": A = A * 3 // 2
    if not phys and a["ab"] == "Solar Power" and w == "sun": A = A * 3 // 2
    if phys and intim: A = A * 2 // 3
    if d["item"] == "Eviolite" and d["name"] in EVOS: D = D * 3 // 2
    if not phys and d["item"] == "Assault Vest": D = D * 3 // 2
    if not phys and w == "sand" and "Rock" in d["t"]: D = D * 3 // 2
    if phys and d["ab"] == "Fur Coat" and a["ab"] not in BREAK: D *= 2
    if a["ab"] == "Technician" and bp <= 60: bp *= 1.5
    base = math.floor(math.floor(math.floor(2 * a["lv"] / 5 + 2) * bp * A / D) / 50) + 2
    stab = (2 if a["ab"] == "Adaptability" else 1.5) if mt in a["t"] else 1
    e = effd(a, d, mt)
    item = 1.2 if BOOST.get(a["item"]) == mt else 1.3 if a["item"] == "Life Orb" else 1.5 if ((a["item"] == "Choice Band" and phys) or (a["item"] == "Choice Specs" and not phys)) else 1.1 if ((a["item"] == "Muscle Band" and phys) or (a["item"] == "Wise Glasses" and not phys)) else 1.2 if (a["item"] == "Expert Belt" and e > 1) else 1
    wm = 1
    if w == "rain": wm = 1.5 if mt == "Water" else 0.5 if mt == "Fire" else 1
    if w == "sun": wm = 1.5 if mt == "Fire" else 0.5 if mt == "Water" else 1
    if w == "sand" and a["ab"] == "Sand Force" and mt in ("Rock", "Ground", "Steel"): wm = 1.3
    return base * 0.925 * stab * e * item * MULTI.get(move, 1) * wm

def best(a, d, intim, skip=(), w=""):
    mv = [m for m in a["moves"] if m not in skip]
    if not mv: return (0, "")
    return max((damage(a, d, m, intim, w), m) for m in mv)

def hits(a, d, move, dn, w):
    """How many of a's hits it takes to knock d out: the first hit can be changed by a berry, a Gem, Multiscale, a Focus Sash..."""
    if dn <= 0: return 99
    hp = d["st"]["hp"]; mt = mtype(move, w); mb = a["ab"] in BREAK
    d1 = dn
    if a["item"] == mt + " Gem" and move != "Acrobatics": d1 = d1 * 1.5
    if RESIST.get(d["item"]) == mt and eff(mt, d["t"]) > 1: d1 = d1 * 0.5
    if d["item"] == "Chilan Berry" and mt == "Normal": d1 = d1 * 0.5
    if d["ab"] in ("Multiscale", "Shadow Shield") and not mb: d1 = d1 * 0.5
    if d["ab"] == "Disguise" and not mb: d1 = 0
    if d1 >= hp and (d["item"] == "Focus Sash" or (STURDY and d["ab"] == "Sturdy" and not mb)): d1 = hp - 1
    if d1 >= hp: return 1
    extra = hp // 4 if d["item"] == "Sitrus Berry" else 10 if d["item"] == "Oran Berry" else 20 if d["item"] == "Berry Juice" else 0
    heal = hp // 16 if (d["item"] == "Leftovers" or (d["item"] == "Black Sludge" and "Poison" in d["t"])) else 0
    if dn - heal <= 0: return 99
    return 1 + math.ceil((hp - d1 + extra) / (dn - heal))

def speed(m, w):
    s = m["st"]["sp"]
    if m["item"] == "Choice Scarf": s = s * 3 // 2
    if w and WSPEED.get(m["ab"]) == w: s *= 2
    return s

def matchup(p, b):
    w = WAB.get(p["ab"]) or b.get("w", "")
    pd, pm = best(p, b, b["ab"] == "Intimidate", NOUSE, w)
    bd, bm = best(b, p, p["ab"] == "Intimidate", (), w)
    first = speed(p, w) >= speed(b, w)
    win = False
    if pd > 0:
        ph = hits(p, b, pm, pd, w); bh = hits(b, p, bm, bd, w)
        win = ph <= bh if first else ph < bh
    return [1 if win else 0, pm, round(pd / b["st"]["hp"] * 100 * .85 / .925), round(pd / b["st"]["hp"] * 100 / .925), bm,
            round(bd / p["st"]["hp"] * 100 * .85 / .925), round(bd / p["st"]["hp"] * 100 / .925), 1 if first else 0]

def bossmon(m):
    return mon(m["s"], m["l"], m["iv"], m["n"], m["a"], m["i"], m["m"], m.get("bs"))


def bossteam(team):
    """The boss team with the weather each one fights under: its own weather ability or move, else the lead's."""
    ms = [bossmon(m) for m in team]
    own = lambda x: WAB.get(x["ab"]) or next((WMOVE[m] for m in x["moves"] if m in WMOVE), "")
    lead = own(ms[0]) if ms else ""
    for x in ms: x["w"] = own(x) or lead
    return ms
