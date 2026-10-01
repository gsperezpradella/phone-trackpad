"""Phone Trackpad: usa el teléfono como trackpad de esta laptop.

Uso: python server.py [--port 8765]
Abre en el teléfono la URL (o QR) que se imprime; misma red WiFi.
"""
import argparse
import asyncio
import hmac
import json
import secrets
import socket
from pathlib import Path

from aiohttp import WSMsgType, web
from pynput.mouse import Button, Controller

STATIC = Path(__file__).parent / "static"
BUTTONS = {"left": Button.left, "right": Button.right, "middle": Button.middle}
MAX_DELTA = 500  # límite por mensaje, evita saltos absurdos

mouse = Controller()


def clamp(v):
    try:
        return max(-MAX_DELTA, min(MAX_DELTA, int(round(float(v)))))
    except (TypeError, ValueError):
        return 0


def handle(msg):
    t = msg.get("t")
    if t == "move":
        mouse.move(clamp(msg.get("dx")), clamp(msg.get("dy")))
    elif t == "scroll":
        mouse.scroll(clamp(msg.get("dx")), clamp(msg.get("dy")))
    elif t in ("click", "down", "up"):
        b = BUTTONS.get(msg.get("b"))
        if b is None:
            return
        if t == "click":
            mouse.click(b, 2 if msg.get("n") == 2 else 1)
        elif t == "down":
            mouse.press(b)
        else:
            mouse.release(b)


async def ws_handler(request):
    if not hmac.compare_digest(request.query.get("k", ""), request.app["token"]):
        raise web.HTTPForbidden()
    ws = web.WebSocketResponse(heartbeat=15)
    await ws.prepare(request)
    held = set()
    try:
        async for m in ws:
            if m.type != WSMsgType.TEXT:
                continue
            try:
                msg = json.loads(m.data)
                if msg.get("t") == "down":
                    held.add(msg.get("b"))
                elif msg.get("t") == "up":
                    held.discard(msg.get("b"))
                handle(msg)
            except (ValueError, AttributeError):
                continue
    finally:
        for b in held:  # no dejar botones pegados si se corta la conexión
            if b in BUTTONS:
                mouse.release(BUTTONS[b])
    return ws


async def index(request):
    if not hmac.compare_digest(request.query.get("k", ""), request.app["token"]):
        raise web.HTTPForbidden(text="Token inválido. Usa la URL impresa en la laptop.")
    return web.FileResponse(STATIC / "index.html")


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--token", default=None, help="token fijo (por defecto, aleatorio)")
    a = p.parse_args()

    app = web.Application()
    app["token"] = a.token or secrets.token_urlsafe(6)
    app.add_routes([web.get("/", index), web.get("/ws", ws_handler)])

    url = f"http://{local_ip()}:{a.port}/?k={app['token']}"
    print(f"\nAbre en el teléfono (misma WiFi):\n\n  {url}\n")
    try:
        import qrcode

        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.print_ascii(invert=True)
    except ImportError:
        pass
    web.run_app(app, host="0.0.0.0", port=a.port, print=None)


if __name__ == "__main__":
    main()
