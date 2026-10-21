"""Catálogo y fichas PUQ con los componentes reales de Gastronomía EC.

Solo escribe /gastronomia/ y /vida-nocturna/. No altera otras rutas.
"""
from pathlib import Path
from urllib.parse import quote
import html
import json
import re
import unicodedata

E = html.escape

def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value)) if not unicodedata.combining(c)).lower()

def render(root, out, site_head, site_footer, write):
    source = root / 'data/dining/venues.json'
    if not source.exists():
        return
    data = json.loads(source.read_text())
    venues = data['venues']
    by_id = {v['id']: v for v in venues}
    photo_manifest = root / 'data/dining/photos.json'
    manifest = json.loads(photo_manifest.read_text()) if photo_manifest.exists() else {'photos': []}
    photos = manifest['photos']

    def images(v):
        return sorted([p for p in photos if p['venue_id'] == v['id'] and p.get('path') and (root / p['path']).is_file() and p.get('verified_subject')], key=lambda p: not p.get('recommended_hero',False))

    def image_tag(p, name, eager=False):
        return '<img src="/' + E(p['path'], quote=True) + '" alt="' + E(p.get('caption') or name, quote=True) + '" width="' + str(p.get('width', 1280)) + '" height="' + str(p.get('height', 850)) + '" loading="' + ('eager' if eager else 'lazy') + '" decoding="async">'

    def figure(p, v, eager=False):
        return '<figure class="inline-photo">' + image_tag(p, v['name'], eager) + (('<figcaption>' + E(p['caption']) + '</figcaption>') if p.get('caption') else '') + '</figure>'

    def researched_date(v):
        raw=v.get('researched_at','2026-10-18')
        year,month,day=raw.split('-')
        months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
        return str(int(day))+' de '+months[int(month)-1]+' de '+year

    def url(v):
        return '/' + v['section'] + '/' + v['slug'] + '/'

    def head(v, detail=False):
        title = v['name'] if detail else v
        description = v['intro'] if detail else ('Restaurantes, cafés y sabores de Punta Arenas.' if v == 'Gastronomía' else 'Bares, cervecerías y noches de Punta Arenas.')
        # El encabezado y pie aprobados de Patagonia se conservan.
        s = site_head(title, description, 'home')
        css = 'dining-detail' if detail else 'dining-catalog'
        s = s.replace('</head>', '<link rel="stylesheet" href="/assets/css/' + css + '.css"><link rel="stylesheet" href="/assets/css/dining-adaptation.css">' + ('<link rel="stylesheet" href="/assets/css/type.css">' if detail else '') + '</head>')
        return s.replace('class="page-home"', 'class="page-home pv-dining ' + ('pv-dining-detail' if detail else 'pv-dining-catalog') + '"')

    def tags(v):
        return '<div class="restaurant-tags">' + ''.join('<span class="tag">' + E(t) + '</span>' for t in v['tags'][:4]) + '</div>'

    def card(v, featured=False):
        pp = images(v)
        media = image_tag(pp[0], v['name']) if pp else ''
        if featured:
            return '<a class="feature-card" href="' + url(v) + '">' + (media or '<div class="feature-image-empty" aria-hidden="true"></div>') + '<div class="feature-copy"><span class="feature-place">' + E(v['sector']) + '</span><h3>' + E(v['name']) + '</h3><p>' + E(v['intro']) + '</p>' + tags(v) + '<span class="restaurant-link">Abrir ficha →</span></div></a>'
        return '<a class="restaurant" href="' + url(v) + '" data-search="' + E(norm(' '.join([v['name'], v['intro'], v['sector'], ' '.join(v['tags'])])), quote=True) + '" data-categories="' + E(' '.join(v['filters']), quote=True) + '" data-neighborhood="' + E(norm(v['sector']), quote=True) + '"><div class="restaurant-media' + ('' if pp else ' restaurant-media--empty') + '">' + media + '</div><div class="restaurant-content"><span class="restaurant-place">' + E(v['sector']) + '</span><h3>' + E(v['name']) + '</h3><p class="restaurant-description">' + E(v['intro']) + '</p>' + tags(v) + '<span class="restaurant-link">Abrir ficha <span aria-hidden="true">→</span></span></div></a>'

    for section in ('gastronomia', 'vida-nocturna'):
        vv = [v for v in venues if v['section'] == section and v['publishable']]
        if not vv:
            continue
        night = section == 'vida-nocturna'
        title = 'Vida nocturna' if night else 'Gastronomía'
        featured = sorted(vv, key=lambda v: (-len(images(v)), v['name']))[:8]
        hero = next((images(v)[0]['path'] for v in featured if images(v)), '')
        s = head(title) + '<main class="gast-shell" id="inicio"><section class="gast-hero"' + ((' style="--gast-hero-image:url(\'/' + E(hero, quote=True) + '\')"') if hero else '') + '><div class="gast-hero-inner"><p class="gast-eyebrow">PATAGONIA VIVA · PUNTA ARENAS</p><h1>' + ('La noche austral.<br><em>A tu manera.</em>' if night else 'Comer Punta Arenas.<br><em>A tu manera.</em>') + '</h1><p class="gast-intro">' + ('Barras, cervezas y música para encontrar tu forma de salir en Punta Arenas. Explora cada propuesta y organiza la vuelta antes de empezar la noche.' if night else 'Centolla, cocina magallánica, mesas de autor y cafés donde detener el viaje. Encuentra un lugar por sector, cocina o momento del día.') + '</p><div class="gast-stats"><span><strong>' + str(len(vv)) + '</strong> establecimientos investigados</span><span><strong>' + str(sum(bool(images(v)) for v in vv)) + '</strong> locales con fotos</span><span>Guía local de Punta Arenas</span></div><a class="gast-cta" href="#catalogo">Explorar la guía <span aria-hidden="true">↓</span></a></div></section>'
        s += '<section class="gast-featured" aria-labelledby="featured-title"><div class="gast-section-heading"><div><p class="gast-eyebrow">UNA PRIMERA SELECCIÓN</p><h2 id="featured-title">' + ('Encuentra tu noche.' if night else 'Punta Arenas tiene muchas mesas.') + '</h2><p>' + ('Pubs, cervecerías, coctelería y música.' if night else 'Sabores del estrecho, cocina local, cafés y dulces.') + '</p></div><div class="carousel-controls"><button type="button" data-carousel-prev aria-label="Ver lugares anteriores">←</button><button type="button" data-carousel-next aria-label="Ver más lugares">→</button></div></div><div class="feature-track" id="gastronomia-carousel" tabindex="0" aria-label="Establecimientos destacados">' + ''.join(card(v, True) for v in featured) + '</div></section>'
        s += '<section class="gast-guide-note"><div><p class="gast-eyebrow">DATO DE ERNESTINHO</p><h2>' + ('Elige el ambiente.<br>Después, la hora.' if night else 'Una buena mesa<br>también es el viaje.') + '</h2></div><p>' + ('Una cervecería, una barra de hotel y un local con música no ofrecen la misma noche. Consulta la programación del día y la hora de cocina, acuerda un transporte de regreso y lleva abrigo aunque el recorrido parezca corto.' if night else 'Yo organizaría el paseo alrededor de la mesa: el centro permite combinar patrimonio y café, mientras que una comida con cordero o centolla merece tiempo propio. Consulta la carta del día y reserva cuando esa comida sea el plan principal.') + '</p></section>'
        sectors = sorted({v['sector'] for v in vv})
        filters = sorted({f for v in vv for f in v['filters']})
        s += '<section class="gast-catalog" id="catalogo" aria-labelledby="catalog-title"><div class="gast-section-heading catalog-heading"><div><p class="gast-eyebrow">EL CATÁLOGO COMPLETO</p><h2 id="catalog-title">Encuentra tu próximo lugar.</h2><p>Información práctica y una ficha propia para cada establecimiento.</p></div><strong class="catalog-total">' + str(len(vv)) + '<span>fichas</span></strong></div><div class="catalog-controls"><label class="search-wrap"><span class="sr-only">Buscar establecimientos</span><input class="search" id="q" type="search" placeholder="Buscar por nombre, sector, cocina o estilo…" autocomplete="off"></label><label class="place-select-label"><span class="sr-only">Filtrar por sector</span><select id="place-filter"><option value="">Todos los sectores</option>' + ''.join('<option value="' + E(norm(x), quote=True) + '">' + E(x) + '</option>' for x in sectors) + '</select></label></div><div class="filters" id="filters" aria-label="Filtrar por propuesta"><button class="filter is-active" data-filter="" type="button" aria-pressed="true">Todos</button>' + ''.join('<button class="filter" type="button" data-filter="' + E(f, quote=True) + '" aria-pressed="false">' + E(data['filter_labels'].get(f, f)) + '</button>' for f in filters) + '</div><p class="count" id="count" aria-live="polite">' + str(len(vv)) + ' de ' + str(len(vv)) + ' fichas visibles</p><div class="restaurant-grid" id="restaurants">' + ''.join(card(v) for v in sorted(vv, key=lambda v: norm(v['name']))) + '</div><p class="no-results" id="empty" hidden>No encontramos un lugar con esa búsqueda. Prueba otra palabra o cambia el filtro.</p></section></main><script src="/assets/dining.js" defer></script>' + site_footer()
        write('/' + section + '/', s)

        for v in vv:
            pp = images(v)
            s = head(v, True) + '<nav class="back" aria-label="Volver al catálogo"><a href="/' + section + '/">← Volver a ' + title + '</a></nav>'
            s += '<header class="hero"' + ((' style="--venue-hero:url(\'/' + E(pp[0]['path'], quote=True) + '\')"') if pp else '') + '><div><div class="ey">Patagonia Viva · ' + E(v['sector']) + '</div><h1>' + E(v['name']) + '</h1><p>' + E(v['intro']) + '</p></div></header><main class="wrap" id="inicio"><div class="tags">' + ''.join('<span class="tag">' + E(t) + '</span>' for t in v['tags']) + '</div><div class="grid"><section class="venue-story" aria-label="Guía del establecimiento">'
            # La portada reutiliza la miniatura del mismo local; las fotos interiores son únicas.
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
            for field, label in [('hours', 'Horarios'), ('price', 'Precios orientativos'), ('accessibility', 'Accesibilidad')]:
                if v.get(field):
                    s += '<p><strong>' + label + '</strong><br>' + E(v[field]) + '</p>'
            for key, label in [('website', 'Sitio oficial'), ('instagram', 'Instagram oficial'), ('reservation', 'Reservas oficiales'), ('whatsapp', 'WhatsApp')]:
                val = contact.get(key)
                if val and val.startswith('https://'):
                    s += '<a class="btn" href="' + E(val, quote=True) + '" target="_blank" rel="noopener noreferrer">' + label + ' ↗</a>'
            if contact.get('phone'):
                tel = re.sub(r'[^\d+]', '', contact['phone'])
                s += '<p><strong>Teléfono</strong><br><a href="tel:' + tel + '">' + E(contact['phone']) + '</a></p>'
            q = quote(v['name'] + ', ' + v['address'] + ', Punta Arenas, Chile')
            s += '<a class="btn" href="https://www.google.com/maps/search/?api=1&amp;query=' + q + '" target="_blank" rel="noopener noreferrer">Cómo llegar ↗</a><p class="venue-date">Información consultada el ' + researched_date(v) + '. Confirma carta, horarios y disponibilidad al reservar.</p></article>'
            other = [x for x in vv if x['id'] != v['id'] and x['sector'] == v['sector']][:3]
            if len(other) < 3:
                other += [x for x in vv if x['id'] != v['id'] and x not in other][:3 - len(other)]
            s += '<article class="card facts"><h2>Sigue explorando</h2>' + ''.join('<p><a href="' + url(x) + '">' + E(x['name']) + ' →</a></p>' for x in other) + '<p><a href="/' + ('gastronomia' if night else 'vida-nocturna') + '/">' + ('Dónde comer' if night else 'Vida nocturna') + ' →</a></p><p><a href="/atracciones/">Atracciones de Punta Arenas →</a></p></article></aside></div>'
            # Ubicación individual al final, como requiere la guía de PUQ.
            s += '<article class="card venue-map"><p class="ey">UBÍCATE</p><h2>Mapa y cómo llegar</h2><p>' + E(v['address']) + ', Punta Arenas.</p><iframe class="map" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Mapa de ' + E(v['name'], quote=True) + '" src="https://www.google.com/maps?q=' + q + '&amp;output=embed"></iframe><a class="btn" href="https://www.google.com/maps/search/?api=1&amp;query=' + q + '" target="_blank" rel="noopener noreferrer">Abrir ubicación en Google Maps ↗</a></article></main>' + site_footer()
            write(url(v), s)
    # Las antiguas fichas no corroboradas dejan de servir datos o fotos dudosos.
    live_routes={url(v) for v in venues if v['publishable']}
    legacy=['/gastronomia/cuatro-estaciones/','/gastronomia/dona-ines/','/vida-nocturna/coyote/','/vida-nocturna/el-trebol/','/vida-nocturna/kamikaze/']
    for route in legacy:
        if route in live_routes:continue
        target='/' + route.strip('/').split('/')[0] + '/'
        write(route,'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url='+target+'"><title>Explorar Punta Arenas | Patagonia Viva</title></head><body><a href="'+target+'">Volver al catálogo de Punta Arenas</a></body></html>')
    print(json.dumps({'dining_rendered': sum(bool(v['publishable']) for v in venues), 'dining_photos': len(photos)}, ensure_ascii=False))
