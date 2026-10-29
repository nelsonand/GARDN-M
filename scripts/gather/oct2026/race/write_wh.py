import sys, io, pandas as pd
from bs4 import BeautifulSoup
src, idx, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
s=BeautifulSoup(open(src,encoding='utf-8').read(),'html.parser')
df=pd.read_html(io.StringIO(str(s.find_all('table')[idx])))[0]
df.columns=[c.replace('*','').strip() for c in df.columns]
df=df.rename(columns={'Total Score':'Score','Overall Rank':'Overall_Rank'})
df.columns=[c.replace(' & ','_').replace(' ','_') for c in df.columns]
cols=['State','Score']+[c for c in df.columns if c not in ('State','Score')]
df=df[cols]
print(df.shape, df.State.tolist()[-3:], 'DC' if df.State.str.contains('District').any() else 'noDC')
df.to_csv(out,index=False)
