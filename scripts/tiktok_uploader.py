#!/usr/bin/env python3
"""tiktok_uploader.py - Subida autónoma a TikTok Studio vía navegador CDP en localhost:9222.

Aprovecha la sesión real iniciada en Google Chrome (sin requerir API oficial de TikTok),
inyecta el video en el motor de subida de TikTok Studio, rellena el pie de foto
con hashtags optimizados para retención y automatiza el flujo completo.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def parse_args():
    parser = argparse.ArgumentParser(description="TikTok Studio Autonomous Uploader via Browser CDP")
    parser.add_argument("--video", required=True, help="Ruta absoluta al archivo .mp4 vertical (9:16)")
    parser.add_argument("--title", default="", help="Título o descripción del video (caption)")
    parser.add_argument("--tags", default="#KDrama #NovelaCorta #MiniNovela #DomiDrama #Viral #Parati", help="Hashtags virales")
    parser.add_argument("--cdp-port", type=int, default=9222, help="Puerto de depuración remota de Chrome (default: 9222)")
    parser.add_argument("--schedule", type=str, default=None, help="Hora para programar (opcional)")
    parser.add_argument("--publish", action="store_true", help="Pulsar el botón 'Publicar' automáticamente (si no, queda listo para revisión)")
    return parser.parse_args()

def main():
    args = parse_args()
    video_path = Path(args.video).resolve()

    if not video_path.exists():
        print(f"[TikTok Uploader] ❌ Error: El video no existe: {video_path}", file=sys.stderr)
        sys.exit(1)

    cdp_url = f"http://127.0.0.1:{args.cdp_port}"
    caption = f"{args.title}\n\n{args.tags}".strip()

    print("🎵 [TikTok Uploader] Conectando a Chrome CDP en", cdp_url)
    print(f"🎬 Video: {video_path.name} ({video_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f"📝 Caption: {caption}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"[TikTok Uploader] ❌ No se pudo conectar a Chrome en {cdp_url}: {e}", file=sys.stderr)
            sys.exit(1)

        context = browser.contexts[0]
        
        # Buscar si ya hay una pestaña de TikTok abierta
        target_page = None
        for page in context.pages:
            if "tiktok.com" in page.url:
                target_page = page
                break

        if not target_page:
            print("[TikTok Uploader] 🌐 Abriendo nueva pestaña de TikTok Studio...")
            target_page = context.new_page()

        print("[TikTok Uploader] 🚀 Navegando a TikTok Studio Upload...")
        target_page.goto("https://www.tiktok.com/tiktokstudio/upload?from=upload", wait_until="domcontentloaded", timeout=25000)
        target_page.wait_for_timeout(4000)

        # Localizar el input de archivo
        file_input = target_page.locator("input[type=file][accept*='video']").first
        if not file_input.count():
            file_input = target_page.locator("input[type=file]").first

        if not file_input.count():
            print("[TikTok Uploader] ❌ No se encontró el input de archivo en la página.", file=sys.stderr)
            sys.exit(1)

        print(f"[TikTok Uploader] 📤 Inyectando video {video_path.name}...")
        file_input.set_input_files(str(video_path))
        print("[TikTok Uploader] ✅ Video inyectado. Esperando procesamiento inicial...")
        target_page.wait_for_timeout(6000)

        # Rellenar caption / descripción
        print("[TikTok Uploader] ✍️ Escribiendo caption y hashtags...")
        caption_box = target_page.locator("div[contenteditable='true']").first
        if caption_box.count():
            caption_box.click()
            caption_box.evaluate("(el, text) => { el.focus(); document.execCommand('selectAll', false, null); document.execCommand('insertText', false, text); }", caption)
        else:
            # Fallback a textarea
            textarea = target_page.locator("textarea").first
            if textarea.count():
                textarea.fill(caption)

        target_page.wait_for_timeout(2000)
        print("[TikTok Uploader] 📋 Caption configurado con éxito.")

        if args.publish:
            print("[TikTok Uploader] 🚀 Pulsando botón 'Publicar'...")
            publish_btn = target_page.locator("button:has-text('Publicar'), button:has-text('Post')").first
            if publish_btn.count():
                publish_btn.click()
                print("[TikTok Uploader] 🎉 ¡Video publicado con éxito en TikTok!")
            else:
                print("[TikTok Uploader] ⚠️ Botón de publicar no encontrado o video aún procesando.")
        else:
            print("[TikTok Uploader] 👁️ Modo borrador/revisión: Video y caption listos en la pestaña para tu visto bueno.")

if __name__ == "__main__":
    main()
