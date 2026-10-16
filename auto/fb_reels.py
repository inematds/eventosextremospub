#!/usr/bin/env python3
"""Últimos reels da página do Facebook do canal de previsão (reserva quando o YouTube não tem vídeo; Nei, 16/10/2026).
O yt-dlp não lista abas do Facebook: lê a página /reels/ com os cookies do Firefox e pega a data de cada reel com o yt-dlp.
uso: fb_reels.py [N]  → linhas "fb:<id>|aaaammdd|título" (mais recente primeiro)"""
import re, subprocess, sys, urllib.request
from yt_dlp.cookies import extract_cookies_from_browser

PAGINA = "https://www.facebook.com/meteorologistapiterscheuer/reels/"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4

op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(extract_cookies_from_browser("firefox")))
op.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"),
                 ("Accept", "text/html"), ("Accept-Language", "pt-BR,pt;q=0.9"), ("Sec-Fetch-Mode", "navigate")]
h = op.open(PAGINA, timeout=60).read().decode("utf8", "ignore")
ids = list(dict.fromkeys(re.findall(r'(?:reel\\?/|"video_id":")(\d{12,})', h)))[:N]
for i in ids:
    r = subprocess.run(["timeout", "90", "yt-dlp", "--skip-download", "--print", "%(upload_date)s|%(title)s",
                        f"https://www.facebook.com/reel/{i}"], capture_output=True, text=True)
    linha = r.stdout.strip().splitlines()[-1:] if r.returncode == 0 else []
    if linha:
        d, t = linha[0].split("|", 1)
        print(f"fb:{i}|{d}|{t.replace(chr(10), ' ')[:150]}")
