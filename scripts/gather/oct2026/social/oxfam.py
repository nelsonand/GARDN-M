import re,sys,csv
t=open(sys.argv[1]).read().replace('\n',' ')
t=t.split('Rights to Organize Score',1)[1]
t=t.replace('State Ranking Overall Score Wages Score Worker Protections Score Rights to Organize Score',' ')
t=re.sub(r'1\s+We note that.*?simplicity\.','',t)
pat=re.compile(r'([A-Z][A-Za-z\. ]+?) (\d{1,2}) (\d+(?:\.\d+)?) (\d+(?:\.\d+)?) (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)')
rows=[(m.group(1).strip(),)+m.groups()[1:] for m in pat.finditer(t)]
print(len(rows))
ranks=[int(r[1]) for r in rows]; assert ranks==list(range(1,53)), ranks
rows=[r for r in rows if r[0]!='Puerto Rico']
with open(sys.argv[2],'w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Score','oxfam_rank_of52','wages_dim','protections_dim','organize_dim','year'])
    for r in rows: w.writerow([r[0],r[2],r[1],r[3],r[4],r[5],2025])
print(len(rows))
