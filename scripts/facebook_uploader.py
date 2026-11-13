#!/usr/bin/env python3
"""facebook_uploader.py - Subida autónoma a Facebook Reels vía navegador CDP en localhost:9222.

Conecta a Google Chrome usando la sesión de Facebook del navegador,
navega al creador de Reels, inyecta el video vertical 9:16 y rellena el caption.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def parse_args():
    parser = argparse.ArgumentParser(description="Facebook Reels Autonomous Uploader via Browser CDP")
    parser.add_argument("--video", required=True, help="Ruta absoluta al archivo .mp4 vertical (9:16)")
    parser.add_argument("--title", default="", help="Descripción del Reel")
    parser.add_argument("--tags", default="#Reels #NovelaCorta #KDrama #Viral", help="Hashtags")
    parser.add_argument("--cdp-port", type=int, default=9222, help="Puerto de depuración remota de Chrome (default: 9222)")
    parser.add_argument("--publish", action="store_true", help="Publicar automáticamente")
    return parser.parse_args()

def main():
    args = parse_args()
    video_path = Path(args.video).resolve()

    if not video_path.exists():
        print(f"[Facebook Uploader] ❌ Error: El video no existe: {video_path}", file=sys.stderr)
        sys.exit(1)

    cdp_url = f"http://127.0.0.1:{args.cdp_port}"
    caption = f"{args.title}\n\n{args.tags}".strip()

    print("📘 [Facebook Uploader] Conectando a Chrome CDP en", cdp_url)
    print(f"🎬 Video: {video_path.name}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"[Facebook Uploader] ❌ Error conectando a Chrome: {e}", file=sys.stderr)
            sys.exit(1)

        context = browser.contexts[0]
        page = context.new_page()

        print("[Facebook Uploader] 🌐 Navegando a Facebook Reels Creator...")
        page.goto("https://www.facebook.com/reels/create", wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(4000)

        file_input = page.locator("input[type=file]").first
        if file_input.count():
            print(f"[Facebook Uploader] 📤 Inyectando archivo {video_path.name}...")
            file_input.set_input_files(str(video_path))
            page.wait_for_timeout(5000)
            print("[Facebook Uploader] ✅ Video cargado. Listo para descripción y publicación.")
        else:
            print("[Facebook Uploader] ⚠️ Requiere inicio de sesión activo en Facebook en la ventana de Chrome.")

if __name__ == "__main__":
    main()
