import sys,re
from bs4 import BeautifulSoup
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'html.parser')
for h in s.find_all(['h2','h3']): print('H:',h.get_text(' ',strip=True)[:120])
for t in s.find_all('table'):
    p=t.find_previous(['h2','h3','p'])
    print('BEFORE TABLE:',p.get_text(' ',strip=True)[:200] if p else None)
txt=s.get_text(' ')
for m in re.finditer(r'(Updated|Published|Last updated)[^\n]{0,60}',txt): print(m.group(0)[:80])
for m in re.finditer(r'"date(Published|Modified)"\s*:\s*"[^"]+"',str(s)): print(m.group(0))
