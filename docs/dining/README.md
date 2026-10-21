# Gastronomía y Vida nocturna · Patagonia Viva

Rama: `revision/gastronomia-vida-nocturna-20261018`. Producción sin cambios.

## Lote consolidado · 21 de octubre de 2026

- 50 fichas gastronómicas y 20 nocturnas construidas para revisión.
- 216 fotografías identificadas, sin coincidencias dHash256 en la revisión realizada.
- 23 locales reúnen al menos cinco fotografías. Las brechas restantes están documentadas, sin rellenar con fotografías genéricas.
- Cuatro locales quedan fuera del catálogo confirmado por ubicación u operación actual no corroborada: La Cafetera, Xiaoyan, Círculo Italiano y Nuevo Siglo. No se afirma que estén cerrados.
- Se incorporó Surista con información oficial de su sede de Punta Arenas.
- No está listo para aprobación final: falta completar fotografías, revisar visualmente escritorio/móvil y comprobar los pines físicos de los mapas.

## Sistema visual

El catálogo conserva el bloque real de estilos de Gastronomía EC. Las fichas usan los componentes de Palace y las proporciones verificadas de ¡Venga! Ipanema: portada de 72vh/62vh en móvil, columnas 1.45fr/.8fr, tarjetas verdes y mapa final. El consejo de Ernestinho se distingue con fondo dorado y texto oscuro. Los ajustes sólo se cargan en las dos secciones.

## Validación

`python3 build.py` compila. `python3 audit_dining.py` no detecta archivos de imagen ausentes, fotografías idénticas por SHA, IDs duplicados, enlaces internos rotos ni discrepancia entre la dirección investigada y la consulta del mapa. Las 122 rutas de la base fuera de ambas secciones coinciden byte a byte. No se simula QA de navegador ni verificación visual de cada pin.

La vista previa de Vercel no pudo verificarse: su conexión devuelve 403 para el equipo Patagonia, que requiere conceder acceso a esa conexión. No se desplegó en producción.

## Inventario y procedencia

`inventory.csv` conserva nombre, categoría, dirección, fotos, extensión y fuentes. `data/dining/photos.json` registra URL original, página, autor cuando se conoce, huella y permisos provisionales pendientes. Los documentos de investigación conservan la fecha y las incertidumbres. La revisión ampliada se realizó el 20 de octubre y los controles locales se repitieron el 21.

## Reproducción

Construir con `python3 build.py`. Los paquetes `dining-photo-assets.zip` y `dining-photo-assets-extra.zip` restauran las imágenes por establecimiento antes de compilar. `prepare_dining.py` es un importador de investigación, no un requisito de compilación.

## Tanda visual adicional

Surista y The Endurance cuentan con una portada del salón y cinco fotografías diferentes entre los textos. Se agregó una foto de la cocina de Dejavu. Se descartaron las variaciones de tamaño, el recorte de un mismo plato, un collage y una ilustración del velero. La importación puede reconstruirse con los documentos versionados y conserva el inventario de fotos aunque no estén las búsquedas temporales. Los paquetes no sobrescriben imágenes ya presentes.
