# Patagonia Viva · Punta Arenas

Plataforma turística independiente de Punta Arenas y Magallanes.

## Construir

```sh
python3 build.py
```

Salida: `dist/`. No requiere paquetes externos para construir.

`content.py` conserva el contenido editorial; `editorial-inventory.json` permite revisar temas y fuentes. Las imágenes son provisionales y su procedencia se conserva en `image-sources.json` y `additional-images.json`. Las fotos de contexto no representan locales específicos.

La primera versión se mantiene fuera de indexación mientras se revisa el contenido. Dos referencias nocturnas necesitan verificar su operación actual. La vinculación automática entre GitHub y Vercel requiere instalar la integración de GitHub en la cuenta de Patagonia.
