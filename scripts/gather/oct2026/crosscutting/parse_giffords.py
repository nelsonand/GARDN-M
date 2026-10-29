import re,sys,csv
t=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
rows=re.findall(r'data-state-name="([^"]+)" data-grade=\'([^\']+)\' data-safety=\'(\d+)\' data-death=\'(\d+)\' data-per100k=\'([\d.]+)\'',t)
print(len(rows))
w=csv.writer(sys.stdout)
w.writerow(['State','Rank','Grade','GunDeathRateRank','GunDeathsPer100k'])
for r in sorted(rows,key=lambda r:int(r[2])): w.writerow([r[0],r[2],r[1],r[3],r[4]])
