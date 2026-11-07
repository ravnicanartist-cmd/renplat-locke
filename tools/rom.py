import ndspy.rom, ndspy.narc
R=ndspy.rom.NintendoDSRom.fromFile('/home/claude/rom/game.nds')
def narc(p): return ndspy.narc.NARC(R.getFileByName(p)).files
GT=['Normal','Fighting','Flying','Poison','Ground','Rock','Bug','Ghost','Steel','Fairy','Fire','Water','Grass','Electric','Psychic','Ice','Dragon','Dark']
SP=[l.strip() for l in open('ref/text_Species_en.txt',encoding='utf-8-sig')]
AB=[l.strip() for l in open('ref/text_Abilities_en.txt',encoding='utf-8-sig')]
def personal():
    out={}
    for i,b in enumerate(narc('poketool/personal/pl_personal.narc')):
        if len(b)<0x18: continue
        t=[GT[b[6]]]+([GT[b[7]]] if b[7]!=b[6] else [])
        out[i]={'bs':list(b[0:6]),'t':t,'ab':[AB[b[0x16]]]+([AB[b[0x17]]] if b[0x17] else []),'growth':b[0x13]}
    return out
MV=[l.strip() for l in open('ref/text_Moves_en.txt',encoding='utf-8-sig')]
REPL={'Barrage':'Draining Kiss','Brine':'Scald','Constrict':'Icicle Crash','Horn Drill':'Drill Run','Lunar Dance':'Moonblast','Luster Purge':'Dazzling Gleam','Mist Ball':'Disarming Voice','Sand Tomb':'Bulldoze','Submission':'Play Rough','Twister':'Hurricane','Volt Tackle':'Wild Charge'}
MOVES=[REPL.get(m,m) for m in MV[:468]]
import struct
def levelup():
    out={}
    for i,b in enumerate(narc('poketool/personal/wotbl.narc')):
        l=[]
        for k in range(0,len(b)-1,2):
            v=struct.unpack_from('<H',b,k)[0]
            if v==0xFFFF: break
            l.append([v>>9, MOVES[v&0x1FF]])
        out[i]=l
    return out
CAT=['Physical','Special','Status']
def movedata():
    out={}
    for i,b in enumerate(narc('poketool/waza/pl_waza_tbl.narc')):
        if i>=len(MOVES) or i==0: continue
        out[MOVES[i]]={'c':CAT[b[2]],'bp':b[3],'t':GT[b[4]],'acc':b[5],'pp':b[6],'pri':struct.unpack_from('<b',b,10)[0]}
    return out
IT=[l.strip() for l in open('ref/text_Items_en.txt',encoding='utf-8-sig')]
EVM={1:'friendship',2:'friendship',3:'friendship',4:'level',5:'trade',6:'tradeitem',7:'item',8:'level',9:'level',10:'level',11:'level',12:'level',13:'level',14:'shedinja',15:'beauty',16:'item',17:'item',18:'helditem',19:'helditem',20:'move',21:'teammate',22:'level',23:'level',24:'place',25:'place',26:'place'}
def evolutions():
    out={}
    for i,b in enumerate(narc('poketool/personal/evo.narc')):
        for k in range(0,len(b)-5,6):
            m,p,t=struct.unpack_from('<HHH',b,k)
            if m==0: continue
            kind=EVM.get(m,'?%d'%m)
            param = p if kind in('level','beauty') else (IT[p] if kind in('item','helditem','tradeitem') else (MOVES[p] if kind=='move' else (SP[p] if kind=='teammate' else p)))
            out.setdefault(i,[]).append({'to':t,'kind':kind,'m':m,'p':param})
    return out
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
        key2=(0x91BD3*(i+1))&0xFFFF; s=''
        for c in range(ln):
            v=struct.unpack_from('<H',b,off+c*2)[0]^key2; key2=(key2+0x493D)&0xFFFF
            if v==0xFFFF: break
            s+=G4TAB[v] if v<len(G4TAB) else ('\n' if v==0xE000 else '')
        out.append(s)
    return out
def messages():
    return narc('msgdata/pl_msg.narc')
def trainers():
    TD=narc('poketool/trainer/trdata.narc'); TP=narc('poketool/trainer/trpoke.narc')
    ITN=msgfile(messages()[392]); MVN=msgfile(messages()[647]); SPN=msgfile(messages()[412])
    out={}
    for i,(d,p) in enumerate(zip(TD,TP)):
        flags,cls,bt,n=d[0],d[1],d[2],d[3]
        hasm,hasi=flags&1,flags&2
        sz=6+(2 if hasi else 0)+(8 if hasm else 0)+2
        mons=[]
        for k in range(n):
            o=k*sz
            if o+6>len(p): break
            diff,abg,lv,spf=struct.unpack_from('<BBHH',p,o); q=o+6
            item='' 
            if hasi: item=ITN[struct.unpack_from('<H',p,q)[0]]; q+=2
            mv=[]
            if hasm: mv=[MVN[x] for x in struct.unpack_from('<4H',p,q) if x]; q+=8
            mons.append({'s':SPN[spf&0x3FF],'form':spf>>10,'l':lv,'diff':diff,'abg':abg,'i':item if item!='None' else '','m':mv})
        out[i]={'n':n,'mons':mons,'double':bt,'flags':flags}
    return out
