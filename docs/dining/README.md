# Gastronomía y Vida nocturna · Patagonia Viva

Rama: `revision/gastronomia-vida-nocturna-20261018`. Última producción autorizada: commit `9e5153a`. Esta tanda visual se conserva en la misma rama y requiere revisión en vista previa.

## Lote consolidado · 21 de octubre de 2026

- 50 fichas gastronómicas y 20 nocturnas construidas para revisión.
- 359 fotografías identificadas, sin coincidencias dHash256 en la revisión realizada.
- 45 locales reúnen al menos cinco fotografías. Las brechas restantes están documentadas, sin rellenar con fotografías genéricas.
- Cuatro locales quedan fuera del catálogo confirmado por ubicación u operación actual no corroborada: La Cafetera, Xiaoyan, Círculo Italiano y Nuevo Siglo. No se afirma que estén cerrados.
- Se incorporó Surista con información oficial de su sede de Punta Arenas.
- No está listo para aprobación final: falta completar fotografías, revisar visualmente escritorio/móvil y comprobar los pines físicos de los mapas.

## Sistema visual

El catálogo conserva el bloque real de estilos de Gastronomía EC. Las fichas usan los componentes de Palace y las proporciones verificadas de ¡Venga! Ipanema: portada de 72vh/62vh en móvil, columnas 1.45fr/.8fr, tarjetas verdes y mapa final. El consejo de Ernestinho se distingue con fondo dorado y texto oscuro. Los ajustes sólo se cargan en las dos secciones.

## Validación

`python3 build.py` compila. `python3 audit_dining.py` no detecta archivos de imagen ausentes, fotografías idénticas por SHA, IDs duplicados, enlaces internos rotos ni discrepancia entre la dirección investigada y la consulta del mapa. Las 122 rutas de la base fuera de ambas secciones coinciden byte a byte. No se simula QA de navegador ni verificación visual de cada pin.

El repositorio quedó conectado al proyecto Vercel `patagonia-viva-puq`. El commit `9e5153a` fue verificado en vista previa y publicado en producción por autorización explícita del usuario. La tanda de fotografías posterior se verifica por separado.

## Inventario y procedencia

`inventory.csv` conserva nombre, categoría, dirección, fotos, extensión y fuentes. `data/dining/photos.json` registra URL original, página, autor cuando se conoce, huella y permisos provisionales pendientes. Los documentos de investigación conservan la fecha y las incertidumbres. La revisión ampliada se realizó el 20 de octubre y los controles locales se repitieron el 21.

## Reproducción

Construir con `python3 build.py`. Los paquetes versionados `dining-photo-assets*.zip` restauran las imágenes por establecimiento antes de compilar. `prepare_dining.py` es un importador de investigación, no un requisito de compilación.

## Tanda visual adicional

Surista y The Endurance cuentan con una portada del salón y cinco fotografías diferentes entre los textos. Se agregó una foto de la cocina de Dejavu. Se descartaron las variaciones de tamaño, el recorte de un mismo plato, un collage y una ilustración del velero. La importación puede reconstruirse con los documentos versionados y conserva el inventario de fotos aunque no estén las búsquedas temporales. Los paquetes no sobrescriben imágenes ya presentes.

## Afinación de fotografías · Café Sarmiento y locales pendientes

175 imágenes nuevas revisadas; 32 piezas retiradas por anuncios, capturas, oscuridad añadida o dibujos superpuestos. Café Sarmiento dispone de portada del salón con vista al Estrecho y cinco fotos distintas intercaladas. Se preservan 359 fotos en 70 fichas; 45 locales reúnen al menos cinco fotos. `photo-gaps-current.json` mantiene la lista exacta de brechas para completar seis fotos por local. No se declara finalizada la biblioteca. Los candidatos inaccesibles o dudosos de Casa Jelva, Sky Bar y otros locales no se reemplazan por stock. El Árbol requiere corroborar operación actual tras la noticia de incendio.
