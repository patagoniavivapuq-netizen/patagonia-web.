# Gastronomía y Vida nocturna · Patagonia Viva

Rama: `revision/gastronomia-vida-nocturna-20261018`. Producción sin cambios.

## Estado de esta tanda

- 51 fichas gastronómicas y 20 nocturnas construidas para revisión.
- 153 fotografías identificadas; 16 locales reúnen cinco imágenes.
- La Cafetera y Xiaoyan quedan fuera del catálogo confirmado por discrepancias de ubicación.
- Las fichas todavía requieren ampliación editorial y completar la biblioteca visual. No están listas para aprobación final.

## Referencia y alcance

El CSS del catálogo se extrajo del primer bloque inline de la página real de Gastronomía EC. Las fichas conservan el primer bloque de estilos de Palace, sustituyendo únicamente la URL de portada por una variable local. Las adaptaciones se cargan solo en Gastronomía y Vida nocturna. Los consejos llevan un recuadro dorado con texto verde oscuro y el mapa aparece al final de cada ficha.

## Validación

`python3 build.py` compila. `python3 audit_dining.py` no detecta archivos de imagen ausentes, fotografías idénticas por SHA, IDs duplicados, enlaces internos rotos ni discrepancia entre la dirección investigada y la consulta del mapa. Las 122 rutas de la base fuera de ambas secciones coinciden byte a byte. La auditoría no equivale a comprobar visualmente cada pin ni la adaptación móvil: ambas revisiones permanecen pendientes.

## Inventario y procedencia

`inventory.csv` conserva nombre, categoría, dirección, cantidad de imágenes y brechas. `data/dining/photos.json` registra URL de imagen y página original, autor cuando se conoce, huella y permisos provisionales. No se atribuye autorización comercial a las imágenes de terceros. Los datos consultados el 18 de octubre conservan esa fecha; los nuevos hallazgos se registran por separado.

## Reproducción

Construir con `python3 build.py`. El paquete `dining-photo-assets.zip` restaura las imágenes por establecimiento antes de la compilación. `prepare_dining.py` requiere los documentos de investigación en la carpeta superior y es una herramienta de importación, no un requisito para construir el repositorio.
