import re, json, os
SRC = "/home/claude/src"
MARKS = re.compile(r"[᠎឵᠋​⁠﻿]")

def clean(c):
    c = MARKS.sub("", c or "").replace("\\n", " ")
    c = re.sub(r"\(\s*!+\s*\)?", "", c)
    return re.sub(r"\s+", " ", c).strip()

def grid(name, folder="doc"):
    rows = [l.rstrip("\n").split("\t") for l in open(f"{SRC}/{folder}/{name}.tsv", encoding="utf-8")]
    w = max(len(r) for r in rows)
    return [r + [""] * (w - len(r)) for r in rows]

def num(c):
    c = clean(c)
    try:
        return float(c)
    except ValueError:
        return None

TYPES = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying",
         "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]

def tname(c):
    c = clean(c).title()
    return c if c in TYPES else None

def mon_name(c):
    """'#001 Bulbasaur' -> 'Bulbasaur' ; keeps form names like 'Rotom (Heat)'."""
    c = clean(c)
    m = re.match(r"#\d+(?:,\d+)?\s+(.+)$", c)
    n = m.group(1) if m else c
    n = n.replace("Nidoran ♀", "Nidoran-F").replace("Nidoran ♂", "Nidoran-M").replace("Nidoran♀", "Nidoran-F").replace("Nidoran♂", "Nidoran-M")
    return n.strip()

def dexno(c):
    m = re.match(r"#0*(\d+)", clean(c))
    return int(m.group(1)) if m else None

def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
