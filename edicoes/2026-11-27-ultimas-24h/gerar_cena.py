#!/usr/bin/env python3
"""Gera a cena vertical de 27/11/2026. --canto usa os tempos do avatar."""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "27/11/2026"
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
DIA = '2026-11-27'
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
assert (brasil, len(sensores)) == (11742.59, 1293)
assert [(uf, round(v, 2)) for uf, v in ranking] == [('MG', 4238.63), ('RJ', 2339.41), ('ES', 1697.62)]

locais = {
    'f2': ('Iconha', -40.81, -20.79, 17331, 131.4, '131,4', 1),
    'f3': ('Petrópolis', -43.18, -22.51, 3321, 120.61, '120', 2),
    'f4': ('Rolim de Moura', -61.77, -11.73, 17360, 87.4, '87,4', 1),
    'f5': ('Coxim', -54.76, -18.50, 7917, 43.8, '43,8', 1),
    'f6': ('Ituporanga', -49.60, -27.41, 3992, 54.33, '54', 2),
}
for cidade, _, _, sensor, valor, _, _ in locais.values():
    x, _, v = sensores[sensor]
    assert cidade.upper() == x['cidade'] and v == valor

avisos = json.loads((B / 'inmet_avisos_ativos.json').read_text())
uf_por_codigo = dict(zip(
    ('21','22','23','24','25','26','27','28','29','31','32','33','35','41','42','43','50','51','52'),
    ('MA','PI','CE','RN','PB','PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO'),
))


def aviso(grupo, data, tipo, severidade, id_, quantidade, horario):
    candidatos = [a for a in avisos[grupo] if a['inicio'][:10] == data
                  and a['descricao'] == tipo and a['severidade'] == severidade]
    assert len(candidatos) == 1
    a = candidatos[0]
    codigos = set(filter(None, a['geocodes'].split(',')))
    assert (a['id'], len(codigos), a['inicio'][11:], a['fim'][11:]) == (id_, quantidade, *horario)
    return a, codigos, sorted({uf_por_codigo[c[:2]] for c in codigos})


laranja, cod_laranja, sul = aviso('hoje', DIA, 'Chuvas Intensas', 'Perigo', 56515, 233, ('09:40','23:59'))
amarelo, cod_amarelo, ufs_hoje = aviso('hoje', DIA, 'Chuvas Intensas', 'Perigo Potencial', 56513, 2154, ('09:30','23:59'))
seco, cod_seco, _ = aviso('hoje', '2026-11-26', 'Baixa Umidade', 'Perigo Potencial', 56512, 589, ('10:00','22:00'))
sabado, cod_sabado, ufs_amanha = aviso('futuro', '2026-11-28', 'Chuvas Intensas', 'Perigo Potencial', 56516, 1142, ('00:00','23:59'))
assert sul == ['PR', 'RS', 'SC']
assert seco['fim'][:10] == DIA and '4205407' in cod_sabado
assert any('50 e 100 mm/dia' in risco for risco in laranja['riscos'])

focos = {}
ref = 0
ref_ma = 0
with (B / 'inpe_focos_diario_br_20261126.csv').open() as f:
    for linha in csv.DictReader(f):
        assert linha['data_hora_gmt'].startswith('2026-11-26')
        if linha['satelite'] != 'AQUA_M-T':
            continue
        ref += 1
        ref_ma += linha['estado'] == 'MARANHÃO'
        lat, lon = float(linha['lat']), float(linha['lon'])
        focos.setdefault((round(lat / .05), round(lon / .05)), [lon, lat])
assert (ref, ref_ma) == (1167, 425)

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
assert total7 == 937.4
assert abs(sum(regioes.values()) - total7) < .2
assert abs(sum(d['soma_chuva_mm'] for d in dias) - total7) < .2
pico_chuva = max(dias, key=lambda d: d['soma_chuva_mm'])
assert (pico_chuva['dia'], pico_chuva['soma_chuva_mm']) == ('2026-12-03', 162.6)
assert max(regioes, key=regioes.get) == 'N' and regioes['N'] == 322.3
assert max(d['tmax_pico'] for d in dias) == [39.9, 'Teresina']

capitais = json.loads((B / 'openmeteo_capitais_3d.json').read_text())
floripa = capitais[21]
vitoria = capitais[17]
assert -27.8 < floripa['latitude'] < -27.3 and -20.4 < vitoria['latitude'] < -20.2
assert floripa['daily']['time'][1] == p7['dias'][1] and floripa['daily']['precipitation_sum'][1] == 30.6
assert vitoria['daily']['time'][0] == p7['dias'][0] and vitoria['daily']['precipitation_sum'][0] == 35.4

petropolis = em('f3', 'Em', 1)
amanha = em('f8', 'amanhã')
angra = (-44.32, -23.01)
br = (-53, -13, 5.0)
vistas = {
    'f1': (-48.7, -22.3, 5.15), 'f7': (-44.5, -6.1, 5.65),
    'f8': (-54.1, -27.2, 5.6), 'f9': br, 'f10': (-51, -15, 5.1),
    'f11': br, 'f12': br,
}
for fid, (_, lon, lat, *_) in locais.items():
    vistas[fid] = (lon, lat, 5.95)


def vista(t, v, pitch=0, rumo=0):
    lon, lat, zoom = v
    return {'t': t, 'lon': lon, 'lat': lat, 'zoom': zoom, 'pitch': pitch, 'bearing': rumo}


camera = [vista(0, vistas['f1'])]
for t in T:
    fid, a, b = t['id'], t['ini'], t['fim']
    v = vistas[fid]
    if fid != 'f1':
        inicial = (*angra, 6) if fid == 'f3' else v
        camera.append(vista(a + min(.38, (b-a)/6), inicial, 7))
    if fid == 'f3':
        camera.append(vista(petropolis + min(.45, (b-petropolis)/3), v, 9))
    if fid == 'f8':
        camera.append(vista(amanha - min(.3, (amanha-a)/4), v, 8))
        v = (-48.5, -26.6, 5.65)
        camera.append(vista(amanha + min(.5, (b-amanha)/3), v, 9))
    lon, lat, zoom = v
    camera.append(vista(b - min(.24, (b-a)/5), (lon, lat, zoom+.07), 9, 1))
assert all(a['t'] < b['t'] for a, b in zip(camera, camera[1:]))

horas = json.loads((AQUI / 'sat/web/ir_tempos.json').read_text())
assert len(horas) == 49 and horas[0] == '2026-11-26T08:00:00Z' and horas[-1] == '2026-11-27T08:00:00Z'
ir = [(f'sat/web/ir{i:02d}-suave.png', h) for i, h in enumerate(horas) if h != '2026-11-26T11:00:00Z']
assert len(ir) == 48
quadros = [f for f, _ in ir]
assert all((AQUI / f).is_file() for f in [*quadros, 'sat/web/mundo.jpg', 'sat/web/geocolor-suave.png'])
sat = {
    'fundo': {'src': 'sat/web/mundo.jpg', 'bbox': [-180, -60, 180, 75], 'tint': [170, 170, 175]},
    'base': 'sat/web/geocolor-suave.png', 'bbox': [-76, -35, -33, 7], 'tint': [170, 170, 175],
    'ir': {'frames': quadros, 'tempos': [b_rt(datetime.fromisoformat(h.replace('Z', '+00:00'))) for _, h in ir],
           'ini': 0, 'fim': ini('f2'), 'dur': max(.5, ini('f2')-.3), 'alfa': .89, 'rotulo': 'GOES-19 · IR · 26–27/11'},
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


a7, a8, a9, a10, a11, a12 = (ini(f'f{i}') for i in range(7, 13))
estados = [estado('abertura', ['ES', 'RJ'], -.7, ini('f2'), [60, 150, 255], .26),
           estado('angra', ['RJ'], ini('f3'), petropolis, [60, 150, 255]),
           estado('ma', ['MA'], a7, a8, [255, 140, 26], .25),
           estado('hoje', ufs_hoje, a8, amanha, [250, 204, 21], .14),
           estado('amanha', ufs_amanha, amanha, a9, [250, 204, 21], .14)]

# Imagens transparentes com o polígono oficial, ancoradas nas coordenadas do aviso.
imagens = []
for a, inicio, fim_ in [(laranja, 0, ini('f2')), (laranja, a8, amanha), (sabado, amanha, a9)]:
    bruto = json.loads(a['poligono'])
    assert bruto['type'] == 'Polygon'
    ring = bruto['coordinates'][0]
    bbox = [min(p[0] for p in ring), min(p[1] for p in ring),
            max(p[0] for p in ring), max(p[1] for p in ring)]
    src = f"sat/web/aviso-{a['id']}.png"
    assert (AQUI / src).is_file()
    imagens.append({'src': src, 'bbox': bbox, 'ini': inicio, 'fim': fim_, 'alfa': .8})

pinos = [pin('Angra dos Reis (RJ)', 'Alagamentos pontuais', *angra, ini('f3')+.25, petropolis),
         pin('Florianópolis (SC)', 'Previsão para sábado', floripa['longitude'], floripa['latitude'], amanha+.25, a9)]
paineis = [{'ini': ini('f3'), 'fim': petropolis, 'k': 'ANGRA DOS REIS (RJ)',
            'itens': [{'t': em('f3', 'alagamentos'), 'txt': 'Alagamentos pontuais'}],
            'l': 'Defesa Civil municipal · 26/11'}]
fontes = [
    {'ini': 0, 'fim': ini('f2'), 'html': '<b>CEMADEN · Agência Brasil · INMET</b> | Satélite: NASA GIBS / GOES-19'},
    {'ini': ini('f3'), 'fim': petropolis, 'html': '<b>Agência Brasil / Defesa Civil de Angra</b> · 26/11 às 20h56 BRT'},
]
for fid, (cidade, lon, lat, sensor, valor, palavra, dec) in locais.items():
    x, t, _ = sensores[sensor]
    a, b = (petropolis if fid == 'f3' else ini(fid)), seguinte(fid)
    estados.append(estado(fid, [x['uf']], a, b, [60, 150, 255]))
    pinos.append(pin(f'{cidade} ({x["uf"]})', 'Pluviômetro CEMADEN', lon, lat, a+.2, b))
    paineis.append({'ini': a, 'fim': b, 'k': f'CHUVA MEDIDA · {cidade}',
                    'contador': contagem(valor, 'MM EM 24 H', em(fid, palavra), a, dec=dec),
                    'l': x['nomeestacao']})
    fontes.append({'ini': a, 'fim': b, 'html': f'<b>CEMADEN</b> · sensor {sensor} · {b_rt(t)} BRT'})

pontos = [{'id': 'fogo', 'ini': a7, 'fim': a8, 'dados': [{'p': p, 'i': i} for i, p in enumerate(focos.values())],
           'dur': 1.5, 'raio': 2.4, 'cor': [255, 100, 26]}]
hero = [{
    'ini': 0, 'fim': ini('f2')-.05,
    'html': f'<div class="t1" style="font-size:118px;margin-bottom:18px">{DATA}</div>'
            '<div class="t3" style="margin-top:0">131,4 MM</div>'
            '<div class="t4">CHUVA MEDIDA EM ICONHA (ES)</div>'
            '<div class="t4" style="margin-top:18px">Alagamentos em Angra<br><span style="color:#fb923c">Alerta laranja no Sul</span></div>',
}]
paineis += [
    {'ini': a7, 'fim': a8, 'k': 'FOCOS DE CALOR · MARANHÃO',
     'contador': contagem(ref_ma, 'FOCOS', em('f7', '425'), a7, LARANJA),
     'itens': [{'t': em('f7', 'focos'), 'txt': f'Brasil: {formato(ref)} focos'}],
     'l': 'INPE · satélite de referência · 26/11 UTC'},
    {'ini': a8, 'fim': amanha, 'k': 'HOJE · ALERTA LARANJA NO SUL',
     'contador': contagem(len(cod_laranja), 'MUNICÍPIOS' if not CANTO else 'CIDADES', em('f8', 'Sul'), a8, LARANJA),
     'itens': [{'t': em('f8', 'chuva'), 'txt': 'Previsão de 50 a 100 mm/dia'}],
     'l': 'PR, SC e RS · das 09h40 às 23h59'},
    {'ini': amanha, 'fim': a9, 'k': 'SÁBADO · CHUVA EM FLORIANÓPOLIS',
     'contador': contagem(30.6, 'MM PREVISTOS', em('f8', '30'), amanha, AMARELO, 1),
     'l': f'Aviso amarelo · {formato(len(cod_sabado))} municípios'},
    {'ini': a9, 'fim': a10, 'k': 'CHUVA PREVISTA · 7 DIAS' if CANTO else 'CHUVA PREVISTA · 7 DIAS · 27 CAPITAIS',
     'contador': contagem(int(total7), 'MM SOMADOS', em('f9', 'capitais'), a9),
     'grafico': {'rotulos': rotulos, 'series': series, 'marcar': [], 'marcar_x': list(range(7)),
                 'previsto_a_partir': 0, 'ini': a9+.3, 'dur': 1.6,
                 'linha': {'nome': 'Máx. média (°C)<style>.graf circle+text{display:none}</style>',
                           'cor': VERMELHO, 'v': [d['tmax_media'] for d in dias]}},
     'itens': [] if CANTO else [
         {'t': em('f9', 'quinta-feira'), 'txt': 'Quinta (03/12): 162,6 mm'},
         {'t': em('f9', 'Norte'), 'txt': 'Norte: 322,3 mm'},
         {'t': em('f9', 'Teresina'), 'txt': 'Teresina: até 39,9 °C'},
     ],
     'l': 'Open-Meteo · soma das capitais'},
    {'ini': a10, 'fim': a11, 'k': 'SOMA DOS PLUVIÔMETROS · 24 H',
     'contador': contagem(int(brasil), 'MM·ESTAÇÃO', em('f10', '11.742'), a10),
     'ranking': {'itens': [{'nome': uf, 'v': int(v)} for uf, v in ranking], 'cor': AZUL,
                 'unid': '', 'ini': a10+.3, 'dur': 1.0},
     'itens': [{'t': em('f10', '937'), 'txt': 'Capitais: 937 mm' if CANTO else '7 dias nas capitais: 937 mm previstos'}],
     'l': 'CEMADEN · 1.293 sensores<style>.painel .rk .r .nm{flex:0 0 18%}</style>'},
    {'ini': a11, 'fim': a12, 'k': 'COMENTA AQUI',
     'itens': [{'t': em('f11', 'região'), 'txt': 'Sua região?'}, {'t': em('f11', 'cidade'), 'txt': 'Sua cidade?'}]},
]
for p in paineis:
    c = p.get('contador')
    if c:
        assert p['ini'] <= c['ini'] < c['ini'] + c['dur'] < p['fim'], p['k']

fontes += [
    {'ini': a7, 'fim': a8, 'html': '<b>INPE Queimadas</b> · AQUA_M-T · 26/11 UTC'},
    {'ini': a8, 'fim': amanha, 'html': '<b>INMET 56515</b> · 56513 (chuva amarela) · 56512 (baixa umidade)'},
    {'ini': amanha, 'fim': a9, 'html': '<b>INMET 56516</b> · 28/11 · <b>Open-Meteo</b> · Florianópolis'},
    {'ini': a9, 'fim': a10, 'html': '<b>Open-Meteo</b> · 27/11–03/12 · 27 capitais<br>Qui 162,6 mm · Norte 322,3 mm · Teresina até 39,9 °C'},
    {'ini': a10, 'fim': a11, 'html': '<b>CEMADEN</b> · mm·estação · <b>Open-Meteo</b> · previsão nas capitais'},
    {'ini': a11, 'fim': a12, 'html': f'CLIMA 24 H · {DATA}'},
]
cta = {'ini': a12, 'fim': DUR, 'a': 'APRENDA IA', 'b': 'inema.club', 'img': False}

cores = {**dict.fromkeys(('chuva', 'milimetros', 'pluviometro', 'pluviometros', 'somados'), AZUL),
         **dict.fromkeys(('laranja', 'intensa', 'alerta', 'focos'), LARANJA),
         **dict.fromkeys(('alagamentos', 'calor', 'graus'), VERMELHO),
         **dict.fromkeys(('comenta', 'inteligencia', 'artificial', 'inemaclub'), AMARELO)}
lugares = {'iconha', 'angra', 'petropolis', 'rolim', 'coxim', 'ituporanga', 'maranhao',
           'florianopolis', 'teresina', 'norte', 'sul'}
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
      f'INMET {len(cod_laranja)}/{len(cod_sabado)} · INPE {ref_ma}/{ref} · previsão {total7} mm')
