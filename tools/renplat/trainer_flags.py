import re
vals={}; nxt=0; bad=0
for i,line in enumerate(open('vft.txt')):
    s=line.strip()
    if not s: continue
    if '=' in s:
        a,b=[x.strip() for x in s.split('=')]
        b=vals[b] if b in vals else int(b,0)
        vals[a]=b
        if a.startswith(('FLAG_','VAR_')): nxt=b+1; name=a; v=b
        else:
            if not a.endswith('_END'): nxt=b
            continue
    elif s.startswith(('FLAG_','VAR_')):
        vals[s]=nxt; name=s; v=nxt; nxt+=1
    else:
        vals[s]=nxt; continue
    m=re.search(r'_0x([0-9A-F]+)$',name)
    if m and int(m.group(1),16)!=v and 'MAP_LOCAL' not in name: bad+=1
print("mismatches",bad)
for k in ['TRAINER_DEFEATED_FLAGS_START','FLAG_DEFEATED_TRAINER_LEADER_ROARK','VAR_PLAYER_STARTER','FLAG_GAME_COMPLETED','FLAG_DEFEATED_TRAINER_RIVAL_ROUTE_201_PIPLUP']:
    print(k, vals.get(k))
print([(k,v) for k,v in vals.items() if 'HALL_OF_FAME' in k or 'COMPLETED' in k][:8])
inv={v:k for k,v in vals.items() if k.startswith('FLAG_')}
for n in [318,350,214,2404]: print(n, inv.get(n))
