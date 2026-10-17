#!/usr/bin/env python3
"""Roteiro visual VIRAL 16:9 da Previsão do Dia 17/10/2026 (refaz do Short ZqAXBCjfGtY com o mesmo avatar).
Deixas = trechos literais da fala gravada (eventosextremospub/edicoes/2026-10-17-previsao-do-dia/falas.json).
A fonte (canal de meteorologia) nunca é citada; números de INMET e Open-Meteo como no yt.txt da edição."""
import json
from pathlib import Path

O = Path.home() / 'projetos/output/explica-previsao-1710-viral'
M = O / 'media'
m = lambda n: str(M / n)
INMET = 'INMET · 17/10/2026'
OM = 'Open-Meteo · 17/10/2026'
SUL = [-58.5, -34, -47, -22]


def foto(at, src, **kw):
    return dict({'type': 'foto', 'at': at, 'src': src, 'focus': [0.5, 0.5], 'zoom': [1.04, 1.18]}, **kw)


def carimbo(at, txt, y=0.7, cor='var(--amber)', x=None):
    d = {'type': 'carimbo', 'at': at, 'keep': True, 'txt': txt, 'y': y, 'cor': cor}
    if x is not None:
        d['x'] = x
    return d


def lado(at, txt, y=0.3, cor='var(--amber)'):   # carimbo acima da caixa do avatar (livre nos gráficos)
    return carimbo(at, txt, y, cor, 0.82)


S = {}
S['1'] = [
    {'type': 'capa', 'at': '@start', 'src': m('capa.png'), 'zoom': [1.0, 1.04], 'selo': 'PREVISÃO DO DIA', 'selo_at': 'sábado'},
    foto('A segunda pode', m('geada-close.png'), titulo='**geada** na segunda', titulo_at='com geada'),
    foto('abaixo de zero', m('frio-serra.png'), titulo='**abaixo de 0 °C**', titulo_at='abaixo de zero',
         pontos=[{'at': 'Serra Catarinense', 'focus': [0.35, 0.45], 'zoom': 1.22}]),
    lado('Serra Catarinense', 'SERRA SC', 0.3),
]
S['2'] = [
    {'type': 'capitulo', 'at': 'O motivo', 'src': m('ciclone-mar.png'), 'k': 'o motivo', 'text': '**ciclone** extratropical',
     'sub': 'no Atlântico', 'sub_at': 'extratropical'},
    foto('deixa o mar', m('ciclone-mar.png'), titulo='mar **agitado**', titulo_at='mar agitado'),
    foto('e o ar frio', m('frio-serra.png'), titulo='o **ar frio** toma o Sul', titulo_at='toma conta'),
]
S['3'] = [
    {'type': 'mapa', 'at': 'Hoje, o sol', 'base': 'brasil-uf', 'extent': SUL,
     'camera': [{'at': 'Hoje, o sol', 'centro': [-52, -28], 'zoom': 1.0}, {'at': 'pancadas passageiras', 'centro': [-52.5, -30], 'zoom': 1.5}],
     'destaques': [{'nome': 'Rio Grande do Sul', 'at': 'pancadas passageiras'}],
     'pinos': [{'lon': -52, 'lat': -30, 'txt': 'PANCADAS', 'at': 'gaúcho', 'sub': 'centro-leste **gaúcho**', 'sub_at': 'gaúcho'}],
     'fonte': INMET},
    {'type': 'bignum', 'at': 'No litoral', 'de': 0, 'ate': 115, 'unid': ' cidades', 'k': 'alerta de ventos costeiros · SC e RS',
     'hit_at': 'cidades estão em', 'src': m('vento-litoral.png'), 'fonte': INMET},
    lado('ventos costeiros', 'VENTO', 0.3, 'var(--rose)'),
]
S['4'] = [
    foto('No sudeste', m('temporal-minas.png'), titulo='**temporais** no Sudeste', titulo_at='pode ter temporais'),
    {'type': 'ranking', 'at': 'Em Minas', 'titulo': 'cidades em **alerta laranja** · tempestade', 'src': m('temporal-minas.png'), 'lw': 300,
     'itens': [{'n': 'Minas Gerais', 'v': 245, 'at': 'Em Minas', 'v_at': 'cidades em alerta'},
               {'n': 'Brasil', 'v': 370, 'hl': True, 'at': 'No Brasil', 'v_at': 'trezentas e setenta'}], 'fonte': INMET},
    lado('alerta laranja', 'LARANJA', 0.28, 'var(--rose)'),
]
S['5'] = [
    {'type': 'bignum', 'at': 'No Rio de', 'de': 0, 'ate': 26, 'unid': ' mm', 'k': 'chuva prevista hoje · Rio de Janeiro',
     'hit_at': 'milímetros de chuva', 'l': 'no **Rio de Janeiro**', 'l_at': 'a previsão', 'src': m('chuva-rio.png'), 'fonte': OM},
    lado('chuva hoje', 'HOJE', 0.3),
]
S['6'] = [
    foto('No domingo, as', m('pancadas-cerrado.png'), titulo='**domingo**: pancadas', titulo_at='se concentram'),
    {'type': 'mapa', 'at': 'no sudeste', 'base': 'brasil-uf', 'extent': [-74, -34, -34, 6],
     'camera': [{'at': 'no sudeste', 'centro': [-54, -14], 'zoom': 1.0}],
     'destaques': [{'nome': 'Minas Gerais', 'at': 'no sudeste'}, {'nome': 'São Paulo', 'at': 'no sudeste'},
                   {'nome': 'Goiás', 'at': 'Centro-Oeste'}, {'nome': 'Mato Grosso', 'at': 'Centro-Oeste'},
                   {'nome': 'Pará', 'at': 'norte'}, {'nome': 'Amazonas', 'at': 'norte'}],
     'pinos': [{'lon': -45, 'lat': -20, 'txt': 'SUDESTE', 'at': 'no sudeste'},
               {'lon': -52, 'lat': -14, 'txt': 'CENTRO-OESTE', 'at': 'Centro-Oeste'},
               {'lon': -58, 'lat': -4, 'txt': 'NORTE', 'at': 'norte'}], 'fonte': INMET},
]
S['7'] = [
    {'type': 'cinetica', 'at': 'E o frio aperta', 'src': m('topo-serra.png'),
     'palavras': [{'t': 'O FRIO', 'at': 'E o frio'}, {'t': 'APERTA', 'at': 'frio aperta', 'hl': True}]},
    {'type': 'mapa', 'at': 'a Serra Catarinense', 'base': 'brasil-uf', 'extent': SUL,
     'camera': [{'at': 'a Serra Catarinense', 'centro': [-51, -27], 'zoom': 1.6}],
     'destaques': [{'nome': 'Santa Catarina', 'at': 'a Serra Catarinense'}, {'nome': 'Paraná', 'at': 'campos de Palmas'}],
     'pinos': [{'lon': -49.9, 'lat': -28.1, 'txt': 'SERRA SC', 'at': 'a Serra Catarinense'},
               {'lon': -51.99, 'lat': -26.48, 'txt': 'PALMAS (PR)', 'at': 'campos de Palmas'}], 'fonte': OM},
    {'type': 'bignum', 'at': 'podem marcar', 'de': 15, 'ate': 5, 'unid': ' °C', 'k': 'ao amanhecer · domingo',
     'hit_at': 'graus ao amanhecer', 'src': m('frio-serra.png'), 'fonte': OM},
]
S['8'] = [
    {'type': 'capitulo', 'at': 'Na segunda', 'src': m('geada-close.png'), 'k': 'segunda-feira', 'text': '**GEADA**',
     'sub': 'na serra e em Palmas', 'sub_at': 'pode ter geada'},
    lado('em Palmas', 'PALMAS', 0.46),
    foto('com temperatura abaixo', m('topo-serra.png'),
         titulo='**abaixo de zero** no topo da serra', titulo_at='topo da Serra'),
    lado('abaixo de zero', '< 0 °C', 0.3, 'var(--rose)'),
]
S['9'] = [
    foto('Na terça', m('sol-degelo.png'), titulo='o frio **perde força**', titulo_at='perde força'),
    foto('À noite', m('chuva-parana.png'), titulo='a chuva **volta**', titulo_at='a chuva volta'),
    {'type': 'mapa', 'at': 'ao Paraná', 'base': 'brasil-uf', 'extent': SUL,
     'camera': [{'at': 'ao Paraná', 'centro': [-52, -25.5], 'zoom': 1.4}],
     'destaques': [{'nome': 'Paraná', 'at': 'ao Paraná'}, {'nome': 'Santa Catarina', 'at': 'oeste de Santa'}],
     'pinos': [{'lon': -52.5, 'lat': -27, 'txt': 'OESTE SC', 'at': 'oeste de Santa'}], 'fonte': INMET},
]
S['10'] = [
    {'type': 'cinetica', 'at': 'Quarta e quinta', 'src': m('baixa-pressao.png'),
     'palavras': [{'t': 'NOVA BAIXA', 'at': 'nova baixa'}, {'t': 'PRESSÃO', 'at': 'pressão', 'hl': True}]},
    foto('pode trazer temporais', m('chuva-parana.png'), focus=[0.4, 0.45], zoom=[1.1, 1.22],
         titulo='**temporais** no PR e em SC', titulo_at='trazer temporais',
         pontos=[{'at': 'aos dois estados', 'focus': [0.6, 0.5], 'zoom': 1.24}]),
    lado('dois estados', 'PR + SC', 0.3),
    {'type': 'bignum', 'at': 'Na sexta', 'de': 0, 'ate': 53, 'unid': ' mm', 'k': 'capitais do Sul · sexta',
     'hit_at': 'cinquenta e três', 'l': 'nas **capitais do Sul**', 'l_at': 'somam', 'src': m('baixa-pressao.png'), 'fonte': OM},
    lado('capitais do sul', 'SEXTA', 0.3),
    lado('previstos', 'PREVISÃO', 0.46),
]
S['11'] = [
    {'type': 'rosto', 'at': 'De onde você', 'txt': 'de onde você **assiste**?', 'txt_at': 'está assistindo'},
    foto('E como está', m('pancadas-cerrado.png'), focus=[0.6, 0.5], titulo='como está o **tempo aí**?', titulo_at='tempo aí'),
    carimbo('Comenta aqui', 'COMENTA', 0.3),
]
S['12'] = [
    {'type': 'cta', 'at': 'No inema ponto', 'src': m('geada-close.png'), 'url': '**inema.club**', 'url_at': 'inema ponto club',
     'sub': 'aprenda **inteligência artificial**', 'sub_at': 'inteligência artificial'},
]

out = {'block': 'pt-b01', 'scenes': {k: {'takeaway': False, 'fundo': m('frio-serra.png'), 'shots': v} for k, v in S.items()}}
(O / 'visual').mkdir(exist_ok=True)
(O / 'visual/viral-pt-b01.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print('shots', sum(len(v) for v in S.values()))
