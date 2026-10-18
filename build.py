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
TOUR_PRICES={"city-tour":48000,"isla-magdalena":120000,"tierra-del-fuego":120000,"parque-del-estrecho":48000,"isla-marta-magdalena":156000,"ballenas-glaciares":294000,"ruta-glaciares":270000,"kayak-estrecho":138000,"cabalgata-bosques":156000,"delfines-australes":138000,"reserva-magallanes":48000,"faro-san-isidro":84000,"monte-tarn":102000,"pali-aike":96000,"torres-del-paine":108000,"base-torres":132000,"cabo-froward":336000,"full-day-punta-arenas":96000}
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
FEATURED_TOURS={'city-tour','isla-magdalena','tierra-del-fuego','parque-del-estrecho','torres-del-paine'}
SHOWCASE_STYLE="""<style>.sc-booking{border:2px solid #0b8179;box-shadow:0 18px 45px #0c434120}.sc-booking-head{padding-bottom:12px;border-bottom:1px solid #d7e6e2}.sc-booking .sc-form{max-width:850px;margin:25px auto}.sc-booking .sc-button{width:100%}
.showcase{background:#f6f7f4;color:#152326;padding:42px 0 90px}.sc-wrap{max-width:1180px;margin:auto;padding:0 26px}.sc-back{font-weight:850;color:#216a69;text-transform:uppercase;letter-spacing:.08em;font-size:12px}.sc-head{text-align:center;max-width:900px;margin:30px auto 35px}.sc-tag{display:inline-block;padding:10px 20px;border-radius:40px;background:#ffc44c;color:#16312f;letter-spacing:.12em;font-weight:950;font-size:12px}.sc-head h1{font-weight:950;text-transform:uppercase;font-size:clamp(43px,6.3vw,78px);line-height:1.03;letter-spacing:-.05em;margin:22px 0}.sc-head h1 em{font-style:normal;color:#bc7a00}.sc-head p{color:#4b6365;font-size:19px;line-height:1.65}.sc-hero{position:relative;border-radius:30px;overflow:hidden;margin:0 0 32px;max-height:530px;background:#102724}.sc-hero img{width:100%;height:clamp(280px,44vw,520px);object-fit:cover;display:block}.sc-hero:after{content:"";position:absolute;inset:50% 0 0;background:linear-gradient(transparent,#071d1ddd)}.sc-hero-label{position:absolute;z-index:1;bottom:25px;left:30px;color:#fff;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.sc-card{background:#fff;border:1px solid #dce6e2;border-radius:28px;padding:clamp(24px,4vw,42px);margin:0 0 28px;box-shadow:0 12px 40px #173a3510}.sc-top{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:40px;align-items:start}.sc-eyebrow{font-size:12px;letter-spacing:.15em;font-weight:950;color:#138480;text-transform:uppercase}.sc-card h2{font-size:clamp(29px,3.5vw,44px);letter-spacing:-.035em;line-height:1.1;margin:10px 0 20px;color:#122b2a}.sc-card p{line-height:1.8;color:#4c6365}.sc-price{padding:22px 30px;border-radius:20px;background:#ffc44c;min-width:185px;text-align:center;color:#132b28}.sc-price small{font-size:11px;letter-spacing:.1em;font-weight:950;text-transform:uppercase;display:block}.sc-price strong{font-size:clamp(27px,3vw,39px);display:block;margin:6px 0}.sc-price span{font-size:12px;font-weight:750}.sc-stops{display:flex;flex-direction:column;gap:34px;margin-top:40px}.sc-stop{display:grid;grid-template-columns:1fr 1fr;gap:34px;align-items:center;padding-bottom:26px;border-bottom:1px solid #dbe5e3}.sc-stop:nth-child(2n) .sc-image{order:2}.sc-image{height:300px;overflow:hidden;border-radius:24px;background:#e4efeb}.sc-image img{width:100%;height:100%;object-fit:cover;display:block}.sc-illustration{height:100%;display:flex;justify-content:center;align-items:center;font-size:70px;color:#116c68;background:linear-gradient(125deg,#c4e6df,#eaf6ee)}.sc-copy h3{font-size:clamp(23px,3vw,33px);line-height:1.15;color:#142b2b;letter-spacing:-.025em;margin:12px 0}.sc-copy p{margin:0}.sc-num{display:inline-flex;align-items:center;gap:10px;font-weight:950;color:#ba7600;letter-spacing:.14em;font-size:13px}.sc-info{background:#102927;color:#fff}.sc-info h2{color:#fff}.sc-info .sc-eyebrow{color:#ffc44c}.sc-info-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.sc-info-grid>div{padding:23px;border-radius:19px;background:#ffffff11}.sc-info-grid b{display:block;color:#fff;font-size:17px;margin-bottom:5px}.sc-info-grid p{color:#bdd5d0;margin:0;font-size:14px}.sc-facts{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-top:24px;padding-top:22px;border-top:1px solid #ffffff33}.sc-facts small{display:block;color:#9cbeb8;font-weight:850;font-size:11px;letter-spacing:.07em}.sc-facts strong{display:block;color:#fff;margin-top:7px;font-size:15px}.sc-final{display:flex;justify-content:space-between;align-items:center;gap:25px;background:#ffc44c}.sc-final h2{font-size:clamp(34px,4vw,50px);margin:8px 0}.sc-final p{color:#3f3925}.sc-button{background:#102927;color:#fff!important;display:inline-block;border:0;border-radius:16px;padding:18px 25px;cursor:pointer;font-size:13px;font-weight:950;letter-spacing:.07em;text-transform:uppercase;text-decoration:none}.sc-modal[hidden]{display:none}.sc-modal{position:fixed;inset:0;background:#000b;z-index:20000;display:grid;place-items:center;padding:20px}.sc-dialog{background:white;border-radius:25px;padding:28px;width:min(680px,100%);max-height:92vh;overflow:auto;color:#1a3030}.sc-dialog-head{display:flex;justify-content:space-between;align-items:center}.sc-dialog h2{margin:0;font-size:30px}.sc-close{font-size:29px;border:0;background:transparent;cursor:pointer}.sc-form{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:22px}.sc-form label{font-size:13px;font-weight:850}.sc-form input,.sc-form textarea,.sc-form select{width:100%;box-sizing:border-box;padding:13px;margin-top:7px;border:1px solid #bdcfcb;border-radius:12px;background:#fff;color:#162b2a;font:inherit}.sc-wide{grid-column:1/-1}.sc-form .sc-button{grid-column:1/-1;background:#087d77}.sc-note{font-size:12px;color:#5e7573}.sc-tip{border-left:6px solid #ffc44c;padding-left:20px;font-style:italic;color:#345655;font-weight:700}@media(max-width:760px){.showcase{padding-top:25px}.sc-wrap{padding:0 16px}.sc-top,.sc-stop{grid-template-columns:1fr}.sc-stop:nth-child(2n) .sc-image{order:0}.sc-image{height:250px}.sc-info-grid,.sc-facts,.sc-form{grid-template-columns:1fr}.sc-final{display:block}.sc-final .sc-button{width:100%;text-align:center;box-sizing:border-box;margin-top:18px}.sc-price{width:max-content}.sc-head h1{font-size:44px}.sc-form .sc-button,.sc-wide{grid-column:auto}}
</style>"""
def showcase_tour(a):
 selected=photos_for(a)
 hero='p-'+selected[0] if selected else article_image(a)
 n=TOUR_PRICES.get(a['slug'])
 price=('CLP $'+format(n,',').replace(',','.')) if n else 'Consultar'
 page=head(a['title'],a['intro'],'article')+SHOWCASE_STYLE+'<main class="showcase" id="inicio"><div class="sc-wrap">'
 page+='<a class="sc-back" href="/tours/">← Volver a Tours</a><header class="sc-head"><span class="sc-tag">★ Experiencia austral destacada</span><h1>'+E(a['title'])+'</h1><p>'+E(a['intro'])+'</p></header>'
 page+='<div class="sc-hero"><img src="'+("https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Cuernos_del_Paine_from_Lake_Peho%C3%A9.jpg/1280px-Cuernos_del_Paine_from_Lake_Peho%C3%A9.jpg" if a['slug']=='torres-del-paine' else img(hero))+'" alt="'+E('Cuernos del Paine y Lago Pehoé, Parque Nacional Torres del Paine' if a['slug']=='torres-del-paine' else IMAGEDESC.get(hero,a['title']),quote=True)+'"><div class="sc-hero-label">PATAGONIA VIVA · PUNTA ARENAS</div></div>'
 page+='<section class="sc-card"><div class="sc-top"><div><span class="sc-eyebrow">Descubre la experiencia</span><h2>Una aventura para recordar</h2><p>'+E(a['intro'])+'</p><p>Conoce cada parada, las condiciones de la actividad y qué debes confirmar para disfrutar sin sorpresas.</p></div><div class="sc-price"><small>Precio de referencia</small><strong>'+price+'</strong><span>por persona · sujeto a confirmación</span></div></div><div class="sc-stops">'
 extra=selected[1:]
 for i,sec in enumerate(a['sections'],1):
  imagekey=extra[(i-1)%len(extra)] if extra else None
  # Show each actual tour photo only once; remaining spots use designed editorial panels instead of unrelated imagery.
  showphoto=imagekey if imagekey and i<=len(extra) else None
  page+='<article class="sc-stop"><div class="sc-image">'
  if showphoto:page+='<img src="'+img('p-'+showphoto)+'" loading="lazy" alt="'+E(CATALOG[showphoto]['caption'],quote=True)+'">'
  else:page+='<div class="sc-illustration" aria-hidden="true">'+('✦' if i%3==1 else '❖' if i%3==2 else '✧')+'</div>'
  page+='</div><div class="sc-copy"><span class="sc-num">'+f'{i:02d}'+' · PUNTA ARENAS</span><h3>'+E(sec['title'])+'</h3><p>'+E(sec['text'])+'</p></div></article>'
 page+='</div></section>'
 page+='<section class="sc-card sc-info"><span class="sc-eyebrow">Información práctica</span><h2>Prepara tu experiencia</h2><div class="sc-info-grid"><div><b>✓ Itinerario</b><p>El recorrido se confirma según la modalidad contratada y la operación del día.</p></div><div><b>✓ Encuentro</b><p>Indica tu hotel, hospedaje o muelle; comprobaremos si corresponde recogida.</p></div><div><b>✓ Condiciones</b><p>Clima, entradas, alimentación y cancelación se confirman antes del pago.</p></div><div><b>✓ Asesoramiento</b><p>Cuéntanos las edades, dificultades de movilidad o necesidades especiales.</p></div></div><div class="sc-facts"><div><small>DESTINO</small><strong>Magallanes</strong></div><div><small>IDIOMA</small><strong>A confirmar</strong></div><div><small>DISPONIBILIDAD</small><strong>Según fecha</strong></div><div><small>RESERVA</small><strong>Por WhatsApp</strong></div></div></section>'
 page+='<section class="sc-card"><span class="sc-eyebrow">Consejo de la casa</span><h2>Dato Austral</h2><p class="sc-tip">'+E(a['tip'])+'</p></section>'
 page+='<section class="sc-card sc-final"><div><span class="sc-eyebrow">Tu próxima aventura</span><h2>¿Nos vamos?</h2><p>Envíanos tu fecha y cantidad de pasajeros. Confirmaremos itinerario, disponibilidad y precio final antes de reservar.</p></div><a class="sc-button" href="#solicitar-reserva">Completar solicitud ↓</a></section>'
 page+='<section class="sc-card sc-booking" id="solicitar-reserva"><div class="sc-booking-head"><span class="sc-eyebrow">Tu reserva, paso a paso</span><h2>Solicita tu experiencia</h2><p>Completa los datos y envíanos tu solicitud por WhatsApp.</p></div><p>'+E(a['title'])+'</p><form class="sc-form" id="sc-form"><label>Nombre del responsable<input name="nombre" required autocomplete="name"></label><label>Teléfono / WhatsApp<input type="tel" name="telefono" required autocomplete="tel" placeholder="+56 9 ..."></label><label>Fecha del tour<input type="date" name="fecha" required></label><label>Adultos<input type="number" name="adultos" min="1" value="2" required></label><label>Niños<input type="number" name="ninos" min="0" value="0"></label><label>Hotel u hospedaje<input name="hotel" required></label><label class="sc-wide">Dirección / punto de recogida<input name="direccion" required></label><label class="sc-wide">Observaciones<textarea name="observaciones" rows="3"></textarea></label><p class="sc-wide sc-note">Al enviar abrirás WhatsApp con los datos. La solicitud no confirma una reserva ni el valor final.</p><button class="sc-button" type="submit">Enviar consulta por WhatsApp ↗</button></form></section>'
 page+='<script>(function(){var form=document.getElementById("sc-form");if(!form)return;form.addEventListener("submit",function(e){e.preventDefault();var d=new FormData(form),fields=["nombre","telefono","fecha","adultos","ninos","hotel","direccion","observaciones"];var msg="Hola, quiero consultar el tour: '+E(a['title'])+'\\n"+fields.map(function(k){return k+": "+(d.get(k)||"-")}).join("\\n");window.open("https://wa.me/5521969946938?text="+encodeURIComponent(msg),"_blank","noopener,noreferrer")})})();</script>'

 return page+'</div></main>'+footer()

# Fichas: imagen bajo título, bloques numerados, foto intercalada y consejo propio.
for a in ARTICLES:
 cat=a['category'];title=CAT[cat][1];key=article_image(a)
 if cat=='tours' and a['slug'] in FEATURED_TOURS:
  write(url(a),showcase_tour(a))
  continue
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
 if cat=='tours' and not (a['status'] or '').startswith('Ficha en preparación'):
  n=TOUR_PRICES.get(a['slug'])
  label='Desde CLP '+format(n,',').replace(',','.')+' por persona (referencia)' if n else 'Consultar precio'
  page+='<section class="related"><h2>Solicita esta experiencia</h2><p>'+label+'</p><p>Tarifa final y disponibilidad sujetas a confirmación.</p>'
  page+='<form class="tour-request" data-title="'+E(a['title'],quote=True)+'">'
  page+='<label>Fecha <input type="date" name="fecha" required></label><label>Adultos <input type="number" name="adultos" min="1" value="2" required></label>'
  page+='<label>Niños <input type="number" name="ninos" min="0" value="0"></label><label>Responsable de la reserva <input name="nombre" autocomplete="name" required></label><label>Teléfono / WhatsApp con código de país <input type="tel" name="telefono" autocomplete="tel" required></label>'
  page+='<label>Hotel <input name="hotel" required></label><label>Notas <textarea name="notas"></textarea></label>'
  page+='<button type="submit" class="primary">CONSULTAR POR WHATSAPP</button></form></section>'
  page+='<script>(function(){var f=document.querySelector(".tour-request");if(!f)return;f.addEventListener("submit",function(e){e.preventDefault();var d=new FormData(f);var msg="Consulta: "+f.dataset.title+" | Fecha: "+d.get("fecha")+" | Adultos: "+d.get("adultos")+" | Niños: "+d.get("ninos")+" | Responsable: "+d.get("nombre")+" | Teléfono: "+d.get("telefono")+" | Hotel: "+d.get("hotel")+" | Notas: "+d.get("notas");window.open("https://wa.me/5521969946938?text="+encodeURIComponent(msg),"_blank");});})();</script>'
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
