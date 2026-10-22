"""Checks exact preservation of approved pages and the new civic visitor guides."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,re
from PIL import Image
ROOT=Path(__file__).resolve().parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.links=[];self.frames=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='img':self.images.append(a)
  if a.get('href'):self.links.append(a['href'])
  if t=='iframe':self.frames.append(a.get('src',''))
  if a.get('id'):self.ids.append(a['id'])
def audit(root=ROOT):
 out=root/'dist';venues=json.loads((root/'data/civic/venues.json').read_text())['venues'];photos=json.loads((root/'data/civic/photos.json').read_text())['photos'];errors=[];rows=[];hashes=set()
 assert len({v['id']for v in venues})==len(venues)==32
 for p in photos:
  f=root/p['path'];sha=hashlib.sha256(f.read_bytes()).hexdigest()
  if sha!=p['sha256']:errors.append('Changed photo '+p['path'])
  if sha in hashes:errors.append('Repeated photo '+p['path'])
  hashes.add(sha)
  with Image.open(f)as im:im.verify()
  for field in ['source_url','source_page','author','permissions','reviewed_at','visual_review']:
   if not p.get(field):errors.append('Missing provenance '+p['path']+' '+field)
 for v in venues:
  path=out/v['section']/v['slug']/'index.html';s=path.read_text();p=Page();p.feed(s)
  vp=[i for i in photos if i['venue_id']==v['id']];words=len(' '.join(t for b in v['sections']for t in b['paragraphs']).split())
  if words<350:errors.append('Thin content '+v['id']+' '+str(words))
  if len(v['sections'])<8:errors.append('Missing sections '+v['id'])
  if len(p.frames)!=1 or 'google.com/maps?q='not in p.frames[0]:errors.append('Individual map '+v['id'])
  if len(p.ids)!=len(set(p.ids)):errors.append('Duplicate id '+v['id'])
  inline=[i for i in p.images if i.get('src','').startswith('/assets/civic/')]
  if len(inline)!=len(vp)-1:errors.append('Photo distribution '+v['id'])
  if len({i['src']for i in inline})!=len(inline):errors.append('Duplicate inline '+v['id'])
  if not vp:errors.append('No genuine photo '+v['id'])
  rows.append(dict(id=v['id'],route='/'+v['section']+'/'+v['slug']+'/',words=words,sections=len(v['sections']),photos=len(vp),photo_gap=max(0,5-len(vp)),map=True))
 # All local references in the new catalogues and pages must resolve.
 new_routes={v['section']+'/'+v['slug']+'/index.html'for v in venues}|{'cultura/index.html','familia/index.html','cultura/iglesias/index.html','cultura/centros-culturales/index.html','cultura/bibliotecas/index.html','cultura/cines/index.html'}
 for route in new_routes:
  p=Page();p.feed((out/route).read_text())
  for u in p.links+[i.get('src','')for i in p.images]:
   if u.startswith('/')and not u.startswith('//'):
    target=out/unquote(urlsplit(u).path).lstrip('/')
    if not target.is_file()and not(target/'index.html').is_file():errors.append('Broken local '+route+' '+u)
 preserved=0
 baseline=json.loads((root/'data/civic/approved-baseline.json').read_text())
 for rel,sha in baseline.items():
  if rel in new_routes:continue
  f=out/rel
  if not f.is_file()or hashlib.sha256(f.read_bytes()).hexdigest()!=sha:errors.append('Approved page changed '+rel)
  else:preserved+=1
 catalog_counts={}
 for route in ['cultura','cultura/iglesias','cultura/centros-culturales','cultura/bibliotecas','cultura/cines','familia']:
  s=(out/route/'index.html').read_text();catalog_counts[route]=s.count('class="restaurant"')
 assert catalog_counts['cultura/iglesias']==8
 assert catalog_counts['cultura/cines']==2
 assert catalog_counts['cultura/centros-culturales']==4
 assert catalog_counts['cultura/bibliotecas']==2
 report=dict(review_date='2026-10-22',base_commit='29819de',venues=len(venues),words=sum(r['words']for r in rows),photos=len(photos),venues_with_five_photos=sum(r['photos']>=5 for r in rows),catalogs=catalog_counts,previous_pages_preserved=preserved,html_pages=len(list(out.rglob('*.html'))),photo_gaps=[r for r in rows if r['photo_gap']],details=rows,errors=errors,rights=json.loads((root/'data/civic/photos.json').read_text()).get('rights','Provenance recorded.'),map_note='Individual map search uses researched place and address. No undocumented exact GPS pins invented.')
 return report
if __name__=='__main__':
 r=audit();p=ROOT/'docs/civic';p.mkdir(exist_ok=True);(p/'verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in ['details','photo_gaps']},ensure_ascii=False));raise SystemExit(bool(r['errors']))
