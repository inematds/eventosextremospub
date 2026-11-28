#!/usr/bin/env python3
"""Gera a cena vertical de 28/11/2026. --canto usa os tempos do avatar."""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
DATA = "28/11/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
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


ROT = {f["id"]: f["legenda"] for f in json.loads((AQUI / "falas.json").read_text())}
assert [t["id"] for t in T] == list(ROT)
assert all(t["palavras"] for t in T)
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
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
DIA = '2026-11-28'
DIAS = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']
AZUL = '#5ec8ff'
LARANJA = '#fb923c'
AMARELO = '#facc15'
VERMELHO = '#ff2a1f'
R = json.loads((B / 'resumo.json').read_text())
CORTE = datetime.fromisoformat(R['janela_utc'][1])
assert CORTE.date().isoformat() == DIA


def b_rt(utc):
    local = utc.astimezone(timezone(timedelta(hours=-3)))
    return local.strftime('%d/%m · %Hh%M')


sensores = {}
soma = {}
for x in json.loads((B / 'cemaden_getJson2_todas_ufs.json').read_text()):
    try:
        t = datetime.strptime(x['datahoraUltimovalor'], '%d/%m/%y %H:%M').replace(tzinfo=timezone.utc)
        valor = float(x['acc24hr'])
    except (KeyError, ValueError, TypeError):
        continue
    if x['tipoestacao'] == 1 and CORTE - timedelta(hours=6) < t <= CORTE and valor >= 0:
        assert x['idestacao'] not in sensores
        sensores[x['idestacao']] = (x, t, valor)
        soma[x['uf']] = soma.get(x['uf'], 0) + valor

brasil = round(sum(soma.values()), 2)
ranking = sorted(soma.items(), key=lambda x: -x[1])[:3]
assert (brasil, len(sensores)) == (7727.71, 1318)
assert [(uf, round(v, 2)) for uf, v in ranking] == [('MG', 1577.65), ('RS', 1305.20), ('PR', 1109.42)]

locais = {
    'f2': ('Porto Vera Cruz', -54.89, -27.74, 17072, 96.2, '96,2'),
    'f3': ('Ipuã', -48.02, -20.44, 19808, 82.8, '82,8'),
    'f4': ('Manoel Urbano', -69.26, -8.84, 17606, 66.4, '66,4'),
    'f5': ('Aparecida de Goiânia', -49.25, -16.76, 6763, 47.8, '47,8'),
}
for cidade, _, _, sensor, valor, _ in locais.values():
    x, _, v = sensores[sensor]
    assert cidade.upper() == x['cidade'] and v == valor

# O arquivo de 27/11 preserva o aviso que já havia sido emitido para 28/11.
# Se o serviço voltou, só os avisos vigentes no corte da edição entram no mapa.
arquivo_atual = B / 'inmet_avisos_ativos.json'
fonte_avisos = arquivo_atual if arquivo_atual.is_file() else B / 'inmet_avisos_arquivo_20261127.json'
avisos = json.loads(fonte_avisos.read_text())
corte_local = CORTE.astimezone(timezone(timedelta(hours=-3))).strftime('%Y-%m-%d %H:%M')
chuva_inmet = [a for grupo in ('hoje', 'futuro') for a in avisos[grupo]
               if a['descricao'] == 'Chuvas Intensas'
               and a['inicio'] <= corte_local <= a['fim']]
assert chuva_inmet
if fonte_avisos != arquivo_atual:
    assert len(chuva_inmet) == 1
    a = chuva_inmet[0]
    assert (a['id'], a['severidade'], a['inicio'], a['fim']) == (
        56516, 'Perigo Potencial', DIA + ' 00:00', DIA + ' 23:59')
    assert len(set(filter(None, a['geocodes'].split(',')))) == 1142

focos = {'MARANHÃO': {}, 'PARÁ': {}}
ref = 0
contados = dict.fromkeys(focos, 0)
with (B / 'inpe_focos_diario_br_20261127.csv').open() as f:
    for linha in csv.DictReader(f):
        assert linha['data_hora_gmt'].startswith('2026-11-27')
        if linha['satelite'] != 'AQUA_M-T':
            continue
        ref += 1
        uf = linha['estado']
        if uf in focos:
            contados[uf] += 1
            lat, lon = float(linha['lat']), float(linha['lon'])
            focos[uf].setdefault((round(lat / .05), round(lon / .05)), [lon, lat])
assert ref == 1908 and contados == {'MARANHÃO': 603, 'PARÁ': 775}

p7 = json.loads((B / 'previsao7d.json').read_text())
d0 = datetime.fromisoformat(DIA)
assert p7['dias'] == [(d0 + timedelta(days=i)).date().isoformat() for i in range(7)]
rotulos = [DIAS[datetime.fromisoformat(d).weekday()] for d in p7['dias']]
dias = p7['por_dia']
regioes = p7['soma_7d_por_regiao_mm']
total7 = p7['soma_7d_mm']
reg_cores = [('N', '#2dd4bf'), ('NE', AMARELO), ('CO', LARANJA), ('SE', '#f472b6'), ('S', AZUL)]
series = [{'nome': r, 'cor': c, 'v': [d['por_regiao_mm'][r] for d in dias]} for r, c in reg_cores]
assert [d['dia'] for d in dias] == p7['dias']
for i, d in enumerate(dias):
    assert abs(sum(s['v'][i] for s in series) - d['soma_chuva_mm']) < .2
for s in series:
    assert abs(sum(s['v']) - regioes[s['nome']]) < .2
assert total7 == 983.0
assert abs(sum(regioes.values()) - total7) < .2
assert abs(sum(d['soma_chuva_mm'] for d in dias) - total7) < .2
pico_chuva = max(dias, key=lambda d: d['soma_chuva_mm'])
assert (pico_chuva['dia'], pico_chuva['soma_chuva_mm']) == ('2026-12-04', 232.6)
assert max(regioes, key=regioes.get) == 'N' and regioes['N'] == 346.2
assert max(d['tmax_pico'] for d in dias) == [40.0, 'Teresina']

capitais = json.loads((B / 'openmeteo_capitais_3d.json').read_text())
sp, rio = capitais[19], capitais[18]
assert -24 < sp['latitude'] < -23 and -23.1 < rio['latitude'] < -22.8
assert sp['daily']['time'][0] == p7['dias'][0] and sp['daily']['precipitation_sum'][0] == 43.7
assert rio['daily']['time'][1] == p7['dias'][1] and rio['daily']['precipitation_sum'][1] == 23.6

br = (-53, -13, 4.4)
amanha = em('f8', 'Amanhã')
mapa_brasil = em('f7', 'Brasil')
vistas = {
    'f1': (-52.3, -24.0, 4.65), 'f6': (-45.5, -5.4, 5.45), 'f7': (-51.8, -5.1, 5.05),
    'f8': (sp['longitude'], sp['latitude'], 5.7), 'f9': br, 'f10': br, 'f11': br, 'f12': br,
}
for fid, (_, lon, lat, *_) in locais.items():
    vistas[fid] = (lon, lat, 5.95)


def vista(t, v, pitch=0):
    lon, lat, zoom = v
    return {'t': t, 'lon': lon, 'lat': lat, 'zoom': zoom, 'pitch': pitch}


camera = [vista(0, vistas['f1'])]
for t in T:
    fid, a, b = t['id'], t['ini'], t['fim']
    v = vistas[fid]
    if fid != 'f1':
        camera.append(vista(a + min(.38, (b-a)/6), v, 6))
    if fid == 'f7':
        camera.append(vista(mapa_brasil - .45, v, 6))
        v = br
        camera.append(vista(mapa_brasil + .65, v, 6))
    if fid == 'f8':
        camera.append(vista(amanha - min(.3, (amanha-a)/4), v, 6))
        v = (rio['longitude'], rio['latitude'], 5.85)
        camera.append(vista(amanha + min(.5, (b-amanha)/3), v, 7))
    lon, lat, zoom = v
    camera.append(vista(b - min(.24, (b-a)/5), (lon, lat, zoom+.07), 7))
assert all(a['t'] < b['t'] for a, b in zip(camera, camera[1:]))

horas = json.loads((AQUI / 'sat/web/ir_tempos.json').read_text())
assert len(horas) == 49 and horas[0] == '2026-11-27T08:00:00Z' and horas[-1] == '2026-11-28T08:00:00Z'
ir = [(f'sat/web/ir{i:02d}-suave.png', h) for i, h in enumerate(horas) if i not in {23, 39, 44}]
assert len(ir) == 46
quadros = [f for f, _ in ir]
assert all((AQUI / f).is_file() for f in [*quadros, 'sat/web/mundo.jpg', 'sat/web/geocolor-suave.png'])
sat = {
    'fundo': {'src': 'sat/web/mundo.jpg', 'bbox': [-180, -60, 180, 75], 'tint': [170, 170, 175]},
    'base': 'sat/web/geocolor-suave.png', 'bbox': [-76, -35, -33, 7], 'tint': [170, 170, 175],
    'ir': {'frames': quadros, 'tempos': [b_rt(datetime.fromisoformat(h.replace('Z', '+00:00'))) for _, h in ir],
           'ini': 0, 'fim': ini('f2'), 'dur': max(.5, ini('f2')-.3), 'alfa': .89, 'rotulo': 'GOES-19 · IR · 27–28/11'},
}


def seguinte(fid):
    return ini(f'f{int(fid[1:])+1}')


def estado(id_, ufs, a, b, cor, alfa=.28):
    return {'id': id_, 'ufs': ufs, 'ini': a, 'fim': b, 'cor': cor, 'alfa': alfa}


def pin(nome, sub, lon, lat, a, b):
    return {'nome': nome, 'sub': sub, 'lon': lon, 'lat': lat, 'ini': a, 'fim': b, 'h': 46}


def contagem(valor, unid, fim_anim, inicio_painel, cor=AZUL, dec=0):
    inicio = max(inicio_painel, fim_anim - 1)
    return {'de': 0, 'ate': valor, 'unid': unid, 'ini': inicio, 'dur': max(.1, fim_anim-inicio),
            'cor': cor, 'dec': dec}


a6, a7, a8, a9, a10, a11, a12 = (ini(f'f{i}') for i in range(6, 13))
estados = [
    estado('abertura', ['RS', 'SP'], -.7, ini('f2'), [60, 150, 255], .26),
    estado('ma', ['MA'], a6, a7, [255, 140, 26]),
    estado('pa', ['PA'], a7, mapa_brasil, [255, 140, 26]),
    estado('sp-prev', ['SP'], a8, amanha, [250, 204, 21], .20),
    estado('rj-prev', ['RJ'], amanha, a9, [94, 200, 255], .24),
]

imagens = []
cores_aviso = {'Perigo Potencial': (250, 204, 21), 'Perigo': (251, 146, 60),
               'Grande Perigo': (255, 42, 31)}
for a in sorted(chuva_inmet, key=lambda x: list(cores_aviso).index(x['severidade'])):
    geo = json.loads(a['poligono'])
    assert geo['type'] in {'Polygon', 'MultiPolygon'}
    polys = [geo['coordinates']] if geo['type'] == 'Polygon' else geo['coordinates']
    coords = [p for rings in polys for p in rings[0]]
    x0, y0 = min(p[0] for p in coords), min(p[1] for p in coords)
    x1, y1 = max(p[0] for p in coords), max(p[1] for p in coords)
    w = h = 1024
    mask = Image.new('L', (w, h))
    draw = ImageDraw.Draw(mask)
    for rings in polys:
        for i, ring in enumerate(rings):
            px = [((x-x0)/(x1-x0)*(w-1), (y1-y)/(y1-y0)*(h-1)) for x, y in ring]
            draw.polygon(px, fill=145 if i == 0 else 0)
    img = Image.new('RGB', (w, h), cores_aviso[a['severidade']])
    img.putalpha(mask)
    src = f"sat/web/aviso-{a['id']}.png"
    img.save(AQUI / src)
    imagens.append({'src': src, 'bbox': [x0, y0, x1, y1], 'ini': a8,
                    'fim': amanha, 'alfa': .78})
ids_inmet = ', '.join(str(a['id']) for a in chuva_inmet)

pinos = [
    pin('São Paulo (SP)', 'Previsão de sábado', sp['longitude'], sp['latitude'], a8+.2, amanha),
    pin('Rio de Janeiro (RJ)', 'Previsão de domingo', rio['longitude'], rio['latitude'], amanha+.2, a9),
]
paineis = []
fontes = [{
    'ini': 0, 'fim': ini('f2'),
    'html': '<b>CEMADEN · Open-Meteo</b> | Satélite: NASA GIBS / GOES-19',
}]
for fid, (cidade, lon, lat, sensor, valor, palavra) in locais.items():
    x, t, _ = sensores[sensor]
    a, b = ini(fid), seguinte(fid)
    estados.append(estado(fid, [x['uf']], a, b, [60, 150, 255]))
    pinos.append(pin(f'{cidade} ({x["uf"]})', 'Pluviômetro CEMADEN', lon, lat, a+.2, b))
    paineis.append({'ini': a, 'fim': b, 'k': f'CHUVA MEDIDA · {cidade}',
                    'contador': contagem(valor, 'MM EM 24 H', em(fid, palavra), a, dec=1),
                    'l': x['nomeestacao']})
    fontes.append({'ini': a, 'fim': b, 'html': f'<b>CEMADEN</b> · sensor {sensor} · {b_rt(t)} BRT'})

pontos = [
    {'id': uf, 'ini': a, 'fim': b,
     'dados': [{'p': p, 'i': i} for i, p in enumerate(focos[uf].values())],
     'dur': 1.5, 'raio': 3, 'cor': [255, 100, 26]}
    for uf, a, b in [('MARANHÃO', a6, a7), ('PARÁ', a7, mapa_brasil)]
]
hero = [{
    'ini': 0, 'fim': ini('f2')-.05,
    'html': f'<div class="t1" style="font-size:118px;margin-bottom:18px">{DATA}</div>'
            '<div class="t3" style="margin-top:0">96,2 MM</div>'
            '<div class="t4">CHUVA EM PORTO VERA CRUZ (RS)</div>'
            '<div class="t4" style="margin-top:18px">Ipuã (SP): 82,8 mm<br>Capital paulista: chuva forte prevista</div>',
}]
paineis += [
    {'ini': a6, 'fim': a7, 'k': 'FOCOS DE CALOR · MARANHÃO',
     'contador': contagem(contados['MARANHÃO'], 'FOCOS', em('f6', '603'), a6, LARANJA),
     'l': 'INPE · satélite de referência · 27/11 UTC'},
    {'ini': a7, 'fim': mapa_brasil, 'k': 'FOCOS DE CALOR · PARÁ',
     'contador': contagem(contados['PARÁ'], 'FOCOS', em('f7', '775'), a7, LARANJA),
     'l': 'INPE · satélite de referência · 27/11 UTC'},
    {'ini': mapa_brasil, 'fim': a8, 'k': 'FOCOS DE CALOR · BRASIL',
     'contador': contagem(ref, 'FOCOS', em('f7', '1.908'), mapa_brasil, LARANJA),
     'l': 'INPE · satélite de referência · 27/11 UTC'},
    {'ini': a8, 'fim': amanha, 'k': 'SÁBADO · SÃO PAULO',
     'contador': contagem(43.7, 'MM PREVISTOS', em('f8', '43,7'), a8, AMARELO, 1),
     'itens': [{'t': em('f8', 'aviso'), 'txt': 'INMET · chuva intensa'}],
     'l': 'Open-Meteo · previsão para a capital'},
    {'ini': amanha, 'fim': a9, 'k': 'DOMINGO · RIO DE JANEIRO',
     'contador': contagem(23.6, 'MM PREVISTOS', em('f8', '23,6'), amanha, AZUL, 1),
     'l': 'Open-Meteo · previsão para a capital'},
    {'ini': a9, 'fim': a10, 'k': 'CHUVA PREVISTA · 7 DIAS' if CANTO else 'CHUVA PREVISTA · 7 DIAS · 27 CAPITAIS',
     'contador': contagem(int(total7), 'MM SOMADOS', em('f9', 'dias'), a9),
     'grafico': {'rotulos': rotulos, 'series': series, 'marcar': [], 'marcar_x': list(range(7)),
                 'previsto_a_partir': 0, 'ini': a9+.3, 'dur': 1.6,
                 'linha': {'nome': 'Máx. média (°C)<style>.graf circle+text{display:none}</style>',
                           'cor': VERMELHO, 'v': [d['tmax_media'] for d in dias]}},
     'itens': [] if CANTO else [
         {'t': em('f9', 'sexta'), 'txt': 'Sexta (04/12): 232,6 mm'},
         {'t': em('f9', 'Norte'), 'txt': 'Norte: 346,2 mm'},
         {'t': em('f9', 'Teresina'), 'txt': 'Teresina: até 40 °C'},
     ],
     'l': 'Open-Meteo · soma das capitais'},
    {'ini': a10, 'fim': a11, 'k': 'SOMA DOS PLUVIÔMETROS · 24 H',
     'contador': contagem(int(brasil), 'MM·ESTAÇÃO', em('f10', '7.727'), a10),
     'ranking': {'itens': [{'nome': uf, 'v': int(v)} for uf, v in ranking], 'cor': AZUL,
                 'unid': '', 'ini': a10+.3, 'dur': 1.0},
     'itens': [{'t': em('f10', '983'), 'txt': 'Capitais: 983 mm' if CANTO else '7 dias nas capitais: 983 mm previstos'}],
     'l': 'CEMADEN · 1.318 pluviômetros<style>.painel .rk .r .nm{flex:0 0 18%}</style>'},
    {'ini': a11, 'fim': a12, 'k': 'COMENTA AQUI',
     'itens': [{'t': em('f11', 'região'), 'txt': 'Sua região?'}, {'t': em('f11', 'cidade'), 'txt': 'Sua cidade?'}]},
]
for p in paineis:
    c = p.get('contador')
    if c:
        assert p['ini'] <= c['ini'] < c['ini'] + c['dur'] < p['fim'], p['k']

fontes += [
    {'ini': a6, 'fim': a8, 'html': '<b>INPE Queimadas</b> · AQUA_M-T · 27/11 UTC'},
    {'ini': a8, 'fim': amanha, 'html': f'<b>INMET {ids_inmet}</b> · 28/11 · <b>Open-Meteo</b> · São Paulo'},
    {'ini': amanha, 'fim': a9, 'html': '<b>Open-Meteo</b> · 29/11 · Rio de Janeiro'},
    {'ini': a9, 'fim': a10, 'html': '<b>Open-Meteo</b> · 28/11–04/12 · 27 capitais<br>Sex 232,6 mm · Norte 346,2 mm · Teresina até 40 °C'},
    {'ini': a10, 'fim': a11, 'html': '<b>CEMADEN</b> · mm·estação · <b>Open-Meteo</b> · previsão nas capitais'},
    {'ini': a11, 'fim': a12, 'html': f'CLIMA 24 H · {DATA}'},
]
cta = {'ini': a12, 'fim': DUR, 'a': 'APRENDA IA', 'b': 'inema.club', 'img': False}

cores = {**dict.fromkeys(('chuva', 'milimetros', 'pluviometro', 'pluviometros', 'somados'), AZUL),
         **dict.fromkeys(('laranja', 'intensa', 'alerta', 'focos'), LARANJA),
         **dict.fromkeys(('alagamentos', 'calor', 'graus'), VERMELHO),
         **dict.fromkeys(('comenta', 'inteligencia', 'artificial', 'inemaclub'), AMARELO)}
lugares = {'porto', 'vera', 'cruz', 'ipua', 'manoel', 'urbano', 'acre', 'aparecida',
           'goiania', 'maranhao', 'para', 'paulo', 'rio', 'teresina', 'norte', 'sul'}
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t['palavras']):
        w = p['w']
        k = n(w)
        if bloco and sum(len(x['w']) + 1 for x in bloco) + len(w) > 19:
            legenda.append({'ini': bloco[0]['t']-.05, 'fim': p['t']+.12, 'palavras': bloco})
            bloco = []
        cor = cores.get(k) or (AMARELO if k in lugares else None) or (AZUL if re.search(r'\d', k) else None)
        bloco.append({'w': w, 't': p['t'], **({'cor': cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in '.?!,:' or i == len(t['palavras'])-1:
            legenda.append({'ini': bloco[0]['t']-.05, 'fim': p['f']+.12, 'palavras': bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a['fim'] = b['ini']

C = {
    'layout': 'canto' if CANTO else 'avatar' if AVATAR else 'cheio',
    'padding_topo': 520, 'padding_baixo': 640 if CANTO else 820, 'duracao': DUR,
    'marca': 'INEMA · CLIMA 24 H', 'selo': 'CEMADEN · INMET · INPE · ' + DATA[:5],
    'camera': camera, 'sat': sat, 'estados': estados, 'imagens': imagens, 'pontos': pontos, 'pinos': pinos,
    'hero': hero, 'paineis': sorted(paineis, key=lambda p: p['ini']), 'cta': cta, 'fontes': sorted(fontes, key=lambda f: f['ini']), 'legenda': legenda,
}
(AQUI / 'cena.js').write_text('window.CENA=' + json.dumps(C, ensure_ascii=False) + ';')
print(f'cena.js · {DUR} s · {len(legenda)} blocos · IR {len(quadros)} quadros · '
      f'INMET {ids_inmet} · INPE {ref} · previsão {total7} mm')
