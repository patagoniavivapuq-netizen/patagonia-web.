from pathlib import Path
import json, html, shutil, re
from collections import defaultdict
from urllib.parse import quote
from content import CATEGORIES, ARTICLES, S
ROOT=Path(__file__).parent
# El paquete mantiene juntas las imágenes provisionales y evita dependencias remotas.
import zipfile
photo_pack=ROOT/'photo-assets.zip'
if photo_pack.exists():
 with zipfile.ZipFile(photo_pack) as pack:
  for info in pack.infolist():
   path=Path(info.filename)
   if path.parts[:2] != ('assets','photos') or '..' in path.parts or path.is_absolute():
    raise ValueError('Ruta de foto no válida')
   pack.extract(info, ROOT)
from media import CATALOG, CATEGORY_PHOTOS, photos_for
OUT=ROOT/'dist' 
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir();shutil.copytree(ROOT/'assets', OUT/'assets')
E=html.escape
CAT={c[0]:c for c in CATEGORIES}
IMAGES={'ciudad':'ciudad.webp','plaza':'plaza.webp','pinguinos':'pinguinos.webp','ferry':'ferry.webp','naturaleza':'naturaleza.webp','bulnes':'bulnes.webp','pali':'pali.webp'}
# Las imágenes de contexto no se presentan como fotos de restaurantes o locales específicos.
CATIMG={'naturaleza':'naturaleza','vida-nocturna':'bulnes'}
ARTICLEIMG={('naturaleza','reserva-magallanes'):'naturaleza',('naturaleza','pali-aike'):'pali',('vida-nocturna','bar-bulnes'):'bulnes'}
IMAGEDESC={'ciudad':'Punta Arenas y el Estrecho de Magallanes desde el mirador.','plaza':'La Plaza Muñoz Gamero, parte del patrimonio del centro.','pinguinos':'Pingüinos magallánicos y paisaje de Isla Magdalena.','ferry':'Navegación y desembarco en Isla Magdalena.','naturaleza':'Paisaje de la Reserva Nacional Magallanes.','bulnes':'Interior de Bar Bulnes, Punta Arenas.','pali':'Paisaje volcánico del Parque Nacional Pali Aike.'}
for media_key,media_item in CATALOG.items():
 if 'path' in media_item:
  IMAGES['p-'+media_key]='../photos/'+Path(media_item['path']).name
  IMAGEDESC['p-'+media_key]=media_item['caption']
for category,media_key in CATEGORY_PHOTOS.items():
 if 'p-'+media_key in IMAGES: CATIMG[category]='p-'+media_key

def img(key):
 return '/assets/photos/'+Path(CATALOG[key[2:]]['path']).name if key and key.startswith('p-') else '/assets/images/'+IMAGES.get(key,IMAGES['ciudad'])
def article_image(a):
 selected=photos_for(a)
 if selected:return 'p-'+selected[0]
 if a['category']=='vida-nocturna' and a['slug'] in ('el-trebol','kamikaze'):return None
 return ARTICLEIMG.get((a['category'],a['slug']),a['image'])
def url(a):return '/'+a['category']+'/'+a['slug']+'/'
NAV=[('guia','Guía Punta Arenas'),('tours','Tours'),('transportes','Transportes'),('hospedaje','Hospedajes'),('gastronomia','Gastronomía')]
def head(title,desc,kind='home'):
 css=['tokens','app','components','home-reference']
 if kind=='category':css+=['reference-guia','guia-adn']
 if kind=='article':css+=['reference-viajar-solo','guia-adn']
 css+=['patagonia']
 return '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071c1b"><title>'+E(title)+' | Patagonia Viva</title><meta name="description" content="'+E(desc,quote=True)+'"><meta name="robots" content="noindex,nofollow"><link rel="icon" href="/assets/brand.svg">'+''.join('<link rel="stylesheet" href="/assets/css/'+x+'.css">' for x in css)+'</head><body class="page-'+kind+'"><a class="skip" href="#inicio">Saltar al contenido</a><div class="mini-strip"><span class="badge"><strong>PUQ</strong> guía local</span><span>PUNTA ARENAS · PATAGONIA</span><span>Planifica menos. Vive más.</span></div><header class="topbar"><a class="brand" href="/" aria-label="Patagonia Viva · inicio"><img src="/assets/brand.svg" width="45" height="45" alt="Patagonia Viva"></a><nav class="ec-primary-nav" aria-label="Navegación principal">'+''.join('<a href="/'+k+'/">'+v+'</a>' for k,v in NAV)+'</nav><a class="nav-explore" href="/#explora">EXPLORAR PUQ <span aria-hidden="true">↗</span></a></header>'
def footer():
 return '<section class="ec-corporate-closing"><div class="ec-closing-cta"><div><p class="kicker">PATAGONIA VIVA</p><h2>Tu viaje empieza<br>con una buena historia.</h2><p>Descubre Punta Arenas con tiempo, curiosidad y mirada local.</p></div><a href="/guia/">PREPARAR MI VIAJE →</a></div></section><footer class="ec-corporate-footer"><div class="ec-footer-brand"><img src="/assets/brand.svg" width="60" height="60" alt=""><div><strong>PATAGONIA <em>VIVA</em></strong><small>PUNTA ARENAS, DESDE MI MIRADA</small></div></div><div class="ec-footer-legal"><p>© 2026 Patagonia Viva.</p><p>Punta Arenas · Magallanes · Chile</p><a href="/#explora">EXPLORAR LA CIUDAD →</a></div></footer><div class="mobile-dock"><a href="/">Inicio</a><a href="/guia/">Guía</a><a href="/#explora">Explorar</a></div><script src="/assets/site.js" defer></script></body></html>'
def write(route,text):
 p=OUT/route.strip('/')/'index.html' if route!='/' else OUT/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def photo(key,priority=False):
 if key is None:return ''
 return '<figure class="ec-inline-photo"><img src="'+img(key)+'" alt="'+E(IMAGEDESC.get(key,IMAGEDESC['ciudad']))+'" '+('fetchpriority="high"' if priority else 'loading="lazy"')+' width="1280" height="800"><figcaption>'+E(IMAGEDESC.get(key,IMAGEDESC['ciudad']))+'</figcaption></figure>'
def door(cat):
 k,title,desc,key=cat;key=CATIMG.get(k,key)
 return '<a class="door" href="/'+k+'/"><img class="card-image" src="'+img(key)+'" alt="" loading="lazy" width="620" height="400"><span class="door-copy"><b>'+E(title)+'</b><span class="card-copy">'+E(desc)+'</span><small>EXPLORAR</small></span></a>'
def thumb(a):
 key=article_image(a)
 visual='<img class="guide-thumb" src="'+img(key)+'" alt="" loading="lazy" width="640" height="420">' if key else ''
 return '<a href="'+url(a)+'">'+visual+'<b>'+E(a['title'])+'</b><span>ABRIR GUÍA →</span></a>'
# Home: mantiene clases, CSS y jerarquía de la referencia pública autorizada.
home=head('Guía de Punta Arenas y Patagonia','Descubre Punta Arenas: guía práctica, tours, transportes, alojamiento, gastronomía y vida local.')
home+='<main id="inicio"><section class="hero"><picture class="hero-visual"><img src="'+img('ciudad')+'" alt="Punta Arenas y el Estrecho de Magallanes" width="1600" height="900" fetchpriority="high"></picture><div class="hero-copy"><p class="kicker">PATAGONIA VIVA · PUNTA ARENAS</p><h1>Punta Arenas<br>no se visita.<br><em>Se vive.</em></h1><p class="lead">Mi guía para descubrir Punta Arenas: cómo preparar tu viaje, dónde comer, cómo moverte y experiencias que vas a recordar.</p><a class="primary" href="#explora">DESCUBRIR PUNTA ARENAS</a></div></section>'
home+='<section class="intro" id="explora"><p class="kicker">MI PATAGONIA, A TU MANERA</p><h2>¿Por dónde quieres empezar?</h2><p>Quiero ayudarte a encontrar la Punta Arenas que encaja contigo. Elige tu próximo paso.</p></section><section class="door-grid" aria-label="Explorar Punta Arenas">'+''.join(door(c) for c in CATEGORIES)+'</section>'
home+='<section class="today"><div><p class="kicker">AQUÍ · AHORA</p><h2>¿Qué hago hoy?</h2><p>Una caminata con buena vista, un museo, algo rico o un plan para cuando cambia el tiempo. Empieza por tu momento.</p></div><a class="primary" href="/consejos/">ENCONTRAR MI PLAN →</a></section>'
home+='<section class="editorial night"><div class="section-head"><p class="kicker">TOURS Y EXPERIENCIAS</p><h2>De conocer el sur<br>a vivirlo.</h2><p>Historias de navegación, encuentros con fauna y caminos que abren la puerta a Magallanes.</p></div><div class="feature-grid experience-carousel">'
for a in [a for a in ARTICLES if a['category']=='tours']:
 home+='<a class="feature" href="'+url(a)+'"><img class="card-image" src="'+img(article_image(a))+'" alt="" loading="lazy"><b>'+E(a['title'])+'</b><span class="card-copy">'+E(a['intro'])+'</span><small>EXPLORAR →</small></a>'
home+='</div></section><section class="home-highlights">'
for title,copy,href,key in [('ANTES DE VENIR','Elige tu mes y prepara el viaje con calma.','/guia/mes-a-mes/','p-invierno'),('NATURALEZA AUSTRAL','Bosques, costa y encuentros con fauna.','/naturaleza/','p-bosque')]:
 home+='<a class="home-highlight" href="'+href+'"><img src="'+img(key)+'" alt="" loading="lazy"><div><small>'+title+'</small><h2>'+('Punta Arenas mes a mes' if 'mes' in href else 'Otra forma de mirar')+'</h2><p>'+copy+'</p><small>ABRIR GUÍA →</small></div></a>'
home+='</section></main>'+footer();write('/',home)
# Portadas de categoría: tarjetas con miniatura y página propia por tema.
for cat,title,desc,key in CATEGORIES:
 articles=[a for a in ARTICLES if a['category']==cat];key=CATIMG.get(cat,key)
 page=head(title,desc,'category')+'<main id="inicio"><section class="hero category-hero"><div class="hero-copy"><p class="kicker">PATAGONIA VIVA · PUNTA ARENAS</p><h1>'+E(title)+'.</h1><p class="lead">'+E(desc)+'</p></div></section><div class="category-controls"><a href="/">← Inicio</a><span>'+str(len(articles))+' temas para explorar</span><label class="search-label">Buscar en esta sección<input type="search" data-filter placeholder="Escribe un tema…" autocomplete="off"></label></div>'
 groups=defaultdict(list)
 for a in articles:groups[a['group']].append(a)
 for group,aa in groups.items():
  page+='<section class="guide-group"><h2>'+E(group if group!='Explorar' else '¿Qué quieres descubrir?')+'</h2><div class="guide-grid">'+''.join(thumb(a) for a in aa)+'</div></section>'
 page+='<p class="empty-results" hidden>No encontramos ese tema. Prueba otra palabra.</p></main>'+footer();write('/'+cat+'/',page)
# Fichas: imagen bajo título, bloques numerados, foto intercalada y consejo propio.
for a in ARTICLES:
 cat=a['category'];title=CAT[cat][1];key=article_image(a)
 page=head(a['title'],a['intro'],'article')+'<main class="guide" id="inicio"><div class="breadcrumbs"><a href="/">Inicio</a><span> / </span><a href="/'+cat+'/">'+E(title)+'</a></div><p class="kicker">'+E(title)+'</p><h1>'+E(a['title'])+'</h1>'+photo(key,True)+'<p class="article-intro">'+E(a['intro'])+'</p>'
 if a['status']:page+='<p class="status-note">'+E(a['status'])+'</p>'
 selected_photos=photos_for(a)
 interleaved={}
 for n,media_key in enumerate(selected_photos[1:],1):
  after=max(1,min(len(a['sections']),round(n*len(a['sections'])/len(selected_photos))))
  interleaved.setdefault(after,[]).append('p-'+media_key)
 page+='<section class="items">'
 for i,sec in enumerate(a['sections'],1):
  page+='<article id="tema-'+str(i)+'"><span>'+f'{i:02d}'+'</span><h2>'+E(sec['title'])+'</h2><p>'+E(sec['text'])+'</p></article>'
  for inline_photo in interleaved.get(i,[]):page+=photo(inline_photo)
 page+='</section><aside class="tip"><b>Dato Austral</b><p>'+E(a['tip'])+'</p></aside>'
 if cat=='guia' and a['slug']=='internet-y-esim':
  page+='<section class="related" id="airalo-esim"><p class="kicker">INTERNET PARA TU VIAJE</p><h2>Encuentra una eSIM para Chile y la Patagonia con Airalo</h2><p>Compara planes compatibles con Chile, duración y datos incluidos. Antes de reservar comprueba que tu teléfono admita eSIM y esté desbloqueado. Para un cruce a Argentina verifica si el plan también cubre ese país.</p><div id="airalo-puq-widget" style="min-height:190px;overflow:hidden"></div><p id="airalo-puq-fallback" hidden>No pudimos cargar el comparador. Comprueba tu conexión e inténtalo nuevamente.</p><p class="status-note">Publicidad de afiliado: podemos recibir una comisión por las reservas realizadas mediante este comparador.</p></section>'
  page+='<script>(function(){var mount=document.getElementById("airalo-puq-widget");if(!mount)return;var params="trs=573170&shmarker=776744&powered_by=true&color_button=%23f2685f&color_focused=%23f2685f&secondary=%23FFFFFF&dark=%2311100f&light=%23FFFFFF&special=%23C4C4C4&border_radius=5&plain=false&no_labels=true&promo_id=8588&campaign_id=541";var script=document.createElement("script");script.async=true;script.charset="utf-8";script.src="https://tpembd.com/content?"+params+"&locale=es";script.onerror=function(){document.getElementById("airalo-puq-fallback").hidden=false;};mount.appendChild(script);})();</script>'
 if cat=='guia' and a['slug']=='conducir-patagonia':
  page+='<section class="related" id="rentcars"><p class="kicker">ALQUILER DE VEHÍCULOS</p><h2>Compara autos para recorrer Magallanes con Rentcars</h2><p>Selecciona Punta Arenas como punto de recogida si hay disponibilidad. Comprueba cobertura, caminos permitidos, depósito y permisos para cruzar a Argentina o embarcar en un ferry.</p><a class="primary" href="https://www.rentcars.com/es/?requestorid=11142&amp;utm_source=www.ernestinhocarioca.com.br&amp;utm_medium=afiliado-link" target="_blank" rel="sponsored noopener noreferrer">COMPARAR VEHÍCULOS CON RENTCARS ↗</a><p class="status-note">Enlace de nuestra cuenta de afiliados actual. Podemos recibir comisión por una reserva, según las condiciones del proveedor.</p></section>'
 if cat=='guia' and a['slug']=='guardar-equipaje':
  page+='<section class="related" aria-label="Servicio de guarda equipaje"><p class="kicker">SERVICIO PARA TU VIAJE</p><h2>Busca una consigna con Bounce</h2><p>Consulta disponibilidad, dirección, condiciones de custodia y horario de retiro antes de reservar. Los puntos ofrecidos pueden variar.</p><a class="primary" href="https://go.bounce.com/ERNESTINHO8980973466" target="_blank" rel="sponsored noopener noreferrer">CONSULTAR GUARDA EQUIPAJE EN BOUNCE ↗</a><p class="status-note">Enlace de afiliado: podemos recibir una comisión si reservas, sin cambiar el precio indicado por la plataforma.</p></section>'
 if a['place']:
  page+='<section class="map-section"><p class="kicker">UBÍCATE</p><h2>¿Dónde queda?</h2><p>'+E(a['place'])+'</p><a class="ext" target="_blank" rel="noopener noreferrer" href="https://www.google.com/maps/search/?api=1&amp;query='+quote(a['place'])+'">ABRIR UBICACIÓN EN EL MAPA ↗</a></section>'
 if a['sources']:
  # Enlaces prácticos oficiales; el archivo editorial conserva las referencias adicionales.
  official=[S[s] for s in a['sources'] if s in S and s!='restaurantes']
  if official:
   page+='<details class="official-links"><summary>Información oficial para preparar la visita</summary><p>Consulta las condiciones vigentes antes de viajar.</p><ul>'+''.join('<li><a href="'+E(u,quote=True)+'" target="_blank" rel="noopener noreferrer">'+E(n)+' ↗</a></li>' for n,u in dict.fromkeys(official))+'</ul></details>'
 related=[b for b in ARTICLES if b['category']==cat and b['slug']!=a['slug']][:3]
 page+='<section class="related"><p class="kicker">SIGUE EXPLORANDO</p><h2>También te puede servir</h2><div class="related-grid">'+''.join('<a href="'+url(b)+'">'+E(b['title'])+' <span>→</span></a>' for b in related)+'</div></section><a class="ext" href="/'+cat+'/">← VOLVER A '+E(title.upper())+'</a></main>'+footer();write(url(a),page)
write('/404/',head('No encontramos esta página','Vuelve a explorar Punta Arenas.','article')+'<main class="guide" id="inicio"><p class="kicker">PATAGONIA VIVA</p><h1>Volvamos al camino.</h1><p>Esta dirección no está disponible. Puedes encontrar tu próximo plan desde el inicio.</p><a class="primary" href="/">IR AL INICIO →</a></main>'+footer())
shutil.copyfile(OUT/'404/index.html',OUT/'404.html')
(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
(ROOT/'editorial-inventory.json').write_text(json.dumps({'stage':'Primera versión editorial para revisión','categories':len(CATEGORIES),'articles':len(ARTICLES),'review_date':'2026-10-18','sources':S,'items':[{'path':url(a),'title':a['title'],'status':a['status'],'sources':a['sources']} for a in ARTICLES]},ensure_ascii=False,indent=2))
print(json.dumps({'categories':len(CATEGORIES),'articles':len(ARTICLES),'html_files':len(list(OUT.rglob('*.html'))),'output':str(OUT)},ensure_ascii=False))
