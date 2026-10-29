import sys,csv,collections
R=sys.argv[1]; MIN=int(sys.argv[2]); out=sys.argv[3] if len(sys.argv)>3 else None
ag={r['NTD ID']:r for r in csv.DictReader(open(R+'/ntd_2025_reporter_agency_info_jm7a-9hsy.csv',encoding='utf-8-sig'))}
agg=collections.defaultdict(lambda:[0,0,set()]); miss=set()
for r in csv.DictReader(open(R+'/ntd_2025_transit_stations_k9se-yvyg.csv',encoding='utf-8-sig')):
    a=ag.get(r['NTD ID'])
    if not a: miss.add(r['NTD ID']); continue
    u=a['UZA Name']
    ada=int(float(r['Primary Mode ADA Accessible Stations'] or 0)); tot=int(float(r['Primary Mode Total Stations'] or 0))
    agg[u][0]+=ada; agg[u][1]+=tot; agg[u][2].add(a['Agency Name'])
print('missing agencies',miss)
rows=[]
for u,(ada,tot,names) in agg.items():
    if tot<MIN or 'Non-UZA' in u or u.endswith(', PR'): continue
    name,st=u.rsplit(', ',1)
    city=name.split('--')[0].split('/')[0].strip(); state=st.split('--')[0].strip()
    rows.append((state,city,round(100*ada/tot,2),ada,tot,u,len(names)))
rows.sort(key=lambda r:-r[2])
print(len(rows))
for r in rows: print(r[:6])
if out:
    with open(out,'w',newline='') as f:
        w=csv.writer(f); w.writerow(['State','City','Score','ADA accessible stations','Total stations','Urbanized area (UZA)','Number of reporting agencies'])
        w.writerows(rows)
