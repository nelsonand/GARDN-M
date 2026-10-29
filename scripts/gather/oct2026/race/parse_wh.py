import sys, pandas as pd, io
from bs4 import BeautifulSoup
html=open(sys.argv[1],encoding='utf-8').read()
s=BeautifulSoup(html,'html.parser')
print(s.title.text if s.title else '')
for i,t in enumerate(s.find_all('table')):
    try:
        df=pd.read_html(io.StringIO(str(t)))[0]
    except Exception as e:
        print(i,'err',e); continue
    print('TABLE',i,df.shape); print(df.head(3).to_string())
