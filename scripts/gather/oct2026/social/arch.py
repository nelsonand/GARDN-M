import re,sys,csv
rows=[]
for line in open(sys.argv[1]):
    m=re.fullmatch(r'(\d{1,2}) ([A-Z][A-Za-z ]+) (\d\.\d\d)\s*',line)
    if m: rows.append(m.groups())
assert [int(r[0]) for r in rows]==list(range(1,51)) and len({r[1] for r in rows})==50
with open(sys.argv[2],'w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Processed','archbridge_rank','year'])
    for r in rows: w.writerow([r[1],r[2],r[0],2025])
print(len(rows))
