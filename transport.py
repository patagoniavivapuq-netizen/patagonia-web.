"""Render de Transportes; reutiliza el HTML y las clases editoriales existentes."""
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
import html
import json

from transport_content import CHECKED, PAGES, SOURCES

E = html.escape
STYLE = '''<style>
.pv-transport .items article p+p{margin-top:1em}
.pv-transport .transport-table-wrap{max-width:100%;overflow-x:auto;margin:24px 0;border:1px solid #c6d5cf;border-radius:12px;background:#fff;color:#173d39}
.pv-transport table{border-collapse:collapse;width:100%;font:400 15px/1.55 var(--sans)}
.pv-transport caption{text-align:left;padding:16px;font-weight:700;color:#173d39}
.pv-transport th{background:#113b36;color:#fff;text-align:left;font-weight:700}
.pv-transport td,.pv-transport th{padding:14px 16px;border-bottom:1px solid #dce5e2;vertical-align:top;min-width:130px}
.pv-transport tr:last-child td{border-bottom:0}.pv-transport tbody tr:nth-child(even){background:#eff5f2}
.pv-transport .transport-links{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0 0}
.pv-transport .transport-links a{display:inline-block;border:1px solid #d7a43b;border-radius:12px;padding:12px 16px;background:#103c37;color:#fff;font:700 13px/1.5 var(--sans);text-decoration:none}
.pv-transport .transport-links a:hover{background:#18564e}.pv-transport .transport-links a:focus-visible{outline:3px solid #d7a43b;outline-offset:3px}
.pv-transport .transport-note{margin-top:16px!important;padding:15px 18px;border-left:3px solid #d7a43b;background:#fff8e8;color:#61461a;font-size:14px}
.pv-transport .transport-map{border:0;width:100%;height:340px;border-radius:14px;background:#e7eeeb}
.pv-transport .transport-map-label{font:600 15px/1.6 var(--sans);margin:22px 0 10px;color:#173d39}
.pv-transport .transport-map-photo img{object-fit:contain;aspect-ratio:auto;background:#e7eeeb}
.pv-transport .transport-nav{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:28px 0;color:#17423c;font-size:14px}
.pv-transport .transport-nav a{text-decoration:underline;text-underline-offset:4px}
.pv-transport .ec-inline-photo img{max-width:100%}
@media(max-width:600px){.pv-transport table{font-size:13px}.pv-transport td,.pv-transport th{padding:11px;min-width:115px}.pv-transport .transport-map{height:280px}.pv-transport .transport-links a{width:100%}}
</style>'''

def link_buttons(keys):
 return '<div class="transport-links">'+''.join('<a href="'+E(SOURCES[k][1],quote=True)+'" target="_blank" rel="noopener noreferrer">'+E(SOURCES[k][0])+' ↗</a>' for k in keys)+'</div>'

def render(root, out, head, footer, write):
 catalog=json.loads((root/'photo-catalog.json').read_text())
 additions=json.loads((root/'data/transport/photos.json').read_text())['photos']
 photos={key:dict(row) for key,row in catalog.items()}
 photos.update({row['id']:dict(row) for row in additions})
 for row in PAGES:
  assert row['hero'] in photos, 'Fotografía no registrada: '+row['hero']

 def image(key, priority=False):
  p=photos[key]
  caption=p['caption'].replace(' Fotografía de TABSA.','')
  if key=='taxi-candidato':caption='Taxis en el acceso aeroportuario de Punta Arenas.'
  if key=='dap-regional':caption='Conexión aérea Punta Arenas–Puerto Williams publicada por DAP.'
  css='ec-inline-photo'+(' transport-map-photo' if key.startswith('mapa-') or key=='dap-regional' else '')
  return '<figure class="'+css+'"><img src="/'+E(p['path'],quote=True)+'" alt="'+E(caption,quote=True)+'" width="'+str(p['width'])+'" height="'+str(p['height'])+'" '+('fetchpriority="high"' if priority else 'loading="lazy"')+'><figcaption>'+E(caption)+'</figcaption></figure>'

 def title_head(title, intro, kind):
  return head(title,intro,kind).replace('</head>',STYLE+'</head>')

 groups=defaultdict(list)
 for row in PAGES:groups[row['group']].append(row)
 intro='Micros, colectivos, aplicaciones, aeropuerto y cruces del Estrecho. Elige cómo moverte y prepara cada tramo con información práctica.'
 category=title_head('Transportes',intro,'category')+'<main class="pv-transport" id="inicio"><section class="hero category-hero"><div class="hero-copy"><p class="kicker">PATAGONIA VIVA · PUNTA ARENAS</p><h1>Transportes.</h1><p class="lead">'+E(intro)+'</p></div></section>'
 category+='<div class="category-controls"><a href="/">← Inicio</a><span>'+str(len(PAGES))+' guías para moverte</span><label class="search-label">Buscar en esta sección<input type="search" data-filter placeholder="Escribe un tema…" autocomplete="off"></label></div>'
 for group,rows in groups.items():
  category+='<section class="guide-group"><h2>'+E(group)+'</h2><div class="guide-grid">'
  for row in rows:
   p=photos[row['hero']]
   category+='<a href="/transportes/'+row['slug']+'/"><img class="guide-thumb" src="/'+E(p['path'],quote=True)+'" alt="'+E(row['title'],quote=True)+'" loading="lazy" width="640" height="420"><b>'+E(row['title'])+'</b><span>ABRIR GUÍA →</span></a>'
  category+='</div></section>'
 category+='<p class="empty-results" hidden>No encontramos ese tema. Prueba otra palabra.</p></main>'+footer()
 write('/transportes/',category)

 for index,row in enumerate(PAGES):
  page=title_head(row['title'],row['intro'],'article')+'<main class="guide pv-transport" id="inicio"><div class="breadcrumbs"><a href="/">Inicio</a><span> / </span><a href="/transportes/">Transportes</a></div><p class="kicker">'+E(row['group'])+'</p><h1>'+E(row['title'])+'</h1>'
  page+=image(row['hero'],True)+'<p class="article-intro">'+E(row['intro'])+'</p><p class="status-note">Información revisada el '+CHECKED+'. Horarios, tarifas y disponibilidad pueden cambiar; consulta el servicio para tu fecha.</p>'
  page+='<nav class="transport-nav" aria-label="Contenido de esta guía">'+''.join('<a href="#tema-'+str(i)+'">'+str(i).zfill(2)+' · '+E(section['title'])+'</a>' for i,section in enumerate(row['sections'],1))+'</nav><section class="items">'
  for i,section in enumerate(row['sections'],1):
   page+='<article id="tema-'+str(i)+'"><span>'+str(i).zfill(2)+'</span><h2>'+E(section['title'])+'</h2>'
   page+=''.join('<p>'+E(p)+'</p>' for p in section['paragraphs'])
   if section['rows']:
    page+='<div class="transport-table-wrap" tabindex="0" role="region" aria-label="'+E(section['title'],quote=True)+'"><table><caption>'+E(section['title'])+'</caption><thead><tr>'+''.join('<th scope="col">'+E(c)+'</th>' for c in section['columns'])+'</tr></thead><tbody>'
    for cells in section['rows']:page+='<tr>'+''.join('<td>'+E(c)+'</td>' for c in cells)+'</tr>'
    page+='</tbody></table></div>'
   if section['note']:page+='<p class="transport-note">'+E(section['note'])+'</p>'
   if section['links']:page+=link_buttons(section['links'])
   page+='</article>'
   for after,key in row.get('inline',[]):
    if i==after:page+=image(key)
  page+='</section><aside class="tip"><b>Dato Austral</b><p>'+E(row['tip'])+'</p></aside>'
  page+='<section class="map-section"><h2>Ubicaciones para tu viaje</h2><p>Los mapas identifican los puntos indicados; no representan un recorrido de micro o colectivo en vivo.</p>'
  for label,query in row['maps']:
   page+='<h3 class="transport-map-label">'+E(label)+'</h3><iframe class="transport-map" title="'+E(label,quote=True)+'" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q='+quote(query,safe='')+'&amp;output=embed" allowfullscreen></iframe><div class="transport-links"><a href="https://www.google.com/maps/search/?api=1&amp;query='+quote(query,safe='')+'" target="_blank" rel="noopener noreferrer">Abrir ubicación en Google Maps ↗</a></div>'
  page+='</section><details class="official-links"><summary>Enlaces para planificar y comprobar los datos</summary><p>Consulta al operador para la fecha concreta de tu viaje.</p><ul>'+''.join('<li><a href="'+E(SOURCES[k][1],quote=True)+'" target="_blank" rel="noopener noreferrer">'+E(SOURCES[k][0])+' ↗</a></li>' for k in row['sources'])+'</ul></details>'
  related=[p for p in PAGES if p['slug']!=row['slug'] and p['group']==row['group']][:3]
  if len(related)<3:related += [p for p in PAGES if p['slug']!=row['slug'] and p not in related][:3-len(related)]
  page+='<section class="related"><p class="kicker">SIGUE EXPLORANDO</p><h2>También te puede servir</h2><div class="related-grid">'+''.join('<a href="/transportes/'+p['slug']+'/">'+E(p['title'])+' <span>→</span></a>' for p in related)+'</div></section><nav class="transport-nav" aria-label="Navegar entre guías">'
  if index:page+='<a href="/transportes/'+PAGES[index-1]['slug']+'/">← Guía anterior</a>'
  page+='<a href="/transportes/">Volver a Transportes</a>'
  if index+1<len(PAGES):page+='<a href="/transportes/'+PAGES[index+1]['slug']+'/">Guía siguiente →</a>'
  page+='</nav></main>'+footer()
  write('/transportes/'+row['slug']+'/',page)
 print(json.dumps({'transport_guides':len(PAGES),'transport_reviewed':CHECKED},ensure_ascii=False))
