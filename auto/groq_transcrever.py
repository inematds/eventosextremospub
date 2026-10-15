#!/usr/bin/env python3
"""Reserva Groq para transcrever a fonte QUANDO A MÁQUINA ESTÁ CHEIA (autorizado pelo Nei em 15/10/2026:
"o groq entra se temos muita coisa ao mesmo tempo"). Só para isso: transcrição da fonte do eventosextremospub.
uso: groq_transcrever.py <video ou áudio> <pasta fonte> [--forcar]
  sai 2 = máquina não está cheia (o chamador segue no Whisper local); 1 = falhou; 0 = transcript.txt/.srt/.json prontos.
Máquina cheia = carga de 1 min ≥ CARGA_CHEIA (padrão = nº de núcleos) OU outra transcrição Whisper já rodando.
Custo: whisper-large-v3-turbo ≈ US$ 0,04/h de áudio (um boletim de 16 min ≈ US$ 0,01). A key vem do .env em runtime."""
import json, os, subprocess, sys, tempfile
from pathlib import Path

src, F = Path(sys.argv[1]), Path(sys.argv[2])
forcar = "--forcar" in sys.argv

carga = os.getloadavg()[0]
limite = float(os.environ.get("CARGA_CHEIA", os.cpu_count() or 20))
outros = subprocess.run(["pgrep", "-f", "whisper_gpu_worker.py"],
                        capture_output=True, text=True).stdout.split()
if not forcar and carga < limite and not outros:
    print(f"máquina livre (carga {carga:.0f} < {limite:.0f}, sem outro Whisper): segue no Whisper local")
    sys.exit(2)
print(f"máquina cheia (carga {carga:.0f}, Whisper rodando: {len(outros)}): transcrevendo pela Groq")

def chave():
    for env in (Path.home() / "projetos/wifi/.env", Path.home() / "projetos/openpcbotv2/.env"):
        if env.exists():
            for l in env.read_text().splitlines():
                if l.startswith("GROQ_API_KEY="):
                    return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("sem GROQ_API_KEY nos .env")

import requests

with tempfile.TemporaryDirectory() as tmp:
    mp3 = Path(tmp) / "a.mp3"  # mono 16 kHz 48 kbps: 16 min ≈ 6 MB (limite da Groq 25 MB)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", str(mp3)], check=True)
    if mp3.stat().st_size > 24 * 1024 * 1024:
        sys.exit("áudio grande demais para a Groq")
    with open(mp3, "rb") as fh:
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",
                          headers={"Authorization": f"Bearer {chave()}"},
                          data={"model": os.environ.get("GROQ_STT_MODEL", "whisper-large-v3-turbo"), "language": "pt",
                                "response_format": "verbose_json", "temperature": "0"},
                          files={"file": ("a.mp3", fh, "audio/mpeg")}, timeout=600)
if r.status_code != 200:
    sys.exit(f"Groq HTTP {r.status_code}: {r.text[:200]}")
d = r.json()
segs = [{"start": round(s["start"], 3), "end": round(s["end"], 3), "text": s["text"].strip()}
        for s in d.get("segments", []) if s.get("text", "").strip()]
if sum(len(s["text"].split()) for s in segs) < 50:
    sys.exit("Groq devolveu texto curto demais")

def ts(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"

F.mkdir(parents=True, exist_ok=True)
(F / "transcript.txt").write_text(" ".join(s["text"] for s in segs) + "\n", encoding="utf-8")
(F / "transcript.srt").write_text("".join(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text']}\n\n"
                                          for i, s in enumerate(segs, 1)), encoding="utf-8")
(F / "transcript.json").write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
(F / "transcrito-por.txt").write_text(f"groq {d.get('duration', '?')} s de áudio\n")
print(f"Groq: {sum(len(s['text'].split()) for s in segs)} palavras, {d.get('duration', '?')} s de áudio")
