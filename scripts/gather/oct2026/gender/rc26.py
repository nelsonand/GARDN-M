import sys,pypdf,re,csv
sys.path.insert(0,sys.argv[3])
from states import norm
r=pypdf.PdfReader(sys.argv[1])
rows={}
for i,p in enumerate(r.pages):
    t=p.extract_text() or ''
    for m in re.finditer(r'([A-Z][A-Z .]+?)\s*I\s*([A-F]\s?[+-]?)\s+([\d.]+)\s*/\s*100\s*I\s*BREAKDOWN',t):
        name=m.group(1).strip().title().replace(' Of ',' of ')
        if name in ("Dc","D.C."): name="District of Columbia"
        s=norm(name) or ('District of Columbia' if 'COLUMBIA' in m.group(1) or m.group(1).strip()=='DC' else None)
        print(i+1,repr(m.group(1)),s,m.group(2),m.group(3))
        if s: rows[s]=(m.group(3),m.group(2).replace(" ",""))
print(len(rows))
with open(sys.argv[2],'w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Score','letter_grade'])
    for s in sorted(rows): w.writerow([s,*rows[s]])
