"""names the HGSS save reader needs, in the site's spelling -> sg/data/ids.json"""
import json, sys
sys.path.insert(0, "/home/claude/sg")
import rom_sg as R
AP = lambda s: str(s).replace("’", "'")
P = R.narc('a/0/0/2')
ids = {"species": [AP(n) for n in R.SP_[:494]], "moves": R.MV_, "items": R.IT_, "abilities": R.AB_,
       "natures": [l.strip() for l in open('/home/claude/bb2/ref/text_Natures_en.txt', encoding='utf-8-sig')][:25],
       "loc": R.LOCN, "gr": [P[i][0x13] if i < len(P) and len(P[i]) > 0x13 else 0 for i in range(494)]}
ids["species"][0] = ""
json.dump(ids, open('/home/claude/hub/sg/data/ids.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(ids["loc"]), ids["loc"][126:140], ids["natures"][:3], ids["species"][83], ids["moves"][11])
ids["g4"] = "".join(c if c else "\u0000" for c in R.G4TAB)      # Gen 4 character table (one char per code)
json.dump(ids, open('/home/claude/hub/sg/data/ids.json', 'w'), ensure_ascii=False, separators=(',', ':'))
