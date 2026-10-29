import sys,io,pandas as pd
from bs4 import BeautifulSoup
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'html.parser')
t=s.find('div',id='table2023').find('table')
d=pd.read_html(io.StringIO(str(t)))[0]
d=d.rename(columns={'Place Name':'City','2020 Population':'pop_2020','Divergence Rank':'divergence_rank','Divergence Score':'divergence_score','Entropy Score':'entropy_score','Theil H':'theil_H','Black-White Dissimilarity':'dissim_BlackWhite','Hispanic-White Dissimilarity':'dissim_HispanicWhite','Nonwhite-White Dissimilarity':'dissim_NonwhiteWhite'})
D=d.divergence_score
d.insert(2,'Processed',(10*(D.max()-D)/(D.max()-D.min())).round(3))
d=d.sort_values('Processed',ascending=False)
d.to_csv(sys.argv[2],index=False); print(d.shape); print(d.head(5).to_string()); print(d.tail(3).to_string())
