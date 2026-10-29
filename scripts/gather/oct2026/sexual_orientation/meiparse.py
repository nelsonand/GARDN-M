import pypdf,sys,re,glob,csv,os
out=[]; bad=[]
for p in sorted(glob.glob(sys.argv[1]+'/*.pdf')):
    try:
        t=pypdf.PdfReader(p).pages[0].extract_text()
    except Exception as e:
        bad.append((p,str(e))); continue
    lines=[l.strip() for l in t.split('\n')]
    nos=[l.replace(' ','') for l in lines]
    fs=[re.fullmatch(r'FinalScore(\d+)',l) for l in nos]; fs=[m.group(1) for m in fs if m]
    hdr=None
    for i,l in enumerate(nos):
        if '2025MUNICIPALEQUALITYINDEXSCORECARD' in l:
            hdr=lines[i-1]; break
    # header has letter-spacing: collapse single spaces between chars, keep double spaces as word gaps
    if hdr: hdr=re.sub(r'(?<=\S) (?=\S)','',hdr); hdr=re.sub(r'\s+',' ',hdr)
    out.append((os.path.basename(p),hdr,fs))
    if len(fs)!=1 or not hdr: bad.append((p,hdr,fs))
w=csv.writer(open(sys.argv[2],'w',newline=''))
for r in out: w.writerow([r[0],r[1],'|'.join(r[2])])
print(len(out),'bad',len(bad)); [print(b) for b in bad[:20]]
