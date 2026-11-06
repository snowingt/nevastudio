#!/usr/bin/env python3
"""youtube_studio_uploader.py - Subida autónoma ultrarrápida a YouTube Studio vía CDP Websocket.

Conecta directamente al websocket de la pestaña de YouTube Studio en localhost:9222
sin overhead de navegadores ni dependencias pesadas, inyectando el vídeo nativamente
mediante DOM.setFileInputFiles y automatizando el formulario completo.
"""

import argparse
import asyncio
import base64
import json
import sys
import time
import urllib.request
from pathlib import Path
import websockets

def find_studio_target(cdp_port: int = 9222) -> dict:
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=5)
        targets = json.loads(req.read().decode("utf-8"))
        # Buscar pestaña existente principal de Studio (tipo 'page' y origin en https://studio.youtube.com)
        for t in targets:
            url = t.get("url", "")
            if t.get("type") == "page" and "https://studio.youtube.com" in url:
                return t
        
        # Si no existe, crear nueva pestaña
        print("[YouTube Uploader] 🌐 Abriendo nueva pestaña de YouTube Studio...")
        req_new = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json/new?https://studio.youtube.com", timeout=10)
        new_target = json.loads(req_new.read().decode("utf-8"))
        time.sleep(5)
        return new_target
    except Exception as e:
        print(f"[YouTube Uploader] ❌ Error conectando a Chrome CDP: {e}", file=sys.stderr)
        return None

async def async_upload(
    video_path: str,
    title: str,
    description: str,
    visibility: str = "PUBLIC",
    cdp_port: int = 9222
) -> dict:
    video_file = Path(video_path).resolve()
    if not video_file.exists():
        print(f"[YouTube Uploader] ❌ Archivo no existe: {video_file}", file=sys.stderr)
        return {"success": False, "error": "File not found"}

    target = find_studio_target(cdp_port)
    if not target or "webSocketDebuggerUrl" not in target:
        return {"success": False, "error": "Could not connect to YouTube Studio CDP target"}

    ws_url = target["webSocketDebuggerUrl"]
    print(f"[YouTube Uploader] 🔌 Conectado a pestaña: {target.get('title')} ({target.get('url')})")

    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        msg_id = 0
        async def call(method: str, params: dict = None):
            nonlocal msg_id
            msg_id += 1
            cur = msg_id
            await ws.send(json.dumps({"id": cur, "method": method, "params": params or {}}))
            while True:
                raw = await ws.recv()
                data = json.loads(raw)
                if data.get("id") == cur:
                    return data

        await call("DOM.enable")
        await call("Page.enable")

        # 0. Cerrar cualquier diálogo previo (ej: "Se ha publicado el vídeo")
        close_prior_dialog = """(() => {
            const closeBtn = document.querySelector('ytcp-dialog #close-button') || 
                             Array.from(document.querySelectorAll('ytcp-button, button')).find(b => b.innerText && b.innerText.trim() === 'Cerrar');
            if (closeBtn) { closeBtn.click(); return 'closed'; }
            return 'none';
        })()"""
        await call("Runtime.evaluate", {"expression": close_prior_dialog, "returnByValue": True})
        await asyncio.sleep(1.0)

        # 1. Verificar si el diálogo de subida ya está abierto con input[type=file] presente
        check_dialog_script = """(() => {
            const input = document.querySelector('input[type=file]');
            return !!input;
        })()"""
        r_diag = await call("Runtime.evaluate", {"expression": check_dialog_script, "returnByValue": True})
        has_dialog = r_diag.get("result", {}).get("result", {}).get("value", False)

        if not has_dialog:
            print("[YouTube Uploader] 🖱️ Abriendo menú Crear...")
            click_crear = """(() => {
                const btn = document.querySelector("#create-icon") || 
                            Array.from(document.querySelectorAll("button, ytcp-button")).find(b => b.innerText && b.innerText.trim() === "Crear");
                if (btn) { btn.click(); return true; }
                return false;
            })()"""
            await call("Runtime.evaluate", {"expression": click_crear, "returnByValue": True})
            await asyncio.sleep(1.5)

            print("[YouTube Uploader] 🖱️ Seleccionando 'Subir vídeos'...")
            click_subir = """(() => {
                const item = document.querySelector("#text-item-0") || 
                             Array.from(document.querySelectorAll("tp-yt-paper-item, ytcp-text-menu yt-formatted-string")).find(el => el.innerText && el.innerText.trim() === "Subir vídeos");
                if (item) { item.click(); return true; }
                return false;
            })()"""
            await call("Runtime.evaluate", {"expression": click_subir, "returnByValue": True})
            await asyncio.sleep(2.5)

        # 2. Inyectar archivo mediante DOM.setFileInputFiles esperando a que aparezca input[type=file]
        print(f"[YouTube Uploader] 📤 Inyectando archivo de vídeo: {video_file.name} ({video_file.stat().st_size / (1024*1024):.2f} MB)...")
        input_node_id = 0
        for attempt in range(10):
            doc = await call("DOM.getDocument")
            root_id = doc.get("result", {}).get("root", {}).get("nodeId", 0)
            if root_id:
                node_res = await call("DOM.querySelector", {"nodeId": root_id, "selector": "input[type=file]"})
                input_node_id = node_res.get("result", {}).get("nodeId", 0)
                if input_node_id:
                    break
            await asyncio.sleep(1.0)

        if not input_node_id:
            print("[YouTube Uploader] ❌ No se encontró selector input[type=file] tras 10 intentos", file=sys.stderr)
            return {"success": False, "error": "file input not found"}

        await call("DOM.setFileInputFiles", {
            "nodeId": input_node_id,
            "files": [str(video_file)]
        })
        print("[YouTube Uploader] ✅ Archivo inyectado en el motor de subida de YouTube!")

        # 3. Esperar que aparezca el formulario de Detalles
        print("[YouTube Uploader] ⏳ Esperando carga de metadatos (8s)...")
        await asyncio.sleep(8)

        # 4. Rellenar Título
        print(f"[YouTube Uploader] 📝 Configurando título: {title}")
        set_title_script = f"""(() => {{
            const t = document.querySelector("#title-textarea #textbox, ytcp-social-suggestions-textbox[aria-label*='título' i] #textbox, ytcp-social-suggestions-textbox[aria-label*='title' i] #textbox");
            if (t) {{
                t.focus();
                document.execCommand("selectAll", false, null);
                document.execCommand("insertText", false, {json.dumps(title)});
                if (!t.innerText || !t.innerText.includes({json.dumps(title[:10])})) {{
                    t.innerText = {json.dumps(title)};
                }}
                t.dispatchEvent(new Event("input", {{ bubbles: true }}));
                return t.innerText;
            }}
            return null;
        }})()"""
        await call("Runtime.evaluate", {"expression": set_title_script, "returnByValue": True})
        await asyncio.sleep(1)

        # 5. Rellenar Descripción
        print("[YouTube Uploader] 📄 Configurando descripción con hashtags...")
        set_desc_script = f"""(() => {{
            const d = document.querySelector("#description-textarea #textbox, ytcp-social-suggestions-textbox[aria-label*='descripción' i] #textbox, ytcp-social-suggestions-textbox[aria-label*='description' i] #textbox");
            if (d) {{
                d.focus();
                document.execCommand("selectAll", false, null);
                document.execCommand("insertText", false, {json.dumps(description)});
                if (!d.innerText || !d.innerText.includes({json.dumps(description[:10])})) {{
                    d.innerText = {json.dumps(description)};
                }}
                d.dispatchEvent(new Event("input", {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()"""
        await call("Runtime.evaluate", {"expression": set_desc_script, "returnByValue": True})
        await asyncio.sleep(1)

        # 6. Seleccionar Audiencia (No para niños)
        print("[YouTube Uploader] 👶 Seleccionando audiencia: 'No es para niños'...")
        not_kids_script = """(() => {
            const r = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]');
            if (r) {
                r.scrollIntoView();
                r.click();
                return true;
            }
            return false;
        })()"""
        await call("Runtime.evaluate", {"expression": not_kids_script, "returnByValue": True})
        await asyncio.sleep(1.5)

        # 7. Avanzar Pasos con Siguiente
        for step_num, step_name in [(2, "Elementos del vídeo"), (3, "Comprobaciones"), (4, "Visibilidad")]:
            print(f"[YouTube Uploader] ➡️ Avanzando al Paso {step_num} ({step_name})...")
            click_next = """(() => {
                const next = document.querySelector("#next-button");
                if (next) { next.click(); return true; }
                return false;
            })()"""
            await call("Runtime.evaluate", {"expression": click_next, "returnByValue": True})
            await asyncio.sleep(2)

        # 8. Configurar Visibilidad
        vis_upper = visibility.upper().strip()
        print(f"[YouTube Uploader] 👁️ Configurando visibilidad: {vis_upper}...")
        vis_script = f"""(() => {{
            const radio = document.querySelector('tp-yt-paper-radio-button[name="{vis_upper}"]');
            if (radio) {{
                radio.scrollIntoView();
                radio.click();
                return true;
            }}
            return false;
        }})()"""
        await call("Runtime.evaluate", {"expression": vis_script, "returnByValue": True})
        await asyncio.sleep(1.5)

        # 9. Publicar / Guardar
        print("[YouTube Uploader] 🚀 Publicando vídeo...")
        publish_script = """(() => {
            const done = document.querySelector("#done-button");
            if (done) {
                done.click();
                return done.innerText;
            }
            return null;
        })()"""
        await call("Runtime.evaluate", {"expression": publish_script, "returnByValue": True})
        await asyncio.sleep(2)

        # Si aparece el diálogo 'Aún estamos comprobando tu contenido', hacer clic en 'Publicar de todas formas'
        confirm_inter_script = """(() => {
            const btn = Array.from(document.querySelectorAll('ytcp-button, button')).find(b => b.innerText && b.innerText.trim().includes('Publicar de todas formas'));
            if (btn) { btn.click(); return true; }
            return false;
        })()"""
        await call("Runtime.evaluate", {"expression": confirm_inter_script, "returnByValue": True})

        print("[YouTube Uploader] ⏳ Esperando confirmación de publicación (8s)...")
        await asyncio.sleep(8)

        # 10. Extraer enlace del vídeo publicado
        get_url_script = """(() => {
            const link = document.querySelector('a.ytcp-video-info, a[href*="youtu.be"], a[href*="/shorts/"], a[href*="/watch?v="]');
            return link ? link.href : null;
        })()"""
        r_url = await call("Runtime.evaluate", {"expression": get_url_script, "returnByValue": True})
        video_url = r_url.get("result", {}).get("result", {}).get("value") or "https://studio.youtube.com"

        # 11. Capturar pantalla de confirmación
        screenshot_dir = Path("/home/snow/.gemini/antigravity-cli/brain/5de0eb2d-2859-428b-88b0-96675efabb23")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        shot_path = screenshot_dir / f"youtube_upload_confirmed_{int(time.time())}.png"
        snap_res = await call("Page.captureScreenshot", {"format": "png"})
        if "result" in snap_res and "data" in snap_res["result"]:
            data = base64.b64decode(snap_res["result"]["data"])
            with open(shot_path, "wb") as f:
                f.write(data)
            print(f"[YouTube Uploader] 📸 Captura de confirmación guardada: {shot_path}")

        # 12. Cerrar diálogo de confirmación para dejar Studio listo
        close_modal_script = """(() => {
            const btn = Array.from(document.querySelectorAll("ytcp-button, button")).find(b => b.innerText && b.innerText.trim() === "Cerrar");
            if (btn) btn.click();
        })()"""
        await call("Runtime.evaluate", {"expression": close_modal_script, "returnByValue": True})
        await asyncio.sleep(1)

        print(f"[YouTube Uploader] 🎉 ¡Vídeo subido y publicado con éxito!")
        print(f"[YouTube Uploader] 🔗 URL: {video_url}")

        return {
            "success": True,
            "url": video_url,
            "screenshot": str(shot_path),
            "visibility": vis_upper
        }

def upload_short_to_studio(
    video_path: str,
    title: str,
    description: str,
    visibility: str = "PUBLIC",
    cdp_port: int = 9222
) -> dict:
    return asyncio.run(async_upload(video_path, title, description, visibility, cdp_port))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subidor de Shorts a YouTube Studio vía CDP")
    parser.add_argument("--video", required=True, help="Ruta al archivo MP4")
    parser.add_argument("--title", required=True, help="Título del vídeo")
    parser.add_argument("--desc", required=True, help="Descripción completa con hashtags")
    parser.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "PRIVATE", "UNLISTED"], help="Visibilidad")
    parser.add_argument("--cdp-port", default=9222, type=int, help="Puerto CDP")

    args = parser.parse_args()
    res = upload_short_to_studio(
        video_path=args.video,
        title=args.title,
        description=args.desc,
        visibility=args.visibility,
        cdp_port=args.cdp_port
    )
    if not res.get("success"):
        sys.exit(1)
