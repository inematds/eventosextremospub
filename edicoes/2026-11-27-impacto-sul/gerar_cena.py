#!/usr/bin/env python3
"""Impacto Sul 27/11/2026: chuva no noroeste gaúcho e previsão para o Sul."""
import os
import difflib, json, re, subprocess, sys, unicodedata
from collections import Counter
from scipy.optimize import linear_sum_assignment
from datetime import datetime, timezone, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "27/11/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / (os.environ.get("TEMPOS") or ("avatar/tempos.json" if AVATAR else "tempos.json"))).read_text())
B = AQUI / "pesquisa/bruto"


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelo Whisper pelas do roteiro (campo legenda ou fala), mantendo os tempos."""
    tok, W = texto.split(), t["palavras"]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [n(x) for x in tok], [n(p["w"]) for p in W], autojunk=False).get_opcodes():
        if op == "equal":
            out += [{"w": tok[i1 + k], "t": W[j1 + k]["t"], "f": W[j1 + k]["f"]} for k in range(i2 - i1)]
        elif i2 > i1:
            a = W[j1]["t"] if j2 > j1 else (W[j1 - 1]["f"] if j1 else t["ini"])
            b = W[j2 - 1]["f"] if j2 > j1 else (W[j1]["t"] if j1 < len(W) else a + .3)
            d = (b - a) / (i2 - i1)
            out += [{"w": tok[i1 + k], "t": round(a + k * d, 3), "f": round(a + (k + 1) * d, 3)} for k in range(i2 - i1)]
    return out


ROT = {f["id"]: f.get("legenda") or f["fala"] for f in json.loads((AQUI / "falas.json").read_text())}
for t in T:
    t["palavras"] = roteiro(t, ROT[t["id"]])
FALA = {t["id"]: t for t in T}


def em(fid, palavra, k=1):
    achou = 0
    for p in FALA[fid]["palavras"]:
        if n(palavra) == n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]), 3)
FIM_VIDEO = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(AQUI / "avatar/avatar.mp4")], capture_output=True, text=True).stdout or DUR) if AVATAR else DUR
FIM_VIDEO = min(FIM_VIDEO, DUR)   # o compor_avatar corta no fim do avatar: a última cena vale até aqui
DUR = FIM_VIDEO if AVATAR else DUR
FPS = 30
MIN_QUADROS = 75
AMA = [250, 204, 21]
LAR = [255, 140, 26]
AVISOS = json.loads((B / 'inmet_avisos_ativos.json').read_text())
avisos = {a['id']: a for grupo in ('hoje', 'futuro') for a in AVISOS[grupo]}
contagens = {
    56517: {'41': 242, '42': 133, '43': 295},
    56515: {'41': 73, '42': 73, '43': 87},
    56528: {'41': 66, '42': 269, '43': 18},
}
municipios = {
    aid: {c for c in avisos[aid]['geocodes'].split(',') if c[:2] in {'41', '42', '43'}}
    for aid in contagens
}
for aid, esperado in contagens.items():
    assert Counter(c[:2] for c in municipios[aid]) == esperado, aid
assert avisos[56515]['fim'] == '2026-11-27 23:59'
assert '50 e 100 mm/dia' in avisos[56515]['riscos'][0]
assert '60-100 km/h' in avisos[56515]['riscos'][0]
assert avisos[56528]['inicio'] == '2026-11-28 00:00'
assert 'até 50 mm/dia' in avisos[56528]['riscos'][0]

inventario = json.loads((AQUI / 'cenas/inventario.json').read_text())
fortes = [x for x in inventario if x['nota'] >= 4]
extras = [
    ('08', 'f3', 'chovia', 'nuvem'),
    ('09', 'f2', 'água', 'rural'),
    ('10', 'f4', 'noite', 'nuvem'),
    ('11', 'f2', 'estrada', 'rural'),
    ('12', 'f7', 'sábado', 'chuva'),
    ('13', 'f6', 'Cascavel', 'cidade'),
    ('14', 'f8', 'chuva', 'cidade'),
]
grupos = ['nuvem', 'rural', 'nuvem', 'rural', 'rural', 'chuva', 'cidade']
clipes = [dict(x, grupo=g) for x, g in zip(fortes, grupos)]
clipes += [
    {'usado': f'cenas/clip-{i}', 'fala': f, 'palavra': p, 'grupo': g}
    for i, f, p, g in extras
]
quadros = [
    sorted(str(p.relative_to(AQUI)) for p in (AQUI / x['usado']).glob('*.jpg'))
    for x in clipes
]
assert all(len(q) >= MIN_QUADROS for q in quadros)
MAX_QUADROS = min(FPS * 3, min(map(len, quadros))) - 1
ALVOS = [em(x['fala'], x['palavra']) for x in clipes]


def dividir(a, b):
    """Particiona em trechos entre 2,5 e 3 segundos, sem sobras na emenda."""
    n = (b - a + MAX_QUADROS - 1) // MAX_QUADROS
    if n <= 0 or b - a < n * MIN_QUADROS:
        return []
    cortes = [a + (b-a) * i // n for i in range(n+1)]
    return list(zip(cortes, cortes[1:]))


def distribuir_cenas():
    fim_quadro = round(FPS * DUR)
    alvo_mapa = round(FPS * (em('f3', 'Argentina') - .5))
    for tamanho in (126, 90, 0):
        # A capa segura a manchete. Se o avatar acelerar, o mapa cede primeiro.
        for capa in range(90, 76, -1):
            if not tamanho:
                slots = dividir(capa, fim_quadro)
                if len(slots) >= len(fortes):
                    return capa, capa, capa, slots
                continue
            for delta in sorted(range(-37, 38), key=abs):
                a = alvo_mapa + delta
                b = a + tamanho
                esquerda, direita = dividir(capa, a), dividir(b, fim_quadro)
                slots = esquerda + direita
                if esquerda and direita and len(slots) >= len(fortes):
                    return capa, a, b, slots
    raise ValueError(f'{DUR:.2f} s para {len(fortes)} cenas fortes')


capa, mapa_ini, mapa_fim, slots = distribuir_cenas()
CAPA, MAP0, MAP1 = (t / FPS for t in (capa, mapa_ini, mapa_fim))
telas = [{'src': 'capa-dia/abertura.png', 'ini': 0, 'fim': CAPA, 'fade': 0, 'zoom': 0}]
fontes = []
custos = [[abs((a+b)/(2*FPS) - ALVOS[i]) for a, b in slots] for i in range(len(fortes))]
linhas, colunas = linear_sum_assignment(custos)
reservas = dict(zip(map(int, colunas), map(int, linhas)))
historico = []
for j, (a, b) in enumerate(slots):
    inicio = a/FPS
    termino = DUR if j == len(slots)-1 else b/FPS
    i = reservas.get(j)
    if i is None:
        meio = (inicio + termino)/2
        recente = historico[-4:]
        proximo = reservas.get(j+1)
        i = min(range(len(clipes)), key=lambda k: (
            abs(meio - ALVOS[k]) + 8*historico.count(k)
            + 35*(k in recente or k == proximo)
            + 8*bool(historico and clipes[k]['grupo'] == clipes[historico[-1]]['grupo'])
        ))
    historico.append(i)
    telas.append({'seq': quadros[i][:b-a], 'fps': FPS, 'ini': inicio, 'fim': termino,
                  'fade': .14, 'zoom': .015})

# O mapa combina o IR observado e a área em aviso da sexta. Os pinos
# identificam municípios em aviso laranja; a câmera permanece fixa.
SUL = {'lon': -52.8, 'lat': -26.8 if CANTO else -27.8, 'zoom': 5.65, 'pitch': 0, 'bearing': 0}
camera = [{'t': 0, **SUL}, {'t': DUR, **SUL}]
SAT, estados, alertas, pinos, imagens = None, [], [], [], []
if MAP1 > MAP0:
    estados = [{'id': uf, 'ini': MAP0, 'fim': MAP1, 'ufs': [uf], 'cor': AMA, 'alfa': .10}
               for uf in ('RS', 'SC', 'PR')]
    bbox_mun = [-58, -34, -47, -22]
    for aid, cor in [(56517, AMA), (56515, LAR)]:
        alertas.append({'id': aid, 'ini': MAP0, 'fim': MAP1, 'ids': sorted(municipios[aid]),
                        'cor': cor, 'alfa': .52, 'varredura': 0})
    # GEO=geo-br.js tem só estados. A camada da edição usa os mesmos ids
    # dos avisos recortados sobre os municípios do motor regional.
    imagens.append({'src': 'cenas/avisos-inmet.png', 'bbox': bbox_mun,
                    'ini': MAP0, 'fim': MAP1, 'fade': .22})
    for nome, codigo, lon, lat, altura in [
        ('Santa Rosa / RS', '4317202', -54.481, -27.871, 20),
        ('Chapecó / SC', '4204202', -52.618, -27.097, 22),
        ('Cascavel / PR', '4104808', -53.455, -24.956, 30),
    ]:
        assert codigo in municipios[56515]
        pinos.append({'nome': nome, 'lon': lon, 'lat': lat, 'h': altura, 'ini': MAP0, 'fim': MAP1})
    fontes.append({'ini': MAP0, 'fim': MAP1, 'html': '<b>INMET · chuva intensa</b> · áreas em aviso até 23h59 de sexta'})
    SAT = {'base': 'sat/web/geocolor.jpg', 'bbox': [-76, -35, -33, 7], 'tint': [129, 144, 164]}
    if MAP1 - MAP0 >= 4:
        horas = json.loads((AQUI / 'sat/web/ir_tempos.json').read_text())
        indices = list(range(max(0, len(horas)-8), len(horas)))
        locais = [datetime.fromisoformat(horas[i]).astimezone(timezone(timedelta(hours=-3))).strftime('%H:%M')
                  for i in indices]
        SAT['ir'] = {'frames': [f'sat/web/ir{i:02}.jpg' for i in indices], 'tempos': locais,
                     'ini': MAP0, 'fim': MAP1, 'dur': MAP1-MAP0, 'alfa': .66,
                     'rotulo': f'Satélite · infravermelho · {locais[0]}–{locais[-1]}'}


def painel(fid, titulo, *linhas, desde=None, ate=None):
    inicio = ini(fid) if desde is None else desde
    return {'ini': inicio, 'fim': fim(fid) if ate is None else ate, 'k': titulo,
            'itens': [{'t': inicio+.14*i, 'txt': txt} for i, txt in enumerate(linhas)]}


def contador(fid, titulo, valor, unid, detalhe):
    a = em(fid, str(valor)) - 1.0
    return {'ini': a, 'fim': fim(fid), 'k': titulo, 'l': detalhe,
            'contador': {'de': 0, 'ate': valor, 'ini': a, 'dur': 1.0, 'cor': '#FACC15', 'unid': unid}}


paineis = [
    painel('f2', 'CHUVA REGISTRADA · NOROESTE GAÚCHO', 'Tuparendi e Santo Cristo', 'Água sobre estradas'),
    contador('f4', 'NORTE GAÚCHO · PREVISÃO', 100, 'mm/dia', 'Limite do aviso laranja'),
    painel('f5', 'OESTE CATARINENSE · PREVISÃO', 'Chapecó em aviso laranja', 'Até 23h59 de sexta'),
    contador('f6', 'CASCAVEL / PR · PREVISÃO', 100, 'km/h', 'Vento nas áreas do aviso laranja'),
    contador('f7', 'OESTE DE SC · SÁBADO · PREVISÃO', 50, 'mm/dia', 'Limite do aviso amarelo'),
    painel('f8', 'SUL · PREVISÃO', 'Chuva diminui entre sábado e domingo', 'Novos episódios na próxima semana'),
    painel('f9', 'COMENTA AQUI', 'DE ONDE VOCÊ É?', 'COMO ESTÁ AÍ?'),
]
if MAP1 < fim('f3') - .6:
    paineis.append(painel('f3', 'INSTABILIDADE DA ARGENTINA', 'Chuva cedo em Santa Rosa', desde=max(MAP1, ini('f3'))))
if ini('f4') < paineis[1]['ini'] - .6:
    paineis.append(painel('f4', 'NORTE GAÚCHO · PREVISÃO', 'A chuva pode continuar nesta noite', ate=paineis[1]['ini']))
if ini('f6') < paineis[3]['ini'] - .6:
    paineis.append(painel('f6', 'OESTE DO PARANÁ · PREVISÃO', 'Cascavel em aviso laranja', ate=paineis[3]['ini']))
sabado = em('f7', '50') - 1.0
if sabado - ini('f7') > 2.5:
    paineis.append(painel('f7', 'SÁBADO · MUNICÍPIOS EM AVISO AMARELO',
                           'SC 269 · PR 66 · RS 18', 'Chuva ainda pela manhã', ate=sabado))
paineis.sort(key=lambda x: x['ini'])
for p, seguinte in zip(paineis, paineis[1:]):
    p['fim'] = min(p['fim'], seguinte['ini'])

fontes += [
    {'ini': CAPA, 'fim': min(MAP0, fim('f3')) if MAP1 > MAP0 else fim('f3'),
     'html': f'<b>Meteorologia · {DATA}</b> · registro de chuva'},
    {'ini': MAP1, 'fim': fim('f3'),
     'html': f'<b>Meteorologia · {DATA}</b> · avanço da instabilidade'},
    {'ini': ini('f4'), 'fim': fim('f7'), 'html': '<b>INMET</b> · limites para as áreas em aviso · imagens de chuva'},
    {'ini': ini('f8'), 'fim': fim('f8'), 'html': f'<b>Meteorologia · {DATA}</b> · previsão'},
]
cta = {'ini': ini('f10'), 'fim': DUR, 'a': 'APRENDA IA', 'b': 'inema.club', 'img': False}
assert em('f10', 'inema.club') < DUR

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "gelo": "#5ec8ff", "nino": "#5ec8ff",
         "calor": "#ff8c1a", "dispararam": "#ff8c1a", "graus": "#ff8c1a", "combustivel": "#ff8c1a", "arrancaram": "#ff2a1f",
         "tempestade": "#ff2a1f", "tempestades": "#ff2a1f", "granizo": "#ff2a1f", "estragos": "#ff2a1f", "telhados": "#ff2a1f",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "dispara": "#ff8c1a", "atencao": "#ff8c1a", "atento": "#ff8c1a", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "oeste", "norte", "santa", "catarina", "parana", "argentina", "inemaclub", "cidade", "tuparendi", "cristo", "chapeco", "cascavel"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and len(" ".join(b["w"] for b in bloco) + " " + w) > 19:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": t["palavras"][i - 1]["f"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a['fim'] = b['ini']


C = {
    'layout': 'canto' if CANTO else 'avatar' if AVATAR else 'cheio',
    'padding_baixo': 640 if CANTO else 820, 'padding_topo': 180,
    'duracao': DUR, 'marca': 'INEMA · IMPACTO SUL',
    'selo': f'INMET{" · NOAA" if SAT and SAT.get("ir") else ""} · {DATA}',
    'camera': camera, 'sat': SAT, 'telas': telas, 'estados': estados, 'alertas': alertas,
    'pinos': pinos, 'imagens': imagens, 'hero': [], 'paineis': paineis, 'cta': cta,
    'fontes': fontes, 'legenda': legenda,
}
(AQUI / 'cena.js').write_text('window.CENA=' + json.dumps(C, ensure_ascii=False) + ';\n')
print(f'cena.js: {DUR:.2f} s, {len(telas)} telas, {len(fortes)} cenas fortes, mapa {MAP0:.2f}–{MAP1:.2f} s')
