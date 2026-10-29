import sys,pypdf
r=pypdf.PdfReader(sys.argv[1])
out=open(sys.argv[2],'w')
for i,p in enumerate(r.pages):
    out.write(f'\n=====PAGE {i+1}\n'+(p.extract_text(extraction_mode='layout') or ''))
