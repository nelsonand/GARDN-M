import sys,re,json,pandas as pd
h=open(sys.argv[1],encoding='utf-8',errors='replace').read()
i=h.find('"rankings":[{"geography"')
j=h.index(']',i)
arr=json.loads(h[i+len('"rankings":'):j+1])
df=pd.DataFrame(arr)
print(df.shape)
df=df.rename(columns={'geography':'State','opp_eq':'Rank','overall':'Overall_BestStates_rank','opp':'Opportunity_rank',
 'opp_eq_edra':'Race_EducationGap_rank','opp_eq_inra':'Race_IncomeGap_rank','opp_eq_emra':'Race_UnemploymentGap_rank',
 'opp_eq_emdi':'Disability_UnemploymentGap_rank','opp_eq_inge':'Gender_IncomeGap_rank','opp_eq_emge':'Gender_LaborForceGap_rank'})
df=df[['State','Rank','Race_EducationGap_rank','Race_IncomeGap_rank','Race_UnemploymentGap_rank','Gender_IncomeGap_rank','Gender_LaborForceGap_rank','Disability_UnemploymentGap_rank','Opportunity_rank','Overall_BestStates_rank']].sort_values('Rank')
assert sorted(df.Rank)==list(range(1,51)), sorted(df.Rank)
df.to_csv(sys.argv[2],index=False); print(df.head(5).to_string())
json.dump(arr,open(sys.argv[3],'w'),indent=1)
