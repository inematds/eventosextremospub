#!/usr/bin/env python3
"""Corta os clipes reais (mudos) da Situação dos Eventos Extremos numa janela 1080xH:
o trecho inteiro no centro (sem cortar) sobre o mesmo trecho desfocado, e o rótulo do lugar/data no canto.
uso: cortar_clipes.py [altura da janela, padrão 880 = layout canto com avatar]
Saída: clipes/<nome>-<H>.mp4. A moldura do telejornal sai pelo crop; selo "BREAKING NEWS" pelo delogo."""
import json, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
W, H = 1080, int(sys.argv[1]) if len(sys.argv) > 1 else 880
FONTE = Path.home() / ".local/share/fonts/Montserrat-ExtraBold.ttf"
F = AQUI / "fontes"
TERRA = "iw*0.2917:ih*0.926:iw*0.5594:ih*0.037"         # vídeo vertical no meio do quadro da Terra (x 1074, 560 de largura)
CLIPES = json.loads((AQUI / "clipes.json").read_text())

out = AQUI / "clipes"; out.mkdir(exist_ok=True)


def rotulo_png(txt, dst):
    """rótulo do lugar/data (o drawtext do ffmpeg corta o fim quando há acento)"""
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(str(FONTE), 34)
    x0, y0, x1, y1 = f.getbbox(txt)
    im = Image.new("RGBA", (x1 + 32, 34 + 28), (0, 0, 0, 184))
    ImageDraw.Draw(im).text((16, 14 - y0 + 4), txt, font=f, fill="white")
    im.save(dst)
for c in CLIPES:
    pre = []
    if c.get("crop"):
        pre.append(f"crop={TERRA if c['crop'] == 'terra' else c['crop']}")
    if c.get("delogo"):
        pre.append(f"delogo={c['delogo']}")
    pre = (",".join(pre) + ",") if pre else ""
    rot = out / f"{c['nome']}-rotulo.png"; rotulo_png(c["rotulo"], rot)
    fc = (f"[0:v]{pre}setsar=1,split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,eq=brightness=-0.18[bg];"
          f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2[cl];[cl][1:v]overlay=28:H-h-28,"
          f"fps=30,format=yuv420p[v]")
    dst = out / f"{c['nome']}-{H}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["ss"]), "-t", str(c["dur"]), "-i", F / c["src"] / "video.mp4", "-i", rot,
                    "-filter_complex", fc, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "18", "-preset", "fast", dst], check=True)
    print("ok", dst.name)
# folha: quadro do meio de cada clipe
subprocess.run(["ffmpeg", "-v", "error", "-y", *sum([["-ss", str(c["dur"] / 2), "-i", out / f"{c['nome']}-{H}.mp4"] for c in CLIPES], []),
                "-filter_complex", "".join(f"[{i}:v]scale=360:-2[s{i}];" for i in range(len(CLIPES)))
                + "".join(f"[s{i}]" for i in range(len(CLIPES))) + f"xstack=inputs={len(CLIPES)}:layout="
                + "|".join(f"{(i % 4) * 360}_{(i // 4) * (H * 360 // W)}" for i in range(len(CLIPES))) + ":fill=black",
                "-frames:v", "1", out / f"folha-{H}.jpg"], check=True)
print("folha", out / f"folha-{H}.jpg")
