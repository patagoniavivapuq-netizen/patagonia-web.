"""Agenda investigada: reutiliza la identidad editorial aprobada de Patagonia Viva."""
import csv,html,json,shutil
from pathlib import Path
E=html.escape
STATUS_ORDER=['Próximo','Fecha por confirmar','Participación local por confirmar','Por corroborar','Edición pasada','Realización por corroborar']
def render(root,out,head,footer,write):
 data=json.loads((root/'data/events/inventory.json').read_text());events=data['events']
 def date(x):
  def fmt(d):return '/'.join(reversed(d.split('-')))if d else'Fecha por confirmar'
  return fmt(x['start_date'])+(' — '+fmt(x['end_date'])if x['end_date']and x['end_date']!=x['start_date']else'')+(' · '+x['time']if x.get('time')else'')
 dest=out/'eventos/agenda';dest.mkdir(parents=True,exist_ok=True)
 with (dest/'inventario.csv').open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.writer(f);w.writerow(['Nombre','Categoría','Estado al 22/10/2026','Inicio','Fin','Hora publicada','Recinto','Zona','Notas','Fuentes'])
  for x in events:w.writerow([x['name'],x['category'],x['status'],x['start_date'],x['end_date'],x.get('time',''),x['venue'],x['scope'],x['description'],' | '.join(s['url']for s in x['sources'])])
 page=head('Agenda de eventos de Punta Arenas','Carreras, trekking, conciertos, festivales, ferias y panoramas de Punta Arenas. Fechas publicadas y ediciones anuales diferenciadas.','home')
 page=page.replace('class="page-home"','class="page-home pv-dining pv-dining-catalog pv-agenda"').replace('</head>','<link rel="stylesheet" href="/assets/css/dining-catalog.css"><link rel="stylesheet" href="/assets/css/dining-adaptation.css"><link rel="stylesheet" href="/assets/css/event-agenda.css"></head>')
 cats=sorted({x['category']for x in events})
 page+='<main class="gast-shell" id="inicio"><section class="gast-hero"><div class="gast-hero-inner"><p class="gast-eyebrow">PATAGONIA VIVA · AGENDA</p><h1>Lo que pasa.<br><em>Lo que viene.</em></h1><p class="gast-intro">Trekking, carreras, conciertos, carnaval, festivales, ferias para comprar y encuentros de la ciudad. Elige por fecha, interés y lugar.</p><div class="gast-stats"><span><strong>'+str(len(events))+'</strong> eventos y ciclos investigados</span><span>Revisión: 22 de octubre de 2026</span></div><a class="gast-cta" href="#agenda">Explorar fechas ↓</a></div></section>'
 page+='<section class="gast-guide-note"><div><p class="gast-eyebrow">PARA ORGANIZARTE</p><h2>Una fecha.<br>Un buen plan.</h2></div><div><p>La agenda distingue las próximas convocatorias, las ediciones pasadas y los eventos cuya nueva fecha falta confirmar. Las carreras de Torres del Paine y los festivales de otras comunas aparecen en un filtro separado.</p><p>Los horarios se expresan en hora local. Comprueba cambios, invitaciones, cupos y condiciones de acceso en la fuente enlazada antes de salir o comprar.</p><p><a href="/eventos/">Leer las guías del carnaval y los grandes encuentros →</a></p></div></section>'
 page+='<section class="gast-catalog" id="agenda"><div class="gast-section-heading"><div><p class="gast-eyebrow">CALENDARIO INVESTIGADO</p><h2>Encuentra tu próxima salida.</h2></div></div><div class="agenda-controls"><label>Buscar<input id="agenda-search" type="search" placeholder="Artista, feria, carrera o recinto…"></label><label>Tipo de evento<select id="agenda-category"><option value="">Todos los tipos</option>'+''.join('<option>'+E(c)+'</option>'for c in cats)+'</select></label><label>Estado<select id="agenda-status"><option value="Próximo">Próximos con fecha publicada</option><option value="">Todos los estados</option>'+''.join('<option>'+E(s)+'</option>'for s in STATUS_ORDER if s!='Próximo')+'</select></label><label>Ubicación<select id="agenda-scope"><option value="local">Punta Arenas y salidas desde la ciudad</option><option value="regional">Otras comunas</option><option value="">Todas las zonas</option></select></label></div><p id="agenda-count" role="status" aria-live="polite"></p><div class="agenda-list">'
 for x in sorted(events,key=lambda x:(not bool(x['start_date']),x['start_date'],x['name'])):
  outside=x['scope'].startswith('Fuera de Punta Arenas');search=' '.join([x['name'],x['category'],x['venue'],x['description'],x['scope']])
  page+='<article class="agenda-event" data-category="'+E(x['category'],quote=True)+'" data-status="'+E(x['status'],quote=True)+'" data-scope="'+('regional'if outside else'local')+'" data-search="'+E(search,quote=True)+'" id="'+E(x['id'],quote=True)+'"><p class="agenda-date">'+E(date(x))+'</p><div class="restaurant-tags"><span class="tag">'+E(x['status'])+'</span><span class="tag">'+E(x['category'])+'</span></div><h3>'+E(x['name'])+'</h3><p class="agenda-place">'+E(x['venue']or'Recinto por confirmar')+' · '+E(x['scope'])+'</p><p>'+E(x['description'])+'</p>'
  if x.get('occurrences'):
   page+='<details><summary>Fechas y funciones de esta producción</summary><ul>'
   for o in x['occurrences']:
    if isinstance(o,dict):page+='<li>'+E(o['date']+' · '+o.get('time','')+' · '+o.get('venue',''))+' · <a href="'+E(o['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">Ver convocatoria ↗</a></li>'
    else:page+='<li>'+E(o)+'</li>'
   page+='</ul></details>'
  page+='<div class="agenda-links">'+''.join('<a href="'+E(s['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+('Ver entradas o inscripción'if 'Ticketera'in s['type']else'Consultar publicación'if j==0 else'Fuente adicional')+' ↗</a>'for j,s in enumerate(x['sources'])if not s['type'].startswith('Descubrimiento'))+('<a href="'+E(x['guide'],quote=True)+'">Leer guía completa →</a>'if x.get('guide')else'')+'</div></article>'
 page+='</div><p id="agenda-empty" hidden>No hay eventos con estos filtros. Prueba otro tipo de actividad o selecciona todos los estados.</p><noscript><p>Activa JavaScript para filtrar; a continuación puedes leer el inventario completo ordenado por fecha.</p></noscript><p class="agenda-export"><a href="/eventos/agenda/inventario.csv" download>Descargar el inventario de eventos (CSV) ↓</a></p></section></main><script src="/assets/event-agenda.js" defer></script>'+footer()
 write('/eventos/agenda/',page)
 # Solo se añade el acceso a la agenda; las seis guías y su diseño se conservan.
 catalog=out/'eventos/index.html';s=catalog.read_text();s=s.replace('<main','<main',1)
 marker='<section class="guide-group"'
 idx=s.find(marker)
 if idx!=-1:
  s=s[:idx]+'<div class="agenda-entry"><p class="kicker">FECHAS · ENTRADAS · INSCRIPCIONES</p><h2>La agenda completa de Punta Arenas.</h2><p>Conciertos, trekking, carreras, festivales, ferias y encuentros. Próximos eventos y calendario anual con sus fuentes.</p><a class="primary" href="/eventos/agenda/">EXPLORAR LA AGENDA →</a></div>'+s[idx:]
 else:raise ValueError('No se encontró el punto de entrada de Eventos')
 s=s.replace('</head>','<link rel="stylesheet" href="/assets/css/event-agenda.css"></head>')
 catalog.write_text(s)
