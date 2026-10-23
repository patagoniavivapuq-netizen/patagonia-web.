"""Tours y Transportes: presentación editorial sin cambios de datos comerciales."""
import html,json,re
E=html.escape
TOUR_GROUPS={'Fauna y navegación':{'isla-magdalena','isla-marta-magdalena','ballenas-glaciares','ruta-glaciares','delfines-australes','safari-fotografico','avistamiento-aves'},'Trekking y naturaleza':{'kayak-estrecho','cabalgata-bosques','reserva-magallanes','faro-san-isidro','monte-tarn','pali-aike','base-torres','cabo-froward','laguna-parrillar-tour'},'Rutas patagónicas':{'tierra-del-fuego','puerto-natales','torres-del-paine','estancia-patagonica'}}
def render(root,out,head,footer,write,articles,thumb):
 from transport_content import PAGES
 catalog=json.loads((root/'photo-catalog.json').read_text());photos=dict(catalog);photos.update({p['id']:p for p in json.loads((root/'data/transport/photos.json').read_text())['photos']})
 def pic(key,cls='',eager=False):
  p=photos[key];return '<img'+(' class="'+cls+'"'if cls else'')+' src="/'+E(p['path'],quote=True)+'" alt="'+E(p['caption'],quote=True)+'" width="'+str(p['width'])+'" height="'+str(p['height'])+'" '+('fetchpriority="high"'if eager else'loading="lazy"')+' decoding="async">'
 def start(title,intro,section):
  s=head(title,intro,'category').replace('class="page-category"','class="page-category pv-travel-catalog"').replace('</head>','<link rel="stylesheet" href="/assets/css/travel-catalogs.css"></head>')
  return s+'<main id="inicio" class="tt-shell" data-travel-catalog="'+section+'">'
 def hero(eyebrow,title,intro,key,anchor):
  return '<section class="tt-hero">'+pic(key,'tt-hero-photo',True)+'<div><p class="tt-eyebrow">'+eyebrow+'</p><h1>'+title+'</h1><p>'+intro+'</p><a class="tt-button" href="#catalogo">'+anchor+' ↓</a></div></section>'
 def controls(labels,total,placeholder):
  return '<div class="tt-controls"><label>¿Qué estás buscando?<input id="tt-search" type="search" placeholder="'+placeholder+'" autocomplete="off"></label><div class="tt-filters" role="group" aria-label="Filtrar por tipo"><button type="button" data-travel-filter="" aria-pressed="true">Todos</button>'+''.join('<button type="button" data-travel-filter="'+E(x,quote=True)+'" aria-pressed="false">'+E(x)+'</button>'for x in labels)+'</div></div><p id="tt-count" aria-live="polite">'+str(total)+' opciones para explorar</p>'
 def end():return '<p id="tt-empty" hidden>No hay resultados con estos filtros. Prueba otra palabra o selecciona Todos.</p></section></div></main><script src="/assets/travel-catalogs.js" defer></script>'+footer()
 old=(out/'tours/index.html').read_text();write('/propuestas/tours-actual/',old)
 tours=[a for a in articles if a['category']=='tours']
 s=start('Tours y experiencias','Encuentra tu experiencia en Punta Arenas y Patagonia: fauna, navegación, trekking, patrimonio y rutas regionales.','tours')
 s+=hero('PATAGONIA VIVA · TOURS Y EXPERIENCIAS','De conocer el sur.<br><em>A vivirlo.</em>','Pingüinos, bosques, historia y días junto al Estrecho. Elige una experiencia que se parezca a tu forma de viajar.','magdalena-tour','Explorar las 30 experiencias')
 s+='<div class="tt-container"><div class="tt-review"><span>PROPUESTA · TOURS</span><a href="/propuestas/tours-actual/">Comparar con la portada anterior ↗</a></div><section class="tt-featured" aria-label="Tres formas de empezar">'
 for key,title,copy,url in [('magdalena-costa','Encuentros con fauna','Navega hacia Isla Magdalena.','/tours/isla-magdalena/'),('faro-san-isidro','Caminar junto al Estrecho','Descubre la ruta del Faro San Isidro.','/tours/faro-san-isidro/'),('fuerte-bulnes','Historias del extremo sur','Explora el Parque del Estrecho.','/tours/parque-del-estrecho/')]:
  s+='<a href="'+url+'">'+pic(key)+'<div><h2>'+title+'</h2><p>'+copy+'</p><span>Descubrir la experiencia ↗</span></div></a>'
 s+='</section><section class="tt-note"><div><p class="tt-eyebrow">ANTES DE ELEGIR</p><h2>Un viaje a tu ritmo.</h2></div><p>Abre cada ficha para conocer la experiencia, cómo prepararte y qué necesitas consultar antes de reservar. Los valores publicados son orientativos: confirma la tarifa final y la disponibilidad para tu fecha.</p><a href="/transportes/">Organizar mis traslados ↗</a></section><section id="catalogo" class="tt-catalog"><p class="tt-eyebrow">ELIGE TU PRÓXIMA HISTORIA</p><h2>Experiencia por experiencia.</h2>'+controls(list(TOUR_GROUPS)+['Ciudad y cultura'],len(tours),'Pingüinos, trekking, city tour…')+'<div class="tt-tour-grid">'
 for a in tours:
  group=next((g for g,slugs in TOUR_GROUPS.items()if a['slug']in slugs),'Ciudad y cultura');card=thumb(a);intro='<p class="tt-card-description">'+E(a['intro'])+'</p><span class="tt-card-action">Ver experiencia ↗</span>'
  card=card.replace('</h3>','</h3>'+intro,1).replace('class="pv-tour-card"','class="pv-tour-card tt-option" data-group="'+E(group,quote=True)+'" data-search="'+E(a['title']+' '+a['intro']+' '+group,quote=True)+'"',1)
  card=card.replace('<div class="pv-tour-body">','<div class="pv-tour-body"><small class="tt-card-group">'+E(group)+'</small>',1);s+=card
 s+='</div>'+end();write('/tours/',s)
 old=(out/'transportes/index.html').read_text();write('/propuestas/transportes-actual/',old)
 s=start('Transportes','Micros, colectivos, aplicaciones, aeropuerto y cruces del Estrecho. Guías para preparar cada tramo del viaje.','transportes')
 s+=hero('PATAGONIA VIVA · TRANSPORTES','Muévete con calma.<br><em>Sigue explorando.</em>','Desde el aeropuerto hasta un cruce del Estrecho. Encuentra la información que necesitas para cada tramo de tu viaje.','barcaza','Explorar las 12 guías')
 s+='<div class="tt-container"><div class="tt-review"><span>PROPUESTA · TRANSPORTES</span><a href="/propuestas/transportes-actual/">Comparar con la portada anterior ↗</a></div><section class="tt-featured" aria-label="Elige tu próximo tramo">'
 for key,title,copy,url in [('micros','Dentro de la ciudad','Empieza por micros y conexiones urbanas.','/transportes/micros/'),('porvenir-pathagon','Cruzar el Estrecho','Consulta la guía de Punta Arenas a Porvenir.','/transportes/punta-arenas-porvenir/'),('aeropuerto','Llegar y salir de PUQ','Prepara tu traslado al aeropuerto.','/transportes/aeropuerto/')]:
  s+='<a href="'+url+'">'+pic(key)+'<div><h2>'+title+'</h2><p>'+copy+'</p><span>Planificar este tramo ↗</span></div></a>'
 s+='</section><section class="tt-note"><div><p class="tt-eyebrow">LA INFORMACIÓN, A MANO</p><h2>Cada tramo cuenta.</h2></div><p>Las guías reúnen formas de pago, horarios, tarifas, contactos y mapas cuando están documentados. Antes de salir, revisa las condiciones del servicio y los avisos del operador para tu fecha.</p><a href="/guia/maleta-y-clima/">Prepararme para el clima ↗</a></section><section class="tt-catalog" id="catalogo"><p class="tt-eyebrow">DEL PRIMER TRASLADO AL PRÓXIMO DESTINO</p><h2>¿Cómo quieres moverte?</h2>'+controls(list(dict.fromkeys(p['group']for p in PAGES)),len(PAGES),'Micro, colectivo, Uber, barcaza…')+'<div class="tt-transport-grid">'
 for p in PAGES:
  s+='<a class="tt-transport-card tt-option" href="/transportes/'+p['slug']+'/" data-group="'+E(p['group'],quote=True)+'" data-search="'+E(p['title']+' '+p['intro']+' '+p['group'],quote=True)+'">'+pic(p['hero'])+'<div><small class="tt-card-group">'+E(p['group'])+'</small><h3>'+E(p['title'])+'</h3><p>'+E(p['intro'])+'</p><span class="tt-card-action">Abrir guía práctica ↗</span></div></a>'
 s+='</div>'+end();write('/transportes/',s)
 # Reutilizar el sistema visual aprobado en la revisión de Guía.
 for p in PAGES:
  path=out/'transportes'/p['slug']/'index.html';page=path.read_text().replace('class="page-article"','class="page-article pv-guide-detail pv-transit-detail"').replace('</head>','<link rel="stylesheet" href="/assets/css/guide-refresh.css"><link rel="stylesheet" href="/assets/css/travel-catalogs.css"></head>')
  begin=page.index('>',page.index('<main '))+1;items=page.index('<section class="items">',begin);enditems=page.index('</section>',items)+len('</section>');endmain=page.index('</main>',enditems)
  intro=page[begin:items];body=page[items:enditems];tail=page[enditems:endmain]
  fm=re.search(r'<figure.*?</figure>',intro,re.S);fig=fm.group()if fm else''
  if fm:intro=intro[:fm.start()]+intro[fm.end():]
  nm=re.search(r'<nav class="transport-nav".*?</nav>',intro,re.S);nav=nm.group()if nm else''
  if nm:intro=intro[:nm.start()]+intro[nm.end():]
  blocks=[]
  for pattern in [r'<aside class="tip">.*?</aside>',r'<details class="official-links">.*?</details>']:
   m=re.search(pattern,tail,re.S)
   if m:blocks.append(m.group());tail=tail[:m.start()]+tail[m.end():]
  aside='<aside class="pg-sidebar"><details class="pg-outline" open><summary>En esta guía</summary>'+nav+'</details>'+''.join(blocks)+'</aside>'
  updated='<div class="pg-detail-hero"><div class="pg-detail-intro">'+intro+'</div><div class="pg-detail-photo">'+fig+'</div></div><div class="pg-layout"><div class="pg-story">'+body+tail+'</div>'+aside+'</div>'
  page=page[:begin]+updated+page[endmain:];path.write_text(page)
