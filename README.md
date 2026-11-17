# PRECIOS

Web para consultar a cuánto se venden los productos en la comunidad de reventa y a cuánto se pueden comprar.

- **Se vende**: la mediana de las ventas registradas de cada producto.
- **Compra hasta**: ese precio menos el margen que elijas (por defecto 40 €).
- Secciones por categoría, buscador y calculadora de "¿te lo ofrecen a X?".
- Se instala en la pantalla de inicio (Safari → Compartir → Añadir a pantalla de inicio) y funciona sin conexión con los últimos datos.

## Datos

Los datos van cifrados en `data.enc.json` (AES-GCM, clave derivada de la contraseña con PBKDF2-SHA256). La web los descifra en el propio dispositivo; sin la contraseña no se pueden leer. Los datos en claro nunca se suben al repositorio.

`tools/precios.py` cifra y descifra los datos:

```
PRECIOS_PASS='...' python3 tools/precios.py decrypt data.enc.json ventas.json
PRECIOS_PASS='...' python3 tools/precios.py encrypt ventas.json data.enc.json
```

Formato de `ventas.json`: `cats` (categorías en orden), `products` (id, categoría, nombre, alias para el buscador) y `sales` (producto, precio, fecha ISO opcional, nota, origen).

Fuentes: Barlow y Barlow Condensed (SIL Open Font License, ver `fonts/OFL.txt`).
