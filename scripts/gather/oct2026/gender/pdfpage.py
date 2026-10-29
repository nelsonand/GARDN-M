import sys,pypdf
r=pypdf.PdfReader(sys.argv[1])
for i in sys.argv[2].split(','):
    print(f'=====PAGE {i}'); print(r.pages[int(i)-1].extract_text())
