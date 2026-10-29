import re,sys,csv,html
src,out,ncols=sys.argv[1],sys.argv[2],int(sys.argv[3])
h=open(src).read()
i=h.find('Total Score'); t=h[i:]
j=t.find('</table>'); t=t[:j]
cells=[html.unescape(re.sub(r'<[^>]+>','',c)).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>',t,re.S)]
hdr=[html.unescape(re.sub(r'<[^>]+>','',c)).strip() for c in re.findall(r'<th[^>]*>(.*?)</th>',h[h.rfind('<table',0,i):i+3000],re.S)]
print(hdr, len(cells))
rows=[cells[k:k+ncols] for k in range(0,len(cells),ncols)]
print(rows[:2],rows[-1],len(rows))
names=sys.argv[4].split(',')
with open(out,'w',newline='') as f:
    w=csv.writer(f); w.writerow(names)
    for r in rows: w.writerow(r)
