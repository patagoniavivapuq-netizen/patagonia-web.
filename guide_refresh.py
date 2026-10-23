"""Guía compacta: preserva párrafos, fotografías y enlaces de las fichas originales."""
from pathlib import Path
import html,re,json
E=html.escape
GROUPS=[('planifica','Planifica a tu ritmo',['primera-visita','presupuesto','informacion-practica','puerta-patagonia','costumbres-magallanicas','viajar-solo']),('temporada','Cuándo venir y qué llevar',['mejor-epoca','mes-a-mes','mal-tiempo','maleta-y-clima']),('documentos','Documentos y requisitos',['documentos','consulados','viajar-con-menores','permanencia-y-extension']),('moverse','Llegar y moverte',['conducir-patagonia','aeropuertos','terminales-de-bus','cruceros','como-moverse','guardar-equipaje']),('preparado','Salud, dinero y conexión',['seguridad-y-emergencias','seguro-y-salud','vacunas','dinero-y-tarjetas','internet-y-esim','accesibilidad'])]
def render(root,out,head,footer,write,articles,photos_for,catalog):
 guides={a['slug']:a for a in articles if a['category']=='guia'}
 assert set(guides)=={s for _,_,slugs in GROUPS for s in slugs}
 def route(a):return '/guia/'+a['slug']+'/'
 def photo(a):
  keys=photos_for(a);p=catalog[keys[0]]if keys else catalog['centro']
  return '<img src="/'+E(p['path'],quote=True)+'" alt="'+E(p['caption'],quote=True)+'" width="'+str(p['width'])+'" height="'+str(p['height'])+'" loading="lazy" decoding="async">'
 def css(s,klass):return s.replace('</head>','<link rel="stylesheet" href="/assets/css/guide-refresh.css"></head>').replace('class="page-category"','class="page-category pv-guide-catalog"').replace('class="page-article"','class="page-article pv-guide-detail"')
 old=(out/'guia/index.html').read_text();write('/propuestas/guia-actual/',old)
 s=css(head('Guía de Punta Arenas','Prepara el viaje a Punta Arenas: documentos, clima, presupuesto, transporte, salud y vida local.','category'),'catalog')
 s+='<main id="inicio" class="pg-catalog"><section class="pg-hero"><div><p class="pg-eyebrow">PATAGONIA VIVA · TU VIAJE EMPIEZA AQUÍ</p><h1>Menos dudas.<br><em>Más Patagonia.</em></h1><p>Quiero ayudarte a llegar con calma y disfrutar más. Aquí tienes todo lo práctico para preparar tu viaje, elegir cuándo venir y moverte por Punta Arenas.</p><a class="pg-button" href="#temas">Explorar los 26 temas ↓</a></div><img src="/assets/photos/costanera.webp" alt="Costanera de Punta Arenas junto al Estrecho de Magallanes" width="1280" height="960" fetchpriority="high"></section>'
 s+='<div class="pg-shell"><div class="pg-review"><span>PROPUESTA · NUEVA GUÍA</span><a href="/propuestas/guia-actual/">Comparar con la portada anterior ↗</a></div><section class="pg-featured" aria-label="Por dónde empezar">'
 for slug,label in [('primera-visita','01 · TU PRIMER VIAJE'),('mes-a-mes','02 · ELIGE TU MOMENTO'),('mal-tiempo','03 · PLANES PARA OTRO CLIMA')]:
  a=guides[slug];s+='<a class="pg-feature" href="'+route(a)+'">'+photo(a)+'<div><small>'+label+'</small><h2>'+E(a['title'])+'</h2><span>Leer la guía ↗</span></div></a>'
 s+='</section><section class="pg-directory" id="temas"><div class="pg-directory-head"><div><p class="pg-eyebrow">LA INFORMACIÓN, A MANO</p><h2>¿Qué necesitas resolver?</h2></div><label class="pg-search"><span>Buscar en la guía</span><input type="search" id="pg-search" placeholder="Clima, documentos, aeropuerto…" autocomplete="off"></label></div><nav class="pg-jumps" aria-label="Temas de la guía">'+''.join('<a href="#guia-'+gid+'">'+E(title)+'</a>'for gid,title,_ in GROUPS)+'</nav><p id="pg-count" aria-live="polite">26 temas para preparar tu viaje</p>'
 for gid,title,slugs in GROUPS:
  s+='<section class="pg-group" id="guia-'+gid+'" data-guide-group><h2>'+E(title)+'</h2><div class="pg-topics">'
  for slug in slugs:
   a=guides[slug];s+='<a class="pg-topic" href="'+route(a)+'" data-guide-search="'+E(a['title']+' '+a['intro'],quote=True)+'">'+photo(a)+'<div><h3>'+E(a['title'])+'</h3><p>'+E(a['intro'])+'</p><span>Abrir guía ↗</span></div></a>'
  s+='</div></section>'
 s+='<p id="pg-empty" hidden>No encontramos ese tema. Prueba otra palabra o borra la búsqueda para ver todas las guías.</p></section><section class="pg-next"><div><p class="pg-eyebrow">AHORA, A DISFRUTAR</p><h2>De preparar el viaje<br>a vivir la ciudad.</h2></div><div><a href="/gastronomia/">Dónde comer ↗</a><a href="/cultura/">Museos y cultura ↗</a><a href="/transportes/">Transportes en detalle ↗</a><a href="/eventos/agenda/">Consultar la agenda ↗</a><a href="/familia/">Panoramas en familia ↗</a><a href="/tours/">Tours y experiencias ↗</a></div></section></div></main><script src="/assets/guide-refresh.js" defer></script>'+footer()
 write('/guia/',s)
 for a in guides.values():
  path=out/route(a).strip('/')/'index.html';original=path.read_text();page=css(original,'detail')
  # Reordenar los bloques existentes conserva todo el contenido y las fuentes.
  start=page.index('<main ');open_end=page.index('>',start)+1;items_start=page.index('<section class="items">',open_end);items_end=page.index('</section>',items_start)+len('</section>');main_end=page.index('</main>',items_end)
  intro=page[open_end:items_start];body=page[items_start:items_end];tail=page[items_end:main_end]
  pstart=intro.find('<figure');pend=intro.find('</figure>',pstart)+len('</figure>');fig=intro[pstart:pend]if pstart>=0 else'';copy=intro[:pstart]+intro[pend:]if pstart>=0 else intro
  aside=[]
  for pattern in [r'<aside class="tip">.*?</aside>',r'<details class="official-links">.*?</details>']:
   found=re.search(pattern,tail,re.S)
   if found:aside.append(found.group());tail=tail[:found.start()]+tail[found.end():]
  nav='<details class="pg-outline" open><summary>En esta guía</summary><nav aria-label="Índice de '+E(a['title'],quote=True)+'">'+''.join('<a href="#tema-'+str(i)+'"><span>'+str(i).zfill(2)+'</span>'+E(sec['title'])+'</a>'for i,sec in enumerate(a['sections'],1))+'</nav></details>'
  sidebar='<aside class="pg-sidebar" aria-label="Consejos e índice">'+nav+''.join(aside)+'<div class="pg-help"><h2>Sigue preparando tu viaje</h2><a href="/guia/">Todos los temas ↗</a><a href="/transportes/">Cómo moverte ↗</a><a href="/gastronomia/">Dónde comer ↗</a></div></aside>'
  updated='<div class="pg-detail-hero"><div class="pg-detail-intro">'+copy+'</div><div class="pg-detail-photo">'+fig+'</div></div><div class="pg-layout"><div class="pg-story">'+body+tail+'</div>'+sidebar+'</div>'
  page=page[:open_end]+updated+page[main_end:];path.write_text(page)
