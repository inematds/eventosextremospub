#!/usr/bin/env python3
"""Impacto Sul 25/11/2026: cheia no Paraná e aviso de chuva no Sul."""
import os
import difflib, json, re, subprocess, sys, unicodedata
from collections import Counter
from scipy.optimize import linear_sum_assignment
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "25/11/2026"
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
        if (n(palavra)==n(p["w"]) if len(n(palavra))<=2 else n(palavra) in n(p["w"])):
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
    56499: {'41': 399, '42': 280, '43': 164},
    56501: {'41': 398, '42': 24},
    56502: {'41': 399, '42': 92},
    56505: {'41': 223, '42': 247, '43': 154},
}

for aviso_id, esperado in contagens.items():
    codigos = set(avisos[aviso_id]['geocodes'].split(','))
    assert Counter(c[:2] for c in codigos if c[:2] in {'41', '42', '43'}) == esperado
    limite = 100 if aviso_id == 56501 else 50
    assert f'{limite} mm/dia' in avisos[aviso_id]['riscos'][0]
assert avisos[56501]['fim'] == '2026-11-25 23:59'
assert avisos[56502]['inicio'] == '2026-11-26 00:00'
assert avisos[56505]['inicio'] == '2026-11-27 00:00'

inventario = json.loads((AQUI / 'cenas/inventario.json').read_text())
clipes = [x for x in inventario if x['nota'] >= 4]
quadros = [sorted((AQUI / x['usado']).glob('*.jpg')) for x in clipes]
limites = [len(q) for q in quadros]
# Cada clipe tem pelo menos 75 quadros limpos. Separe janelas mais curtas
# para os recortes que acabam antes dos demais.
assert all(l >= MIN_QUADROS for l in limites)
duracao_comum = sorted(limites)[-4]
n_curtos = sum(d < duracao_comum for d in limites)
curto = min(limites)


def distribuir(a, b, curtos=0):
    tamanho = b - a
    n = tamanho // MIN_QUADROS
    if tamanho == 0:
        return []
    if n < max(1, curtos):
        return None
    # Só fixa janelas de 2,5 s quando a diferença entre os clipes exige isso.
    longos = n - curtos
    minimo = tamanho - MIN_QUADROS * curtos
    if longos and not MIN_QUADROS * longos <= minimo <= duracao_comum * longos:
        return None
    if not longos and tamanho > curto * curtos:
        return None
    if not longos:
        curtos = 0
        longos = n
        minimo = tamanho
    cortes = [a + MIN_QUADROS * i for i in range(curtos)]
    base = a + MIN_QUADROS * curtos
    cortes += [base + minimo * i // longos for i in range(longos)]
    return list(zip(cortes, cortes[1:] + [b]))


def distribuir_cenas():
    alvo_capa = max(90, round(FPS * em('f1', 'Impacto')))
    alvo_mapa = round(FPS * max(ini('f6'), em('f6', 'Paraguai') - 1.3))
    fim_quadro = round(FPS * DUR)
    # Ajuste fino para o relógio de cada voz. O mapa cede espaço aos clipes
    # quando a duração do avatar encolhe.
    for tamanho_mapa in (135, 90, 0):
        for capa in dict.fromkeys((alvo_capa, max(90, alvo_capa - 15), 90)):
            for delta in sorted(range(-44, 45), key=abs) if tamanho_mapa else (0,):
                mapa = alvo_mapa + delta if tamanho_mapa else capa
                depois = mapa + tamanho_mapa
                if mapa < capa:
                    continue
                antes = distribuir(capa, mapa)
                restante = distribuir(depois, fim_quadro, n_curtos)
                if antes is None or restante is None:
                    continue
                slots = antes + restante
                if len(slots) >= len(clipes):
                    return capa / FPS, mapa / FPS, depois / FPS, slots
    raise ValueError(f'{DUR:.2f} s não comportam a capa e {len(clipes)} cenas de 2,5 s')


CAPA, MAP0, MAP1, slots = distribuir_cenas()
SUL = {'lon': -52.1, 'lat': -27.5, 'zoom': 5.35, 'pitch': 0, 'bearing': 0}
camera = [{'t': 0, **SUL}, {'t': DUR, **SUL}]


def slot_fala(a, b):
    return next((t['id'] for t in T if t['ini'] <= (a+b)/(2*FPS) < t['fim']), 'f12')


def custo(i, a, b):
    if b - a > limites[i]:
        return 1e6
    x = clipes[i]
    fid = x['fala']
    alvo = em(fid, x['palavra'])
    meio = (a+b)/(2*FPS)
    # Dá prioridade aos três resgates nas falas com município identificado.
    peso = 8 if x['lugar'].endswith('/ PR') else 1
    return abs(meio - alvo) * peso + (20 if slot_fala(a, b) in ('f3', 'f4', 'f5') and fid != slot_fala(a, b) else 0)


custos = [[custo(i, a, b) for a, b in slots] for i in range(len(clipes))]
rows, cols = linear_sum_assignment(custos)
assert all(custos[i][j] < 1e6 for i, j in zip(rows, cols))
escolhas = {int(j): int(i) for i, j in zip(rows, cols)}
telas = [{'src': 'capa-dia/abertura.png', 'ini': 0, 'fim': CAPA, 'fade': 0, 'zoom': 0}]
fontes = []
historico = []
registros = {}
for j, (a, b) in enumerate(slots):
    i = escolhas.get(j)
    if i is None:
        candidatos = [k for k, q in enumerate(quadros) if len(q) >= b-a and k not in historico[-5:] and k != escolhas.get(j+1)]
        i = min(candidatos, key=lambda k: custos[k][j] + 18*historico.count(k))
    historico.append(i)
    inicio, termino = a/FPS, min(b/FPS, DUR) if j == len(slots)-1 else b/FPS
    telas.append({'seq': [str(q.relative_to(AQUI)) for q in quadros[i][:b-a]], 'fps': FPS,
                  'ini': inicio, 'fim': termino, 'fade': 0, 'zoom': 0})
    x = clipes[i]
    if x["lugar"].endswith("/ PR"):
        registros.setdefault(x["fala"], []).append((inicio, termino))
    # O registro continua identificado como paranaense nas falas de previsão para SC e RS.
    fontes.append({'ini': inicio, 'fim': termino,
                   'html': f'<b>Registro da cheia</b> · {x["lugar"]}'})

SAT, estados, alertas, pinos = None, [], [], []
if MAP1 > MAP0:
    cor_estado = [('RS', AMA), ('SC', LAR), ('PR', LAR)]
    estados = [{'id': uf, 'ini': MAP0, 'fim': MAP1, 'ufs': [uf], 'cor': cor, 'alfa': .29}
               for uf, cor in cor_estado]
    for aid, cor in [(56499, AMA), (56501, LAR)]:
        alertas.append({'id': aid, 'ini': MAP0, 'fim': MAP1,
                        'ids': [c for c in avisos[aid]['geocodes'].split(',') if c[:2] in {'41', '42', '43'}],
                        'cor': cor, 'alfa': .45, 'varredura': 0})
    locais_em_aviso = [
        ('Verê / PR', 'Laranja · sudoeste', '4128609', 56501, -52.9051, -25.8772, 108),
        ('Canoinhas / SC', 'Laranja · norte', '4203808', 56501, -50.3950, -26.1766, 12),
        ('Passo Fundo / RS', 'Amarelo · norte', '4314100', 56499, -52.4091, -28.2576, 2),
    ]
    for nome, sub, codigo, aid, lon, lat, altura in locais_em_aviso:
        assert codigo in avisos[aid]['geocodes'].split(','), nome
        pinos.append({'nome': nome, 'sub': sub, 'lon': lon, 'lat': lat, 'h': altura,
                      'ini': MAP0, 'fim': MAP1})
    fontes.append({'ini': MAP0, 'fim': MAP1, 'html': '<b>INMET · avisos desta quarta</b> · risco nas áreas em aviso'})
    if MAP1 - MAP0 >= 4:
        horas = json.loads((AQUI / 'sat/web/ir_tempos.json').read_text())
        imagens_ir = range(38, 48)
        locais = [(datetime.fromisoformat(horas[i]) - timedelta(hours=3)).strftime('%H:%M')
                  for i in imagens_ir]
        SAT = {'base': 'sat/web/geocolor-sul.png', 'bbox': [-76, -35, -33, 7], 'tint': [130, 130, 142],
               'ir': {'frames': [f'sat/web/ir{i:02}-sul.png' for i in imagens_ir],
                      'tempos': locais, 'ini': MAP0, 'fim': MAP1, 'dur': MAP1-MAP0, 'alfa': .78,
                      'rotulo': 'Satélite · infravermelho'}}


def painel(fid, titulo, *linhas):
    a, b = ini(fid), fim(fid)
    return {'ini': a, 'fim': b, 'k': titulo,
            'itens': [{'t': a+i*.28, 'txt': txt} for i, txt in enumerate(linhas)]}


def contador(fid, titulo, valor, detalhe, fim_card=None):
    a = em(fid, str(valor)) - 1.0
    return {'ini': a, 'fim': fim_card if fim_card is not None else fim(fid), 'k': titulo,
            'l': detalhe, 'contador': {'de': 0, 'ate': valor, 'ini': a, 'dur': 1.0,
                                      'cor': '#FACC15', 'unid': 'mm no dia'}}


paineis = [
    painel('f2', 'SUDOESTE DO PARANÁ · HOJE', 'Começa a limpeza', 'Rios fora do leito'),
    contador('f7', 'PR · HOJE · PREVISÃO', 100, 'Limite do aviso laranja', em('f7', '50') - 1),
    contador('f7', 'PR · QUINTA · PREVISÃO', 50, 'Limite do aviso amarelo'),
    contador('f8', 'SC · HOJE · PREVISÃO', 100, 'Nas áreas em aviso laranja', em('f8', '50') - 1),
    contador('f8', 'SC · QUINTA · PREVISÃO', 50, 'Nas áreas em aviso amarelo'),
    contador('f9', 'RS · HOJE · PREVISÃO', 50, 'Limite do aviso amarelo', em('f9', 'sexta') - .24),
    painel('f10', 'OESTE E SUDOESTE DO PR · PREVISÃO', 'Pode voltar a chover forte', 'Evite travessias alagadas'),
    painel('f11', 'COMENTA AQUI', 'DE ONDE VOCÊ É?', 'COMO ESTÁ AÍ?'),
]
for fid, lugar, linha in [
    ('f3', 'SANTA IZABEL DO OESTE / PR', 'Ponte submersa'),
    ('f4', 'SANTO ANTÔNIO DO SUDOESTE / PR', 'Resgate em uma banheira'),
    ('f5', 'AMPÉRE / PR', 'Barco vira na rua alagada'),
]:
    for a, b in registros.get(fid, []):
        a, b = max(a, ini(fid)), min(b, fim(fid))
        if b - a >= .8:
            paineis.append({'ini': a, 'fim': b, 'k': lugar, 'itens': [{'t': a, 'txt': linha}]})
sexta = em('f9', 'sexta') - .24
paineis.append({'ini': sexta, 'fim': fim('f9'), 'k': 'RS · SEXTA · PREVISÃO',
                'itens': [{'t': sexta, 'txt': 'Volta o aviso de chuva intensa'}]})
sistema = max(ini('f6'), MAP1)
if fim('f6') - sistema > .6:
    paineis.append({'ini': sistema, 'fim': fim('f6'), 'k': 'CHUVA AVANÇA DO PARAGUAI',
                    'itens': [{'t': sistema, 'txt': 'Aviso laranja até 23h59'}]})

paineis.sort(key=lambda p: p['ini'])
for p, proximo in zip(paineis, paineis[1:]):
    p['fim'] = min(p['fim'], proximo['ini'])
paineis[0]['ini'] = max(CAPA, paineis[0]['ini'])
if MAP1 > MAP0:
    for p in paineis:
        if p['ini'] < MAP0 < p['fim']:
            p['fim'] = MAP0
paineis = [p for p in paineis if p['fim'] > p['ini']]
# No canto, o cartão deixa a imagem real e o avatar visíveis.
cta = {'ini': ini('f12'), 'fim': DUR, 'a': 'APRENDA IA', 'b': 'inema.club', 'img': False}
assert em('f12', 'inema.club') < DUR

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "gelo": "#5ec8ff", "nino": "#5ec8ff",
         "calor": "#ff8c1a", "dispararam": "#ff8c1a", "graus": "#ff8c1a", "combustivel": "#ff8c1a", "arrancaram": "#ff2a1f",
         "tempestade": "#ff2a1f", "tempestades": "#ff2a1f", "granizo": "#ff2a1f", "estragos": "#ff2a1f", "telhados": "#ff2a1f",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "dispara": "#ff8c1a", "atencao": "#ff8c1a", "atento": "#ff8c1a", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "oeste", "norte", "santa", "catarina", "parana", "paraguai", "inemaclub", "cidade"}
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
    'selo': f'INMET{" · NOAA" if SAT else ""} · {DATA}',
    'camera': camera, 'sat': SAT, 'telas': telas, 'estados': estados, 'alertas': alertas,
    'pinos': pinos, 'hero': [], 'paineis': paineis, 'cta': cta,
    'fontes': fontes, 'legenda': legenda,
}
(AQUI / 'cena.js').write_text('window.CENA=' + json.dumps(C, ensure_ascii=False) + ';\n')
print(f'cena.js: {DUR:.2f} s, {len(telas)} telas, {len(clipes)} cenas fortes, mapa {MAP0:.2f}–{MAP1:.2f} s')
