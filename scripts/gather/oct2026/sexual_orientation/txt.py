import re,sys,html
h=open(sys.argv[1],encoding='utf8',errors='replace').read()
t=re.sub(r'(?s)<script.*?</script>|<style.*?</style>','',h); t=re.sub(r'<[^>]+>',' ',t); print(html.unescape(re.sub(r'\s+',' ',t)))
