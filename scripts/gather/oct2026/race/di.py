import sys, pandas as pd
df=pd.read_csv(sys.argv[1],sep='|',dtype=str)
df=df[df.GEO_ID.str.startswith('0400000US')].copy()
fips={'01':'Alabama','02':'Alaska','04':'Arizona','05':'Arkansas','06':'California','08':'Colorado','09':'Connecticut','10':'Delaware','11':'District of Columbia','12':'Florida','13':'Georgia','15':'Hawaii','16':'Idaho','17':'Illinois','18':'Indiana','19':'Iowa','20':'Kansas','21':'Kentucky','22':'Louisiana','23':'Maine','24':'Maryland','25':'Massachusetts','26':'Michigan','27':'Minnesota','28':'Mississippi','29':'Missouri','30':'Montana','31':'Nebraska','32':'Nevada','33':'New Hampshire','34':'New Jersey','35':'New Mexico','36':'New York','37':'North Carolina','38':'North Dakota','39':'Ohio','40':'Oklahoma','41':'Oregon','42':'Pennsylvania','44':'Rhode Island','45':'South Carolina','46':'South Dakota','47':'Tennessee','48':'Texas','49':'Utah','50':'Vermont','51':'Virginia','53':'Washington','54':'West Virginia','55':'Wisconsin','56':'Wyoming'}
df['f']=df.GEO_ID.str[-2:]
df=df[df.f.isin(fips)].copy()
df['State']=df.f.map(fips)
groups={'NHWhite':'E003','NHBlack':'E004','NHAIAN':'E005','NHAsian':'E006','NHNHPI':'E007','NHOther':'E008','NHTwoPlus':'E009','Hispanic':'E012'}
tot=df['B03002_E001'].astype(float)
ssum=0; chk=0
out=pd.DataFrame({'State':df.State})
for g,c in groups.items():
    v=df['B03002_'+c].astype(float); chk=chk+v
    p=v/tot; ssum=ssum+p**2
    out['pct_'+g]=(100*p).round(2)
assert ((chk-tot).abs()<1).all()
out.insert(1,'Score',(100*(1-ssum)).round(2))
out=out.sort_values('Score',ascending=False)
out.insert(2,'DI_rank',range(1,len(out)+1))
out['total_pop']=tot.astype(int).values if False else tot.loc[out.index].astype(int)
print(out.shape); print(out.head(6).to_string()); print(out.tail(3).to_string())
out.to_csv(sys.argv[2],index=False)
