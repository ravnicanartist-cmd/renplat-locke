"""Pokémon Sacred Gold (PChal QoL, HeartGold base) ROM reader, after /home/claude/build/rom.py (Renegade Platinum)."""
import ndspy.rom, ndspy.narc, struct, sys
sys.path.insert(0, "/home/claude/build")
import importlib.util
_s = importlib.util.spec_from_file_location("rpg4", "/home/claude/build/rom.py")
R = ndspy.rom.NintendoDSRom.fromFile('/home/claude/sg/game.nds')
def narc(p): return ndspy.narc.NARC(R.getFileByName(p)).files
# reuse the Gen 4 text decoder from the Platinum reader without loading the Platinum ROM
src = open("/home/claude/build/rom.py").read()
ns = {}
exec(src.split("import re as _re")[1].split("def messages")[0].replace("G4TAB=_table()", "G4TAB=_table()"), {"_re": __import__("re"), "struct": struct, **ns}, ns) if False else None
import re as _re
def _table():
    s=open('/home/claude/pkhex/pk/PKHeX.Core/PKM/Strings/StringConverter4Util.cs',encoding='utf-8').read()
    i=s.find('TableINT =>'); j=s.find('];',i); body=_re.sub(r'//[^\n]*','',s[i:j]); body=body[body.find('[')+1:]
    toks=_re.findall(r"'(\\.|[^'])'|\b(NUL|EMP|HGM|HGF)\b",body)
    return [(t[0].encode().decode('unicode_escape') if t[0].startswith('\\') else t[0]) if t[0] else {'NUL':'','EMP':'','HGM':'♂','HGF':'♀'}[t[1]] for t in toks]
G4TAB=_table()
def msgfile(b):
    n,seed=struct.unpack_from('<HH',b,0)
    out=[]
    for i in range(n):
        key=(765*(i+1)*seed)&0xFFFF; k32=key|(key<<16)
        off,ln=struct.unpack_from('<II',b,4+i*8); off^=k32; ln^=k32
        key2=(0x91BD3*(i+1))&0xFFFF; s=''; raw=[]
        for c in range(ln):
            v=struct.unpack_from('<H',b,off+c*2)[0]^key2; key2=(key2+0x493D)&0xFFFF
            raw.append(v)
        if raw and raw[0]==0xF100:                       # compressed: 9-bit characters packed in the following words
            bits=0; nb=0; chars=[]
            for w in raw[1:]:
                bits|=(w & 0x7FFF)<<nb; nb+=15
                while nb>=9:
                    chars.append(bits&0x1FF); bits>>=9; nb-=9
            raw=[c for c in chars]
            raw=raw[:raw.index(0x1FF)] if 0x1FF in raw else raw
        for v in raw:
            if v==0xFFFF: break
            s+=G4TAB[v] if v<len(G4TAB) else ('\n' if v==0xE000 else '')
        out.append(s)
    return out
MSG = narc('a/0/2/7')
def bank(i): return msgfile(MSG[i])
GT=['Normal','Fighting','Flying','Poison','Ground','Rock','Bug','Ghost','Steel','Fairy','Fire','Water','Grass','Electric','Psychic','Ice','Dragon','Dark']
SPN = bank(237); ABN = bank(720); MVN = bank(750); ITN = bank(222); LOCN = bank(279); TRN = bank(729); TCN = bank(730)
CAT=['Physical','Special','Status']
def personal():
    out={}
    for i,b in enumerate(narc('a/0/0/2')):
        if len(b)<0x18: continue
        t=[GT[b[6]]]+([GT[b[7]]] if b[7]!=b[6] else [])
        out[i]={'bs':list(b[0:6]),'t':t,'ab':[ABN[b[0x16]]]+([ABN[b[0x17]]] if b[0x17] else []),'growth':b[0x13],'tm':int.from_bytes(b[0x1C:0x2C],'little')}
    return out
def levelup():
    out={}
    for i,b in enumerate(narc('a/0/3/3')):
        l=[]
        for k in range(0,len(b)-1,2):
            v=struct.unpack_from('<H',b,k)[0]
            if v==0xFFFF: break
            l.append([v>>9, v&0x1FF])
        out[i]=l
    return out
def movedata():
    out={}
    for i,b in enumerate(narc('a/0/1/1')):
        out[i]={'c':CAT[b[2]] if b[2]<3 else b[2],'bp':b[3],'t':GT[b[4]] if b[4]<18 else b[4],'acc':b[5],'pp':b[6],'pri':struct.unpack_from('<b',b,10)[0]}
    return out
# ---------------------------------------------------------------- everything with Pokémon Showdown names
import json as _json
NM = _json.load(open('/home/claude/sg/names.json'))
NM['moves'] = [{'SmellingSalt': 'Smelling Salts'}.get(m, m) for m in NM['moves']]
SP_, MV_, AB_, IT_ = NM['species'], NM['moves'], NM['abilities'], NM['items']
GT9 = ['Normal','Fighting','Flying','Poison','Ground','Rock','Bug','Ghost','Steel','???','Fire','Water','Grass','Electric','Psychic','Ice','Dragon','Dark']
EVM={1:'friendship',2:'friendship',3:'friendship',4:'level',5:'trade',6:'tradeitem',7:'item',8:'level',9:'level',10:'level',11:'level',12:'level',13:'level',14:'shedinja',15:'beauty',16:'item',17:'item',18:'helditem',19:'helditem',20:'move',21:'teammate',22:'level',23:'level',24:'place',25:'place',26:'place'}
# TM01-TM92 then HM01-HM08 (same machine list as Diamond/Pearl/Platinum, HM05 Whirlpool, HM08 Rock Climb)
TMLIST = ["Focus Punch","Dragon Claw","Water Pulse","Calm Mind","Roar","Toxic","Hail","Bulk Up","Bullet Seed","Hidden Power","Sunny Day","Taunt","Ice Beam","Blizzard","Hyper Beam","Light Screen","Protect","Rain Dance","Giga Drain","Safeguard","Frustration","Solar Beam","Iron Tail","Thunderbolt","Thunder","Earthquake","Return","Dig","Psychic","Shadow Ball","Brick Break","Double Team","Reflect","Shock Wave","Flamethrower","Sludge Bomb","Sandstorm","Fire Blast","Rock Tomb","Aerial Ace","Torment","Facade","Secret Power","Rest","Attract","Thief","Steel Wing","Skill Swap","Snatch","Overheat","Roost","Focus Blast","Energy Ball","False Swipe","Brine","Fling","Charge Beam","Endure","Dragon Pulse","Drain Punch","Will-O-Wisp","Silver Wind","Embargo","Explosion","Shadow Claw","Payback","Recycle","Giga Impact","Rock Polish","Flash","Stone Edge","Avalanche","Thunder Wave","Gyro Ball","Swords Dance","Stealth Rock","Psych Up","Captivate","Dark Pulse","Rock Slide","X-Scissor","Sleep Talk","Natural Gift","Poison Jab","Dream Eater","Grass Knot","Swagger","Pluck","U-turn","Substitute","Flash Cannon","Trick Room",
          "Cut","Fly","Surf","Strength","Whirlpool","Rock Smash","Waterfall","Rock Climb"]
def mons():
    P = narc('a/0/0/2'); L = narc('a/0/3/3'); E = narc('a/0/3/4')
    out = {}
    for i in range(1, 494):
        b = P[i]
        t = [GT9[b[6]]] + ([GT9[b[7]]] if b[7] != b[6] else [])
        bits = int.from_bytes(b[0x1C:0x2C], 'little')
        lv = []
        lb = L[i]
        for k in range(0, len(lb) - 1, 2):
            v = struct.unpack_from('<H', lb, k)[0]
            if v == 0xFFFF: break
            lv.append([v >> 9, MV_[v & 0x1FF]])
        ev = []
        eb = E[i]
        for k in range(0, len(eb) - 5, 6):
            m, p, to = struct.unpack_from('<HHH', eb, k)
            if m == 0: continue
            kind = EVM.get(m, '?%d' % m)
            par = p if kind in ('level', 'beauty') else (IT_[p] if kind in ('item', 'helditem', 'tradeitem') else (MV_[p] if kind == 'move' else (SP_[p] if kind == 'teammate' else p)))
            ev.append({'to': SP_[to], 'kind': kind, 'm': m, 'p': par})
        out[SP_[i]] = {'no': i, 't': t, 'bs': [b[0], b[1], b[2], b[4], b[5], b[3]],      # hp at df sa sd sp (ROM order hp at df spe spa spd)
                       'ab': [AB_[b[0x16]]] + ([AB_[b[0x17]]] if b[0x17] and b[0x17] != b[0x16] else []), 'gr': b[0x13],
                       'lv': lv, 'tm': [TMLIST[k] for k in range(100) if bits >> k & 1], 'evos': ev}
    return out
def moves():
    out = {}
    for i, b in enumerate(narc('a/0/1/1')):
        if i == 0 or i >= len(MV_): continue
        out[MV_[i]] = {'t': GT9[b[4]], 'c': CAT[b[2]], 'bp': b[3], 'acc': b[5], 'pp': b[6], 'pri': struct.unpack_from('<b', b, 10)[0], 'eff': struct.unpack_from('<H', b, 0)[0]}
    return out
TD = narc('a/0/5/5'); TP = narc('a/0/5/6')
def trainer(tid, LV=None):
    d, p = TD[tid], TP[tid]
    flags, cls, n = d[0], d[1], d[3]
    hasm, hasi = flags & 1, flags & 2
    sz = 6 + (2 if hasi else 0) + (8 if hasm else 0) + 2
    team = []
    for k in range(n):
        o = k * sz
        if o + 6 > len(p): break
        diff, abg, lv, spf = struct.unpack_from('<BBHH', p, o); q = o + 6
        item = ''
        if hasi:
            item = IT_[struct.unpack_from('<H', p, q)[0]]; q += 2
            if item in ('None', '-'): item = ''
        mv = []
        if hasm: mv = [MV_[x] for x in struct.unpack_from('<4H', p, q) if x]; q += 8
        sp = SP_[spf & 0x3FF]
        if not mv and LV:
            seen = []
            for l, m in LV.get(sp, []):
                if l <= lv and m not in seen: seen.append(m)
            mv = seen[-4:]
        team.append({'s': sp, 'form': spf >> 10, 'l': lv, 'i': item, 'm': mv, 'iv': diff * 31 // 255, 'abg': abg})
    return {'id': tid, 'name': TRN[tid] if tid < len(TRN) else '', 'cls': TCN[cls] if cls < len(TCN) else cls, 'double': d[2], 'ai': struct.unpack_from('<I', d, 12)[0], 'team': team}
