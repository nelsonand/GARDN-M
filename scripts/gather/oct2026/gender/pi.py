import sys,re,csv
txt=sys.stdin.read()
rows=re.findall(r'^([A-Z]{2}) ([\d.]+) ([A-F][+-]?)\s*$',txt,re.M)
print(len(rows))
with open(sys.argv[1],'w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Score','letter_grade']); w.writerows(rows)
