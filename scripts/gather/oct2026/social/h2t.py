import re,html,sys
t=open(sys.argv[1],errors='ignore').read()
t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
t=re.sub(r'</(tr|p|div|h\d|li)>','\n',t)
t=re.sub(r'</t[dh]>','\t',t)
t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'[ \r]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
print(t)
