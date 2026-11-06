#!/usr/bin/env python3
"""telegram_dispatcher.py - Despachador de entregas de Snow Studio a Telegram.
Usa conexión IPv4 con TLS 1.2 y pausas de 5 segundos para evitar caídas.
"""

import sys
import time
import subprocess
from pathlib import Path

TOKEN = "8880950682:AAGQHe2tngh2PYGQlTpDebfSdOdkdnKXmKc"
CHAT_ID = "7102984562"

def send_message(text: str):
    time.sleep(5)
    cmd = [
        "curl", "--tls-max", "1.2", "-4", "-s", "--connect-timeout", "20",
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        "-d", f"chat_id={CHAT_ID}",
        "-d", f"text={text}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and '"ok":true' in res.stdout:
        print("[Telegram] ✅ Mensaje enviado.")
        return True
    print(f"[Telegram Error] {res.stdout}")
    return False

def send_photo(photo_path: str, caption: str):
    time.sleep(5)
    cmd = [
        "curl", "--tls-max", "1.2", "-4", "-s", "--connect-timeout", "20", "--max-time", "180",
        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
        "-F", f"chat_id={CHAT_ID}",
        "-F", f"caption={caption}",
        "-F", f"photo=@{photo_path}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and '"ok":true' in res.stdout:
        print(f"[Telegram] ✅ Foto {photo_path} enviada.")
        return True
    print(f"[Telegram Error] {res.stdout}")
    return False

def send_video(video_path: str, caption: str):
    time.sleep(5)
    cmd = [
        "curl", "--tls-max", "1.2", "-4", "-s", "--connect-timeout", "20", "--max-time", "300",
        f"https://api.telegram.org/bot{TOKEN}/sendVideo",
        "-F", f"chat_id={CHAT_ID}",
        "-F", "supports_streaming=true",
        "-F", f"caption={caption}",
        "-F", f"video=@{video_path}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and '"ok":true' in res.stdout:
        print(f"[Telegram] ✅ Video {video_path} enviado.")
        return True
    print(f"[Telegram Error] {res.stdout}")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 telegram_dispatcher.py <tipo: mensaje|foto|video> <contenido/ruta> [caption]")
        sys.exit(1)
    
    tipo = sys.argv[1]
    arg1 = sys.argv[2]
    caption = sys.argv[3] if len(sys.argv) > 3 else ""

    if tipo == "mensaje":
        send_message(arg1)
    elif tipo == "foto":
        send_photo(arg1, caption)
    elif tipo == "video":
        send_video(arg1, caption)
