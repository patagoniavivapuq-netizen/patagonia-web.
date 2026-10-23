"""Propuesta de portada: solo la rama de revisión, sin cambios en fichas."""
from pathlib import Path
import html,json,re
E=html.escape

def render(root,out,head,footer,write,categories):
 old=(out/'index.html').read_text()
 write('/propuestas/home-actual/',old)
 catalog=json.loads((root/'photo-catalog.json').read_text())
 def photo(key,alt='',priority=False):
  p=catalog[key];return '<img src="/'+E(p['path'],quote=True)+'" alt="'+E(alt or p['caption'],quote=True)+'" width="'+str(p['width'])+'" height="'+str(p['height'])+'" '+('fetchpriority="high"'if priority else'loading="lazy"')+' decoding="async">'
 def link(href,text,extra=''):return '<a class="hm-link '+extra+'" href="'+href+'">'+text+' <span aria-hidden="true">↗</span></a>'
 def tile(css,name,sub,href,key):
  return '<a class="hm-tile hm-'+css+'" href="'+href+'">'+photo(key)+'<div class="hm-tile-copy"><span class="hm-tile-mark" aria-hidden="true">↗</span><h3>'+E(name)+'</h3><p>'+E(sub)+'</p></div></a>'
 page=head('Punta Arenas se vive · propuesta de portada','Una nueva mirada para descubrir Punta Arenas: experiencias, gastronomía, cultura, naturaleza y vida local.')
 page=page.replace('class="page-home"','class="page-home pv-home-mosaic"').replace('</head>','<link rel="stylesheet" href="/assets/css/home-mosaic.css"></head>')
 page=page.replace('<img src="/assets/brand.svg" width="45" height="45" alt="Patagonia Viva"></a>','<img src="/assets/brand.svg" width="45" height="45" alt=""><span>PATAGONIA <em>VIVA</em><small>PUNTA ARENAS · CHILE</small></span></a>',1)
 page+='<main id="inicio"><div class="hm-review"><span>PROPUESTA DE PORTADA · MOSAICO + REVISTA</span><a href="/propuestas/home-actual/">Comparar con el home actual ↗</a></div>'
 page+='<section class="hm-hero"><img class="hm-hero-photo" src="/assets/images/ciudad.webp" alt="Punta Arenas y el Estrecho de Magallanes desde el mirador" width="1100" height="763" fetchpriority="high"><div class="hm-hero-copy"><p class="hm-eyebrow">MI PATAGONIA, A TU MANERA</p><h1>Punta Arenas<br>no se visita.<br><em>Se vive.</em></h1><p>Historias, sabores y encuentros en el fin del mundo.<br>Quiero ayudarte a descubrir tu propia Patagonia.</p>'+link('#explora','Encuentra tu próxima historia','hm-button')+'</div><span class="hm-location">53° SUR · ESTRECHO DE MAGALLANES</span></section>'
 page+='<section class="hm-discover hm-container" id="explora"><div class="hm-heading"><div><p class="hm-eyebrow">EMPIEZA POR LO QUE TE MUEVE</p><h2>Hay muchas formas<br>de vivir el sur.</h2></div><p>Una mesa compartida, un paseo junto al Estrecho o una historia que todavía no conocías. Elige tu próximo paso.</p></div><div class="hm-mosaic">'
 for args in [
  ('city','Descubre Punta Arenas','Historia, mar y una ciudad con carácter.','/guia/','costanera'),
  ('experiences','Experiencias','Navegaciones y encuentros con la Patagonia.','/tours/','magdalena-tour'),
  ('food','Gastronomía','Los sabores también cuentan historias.','/gastronomia/','sotitos'),
  ('culture','Cultura','Museos, iglesias, libros y escenarios.','/cultura/','museo-regional'),
  ('family','En familia','Tiempo para jugar y descubrir juntos.','/familia/','familia'),
  ('night','Vida nocturna','Encuentra tu lugar cuando cae la tarde.','/vida-nocturna/','coyote'),
  ('transport','Transportes','Conecta y sigue explorando.','/transportes/','micros')]:page+=tile(*args)
 page+='</div></section>'
 page+='<section class="hm-story hm-container"><div class="hm-story-image">'+photo('sotitos-fachada')+'</div><div class="hm-story-copy"><p class="hm-eyebrow">01 · SABORES CON HISTORIA</p><h2>Conocer una ciudad.<br>También a la mesa.</h2><p>La centolla, el cordero magallánico, un café para entrar en calor. En Punta Arenas, sentarse a comer es otra manera de acercarse al sur.</p><p>Te acompaño a elegir por cocina, ambiente y momento del día, con fotografías y fichas para preparar tu visita.</p>'+link('/gastronomia/','Explorar gastronomía','hm-button')+'</div></section>'
 page+='<section class="hm-story hm-story-reverse hm-container"><div class="hm-story-image">'+photo('catedral')+'</div><div class="hm-story-copy"><p class="hm-eyebrow">02 · UNA CIUDAD POR DESCUBRIR</p><h2>Camina despacio.<br>Mira un poco más.</h2><p>Detrás de las fachadas y junto a la plaza hay historias de viajes, familias y comunidades que le dieron forma a Punta Arenas.</p><p>Descubre sus barrios, museos e iglesias, y combina el paseo con bibliotecas, centros culturales y una pausa en el camino.</p><div class="hm-story-links">'+link('/cultura/','Explorar cultura','hm-button')+link('/barrios/','Recorrer los barrios')+'</div></div></section>'
 page+='<section class="hm-agenda hm-container"><div>'+photo('noche')+'</div><div class="hm-agenda-copy"><p class="hm-eyebrow">03 · EN LA AGENDA</p><h2>La ciudad también<br>se vive en sus encuentros.</h2><p>Carreras, conciertos, carnaval, festivales y ferias. Consulta las fechas publicadas y distingue las próximas convocatorias de las ediciones anteriores.</p>'+link('/eventos/agenda/','Explorar la agenda','hm-button')+'</div></section>'
 # El catálogo completo permanece disponible, con las quince secciones originales.
 page+='<section class="hm-everything hm-container"><div class="hm-heading"><div><p class="hm-eyebrow">TODAS LAS PUERTAS ABIERTAS</p><h2>Tu viaje, a tu manera.</h2></div><p>Todo lo que ya conoces de Patagonia Viva, reunido para que sigas explorando.</p></div><div class="hm-index">'
 labels={'tours':'Tours y experiencias','cultura':'Cultura','guia':'Guía de Punta Arenas'}
 for i,(slug,title,desc,key)in enumerate(categories,1):
  page+='<a href="/'+slug+'/"><span>'+str(i).zfill(2)+'</span><div><h3>'+E(labels.get(slug,title))+'</h3><p>'+E(desc)+'</p></div><b aria-hidden="true">↗</b></a>'
 page+='</div></section>'
 # Conservar todas las tarjetas, textos y enlaces de tours del home anterior.
 start=old.index('<section class="editorial night">');end=old.index('<section class="home-highlights">',start)
 tours=old[start:end].replace('class="editorial night"','class="hm-tours hm-container"',1).replace('TOURS Y EXPERIENCIAS','04 · TOURS Y EXPERIENCIAS',1)
 page+=tours
 page+='<section class="hm-final hm-container"><div>'+photo('bosque')+'</div><div><p class="hm-eyebrow">ANTES DE SALIR</p><h2>Un poco de calma.<br>Y ganas de descubrir.</h2><p>Prepara el viaje según el mes, encuentra ideas para hoy y deja espacio para lo que aparezca en el camino.</p><div class="hm-story-links">'+link('/guia/mes-a-mes/','Punta Arenas mes a mes','hm-button')+link('/consejos/','¿Qué hago hoy?')+link('/naturaleza/','Explorar naturaleza')+'</div></div></section></main>'+footer()
 write('/',page)
