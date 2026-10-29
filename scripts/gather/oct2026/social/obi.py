import json,sys,csv
d=json.load(open(sys.argv[1]))
ds=[c for c in d if c.get('command')=='settings' and 'inclusivenessIndex' in c['settings']][0]['settings']['inclusivenessIndex']['dataSet']
ds=sorted(ds,key=lambda r:int(r['index_order']))
with open(sys.argv[2],'w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Score','obi_order','ranking_text','general_subindex','race_subindex','gender_subindex','lgbtq_subindex','religion_subindex','disability_subindex','year'])
    for r in ds:
        assert r['geo_type']=='state' and r['year']=='2025'
        w.writerow([r['loc_name'],r['index_rank'],r['index_order'],r['ranking_text'],r['general_rank'],r['race_rank'],r['gender_rank'],r['sex_orient_rank'],r['religion_rank'],r['disability_rank'],r['year']])
