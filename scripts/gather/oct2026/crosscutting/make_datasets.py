import re,sys,csv
gif_html, ilrc_csv, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
# --- Giffords 2025 scorecard: gun-law strength rank (1 = strongest laws = best) ---
t=open(gif_html,encoding='utf-8',errors='ignore').read()
rows=re.findall(r'data-state-name="([^"]+)" data-grade=\'([^\']+)\' data-safety=\'(\d+)\' data-death=\'(\d+)\' data-per100k=\'([\d.]+)\'',t)
assert len(rows)==50, len(rows)
with open(f'{outdir}/giffords_gunLawScorecard_2025.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Rank','Grade','GunDeathsPer100k'])
    for r in sorted(rows,key=lambda r:(int(r[2]),r[0])): w.writerow([r[0],r[2],r[1],r[4]])
# --- ILRC 2026 state immigration enforcement map: avg score 1 (most harmful) .. 5 (most protective) ---
with open(ilrc_csv,newline='',encoding='utf-8') as f: d=list(csv.DictReader(f))
assert len(d)==51, len(d)
with open(f'{outdir}/ilrc_stateImmigrationEnforcement_2026.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['State','Processed','ILRC_AvgScore_1to5','Litigation'])
    for r in sorted(d,key=lambda r:r['State Name']):
        s=float(r['Rounded Score (2026)'])
        assert 1<=s<=5
        w.writerow([r['State Name'], round((s-1)/4*10,3), s, r['Impacted by Litigation']])
print('ok')
