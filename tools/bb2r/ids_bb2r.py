import json, re
R='/home/claude/bb2/ref/'
KEY=lambda s: re.sub(r"[^a-z0-9]","",str(s).lower().replace("♀","f").replace("♂","m"))
rd=lambda f:[l.rstrip('\n').replace('﻿','') for l in open(R+f,encoding='utf-8')]
meta=json.load(open('/home/claude/hub/bb2r/data/meta.json'))
mk={KEY(n):n for n in meta['mons']}
sp=rd('text_Species_en.txt')[:650]
species=[mk.get(KEY(n), n.replace("’","'")) for n in sp]
species[0]=''
src=open('/home/claude/ref/dec/backups/bb2redux1-4.js').read()
rep=json.loads(re.search(r'"move_replacements":\s*(\{.*?\})',src,re.S).group(1))
mv=rd('text_Moves_en.txt')[:560]
mvk={KEY(n):n for n in meta['moves']}
moves=[]
for n in mv:
    k=KEY(n); k=rep.get(k,k)
    moves.append(mvk.get(k, n.replace("’","'")))
moves[0]=''
miss=[m for m in moves[1:] if m not in meta['moves']]
print('moves not in meta (status moves ok):',len(miss),miss[:10])
print('replaced e.g.', moves[4], moves[5], moves[11])
items=[x.replace("’","'") for x in rd('text_Items_en.txt')[:639]]
abil=rd('text_Abilities_en.txt')[:165]
nat=rd('text_Natures_en.txt')[:25]
loc=rd('loc5.txt')
ids={'species':species,'moves':moves,'items':items,'abilities':abil,'natures':nat,'loc':loc}
json.dump(ids,open('/home/claude/hub/bb2r/data/ids.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(species),species[29],species[32],species[83],species[122],len(items),items[1],abil[1],nat[:3],loc[117])
# growth rates by national dex number, from PKHeX's personal_b2w2 (0x4C per entry, growth at 0x15)
d=open('/home/claude/bb2/ref/personal_b2w2','rb').read()
ids['gr']=[d[i*0x4C+0x15] for i in range(650)]
json.dump(ids,open('/home/claude/hub/bb2r/data/ids.json','w'),ensure_ascii=False,separators=(',',':'))
