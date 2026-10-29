import json,sys,csv
rows=json.load(open(sys.argv[1]))['response']['data']
h=rows[0]; out=[]
for r in rows[1:]:
    d=dict(zip(h,r))
    if d['NAME']=='Puerto Rico': continue
    g=float(d['B19083_001E'])
    out.append((d['NAME'],round(100*(1-g),2),d['B19083_001E'],d['B19083_001M']))
out.sort(key=lambda x:-x[1])
with open(sys.argv[2],'w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Score','gini_index','gini_moe90','year'])
    for o in out: w.writerow(list(o)+[2025])
print(len(out))
