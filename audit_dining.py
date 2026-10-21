"""Comprobaciones de compilación; las brechas editoriales se reportan, no se ocultan."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import json
from PIL import Image

ROOT=Path(__file__).parent
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

def audit():
    data=json.loads((ROOT/'data/dining/venues.json').read_text())
    photos=json.loads((ROOT/'data/dining/photos.json').read_text())['photos']
    errors=[];hashes=set()
    for p in photos:
        f=ROOT/p['path']
        if not f.is_file():errors.append('Foto ausente: '+p['path']);continue
        h=hashlib.sha256(f.read_bytes()).hexdigest()
        if h in hashes:errors.append('Foto repetida: '+p['path'])
        hashes.add(h)
        with Image.open(f) as im:
            im.verify()
        if not p.get('source_url') or not p.get('source_page'):errors.append('Foto sin procedencia: '+p['path'])
    rendered=[]
    for v in data['venues']:
        if not v['publishable']:continue
        f=OUT/v['section']/v['slug']/'index.html'
        if not f.is_file():errors.append('Ficha ausente: '+v['id']);continue
        page=Page();page.feed(f.read_text())
        if len(page.ids)!=len(set(page.ids)):errors.append('ID HTML duplicado: '+v['id'])
        if len(page.maps)!=1:errors.append('Mapa individual ausente o duplicado: '+v['id'])
        elif v['address'] not in unquote(page.maps[0].get('src','')):errors.append('Dirección no coincide con mapa: '+v['id'])
        venue_images=[p for p in page.images if p.get('src','').startswith(('/assets/venues/','/assets/photos/'))]
        srcs=[p.get('src') for p in venue_images]
        if len(srcs)!=len(set(srcs)):errors.append('Imagen repetida en ficha: '+v['id'])
        for p in page.images:
            src=p.get('src','')
            if src.startswith('/') and not (OUT/src.lstrip('/')).is_file():errors.append('Imagen rota: '+src)
            if 'alt' not in p:errors.append('Imagen sin texto alternativo: '+v['id'])
        for href in page.links:
            if not href.startswith('/'):continue
            path=urlsplit(href).path
            target=OUT/path.lstrip('/')
            if not (target.is_file() or (target/'index.html').is_file()):errors.append('Enlace interno roto: '+href)
        rendered.append({'name':v['name'],'section':v['section'],'slug':v['slug'],'address':v['address'],'characters':v['editorial_characters'],'photos':v['photo_count'],'missing_photos':v['photo_gap'],'sources':v['sources'],'ready':v['acceptance_ready']})
    baseline=ROOT.parent/'approved-baseline.json'
    if not baseline.exists():baseline=ROOT/'docs/dining/approved-baseline.json'
    changed=[]
    if baseline.exists():
        for path,sha in json.loads(baseline.read_text()).items():
            f=OUT/path
            if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=sha:changed.append(path)
        if changed:errors.append('Se modificaron rutas aprobadas: '+str(changed))
    result={'checked_at':'2026-10-21','gastronomia_rendered':sum(v['section']=='gastronomia' for v in rendered),'nightlife_rendered':sum(v['section']=='vida-nocturna' for v in rendered),'photos':len(photos),'venues_with_five':sum(v['photos']>=5 for v in rendered),'editorial_under_6000':[v['slug'] for v in rendered if v['characters']<6000],'photo_deficits':[{'slug':v['slug'],'missing':v['missing_photos']} for v in rendered if v['missing_photos']],'approval_ready':False,'errors':errors,'unchanged_approved_routes':len(json.loads(baseline.read_text())) if baseline.exists() else None,'browser_qa':'No realizada: entorno managed sin skill control-browser disponible. No se simula aprobación visual.','map_limit':'URL individual contrastada con dirección investigada; pin físico pendiente de revisión visual.','rights':'Fotos provisionales; permisos o sustitución pendientes antes de explotación comercial.','venues':rendered}
    dest=ROOT/'docs/dining/verification.json';dest.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ['venues','editorial_under_6000','photo_deficits']},ensure_ascii=False))
    if errors:raise SystemExit(1)
    return result
if __name__=='__main__':audit()
