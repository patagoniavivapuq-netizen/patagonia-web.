"""Verifica la ampliación de transportes y conserva el resto del sitio."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import sys
from PIL import Image
from transport_content import PAGES, SOURCES

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'

class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.images=[];self.links=[];self.maps=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images.append(a)
  if tag=='a' and a.get('href'):self.links.append(a['href'])
  if tag=='iframe':self.maps.append(a)
  if a.get('id'):self.ids.append(a['id'])

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(baseline):
 errors=[];checked=[]
 for file in sorted((OUT/'transportes').rglob('index.html')):
  p=Page();p.feed(file.read_text())
  assert len(p.ids)==len(set(p.ids)),file
  photo_paths=[i['src'] for i in p.images if i.get('src','').startswith(('/assets/photos/','/assets/transportes/'))]
  if file.parent.name!='transportes' and len(photo_paths)!=len(set(photo_paths)):errors.append('Foto repetida dentro de ficha: '+str(file))
  for im in p.images:
   if 'alt' not in im:errors.append('Falta alt: '+str(file))
   source=im.get('src','')
   if source.startswith('/'):
    target=OUT/source.lstrip('/')
    if not target.is_file():errors.append('Imagen ausente: '+source)
    elif target.suffix!='.svg':
     with Image.open(target)as image:image.verify()
  for href in p.links:
   u=urlsplit(href)
   if href.startswith('/'):
    target=OUT/u.path.lstrip('/')
    if not(target.is_file() or (target/'index.html').is_file()):errors.append('Enlace interno roto: '+href)
   if href.startswith('#')and href[1:] not in p.ids:errors.append('Ancla ausente: '+href)
  checked.append(str(file.relative_to(OUT)))
 for row in PAGES:
  file=OUT/'transportes'/row['slug']/'index.html';p=Page();p.feed(file.read_text())
  if len(p.maps)!=len(row['maps']):errors.append('Mapa ausente: '+row['slug'])
  for frame,(_,query)in zip(p.maps,row['maps']):
   if query not in unquote(frame.get('src','')):errors.append('Mapa no coincide: '+row['slug'])
  if len(row['sections'])<5:errors.append('Ficha incompleta: '+row['slug'])
 for k,(_,url)in SOURCES.items():
  if not url.startswith('https://'):errors.append('Fuente inválida: '+k)
 manifest=json.loads((ROOT/'data/transport/photos.json').read_text())
 hashes=[]
 for p in manifest['photos']:
  h=digest(ROOT/p['path']);hashes.append(h)
  if h!=p['sha256']:errors.append('Hash fotográfico distinto: '+p['id'])
  if not p['source_url']or not p['source_page']or not p['permission_status']:errors.append('Procedencia ausente: '+p['id'])
 if len(hashes)!=len(set(hashes)):errors.append('Imagen nueva duplicada')
 unchanged=[];unexpected=[]
 for file in sorted(baseline.rglob('*.html')):
  path=file.relative_to(baseline)
  if path.parts[0]=='transportes':continue
  target=OUT/path
  if not target.is_file() or digest(file)!=digest(target):unexpected.append(str(path))
  else:unchanged.append(str(path))
 if unexpected:errors.append('Rutas ajenas modificadas: '+str(unexpected))
 if len(unchanged)<190:errors.append('Baseline incompleto')
 assert len(checked)==13,(len(checked),checked)
 result=dict(review_date='2026-10-22',guides=12,transport_pages=len(checked),new_images_and_maps=len(hashes),non_transport_pages_unchanged=len(unchanged),gastronomy_pages_unchanged=sum(p.startswith('gastronomia/')for p in unchanged),nightlife_pages_unchanged=sum(p.startswith('vida-nocturna/')for p in unchanged),errors=errors,scope='Solo /transportes/ y activos/módulos propios de esa sección.',variable_data='Tarifas y calendarios fechados. Sin garantía de disponibilidad; limitaciones documentadas en data/transport/research-notes.json.',pages=checked)
 dest=ROOT/'docs/transport';dest.mkdir(parents=True,exist_ok=True)
 (dest/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2))
 if errors:raise SystemExit(1)
 return result

if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Uso: python audit_transport.py /ruta/baseline-dist')
 audit(Path(sys.argv[1]))
