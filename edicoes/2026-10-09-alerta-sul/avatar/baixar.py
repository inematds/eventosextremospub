#!/usr/bin/env python3
"""Espera o vídeo do avatar ficar pronto no HeyGen (leitura de status, sem gerar nada) e baixa avatar.mp4."""
import json, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projetos/explicavideos/engine"))
from heygen_read import get

AQUI = Path(__file__).resolve().parent
vid = (AQUI / "video_id.txt").read_text().strip()
for _ in range(180):  # até 3 h
    d = get("/v3/videos/" + vid); d = d.get("data", d)
    st = d.get("status")
    print(time.strftime("%H:%M"), st, flush=True)
    if st == "completed":
        tmp = AQUI / "avatar.part.mp4"
        with urllib.request.urlopen(d["video_url"], timeout=300) as src, tmp.open("wb") as f:
            while b := src.read(1 << 20):
                f.write(b)
        tmp.replace(AQUI / "avatar.mp4")
        print("BAIXADO", AQUI / "avatar.mp4", flush=True)
        break
    if st == "failed":
        print("FALHOU", d.get("failure_message"), flush=True)
        break
    time.sleep(60)
