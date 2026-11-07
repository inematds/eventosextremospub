#!/usr/bin/env python3
"""Inventário das edições: o que cada vídeo tem de material e o que mostrou na tela.

Uso: python3 auto/inventario.py [--dias 14] > inventario.jsonl
Uma linha JSON por edição (pasta em edicoes/). Só lê arquivos locais.

- disponivel: o que a coleta juntou (fotos e clipes reais em fonte/, quadros de clipe em cenas/, satélite em sat/)
- na_tela: segundos de cada tipo de imagem no vídeo final, lidos do cena.js
  (clipe_real = telas com seq; ilustracao = telas com selo 'ilustração'; satelite_real = imagens;
   abertura = capa do quadro 0; mapa = o resto da duração)
- Edição sem cena.js (alerta, vídeo de câmera) vem com motor='outro' e sem na_tela.
"""
import json, os, re, subprocess, sys
from datetime import date, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ED = os.path.join(RAIZ, 'edicoes')


def conta(pasta, exts):
    if not os.path.isdir(pasta):
        return 0
    n = 0
    for _, _, fs in os.walk(pasta):
        n += sum(1 for f in fs if f.lower().rsplit('.', 1)[-1] in exts)
    return n


def duracao(mp4):
    try:
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return round(float(out), 1)
    except Exception:
        return None


def na_tela(cena):
    s = open(cena, encoding='utf-8').read()
    C = json.loads(s[s.index('{'):s.rindex('}') + 1])
    total = float(C.get('duracao') or 0)
    seg = {'clipe_real': 0.0, 'ilustracao': 0.0, 'satelite_real': 0.0, 'abertura': 0.0}
    for t in C.get('telas') or []:
        d = max(0.0, float(t.get('fim', 0)) - float(t.get('ini', 0)))
        if t.get('seq'):
            seg['clipe_real'] += d
        elif 'abertura' in str(t.get('src', '')):
            seg['abertura'] += d
        elif 'ilustra' in str(t.get('selo', '')):
            seg['ilustracao'] += d
        else:
            seg['ilustracao'] += d  # tela parada sem selo: imagem gerada
    for i in C.get('imagens') or []:
        seg['satelite_real'] += max(0.0, float(i.get('fim', 0)) - float(i.get('ini', 0)))
    seg['mapa'] = max(0.0, total - sum(seg.values()))
    return {k: round(v, 1) for k, v in seg.items()}, round(total, 1)


def serie(nome):
    s = nome[11:]
    for a, b in (('ultimas-24h', 'Clima 24h'), ('previsao-do-dia', 'Previsão do Dia'), ('clima-do-dia', 'Clima do DIA'),
                 ('mundo', 'Clima no Mundo'), ('impacto-sul', 'Impacto Sul'), ('semana', 'Semana')):
        if s.startswith(a):
            return b, True
    return 'avulso: ' + s, False


def main():
    dias = 14
    if '--dias' in sys.argv:
        dias = int(sys.argv[sys.argv.index('--dias') + 1])
    desde = (date.today() - timedelta(days=dias)).isoformat()
    for nome in sorted(os.listdir(ED)):
        p = os.path.join(ED, nome)
        if not (os.path.isdir(p) and re.match(r'\d{4}-\d\d-\d\d-', nome)) or nome[:10] < desde:
            continue
        mp4s = [f for f in ('video-avatar.mp4', 'video.mp4') if os.path.exists(os.path.join(p, f))]
        nome_serie, fixa = serie(nome)
        # peça = mesma ideia; 16:9 e 9:16, -av1 e -v2 são versões da mesma peça
        peca = re.sub(r'(-(169|916|av\d+|v\d+[a-z]?))+$', '', nome)
        reg = {
            'edicao': nome, 'data': nome[:10], 'peca': peca, 'serie': nome_serie, 'serie_fixa': fixa,
            'final': mp4s[0] if mp4s else None, 'com_avatar': 'video-avatar.mp4' in mp4s,
            'duracao_s': duracao(os.path.join(p, mp4s[0])) if mp4s else None,
            'youtube_id': (open(os.path.join(p, 'youtube-lives10.txt')).read().strip() or None)
                          if os.path.exists(os.path.join(p, 'youtube-lives10.txt')) else None,
            'ig_tiktok': os.path.exists(os.path.join(p, 'metritds.txt')),
            'titulo': open(os.path.join(p, 'yt.txt'), encoding='utf-8').readline().strip()
                      if os.path.exists(os.path.join(p, 'yt.txt')) else None,
            'disponivel': {
                'fotos_reais': conta(os.path.join(p, 'fonte'), {'jpg', 'jpeg', 'png', 'webp'}),
                'clipes_reais': conta(os.path.join(p, 'fonte'), {'mp4', 'mov', 'webm'}),
                'quadros_de_clipe': conta(os.path.join(p, 'cenas'), {'jpg', 'png'}),
                'satelite': conta(os.path.join(p, 'sat'), {'jpg', 'png'}),
                'ilustracoes': conta(os.path.join(p, 'capa-dia'), {'jpg', 'png'}),
            },
        }
        cena = os.path.join(p, 'cena.js')
        if os.path.exists(cena):
            try:
                reg['na_tela'], _ = na_tela(cena)
                reg['motor'] = 'mapa'
            except Exception as e:
                reg['motor'] = 'mapa'
                reg['erro'] = f'cena.js: {e}'[:120]
        else:
            reg['motor'] = 'outro'  # alerta / vídeo de câmera: outro motor, sem roteiro de telas
        print(json.dumps(reg, ensure_ascii=False))


if __name__ == '__main__':
    main()
