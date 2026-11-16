#!/usr/bin/env python3
"""Lista fontes sem esconder erros de consulta. Não baixa mídia nem usa API Data.

Saída: id|aaaammdd|título. 0=lista consultada, 4=consulta inconclusiva.
O JSON original e stderr ficam na pasta de diagnóstico da edição.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

CHANNELS = {
    "previsao": "UCGEnQh_FXX9Qny0BqmUbZ2g",
    "dia": "UCGXu6BQZDlJhj99-wFroUEA",
}
BLOCKED = {"subscriber_only", "premium_only", "needs_auth", "private"}


def run(args, log, timeout=120):
    try:
        result = subprocess.run(["yt-dlp", *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        with log.open("a") as f:
            f.write(f"timeout {timeout}s: {args}\n")
        return None
    with log.open("a") as f:
        f.write(f"{dt.datetime.now().isoformat()} rc={result.returncode}: {args}\n{result.stderr}\n")
    if result.returncode:
        return None
    try:
        return json.loads(result.stdout)
    except ValueError:
        with log.open("a") as f:
            f.write("Resposta sem JSON válido\n")
        return None


def candidates(mode, data):
    entries = [e for e in data.get("entries", []) if e and e.get("availability") not in BLOCKED]
    if mode == "dia":
        # O título do boletim traz a data do conteúdo; não usar data UTC de upload.
        import re
        for e in entries:
            title = e.get("title") or ""
            if re.match(r"^(Brasil|Brazil)\s*\|", title, re.I) and not re.search(r"membros|members", title, re.I):
                match = re.search(r"\((\d{2}/\d{2}/\d{4})\)", title)
                if match:
                    yield e["id"], match[1], title
    else:
        for e in entries:
            if e.get("availability") not in BLOCKED:
                yield e["id"], e.get("upload_date"), e.get("title") or ""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("modo", choices=CHANNELS)
    p.add_argument("diagnostico", type=Path)
    a = p.parse_args()
    a.diagnostico.mkdir(parents=True, exist_ok=True)
    log = a.diagnostico / "youtube-erros.log"
    data = run(["--flat-playlist", "--playlist-end", "30" if a.modo == "dia" else "8",
                "--extractor-args", "youtube:lang=pt", "--dump-single-json",
                f"https://www.youtube.com/channel/{CHANNELS[a.modo]}/videos"], log)
    if not data or not data.get("entries"):
        print("Consulta YouTube inconclusiva; ver youtube-erros.log", file=sys.stderr)
        return 4
    (a.diagnostico / "youtube-lista.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    valid = 0
    unresolved = False
    for vid, date, title in candidates(a.modo, data):
        if a.modo == "previsao":
            info = run(["--skip-download", "--ignore-no-formats-error", "--dump-single-json",
                        f"https://www.youtube.com/watch?v={vid}"], log, 90)
            if not info:
                unresolved = True
                continue
            if info.get("availability") in BLOCKED:
                continue
            date, title = info.get("upload_date"), info.get("title") or title
        if not date:
            unresolved = True
            continue
        title = title.replace("|", " / ").replace("\n", " ")
        print(f"{vid}|{date}|{title}", flush=True)
        valid += 1
    # Um canal sem boletim no recorte foi consultado; previsão sem datas é inconclusiva.
    return 4 if unresolved or (a.modo == "previsao" and not valid) else 0


if __name__ == "__main__":
    sys.exit(main())
