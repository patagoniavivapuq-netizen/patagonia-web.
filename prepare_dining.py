"""Importa investigación documentada; no inventa datos faltantes."""
from pathlib import Path
import json
import re
import hashlib
import unicodedata

ROOT = Path(__file__).parent
RESEARCH = ROOT.parent
DEST = ROOT / 'data/dining'
DEST.mkdir(parents=True, exist_ok=True)
ALIASES = {'sotito-s-restaurant':'sotitos','restaurante-hotel-savoy':'savoy','hotel-savoy-restaurant':'savoy','lomito-s':'lomitos','dino-s-pizza':'dinos-pizza','dinos':'dinos-pizza','muchacha-restobar':'muchacha','la-chocolatta':'chocolatta','la-mona-crespa-cafe':'la-mona-crespa','mesita-grande-punta-arenas':'mesita-grande','bruna':'bruna-gastrobar','taberna-club-de-la-union':'taberna-bar-club-de-la-union','la-luna':'la-luna-restaurant'}
def canonical(slug):
    return ALIASES.get(slug, slug)

def research_input(name):
    candidate=RESEARCH/name
    return candidate if candidate.exists() else DEST/name

venues = []
exclusions = []
overlays = {}
overlay_sections={}
base_slugs=set()
external_audit=ROOT/'docs/dining/external-links.json'
unavailable_contact_urls=set()
if external_audit.exists():
    unavailable_contact_urls={r['url'] for r in json.loads(external_audit.read_text()).get('results',[]) if r.get('status') in [404,410]}
for raw_file in ['research-restaurants-a.json','research-restaurants-b.json','research-nightlife.json']:
    if research_input(raw_file).exists():
        base_slugs.update(r['slug'] for r in json.loads(research_input(raw_file).read_text())['records'])
overlay_files={p.name:p for pattern in ['editorial-food-*.json','editorial-night-*.json'] for p in DEST.glob(pattern)}
overlay_files.update({p.name:p for pattern in ['editorial-food-*.json','editorial-night-*.json'] for p in RESEARCH.glob(pattern)})
for overlay_file in sorted(overlay_files.values()):
    document=json.loads(overlay_file.read_text())
    records=document if isinstance(document,list) else document.get('records',[])
    (DEST/overlay_file.name).write_text(json.dumps(document,ensure_ascii=False,indent=2))
    for record in records:
        overlays[record['slug']]=record
        overlay_sections[record['slug']]='vida-nocturna' if overlay_file.name.startswith('editorial-night-') else 'gastronomia'
for file, section in [('research-restaurants-a.json','gastronomia'),('research-restaurants-b.json','gastronomia'),('research-nightlife.json','vida-nocturna')]:
    p = research_input(file)
    if not p.exists():
        raise FileNotFoundError('Falta un documento de investigación; no se reemplaza el inventario: '+file)
    document = json.loads(p.read_text())
    (DEST / file).write_text(json.dumps(document, ensure_ascii=False, indent=2))
    exclusions.extend(document.get('excluded', document.get('candidates_excluded', [])))
    if file in ['research-restaurants-b.json','research-nightlife.json']:
        document['records'] += [r for slug,r in overlays.items() if slug not in base_slugs and overlay_sections[slug]==section]
    for r in document['records']:
        researched_at='2026-10-20' if r['slug'] in overlays else '2026-10-18'
        r = overlays.get(r['slug'],r)
        slug = canonical(r['slug'])
        sections = []
        for b in r.get('sections', []):
            paragraphs = b.get('paragraphs', [b['text']] if b.get('text') else [])
            sections.append({'title': b['title'], 'paragraphs': paragraphs})
        facts = r.get('facts', r.get('verified_facts', []))
        intro = r.get('intro') or (facts[0] if facts else (sections[0]['paragraphs'][0] if sections and sections[0]['paragraphs'] else r['category'] + ' en Punta Arenas.'))
        if len(intro) > 250:
            intro = intro[:247].rsplit(' ', 1)[0] + '…'
        contacts = dict(r.get('contacts') or {})
        for key in ['phone','website','instagram','whatsapp','reservation']:
            if r.get(key):
                contacts[key] = r[key]
        removed_contact_urls=[u for u in contacts.values() if isinstance(u,str) and u in unavailable_contact_urls]
        contacts={k:u for k,u in contacts.items() if not (isinstance(u,str) and u in unavailable_contact_urls)}
        tags = r.get('tags') or re.split(r', | y | / ', r['category'])
        text = unicodedata.normalize('NFKD',' '.join(tags).lower())
        filters = []
        for token, match in [('cafes',r'caf|pastel|chocolat|gelat'),('mar',r'marisc|pescad|centolla'),('carnes',r'parrill|carn|asado|cordero'),('italiana',r'pizza|italian|pasta'),('regional',r'magall|patagon|chilen'),('internacional',r'internacional|frances|asia|chin|peruan|sushi'),('cervecerias',r'cervecer|cerveza'),('cocteleria',r'coctel|cocktail|barra|lounge'),('musica',r'musica|baile|karaoke|disco|club'),('bares',r'bar|pub|taberna|tapas')]:
            if re.search(match,text):filters.append(token)
        if not filters:filters=['bares' if section=='vida-nocturna' else 'regional']
        tip = next((b['paragraphs'][0] for b in sections if b['paragraphs'] and ('dato' in b['title'].lower() or 'consejo' in b['title'].lower())), '')
        issues = list(r.get('pending', [])) + list(r.get('notes', []))
        issues += ['Enlace de contacto omitido por respuesta404/410: '+u for u in removed_contact_urls]
        v = {'id':slug,'slug':slug,'name':r['name'],'section':section,'category':r['category'],'address':r['address'],'sector':r.get('sector',r.get('neighborhood','Punta Arenas')),'intro':intro,'tags':tags,'filters':filters,'sections':sections,'contacts':contacts,'tip':tip,'sources':r.get('sources',r.get('source_urls',[])),'hours':r.get('hours'),'price':r.get('price'),'accessibility':r.get('accessibility'),'research_status':r.get('verification',r.get('verification_status',r.get('status','research-draft'))),'issues':issues,'publishable':bool(r['address'] and len(sections)>=6)}
        if slug in ['patagon-bowling-restobar','opera-bar-grill','el-refugio-club-andino','la-cafetera','xiaoyan-gourmet']:
            v['publishable'] = False
            v['issues'].append('Fuera del catálogo confirmado hasta verificar ubicación, alcance o identidad actual.')
        v['researched_at']=researched_at
        if r.get('address_verified') is False:
            v['publishable']=False
            v['issues'].append('Dirección pendiente de corroboración actual.')
        if slug=='la-cafetera' and r.get('address_verified') is True:
            v['publishable']=True
        if 'operation_verified' in r and r['operation_verified'] is not True:
            v['publishable']=False
            v['issues'].append('Operación actual pendiente de corroboración; no implica cierre confirmado.')
        for field in ['hours','price','accessibility']:
            if isinstance(v.get(field),dict):
                fact = v[field]
                v[field] = fact.get('text')
                if fact.get('source') and fact['source'] not in v['sources']:
                    v['sources'].append(fact['source'])
        if not any(x['id']==slug for x in venues):
            venues.append(v)
        else:
            exclusions.append({'slug':slug,'reason':'Identidad duplicada entre catálogos; no computar dos veces.'})

if not venues:
    raise ValueError('No hay investigación disponible; se conserva el inventario existente.')
existing_photos_file=DEST/'photos.json'
existing_photos=json.loads(existing_photos_file.read_text()).get('photos',[]) if existing_photos_file.exists() else []
photos=[]
hashes=set()
for file in ['photos-new.json','night-photos-new.json','more-food-photos.json','more-night-photos.json','batch21-photos.json']:
    p=RESEARCH/file
    if not p.exists():continue
    for r in json.loads(p.read_text()):
        venue=canonical(r['venue'])
        if venue not in {v['id'] for v in venues}:continue
        path=ROOT/r['path']
        if not path.is_file():continue
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        if sha in hashes:continue
        hashes.add(sha)
        subject_review=r.get('visual_review', r.get('subject_verified',False))
        photos.append(dict(r,venue_id=venue,sha256=sha,verified_subject=bool(subject_review),permission_status='provisional_pending_authorization',author=r.get('author') or 'No identificado'))

# Incorporaciones revisadas y persistidas: no dependen de la carpeta temporal de investigación.
additions_file=DEST/'photo-additions.json'
if additions_file.exists():
    for p in json.loads(additions_file.read_text()).get('photos',[]):
        venue=canonical(p.get('venue_id',p.get('venue','')))
        if venue not in {v['id'] for v in venues}:continue
        path=ROOT/p['path']
        if path.is_file():
            photo_bytes=path.read_bytes()
        else:
            # En un clon limpio, build.py todavía no ha extraído la biblioteca.
            import zipfile
            photo_bytes=None
            for photo_pack in ROOT.glob('dining-photo-assets*.zip'):
                with zipfile.ZipFile(photo_pack) as pack:
                    if p['path'] in pack.namelist():
                        photo_bytes=pack.read(p['path'])
                        break
            if photo_bytes is None:raise ValueError('Foto incorporada ausente: '+p['path'])
        sha=hashlib.sha256(photo_bytes).hexdigest()
        if p.get('sha256') and sha!=p['sha256']:raise ValueError('Foto incorporada distinta del inventario: '+p['path'])
        if sha in hashes:continue
        hashes.add(sha)
        photos.append(dict(p,venue_id=venue,sha256=sha,permission_status='provisional_pending_authorization'))

# Conservar las fotos ya revisadas cuando no estén los archivos temporales de búsqueda.
venue_ids={v['id'] for v in venues}
for p in existing_photos:
    if p.get('venue_id') not in venue_ids or not p.get('sha256') or p['sha256'] in hashes:continue
    hashes.add(p['sha256'])
    photos.append(p)

# Material del primer lote: solo locales concretos; ninguna foto temática se hereda.
catalog=json.loads((ROOT/'photo-catalog.json').read_text())
old_keys={'sotitos':['sotitos','sotitos-fachada','sotitos-mariscos'],'savoy':['savoy','savoy-salon'],'dinos-pizza':['dinos'],'dona-ines':['dona-ines','dona-ines-buffet']}
for venue,keys in old_keys.items():
    if venue not in {v['id'] for v in venues}:continue
    for k in keys:
        p=catalog.get(k)
        if not p or not p.get('path') or not (ROOT/p['path']).is_file():continue
        sha=hashlib.sha256((ROOT/p['path']).read_bytes()).hexdigest()
        if sha in hashes:continue
        hashes.add(sha)
        photos.append({'venue_id':venue,'path':p['path'],'source_url':p['source_url'],'source_page':p.get('source_page'),'caption':p.get('caption',''),'width':p.get('width',1280),'height':p.get('height',850),'sha256':sha,'author':'No identificado','permission_status':'provisional_pending_authorization','verified_subject':True,'visual_review':'Identificación conservada del lote previo; fuente concreta del establecimiento.'})

curation_file=DEST/'photo-curation.json'
if curation_file.exists():
    curation=json.loads(curation_file.read_text())
    excluded_paths=set(curation.get('excluded_paths',[]))
    photos=[p for p in photos if p['path'] not in excluded_paths]
    for p in photos:
        preferred=curation.get('hero_paths',{}).get(p['venue_id'])
        if preferred:p['recommended_hero']=p['path']==preferred

for v in venues:
    pp=[p for p in photos if p['venue_id']==v['id']]
    v['photo_count']=len(pp)
    v['photo_gap']=max(0,5-len(pp))
    v['editorial_characters']=sum(len(b['title'])+sum(map(len,b['paragraphs'])) for b in v['sections'])
    v['acceptance_ready']=v['publishable'] and len(pp)>=5 and v['editorial_characters']>=6000 and not v['issues']

for p in photos:
    source_page=p.get('source_page','') or ''
    if not source_page.startswith(('https://','http://')):
        found=re.search(r'https?://[^\s)]+',source_page)
        if found:
            p['source_title']=source_page
            p['source_page']=found.group(0)

labels={'cafes':'Cafés y dulces','mar':'Pescados y mar','carnes':'Carnes y parrillas','italiana':'Pastas y pizza','regional':'Cocina regional','internacional':'Cocina internacional','cervecerias':'Cervecerías','cocteleria':'Coctelería','musica':'Música y baile','bares':'Bares y pubs'}
(DEST/'venues.json').write_text(json.dumps({'review_date':'2026-10-20','stage':'Investigación y vista previa; pendiente aceptación','filter_labels':labels,'venues':venues,'excluded':exclusions},ensure_ascii=False,indent=2))
(DEST/'photos.json').write_text(json.dumps({'review_date':'2026-10-21','rights':'Material provisional de terceros. Autorización o sustitución antes de explotación comercial.','photos':photos},ensure_ascii=False,indent=2))
print(json.dumps({'records':len(venues),'gastronomia':sum(v['publishable'] and v['section']=='gastronomia' for v in venues),'vida_nocturna':sum(v['publishable'] and v['section']=='vida-nocturna' for v in venues),'photos':len(photos),'with_five':sum(v['photo_count']>=5 for v in venues),'ready':sum(v['acceptance_ready'] for v in venues)},ensure_ascii=False))
