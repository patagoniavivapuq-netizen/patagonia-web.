"""Comprueba contenido, fotos únicas, mapa, enlaces y alcance del cambio."""
import json,hashlib,re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parent
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[];self.images=[];self.frames=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='a' and a.get('href'):self.hrefs.append(a['href'])
  if t=='img':self.images.append(a.get('src',''))
  if t=='iframe':self.frames.append(a.get('src',''))
def audit(root=ROOT,baseline=None):
 d=json.loads((root/'data/museums/venues.json').read_text());vv=d['venues']
 pp=json.loads((root/'data/museums/photos.json').read_text())['photos']
 errors=[];hashes={};rows=[]
 assert len(vv)==len({v['id'] for v in vv})==len({v['slug'] for v in vv})
 for p in pp:
  path=root/p['path']
  if not path.is_file():errors.append('Missing photo '+p['path']);continue
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  if sha in hashes:errors.append('Repeated photo '+p['path']+' and '+hashes[sha])
  hashes[sha]=p['path']
  for field in ['source_url','source_page','author','permissions','caption','reviewed_at']:
   if not p.get(field):errors.append('Missing provenance '+field+' '+p['path'])
  if sha!=p['sha256']:errors.append('Changed photo '+p['path'])
 for v in vv:
  route='/cultura/'+v['slug']+'/'
  path=root/'dist'/route.strip('/')/'index.html'
  if not path.is_file():errors.append('Missing route '+route);continue
  s=path.read_text();h=Links();h.feed(s)
  h.images=[u for u in h.images if u.startswith('/assets/museums/')]
  vp=[p for p in pp if p['venue_id']==v['id']]
  words=len((' '.join(p for b in v['sections'] for p in b['paragraphs'])).split())
  if words<550:errors.append('Thin content '+v['id']+' '+str(words))
  if len(v['sections'])<7:errors.append('Too few sections '+v['id'])
  if len(h.frames)!=1 or 'google.com/maps?q=' not in h.frames[0]:errors.append('Missing individual map '+v['id'])
  if len(h.images)!=len(vp)-1:errors.append('Photo distribution '+v['id'])
  if len(h.images)!=len(set(h.images)):errors.append('Repeated inline photo '+v['id'])
  if len(re.findall(r'<figure class="inline-photo"',s))!=len(vp)-1:errors.append('Not intercalated '+v['id'])
  for u in h.hrefs+h.images:
   if u.startswith('/'):
    target=root/'dist'/unquote(urlsplit(u).path).lstrip('/')
    if u.endswith('/'):target=target/'index.html'
    if not target.exists():errors.append('Broken internal '+v['id']+' '+u)
  rows.append({'id':v['id'],'route':route,'words':words,'sections':len(v['sections']),'photos':len(vp),'map':bool(h.frames)})
 catalog=(root/'dist/cultura/museos/index.html').read_text()
 if len(re.findall(r'class="restaurant"',catalog))!=len(vv):errors.append('Catalog count')
 allowed={'cultura/museos/index.html'}|{'cultura/'+v['slug']+'/index.html' for v in vv}
 unchanged=0
 if baseline:
  for rel,sha in baseline.items():
   if rel in allowed:continue
   p=root/'dist'/rel
   if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:errors.append('Unauthorized page change '+rel)
   else:unchanged+=1
 report={'checked_at':'2026-10-22','venues':len(vv),'photos':len(pp),'with_five_photos':sum(r['photos']>=5 for r in rows),'photo_gaps':[r['id'] for r in rows if r['photos']<5],'unchanged_previous_pages':unchanged,'html_pages':len(list((root/'dist').rglob('*.html'))),'details':rows,'errors':errors}
 return report
if __name__=='__main__':
 base=ROOT/'museum-research/baseline.json'
 report=audit(baseline=json.loads(base.read_text()) if base.exists() else None)
 p=ROOT/'docs/museums';p.mkdir(parents=True,exist_ok=True)
 (p/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if report['errors']:raise SystemExit(1)
