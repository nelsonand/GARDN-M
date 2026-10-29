import pandas as pd,sys
d=pd.read_excel(sys.argv[1],sheet_name='Racial Ethnic Disparity',header=None).iloc[13:64,:3]
d.columns=['State','bw','lw']
d=d[~d.State.isin(['Federal prisons','District of Columbia'])]
d['BlackWhite_ratio']=pd.to_numeric(d.bw.str.replace(':1','',regex=False),errors='coerce')
d['LatinoWhite_ratio']=pd.to_numeric(d.lw.str.replace(':1','',regex=False),errors='coerce')
assert d.BlackWhite_ratio.notna().sum()==50
d['Rank']=d.BlackWhite_ratio.rank(method='min').astype(int)
o=d[['State','Rank','BlackWhite_ratio','LatinoWhite_ratio']].sort_values('Rank')
o.to_csv(sys.argv[2],index=False); print(len(o)); print(o.head(4).to_string()); print(o.tail(3).to_string())
