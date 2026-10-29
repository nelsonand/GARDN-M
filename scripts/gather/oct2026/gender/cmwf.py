import sys,re,csv
sys.path.insert(0,sys.argv[3])
from states import norm
t=open(sys.argv[1]).read()
seg=t[t.find('APPENDIX B2'):]; seg=seg[:seg.find('=====PAGE')]
rows=[]
for line in seg.splitlines():
    m=re.match(r'\s*(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$',line)
    if m and norm(m.group(1)): rows.append([norm(m.group(1))]+[m.group(i) for i in range(2,6)])
print(len(rows))
with open(sys.argv[2],'w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Rank','rank_healthOutcomes','rank_coverageAccessAffordability','rank_qualityPrevention']); w.writerows(rows)
