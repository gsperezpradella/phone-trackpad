# Phone Trackpad

Usa el teléfono como trackpad del mouse de la laptop. Independiente de otros proyectos.

## Uso
```bash
pip install -r requirements.txt
python server.py            # imprime URL + QR
```
Abre la URL en el teléfono (misma WiFi). El token `?k=` evita que otros en la red controlen tu mouse.

## Gestos
| Gesto | Acción |
|---|---|
| 1 dedo arrastrar | mover cursor |
| toque | clic izquierdo |
| 2 dedos arrastrar | scroll |
| toque con 2 dedos | clic derecho |
| toque con 3 dedos | clic medio |
| toque y enseguida mantener + arrastrar | arrastrar (drag) |
| toque-toque | doble clic |

Botones Izq/Med/Der abajo (mantener = arrastrar). Slider de velocidad arriba.

## Notas
- macOS: dar permiso de *Accesibilidad* a la terminal. Linux: requiere X11 (Wayland limita pynput).
- Opciones: `--port 8765`, `--token miclave`.
- Sin HTTPS: úsalo solo en redes de confianza.
