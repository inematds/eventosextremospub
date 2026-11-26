#!/usr/bin/env python3
"""Gera a cena vertical de 26/11/2026. --canto usa os tempos do avatar."""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "26/11/2026"
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
DIA = '2026-11-26'
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
    return local.strftime('%d/%m %Hh%M')


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
assert (brasil, len(sensores)) == (17120.50, 1470)
assert [(uf, round(v, 2)) for uf, v in ranking] == [('SP', 6091.54), ('RJ', 4263.02), ('MG', 4210.47)]

locais = {
    'f2': ('Angra dos Reis', -44.32, -23.01, 3428, 168.84, 'chuva', 2),
    'f3': ('Aparecida', -45.23, -22.85, 4337, 96.2, '96,2', 1),
    'f4': ('Corumbá', -57.65, -19.01, 7916, 93.4, '93,4', 1),
    'f5': ('Timbó', -49.27, -26.82, 4043, 28.06, '28', 2),
}
for cidade, _, _, sensor, valor, _, _ in locais.values():
    x, _, v = sensores[sensor]
    assert cidade.upper() == x['cidade'] and v == valor

avisos = json.loads((B / 'inmet_avisos_ativos.json').read_text())


def aviso(grupo, data, tipo, severidade, esperado):
    dia = [a for a in avisos[grupo] if a['inicio'][:10] == data
           and a['descricao'] == tipo and a['severidade'] == severidade]
    assert len(dia) == 1
    a = dia[0]
    codigos = set(filter(None, a['geocodes'].split(',')))
    assert (a['id'], len(codigos)) == esperado
    return a, codigos


laranja, cod_laranja = aviso('hoje', DIA, 'Chuvas Intensas', 'Perigo', (56503, 1278))
amarelo, cod_amarelo = aviso('hoje', DIA, 'Chuvas Intensas', 'Perigo Potencial', (56502, 2768))
seco, cod_seco = aviso('hoje', DIA, 'Baixa Umidade', 'Perigo Potencial', (56507, 589))
sexta, cod_sexta = aviso('futuro', '2026-11-27', 'Chuvas Intensas', 'Perigo Potencial', (56505, 1225))
assert {c[:2] for c in cod_laranja} == {'31', '32', '33', '35', '50', '52'}

focos = {}
ref = 0
ref_pa = 0
with (B / 'inpe_focos_diario_br_20261125.csv').open() as f:
    for linha in csv.DictReader(f):
        assert linha['data_hora_gmt'].startswith('2026-11-25')
        if linha['satelite'] != 'AQUA_M-T':
            continue
        ref += 1
        ref_pa += linha['estado'] == 'PARÁ'
        lat, lon = float(linha['lat']), float(linha['lon'])
        focos.setdefault((round(lat / .05), round(lon / .05)), [lon, lat])
assert (ref, ref_pa) == (1811, 1488)

metar = next(x for x in json.loads((B / 'noaa_metar_brasil_24h.json').read_text())
             if x['icaoId'] == 'SBTE' and x['temp'] == 40 and
             datetime.fromtimestamp(x['obsTime'], timezone.utc).isoformat() == '2026-11-25T19:00:00+00:00')
teresina = metar['lon'], metar['lat']

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
assert total7 == 1030.3
assert abs(sum(regioes.values()) - total7) < .2
assert abs(sum(d['soma_chuva_mm'] for d in dias) - total7) < .2
pico_chuva = max(dias, key=lambda d: d['soma_chuva_mm'])
assert (pico_chuva['dia'], pico_chuva['soma_chuva_mm']) == ('2026-11-28', 201.1)
assert max(regioes, key=regioes.get) == 'SE' and regioes['SE'] == 381.5
assert max(d['tmax_pico'] for d in dias) == [40.4, 'Teresina']
vitoria = next(x['daily'] for x in json.loads((B / 'openmeteo_capitais_3d.json').read_text())
              if -20.4 < x['latitude'] < -20.2 and -40.4 < x['longitude'] < -40.2)
assert vitoria['time'][:2] == p7['dias'][:2] and vitoria['precipitation_sum'][:2] == [65.9, 58.7]

amanha = em('f8', 'amanhã')
br = (-53, -13, 5.5)
vistas = {
    'f1': (-51, -17, 5.55), 'f6': (-52, -5, 5.75), 'f7': (*teresina, 5.75),
    'f8': (-48, -20, 5.65), 'f9': br, 'f10': (-51, -17, 5.55), 'f11': br, 'f12': br,
}
for fid, (_, lon, lat, *_) in locais.items():
    vistas[fid] = (lon, lat, 5.9)


def vista(t, v, pitch=0, rumo=0):
    lon, lat, zoom = v
    return {'t': t, 'lon': lon, 'lat': lat, 'zoom': zoom, 'pitch': pitch, 'bearing': rumo}


camera = [vista(0, vistas['f1'])]
for t in T:
    fid, a, b = t['id'], t['ini'], t['fim']
    lon, lat, zoom = vistas[fid]
    if fid != 'f1':
        camera.append(vista(a + min(.38, (b-a)/4), vistas[fid], 7))
    if fid == 'f8':
        camera.append(vista(amanha + min(.5, (b-amanha)/3), (-49, -22, 5.65), 9))
        lon, lat = -49, -22
    camera.append(vista(b - min(.24, (b-a)/5), (lon, lat, zoom+.07), 9, 1))
assert all(a['t'] < b['t'] for a, b in zip(camera, camera[1:]))

horas = json.loads((AQUI / 'sat/web/ir_tempos.json').read_text())
assert len(horas) == 49 and horas[0] == '2026-11-25T08:00:00Z' and horas[-1] == '2026-11-26T08:00:00Z'
quadros = [f'sat/web/ir{i:02d}-suave.png' for i in range(len(horas))]
assert all((AQUI / f).is_file() for f in [*quadros, 'sat/web/mundo.jpg', 'sat/web/geocolor-suave.png'])
sat = {
    'fundo': {'src': 'sat/web/mundo.jpg', 'bbox': [-180, -60, 180, 75], 'tint': [170, 170, 175]},
    'base': 'sat/web/geocolor-suave.png', 'bbox': [-76, -35, -33, 7], 'tint': [170, 170, 175],
    'ir': {'frames': quadros, 'tempos': [b_rt(datetime.fromisoformat(h.replace('Z', '+00:00'))) for h in horas],
           'ini': 0, 'fim': ini('f2'), 'dur': max(.5, ini('f2')-.3), 'alfa': .9, 'rotulo': 'GOES-19 · IR · 25–26/11'},
}


def seguinte(fid):
    return ini(f'f{int(fid[1:])+1}')


def estado(id_, ufs, a, b, cor, alfa=.28):
    return {'id': id_, 'ufs': ufs, 'ini': a, 'fim': b, 'cor': cor, 'alfa': alfa}


def pin(nome, sub, lon, lat, a, b):
    return {'nome': nome, 'sub': sub, 'lon': lon, 'lat': lat, 'ini': a, 'fim': b, 'h': 46}


def formato(valor, dec=0):
    return f'{valor:,.{dec}f}'.translate(str.maketrans(',.', '.,'))


def contagem(valor, unid, fim_anim, inicio_painel, cor=AZUL, dec=0):
    inicio = max(inicio_painel, fim_anim - 1)
    return {'de': 0, 'ate': valor, 'unid': unid, 'ini': inicio, 'dur': max(.1, fim_anim-inicio),
            'cor': cor, 'dec': dec}


ufs_laranja = ['ES', 'GO', 'MG', 'MS', 'RJ', 'SP']
estados = [estado('abertura', ufs_laranja, -.7, ini('f2'), [255, 140, 26])]
pinos, paineis = [], []
fontes = [{'ini': 0, 'fim': ini('f2'), 'html': '<b>Agência Brasil · CEMADEN · INMET 56503</b> | Satélite: NASA GIBS / GOES-19'}]
for fid, (cidade, lon, lat, sensor, valor, palavra, dec) in locais.items():
    x, t, _ = sensores[sensor]
    a, b = ini(fid), seguinte(fid)
    estados.append(estado(fid, [x['uf']], a, b, [60, 150, 255]))
    pinos.append(pin(f'{cidade} ({x["uf"]})', 'Pluviômetro CEMADEN', lon, lat, a+.2, b))
    paineis.append({'ini': a, 'fim': b, 'k': f'CHUVA MEDIDA · {cidade}',
                    'contador': contagem(valor, 'MM EM 24 H', em(fid, palavra), a, dec=dec),
                    'l': x['nomeestacao']})
    fontes.append({'ini': a, 'fim': b, 'html': f'<b>CEMADEN</b> · sensor {sensor} · {b_rt(t)} BRT'})

a6, a7, a8, a9, a10, a11, a12 = (ini(f'f{i}') for i in range(6, 13))
estados += [
    estado('pa', ['PA'], a6, a7, [255, 140, 26]),
    estado('pi', ['PI'], a7, a8, [255, 42, 31]),
    estado('chuva-26', ufs_laranja, a8, amanha, [255, 140, 26], .38),
    estado('chuva-27', ['GO', 'MG', 'MS', 'MT', 'PR', 'RS', 'SC', 'SP'], amanha, a9, [250, 204, 21], .34),
]
pontos = [{'id': 'fogo', 'ini': a6, 'fim': a7, 'dados': [{'p': p, 'i': i} for i, p in enumerate(focos.values())],
           'dur': 1.8, 'raio': 2.4, 'cor': [255, 100, 26]}]
pinos.append(pin('Teresina (PI)', 'Aeroporto · NOAA', *teresina, a7+.2, a8))
hero = [{
    'ini': 0, 'fim': ini('f2')-.05,
    'html': f'<div class="t1" style="font-size:118px;margin-bottom:18px">{DATA}</div>'
            '<div class="t3" style="margin-top:0">168,84 MM</div>'
            '<div class="t4">CHUVA MEDIDA EM ANGRA (RJ)</div>'
            '<div class="t4" style="margin-top:18px">Rio suspende aulas<br><span style="color:#fb923c">Alerta laranja em 6 estados</span></div>',
}]
k_7d = 'CHUVA PREVISTA · 7 DIAS' if CANTO else 'CHUVA PREVISTA · 7 DIAS · 27 CAPITAIS'
paineis += [
    {'ini': a6, 'fim': a7, 'k': 'FOCOS DETECTADOS · PARÁ',
     'contador': contagem(ref_pa, 'FOCOS', em('f6', '1.488'), a6, LARANJA),
     'itens': [{'t': em('f6', 'focos'), 'txt': f'Brasil: {formato(ref)} focos'}],
     'l': 'INPE · AQUA · dia 25/11 UTC'},
    {'ini': a7, 'fim': a8, 'k': 'CALOR MEDIDO · TERESINA',
     'contador': contagem(40, '°C', em('f7', '40'), a7, VERMELHO),
     'l': 'Aeroporto · 25/11 às 16h BRT'},
    {'ini': a8, 'fim': amanha, 'k': 'HOJE · ALERTA LARANJA',
     'contador': contagem(len(cod_laranja), 'MUNICÍPIOS', em('f8', 'laranja'), a8, LARANJA),
     'itens': [{'t': a8+.3, 'txt': 'Vitória: 65,9 mm previstos'}],
     'l': 'Até 23h59 · INMET e Open-Meteo'},
    {'ini': amanha, 'fim': a9, 'k': 'AMANHÃ · AVISO AMARELO',
     'contador': contagem(len(cod_sexta), 'MUNICÍPIOS', em('f8', 'amarelo'), amanha, AMARELO),
     'itens': [{'t': amanha+.3, 'txt': 'Vitória: 58,7 mm previstos'}],
     'l': 'PR, SC e RS entre as áreas no aviso'},
    {'ini': a9, 'fim': a10, 'k': k_7d,
     'contador': contagem(int(total7), 'MM SOMADOS', em('f9', 'sábado'), a9),
     'grafico': {'rotulos': rotulos, 'series': series, 'marcar': [], 'marcar_x': list(range(7)),
                 'previsto_a_partir': 0, 'ini': a9+.3, 'dur': 1.6,
                 'linha': {'nome': 'Máx. média (°C)<style>.graf circle+text{display:none}</style>',
                           'cor': VERMELHO, 'v': [d['tmax_media'] for d in dias]}},
     'itens': [{'t': em('f9', 'sábado'), 'txt': 'Sábado: 201,1 mm'},
               {'t': em('f9', 'Sudeste'), 'txt': 'Sudeste: 381,5 mm'},
               {'t': em('f9', 'Teresina'), 'txt': 'Teresina: até 40,4 °C'}],
     'l': 'Open-Meteo · soma das capitais'},
    {'ini': a10, 'fim': a11, 'k': 'SOMA DOS PLUVIÔMETROS · 24 H',
     'contador': contagem(int(brasil), 'MM·ESTAÇÃO', em('f10', '17.120'), a10),
     'ranking': {'itens': [{'nome': uf, 'v': int(v)} for uf, v in ranking], 'cor': AZUL,
                 'unid': '', 'ini': a10+.3, 'dur': 1.0},
     'itens': [{'t': em('f10', '1.030'), 'txt': '7 dias nas capitais: 1.030 mm previstos'}],
     'l': 'CEMADEN · 1.470 sensores'},
    {'ini': a11, 'fim': a12, 'k': 'COMENTA AQUI',
     'itens': [{'t': em('f11', 'região'), 'txt': 'Sua região?'}, {'t': em('f11', 'cidade'), 'txt': 'Sua cidade?'}]},
]
if CANTO:
    for p in paineis:
        if p['ini'] in (a8, amanha):
            p['contador']['unid'] = 'CIDADES'
        if p['ini'] == a9:
            p['itens'] = []
        if p['ini'] == a10:
            p['itens'][0]['txt'] = 'Capitais · 7 dias: 1.030 mm'
for p in paineis:
    if p.get('ranking'):
        p['l'] += '<style>.painel .rk .r .nm{flex:0 0 18%}</style>'
for p in paineis:
    c = p.get('contador')
    if c:
        assert p['ini'] <= c['ini'] < c['ini'] + c['dur'] < p['fim']

fontes += [
    {'ini': a6, 'fim': a7, 'html': '<b>INPE Queimadas</b> · AQUA_M-T · 25/11 UTC'},
    {'ini': a7, 'fim': a8, 'html': '<b>NOAA METAR</b> · SBTE · 25/11 às 19h UTC'},
    {'ini': a8, 'fim': amanha, 'html': '<b>INMET 56503</b> · 56502 (chuva amarela) · 56507 (baixa umidade)<br><b>Open-Meteo</b> · previsão para Vitória'},
    {'ini': amanha, 'fim': a9, 'html': '<b>INMET 56505</b> · 27/11 · <b>Open-Meteo</b> · previsão para Vitória'},
    {'ini': a9, 'fim': a10, 'html': '<b>Open-Meteo</b> · 26/11–02/12 · 27 capitais<br>Sábado 201,1 mm · Sudeste 381,5 mm · Teresina até 40,4 °C'},
    {'ini': a10, 'fim': a11, 'html': '<b>CEMADEN</b> · mm·estação · <b>Open-Meteo</b> · previsão nas capitais'},
    {'ini': a11, 'fim': a12, 'html': f'CLIMA 24 H · {DATA}'},
]
cta = {'ini': a12, 'fim': DUR, 'a': 'APRENDA IA', 'b': 'inema.club', 'img': False}

cores = {**dict.fromkeys(('chuva', 'milimetros', 'pluviometro', 'pluviometros', 'somados'), AZUL),
         **dict.fromkeys(('laranja', 'intensa', 'alerta', 'focos'), LARANJA),
         **dict.fromkeys(('calor', 'graus'), VERMELHO),
         **dict.fromkeys(('amarelo', 'comenta', 'inteligencia', 'artificial', 'inemaclub'), AMARELO)}
lugares = {'angra', 'rio', 'aparecida', 'corumba', 'timbo', 'para', 'teresina', 'sudeste', 'sabado', 'vitoria'}
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
    'camera': camera, 'sat': sat, 'estados': estados, 'pontos': pontos, 'pinos': pinos,
    'hero': hero, 'paineis': paineis, 'cta': cta, 'fontes': fontes, 'legenda': legenda,
}
(AQUI / 'cena.js').write_text('window.CENA=' + json.dumps(C, ensure_ascii=False) + ';')
print(f'cena.js · {DUR} s · {len(legenda)} blocos · IR {len(quadros)} quadros · '
      f'INMET {len(cod_laranja)}/{len(cod_sexta)} · INPE {ref_pa}/{ref} · previsão {total7} mm')
