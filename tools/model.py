"""The 1-on-1 model shared by every game. The caller sets MONS, MOVES (name -> {t, c, bp}), NATURES, FIXED, MULTI."""
import math
from collections import OrderedDict
MONS, MOVES = {}, {}
# Moves left out on the player's side (Carlos never uses them): must recharge, Last Resort, and moves that faint the user
NOUSE = {"Hyper Beam", "Giga Impact", "Blast Burn", "Frenzy Plant", "Hydro Cannon", "Rock Wrecker", "Roar of Time", "Prismatic Laser",
         "Eternabeam", "Meteor Assault", "Last Resort", "Explosion", "Self-Destruct", "Selfdestruct", "Misty Explosion", "Final Gambit", "Memento"}
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

def damage(a, d, move, intim):
    m = MOVES.get(move)
    if not m: return 0
    mt, cat, bp = m["t"], m["c"], m["bp"]
    if move in FIXED:
        return 0 if eff(mt, d["t"]) == 0 else (a["lv"] if FIXED[move] == "level" else FIXED[move])
    if not bp or bp <= 1 or cat == "Status": return 0
    phys = cat == "Physical"
    A = a["st"]["at" if phys else "sa"]; D = d["st"]["df" if phys else "sd"]
    if phys and a["ab"] in ("Huge Power", "Pure Power"): A *= 2
    if phys and intim: A = A * 2 // 3
    if a["ab"] == "Technician" and bp <= 60: bp *= 1.5
    base = math.floor(math.floor(math.floor(2 * a["lv"] / 5 + 2) * bp * A / D) / 50) + 2
    stab = (2 if a["ab"] == "Adaptability" else 1.5) if mt in a["t"] else 1
    item = 1.2 if BOOST.get(a["item"]) == mt else 1.3 if a["item"] == "Life Orb" else 1.5 if ((a["item"] == "Choice Band" and phys) or (a["item"] == "Choice Specs" and not phys)) else 1
    e = eff(mt, d["t"])
    if IMMUNE.get(d["ab"]) == mt: e = 0
    if d["ab"] == "Thick Fat" and mt in ("Fire", "Ice"): e *= 0.5
    return base * 0.925 * stab * e * item * MULTI.get(move, 1)

def best(a, d, intim, skip=()):
    mv = [m for m in a["moves"] if m not in skip]
    if not mv: return (0, "")
    return max((damage(a, d, m, intim), m) for m in mv)

def matchup(p, b):
    pd, pm = best(p, b, b["ab"] == "Intimidate", NOUSE)
    bd, bm = best(b, p, p["ab"] == "Intimidate")
    first = p["st"]["sp"] >= b["st"]["sp"]
    win = False
    if pd > 0:
        ph = math.ceil(b["st"]["hp"] / pd); bh = math.ceil(p["st"]["hp"] / bd) if bd > 0 else 99
        win = ph <= bh if first else ph < bh
    return [1 if win else 0, pm, round(pd / b["st"]["hp"] * 100 * .85 / .925), round(pd / b["st"]["hp"] * 100 / .925), bm,
            round(bd / p["st"]["hp"] * 100 * .85 / .925), round(bd / p["st"]["hp"] * 100 / .925), 1 if first else 0]

def bossmon(m):
    return mon(m["s"], m["l"], m["iv"], m["n"], m["a"], m["i"], m["m"], m.get("bs"))

