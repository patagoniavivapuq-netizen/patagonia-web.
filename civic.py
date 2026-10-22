"""Iglesias, Cultura y Familia: componentes y CSS aprobados de Gastronomía/Museos."""
from pathlib import Path
from urllib.parse import quote
import html,json,re,unicodedata
E=html.escape
def norm(value):
 return ''.join(c for c in unicodedata.normalize('NFKD',str(value))if not unicodedata.combining(c)).lower()
def render(root,out,site_head,site_footer,write):
    source=root/'data/civic/venues.json'
    if not source.exists():return
    venues=json.loads(source.read_text())['venues']
    photos=json.loads((root/'data/civic/photos.json').read_text())['photos']
    museum_data=json.loads((root/'data/museums/venues.json').read_text())['venues']
    museum_photos=json.loads((root/'data/museums/photos.json').read_text())['photos']
    # One canonical fiche per place, linked from more than one thematic catalogue.
    for v in venues:
        v['catalog_route']='/familia/' if v['section']=='familia' else '/cultura/'+v['group']+'/'
        v['catalog_title']={'iglesias':'Iglesias','centros-culturales':'Centros culturales','bibliotecas':'Bibliotecas','cines':'Cines','familia':'Familia'}[v['group']]
    for v in museum_data:v['filters']=['museos']
    photos+=museum_photos
    data={'filter_labels':{'iglesias':'Iglesias','centros-culturales':'Centros culturales','bibliotecas':'Bibliotecas','cines':'Cines','familia':'Juegos y aire libre','museos':'Museos y patrimonio'}}
    def images(v):
        return sorted([p for p in photos if p['venue_id'] == v['id'] and p.get('path') and (root / p['path']).is_file() and p.get('verified_subject')], key=lambda p: not p.get('recommended_hero',False))

    def image_tag(p, name, eager=False):
        return '<img src="/' + E(p['path'], quote=True) + '" alt="' + E(p.get('caption') or name, quote=True) + '" width="' + str(p.get('width', 1280)) + '" height="' + str(p.get('height', 850)) + '" loading="' + ('eager' if eager else 'lazy') + '" decoding="async">'

    def figure(p, v, eager=False):
        # No ampliar originales pequeños hasta volverlos borrosos.
        size = (' style="max-width:' + str(p['width']) + 'px;margin-inline:auto"') if p.get('width', 1280) < 750 else ''
        caption = E(p.get('caption', ''))
        if p.get('license_url') and p.get('source_page'):
            caption += ' Foto: <a href="' + E(p['source_page'], quote=True) + '" target="_blank" rel="noopener noreferrer">' + E(p['author']) + '</a> · <a href="' + E(p['license_url'], quote=True) + '" target="_blank" rel="noopener noreferrer">' + E(p['license']) + '</a>.'
        return '<figure class="inline-photo"' + size + '>' + image_tag(p, v['name'], eager) + (('<figcaption>' + caption + '</figcaption>') if caption else '') + '</figure>'

    def researched_date(v):
        raw=v.get('researched_at','2026-10-18')
        year,month,day=raw.split('-')
        months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
        return str(int(day))+' de '+months[int(month)-1]+' de '+year

    def url(v):
        return '/' + v['section'] + '/' + v['slug'] + '/'

    def head(v, detail=False):
        title = v['name'] if detail else v
        description = v['intro'] if detail else 'Iglesias, cultura y panoramas familiares de Punta Arenas: fotografías, experiencia, contactos y mapas.'
        # El encabezado y pie aprobados de Patagonia se conservan.
        s = site_head(title, description, 'home')
        css = 'dining-detail' if detail else 'dining-catalog'
        s = s.replace('</head>', '<link rel="stylesheet" href="/assets/css/' + css + '.css"><link rel="stylesheet" href="/assets/css/dining-adaptation.css">' + ('<link rel="stylesheet" href="/assets/css/type.css">' if detail else '') + '</head>')
        s=s.replace('</head>','<style>.pv-civic.pv-dining-detail .hero>div{position:relative;z-index:2}</style></head>')
        return s.replace('class="page-home"', 'class="page-home pv-civic pv-dining ' + ('pv-dining-detail' if detail else 'pv-dining-catalog') + '"')

    def tags(v):
        return '<div class="restaurant-tags">' + ''.join('<span class="tag">' + E(t) + '</span>' for t in v['tags'][:4]) + '</div>'

    def card(v, featured=False):
        pp = images(v)
        media = image_tag(pp[0], v['name']) if pp else ''
        if featured:
            return '<a class="feature-card" href="' + url(v) + '">' + (media or '<div class="feature-image-empty" aria-hidden="true"></div>') + '<div class="feature-copy"><span class="feature-place">' + E(v['sector']) + '</span><h3>' + E(v['name']) + '</h3><p>' + E(v['intro']) + '</p>' + tags(v) + '<span class="restaurant-link">Abrir ficha →</span></div></a>'
        return '<a class="restaurant" href="' + url(v) + '" data-search="' + E(norm(' '.join([v['name'], v['intro'], v['sector'], ' '.join(v['tags'])])), quote=True) + '" data-categories="' + E(' '.join(v['filters']), quote=True) + '" data-neighborhood="' + E(norm(v['sector']), quote=True) + '"><div class="restaurant-media' + ('' if pp else ' restaurant-media--empty') + '">' + media + '</div><div class="restaurant-content"><span class="restaurant-place">' + E(v['sector']) + '</span><h3>' + E(v['name']) + '</h3><p class="restaurant-description">' + E(v['intro']) + '</p>' + tags(v) + '<span class="restaurant-link">Abrir ficha <span aria-hidden="true">→</span></span></div></a>'

    catalogs=[
     ('/cultura/','Cultura','La ciudad también.<br><em>Se cuenta así.</em>','Iglesias, museos, cines, escenarios y bibliotecas: descubre las historias y la creación de Punta Arenas.',[v for v in venues if v['section']=='cultura']+museum_data,['catedral','auxiliadora','centro-cultural','teatro','cine-estrella','biblioteca-mistral']),
     ('/cultura/iglesias/','Iglesias','Memoria y comunidad.<br><em>Puertas adentro.</em>','Templos y santuarios para comprender la vida religiosa y los barrios de Punta Arenas. Visitas respetuosas, contactos y ubicación propia.',[v for v in venues if v['group']=='iglesias'],['catedral','auxiliadora','san-miguel','nazareno']),
     ('/cultura/centros-culturales/','Centros culturales','Lo que se crea.<br><em>Lo que se comparte.</em>','Escenarios, exposiciones y espacios de formación. Revisa qué ocurre en cada sede antes de organizar la salida.',[v for v in venues if v['group']=='centros-culturales'],['centro-cultural','teatro','sala-zonaustral','casa-azul']),
     ('/cultura/bibliotecas/','Bibliotecas','Abrir un libro.<br><em>Mirar Magallanes.</em>','Lectura, memoria y consulta: dos bibliotecas con identidad y direcciones propias. Los traslados de sede también forman parte de esta guía.',[v for v in venues if v['group']=='bibliotecas'],['biblioteca-mistral','biblioteca-viel']),
     ('/cultura/cines/','Cines','Una pausa.<br><em>En pantalla grande.</em>','Los dos cines de Punta Arenas, con sus ubicaciones y canales de cartelera. Elige ciudad, función e idioma antes de comprar.',[v for v in venues if v['group']=='cines'],['cine-estrella','cine-star']),
     ('/familia/','En familia','Juntos en el sur.<br><em>A nuestro ritmo.</em>','Karting, bowling, hielo, juegos, cine, parques, lectura y museos. Lugares concretos para elegir por edades, clima y ganas de compartir.',[v for v in venues if v.get('family')]+[v for v in museum_data if v['id']in ['borgatello','nao','rio-seco','recuerdo','naval','estrecho','inach','keu-ken']],['bowling','hielo','fun-times','parque-costanera','cine-estrella','karting'])]
    for route,title,headline,description,vv,priority in catalogs:
        featured=sorted(vv,key=lambda v:priority.index(v['id'])if v['id']in priority else len(priority))[:6]
        hero=next((images(v)[0]['path']for v in featured if images(v)),'')
        s=head(title)+'<main class="gast-shell" id="inicio"><section class="gast-hero"'+((' style="--gast-hero-image:url(\'/' + E(hero,quote=True)+'\')"')if hero else '')+'><div class="gast-hero-inner"><p class="gast-eyebrow">PATAGONIA VIVA · PUNTA ARENAS</p><h1>'+headline+'</h1><p class="gast-intro">'+E(description)+'</p><div class="gast-stats"><span><strong>'+str(len(vv))+'</strong> lugares con ficha propia</span><span>Direcciones · Consejos · Mapas</span></div><a class="gast-cta" href="#catalogo">Explorar la guía ↓</a></div></section>'
        s+='<section class="gast-featured"><div class="gast-section-heading"><div><p class="gast-eyebrow">PARA EMPEZAR</p><h2>Elige tu próxima salida.</h2><p>'+E(description)+'</p></div><div class="carousel-controls"><button type="button" data-carousel-prev aria-label="Ver lugares anteriores">←</button><button type="button" data-carousel-next aria-label="Ver más lugares">→</button></div></div><div class="feature-track" id="gastronomia-carousel" tabindex="0">'+''.join(card(v,True)for v in featured)+'</div></section>'
        s+='<section class="gast-guide-note"><div><p class="gast-eyebrow">EXPLORA A TU MANERA</p><h2>Una ciudad.<br>Muchas historias.</h2></div><div>'+''.join('<p><a href="'+u+'">'+t+' →</a></p>'for u,t in [('/cultura/museos/','Museos y patrimonio'),('/cultura/iglesias/','Iglesias'),('/cultura/centros-culturales/','Centros culturales y teatro'),('/cultura/cines/','Cines'),('/cultura/bibliotecas/','Bibliotecas'),('/familia/','En familia')])+'</div></section>'
        if route=='/familia/':s+='<section class="gast-guide-note"><div><p class="gast-eyebrow">DATO DE ERNESTINHO</p><h2>Una actividad.<br>Tiempo para disfrutar.</h2></div><p>Yo escogería un panorama principal y dejaría una alternativa cubierta por si cambia el clima. Revisa las estaturas para karting, la reserva de los juegos privados y el acceso a parques con obras. Cine y museos conservan una sola ficha, aunque aparezcan en más de una sección.</p></section>'
        sectors=sorted({v['sector']for v in vv});filters=sorted({f for v in vv for f in v['filters']})
        s+='<section class="gast-catalog" id="catalogo"><div class="gast-section-heading catalog-heading"><div><p class="gast-eyebrow">EL CATÁLOGO COMPLETO</p><h2>'+E(title)+', lugar por lugar.</h2><p>Abre la ficha para conocer la experiencia, las condiciones de visita, los contactos y el mapa.</p></div><strong class="catalog-total">'+str(len(vv))+'<span>fichas</span></strong></div><div class="catalog-controls"><label class="search-wrap"><span class="sr-only">Buscar lugares</span><input class="search" id="q" type="search" placeholder="Buscar por lugar, sector o experiencia…" autocomplete="off"></label><label class="place-select-label"><span class="sr-only">Filtrar por sector</span><select id="place-filter"><option value="">Todos los sectores</option>'+''.join('<option value="'+E(norm(x),quote=True)+'">'+E(x)+'</option>'for x in sectors)+'</select></label></div><div class="filters" id="filters"><button class="filter is-active" data-filter="" type="button" aria-pressed="true">Todos</button>'+''.join('<button class="filter" data-filter="'+E(f,quote=True)+'" type="button" aria-pressed="false">'+E(data['filter_labels'].get(f,f))+'</button>'for f in filters)+'</div><p class="count" id="count" aria-live="polite">'+str(len(vv))+' de '+str(len(vv))+' fichas visibles</p><div class="restaurant-grid" id="restaurants">'+''.join(card(v)for v in sorted(vv,key=lambda v:norm(v['name'])))+'</div><p class="no-results" id="empty" hidden>No encontramos un lugar con esa búsqueda. Prueba otra palabra o cambia el filtro.</p></section></main><script src="/assets/dining.js" defer></script>'+site_footer()
        write(route,s)
    # Only new civic fiches are rendered; existing museum fiches remain untouched.
    vv=venues
    if vv:
        for v in vv:
            pp = images(v)
            s = head(v, True) + '<nav class="back" aria-label="Volver al catálogo"><a href="' + E(v['catalog_route']) + '">← Volver a ' + E(v['catalog_title']) + '</a></nav>'
            s += '<header class="hero"' + ((' style="--venue-hero:url(\'/' + E(pp[0]['path'], quote=True) + '\')"') if pp else '') + '><div><div class="ey">Patagonia Viva · ' + E(v['sector']) + '</div><h1>' + E(v['name']) + '</h1><p>' + E(v['intro']) + '</p></div></header><main class="wrap" id="inicio"><div class="tags">' + ''.join('<span class="tag">' + E(t) + '</span>' for t in v['tags']) + '</div><div class="grid"><section class="venue-story" aria-label="Guía del lugar">'
            # La portada reutiliza la miniatura del mismo local; las fotos interiores son únicas.
            if v.get('status'):s += '<article class="card facts"><h2>Antes de ir</h2><p>'+E(v['status'])+'</p></article>'
            available = pp[1:] if pp else []
            sections = v['sections']
            insertions = {}
            for i, p in enumerate(available):
                at = min(len(sections) - 1, max(0, round((i + 1) * len(sections) / (len(available) + 1)) - 1))
                insertions.setdefault(at, []).append(p)
            for i, block in enumerate(sections):
                is_tip = 'dato' in block['title'].lower() or 'consejo' in block['title'].lower()
                s += '<article class="card' + (' venue-tip' if is_tip else '') + '"><p class="ey">' + str(i + 1).zfill(2) + '</p><h2>' + E('Dato de Ernestinho' if is_tip else block['title']) + '</h2>' + ''.join('<p>' + E(p) + '</p>' for p in block['paragraphs']) + '</article>'
                for p in insertions.get(i, []):
                    s += figure(p, v)
            s += '</section><aside><article class="card facts"><h2>Información práctica</h2><p><strong>Dirección</strong><br>' + E(v['address']) + '</p><p><strong>Sector</strong><br>' + E(v['sector']) + '</p><p><strong>Propuesta</strong><br>' + E(', '.join(v['tags'])) + '</p>'
            contact = v['contacts']
            for field, label in [('hours', 'Horarios'), ('price', 'Entrada y precios'), ('accessibility', 'Accesibilidad'), ('status', 'Estado de visita')]:
                if v.get(field):
                    s += '<p><strong>' + label + '</strong><br>' + E(v[field]) + '</p>'
            for key, label in [('website', 'Sitio oficial'), ('information', 'Información institucional'), ('instagram', 'Instagram oficial'), ('reservation', 'Reservas oficiales'), ('whatsapp', 'WhatsApp'), ('facebook', 'Facebook'), ('virtual', 'Recorrido virtual'), ('guide', 'Guía y plano oficial')]:
                val = contact.get(key)
                if val and val.startswith('https://'):
                    s += '<a class="btn" href="' + E(val, quote=True) + '" target="_blank" rel="noopener noreferrer">' + label + ' ↗</a>'
            if contact.get('phone'):
                tel = re.sub(r'[^\d+]', '', contact['phone'])
                s += '<p><strong>Teléfono</strong><br><a href="tel:' + tel + '">' + E(contact['phone']) + '</a></p>'
            if contact.get('phone2'):
                tel2 = re.sub(r'[^\d+]', '', contact['phone2'])
                s += '<p><strong>Otro teléfono</strong><br><a href="tel:' + tel2 + '">' + E(contact['phone2']) + '</a></p>'
            if contact.get('email'):
                s += '<p><strong>Correo</strong><br><a href="mailto:' + E(contact['email'], quote=True) + '">' + E(contact['email']) + '</a></p>'
            q = quote(v.get('map_query') or v['name'] + ', ' + v['address'] + ', Punta Arenas, Chile')
            s += '<a class="btn" href="https://www.google.com/maps/search/?api=1&amp;query=' + q + '" target="_blank" rel="noopener noreferrer">Cómo llegar ↗</a><p class="venue-date">Información consultada el ' + researched_date(v) + '. Confirma apertura, entrada y condiciones antes de la visita.</p></article>'
            other = [x for x in vv if x['id'] != v['id'] and x['sector'] == v['sector']][:3]
            if len(other) < 3:
                other += [x for x in vv if x['id'] != v['id'] and x not in other][:3 - len(other)]
            s += '<article class="card facts"><h2>Sigue explorando</h2>' + ''.join('<p><a href="' + url(x) + '">' + E(x['name']) + ' →</a></p>' for x in other) + '<p><a href="/gastronomia/">Dónde comer →</a></p><p><a href="/transportes/">Cómo moverse →</a></p><p><a href="/atracciones/">Atracciones de Punta Arenas →</a></p></article></aside></div>'
            # Ubicación individual al final, como requiere la guía de PUQ.
            s += '<article class="card venue-map"><p class="ey">UBÍCATE</p><h2>Mapa y cómo llegar</h2><p>' + E(v.get('map_note') or v['address']) + '</p><iframe class="map" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Mapa de ' + E(v['name'], quote=True) + '" src="https://www.google.com/maps?q=' + q + '&amp;output=embed"></iframe><a class="btn" href="https://www.google.com/maps/search/?api=1&amp;query=' + q + '" target="_blank" rel="noopener noreferrer">Abrir ubicación en Google Maps ↗</a></article></main>' + site_footer()
            write(url(v), s)
    print(json.dumps({'civic_rendered':len(venues),'civic_photos':len(photos)-len(museum_photos)},ensure_ascii=False))
