import re,sys,json
h=open(sys.argv[1],encoding='utf8').read()
items=re.findall(r'\{"id":"(US-[A-Z]{2}|[A-Z]{2,3})","title":"([^"]+)","description":"([^"]+)"',h)
d={}
for i,t,desc in items:
    m=re.search(r'(Overall|Sexual Orientation|Gender Identity) Policy Score (-?[\d.]+)\\?/([\d.]+)',desc)
    if m: d.setdefault(t,{})[m.group(1)]=(float(m.group(2)),float(m.group(3)),desc)
print(len(d))
for k in sorted(d): print(k, {a:b[:2] for a,b in d[k].items()}, d[k].get('Overall',('','',''))[2])
