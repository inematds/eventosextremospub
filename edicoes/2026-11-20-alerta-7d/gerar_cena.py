#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 20/11/2026 (sexta) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 21/11 a 27/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "20/11/2026"
SEM = "21 A 27/11"
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


ROT = {f["id"]: f.get("legenda") or f["fala"] for f in json.loads((AQUI / "falas.json").read_text())}
for t in T:
    t["palavras"] = roteiro(t, ROT[t["id"]])
FALA = {t["id"]: t for t in T}


def em(fid, palavra, k=1):
    achou = 0
    for p in FALA[fid]["palavras"]:
        if n(palavra) in n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
chega = lambda fid, palavra: round(em(fid, palavra) - 1.0, 3)  # contador chega ao número quando a palavra é dita (Lesson 13/10)
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
AMAR, AZUL, VERM, LARANJA = [255, 210, 63], [60, 150, 255], [255, 42, 31], [255, 140, 26]

# Previsão exclusiva 21–27/11. Valores locais de grade/capital.
R=json.loads((AQUI/'om/prev15_resumo.json').read_text())
G=json.loads((AQUI/'om/prev15_grade.json').read_text())['pts']
CAP=json.loads((AQUI/'om/prev15_capitais.json').read_text())['capitais']
gs=R['grade']['semana'];pu=gs['por_uf']
assert R['inicio']=='2026-11-21' and gs['dias']=='2026-11-21 a 2026-11-27'
pt=lambda xy:next(q for q in G if q['p']==xy)
cap=lambda nome:next(q for q in CAP if q['cap']==nome)
soma=lambda v:round(sum(x or 0 for x in v),1)
assert pt([-42,-6])['tmax'][4]==42
assert pt([-52.5,-27])['chuva'][3]==93.5
assert soma(pt([-54,-25.5])['chuva'][:7])==162.8
assert cap('Vitória')['chuva'][6]==65.6
assert cap('Florianópolis')['raj'][5]==79.9
assert pt([-51,-28.5])['tmin'][5:7]==[9.5,9.5]
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
assert {a['id'] for a in AV['futuro']} >= {56462,56466}
views=[(-42,-6,4.6),(-52.5,-27,4.9),(-54,-25.5,4.9),(-40.34,-20.32,4.8),(-48.55,-27.6,4.9),(-54,-10,3.7),(-51,-28.5,4.9),(-51,-14,3.7),(-51,-14,3.7),(-51,-14,3.7),(-51,-14,3.7)]
K=lambda t,lon,lat,z:{'t':round(t,3),'lon':lon,'lat':lat,'zoom':z,'pitch':28,'bearing':0}
camera=[]
for i,v in enumerate(views,1):
 fid=f'f{i}'
 camera.extend([K(0 if i==1 else ini(fid)+.4,*v),K(fim(fid)-.35,*v)])
if CANTO:
 camera[0].update(lat=1,zoom=4.4);camera[1].update(lat=1,zoom=4.4)
camera.append(K(DUR,*views[-1]));camera.sort(key=lambda x:x['t'])
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},'base':'sat/web/geocolor.jpg','bbox':[-76,-35,-33,7],'tint':[170,170,175]}
estados=[{'id':'abertura','ini':-1,'fim':fim('f1'),'ufs':['PI'],'cor':VERM,'alfa':.9}]
for fid,ufs,cor in [('f2',['SC'],AZUL),('f3',['PR'],AZUL),('f4',['ES'],AZUL),('f5',['SC'],AMAR),('f6',['TO','AM','MT','GO'],LARANJA),('f7',['RS'],AZUL)]:
 assert all(uf in pu for uf in ufs)
 estados.append({'id':fid,'ini':ini(fid),'fim':fim(fid),'ufs':ufs,'cor':cor,'alfa':.75})
# Avisos são para áreas das UFs. Fundo de previsão, sem inferir alerta uniforme.
estados.append({'id':'chuvaBR','ini':ini('f8'),'fim':DUR,'ufs':[uf for uf,v in pu.items() if v['chuva_max']>=60],'cor':AZUL,'alfa':.35})
CS=[{'id':f'c{i}','p':q['p'],'v':soma(q['chuva'][:7]),'cor':AZUL} for i,q in enumerate(G) if soma(q['chuva'][:7])>=40]
assert max(d['v'] for d in CS)==162.8
colunas=[{'id':'chuva','ini':ini('f2'),'fim':fim('f4'),'dados':CS,'escala':600,'raio':22000,'cor':AZUL,'ordem':{},'varredura':0}]
pinos=[]
for fid,nome,sub,lon,lat in [('f1','Piauí','Até 42 °C previstos · qua 25/11',-42,-6),('f2','Oeste de SC','93,5 mm previstos · ter 24/11',-52.5,-27),('f3','Oeste do Paraná','162,8 mm previstos · 21–27/11',-54,-25.5),('f4','Vitória','65,6 mm previstos · sex 27/11',-40.34,-20.32),('f5','Florianópolis','79,9 km/h previstos · qui 26/11',-48.55,-27.6),('f7','Serra gaúcha','9,5 °C previstos · qui/sex 26–27/11',-51,-28.5)]:
 pinos.append({'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':-1 if fid=='f1' else ini(fid)+.5,'fim':fim(fid),'h':130})
hero=[{'ini':-1,'fim':fim('f1'),'html':f'''<div style="font:400 112px/1 'Archivo Black';margin-bottom:16px">{DATA}</div><div class="dt" style="background:#ff2a1f;color:white;font-size:38px">ALERTA · PRÓXIMOS 7 DIAS</div><div class="t1" style="font-size:158px;color:#ffd23f">ATÉ 42 °C</div><div style="font:900 78px/1.05 Inter">PIAUÍ · QUARTA</div><div style="font:900 46px/1.12 Inter;margin-top:12px">PREVISTO · 25/11</div><div style="font:400 104px/1 'Archivo Black';color:#ff5147;margin-top:22px">SE PREPARE</div>'''}]
def painel(fid,k,valor,unid,palavra,l,cor='#5ec8ff'):
 return {'ini':ini(fid),'fim':fim(fid),'k':k,'contador':{'de':0,'ate':valor,'dec':0 if isinstance(valor,int) else 1,'ini':chega(fid,palavra),'dur':1.0,'cor':cor,'unid':unid},'l':l,'borda':cor}
paineis=[
 painel('f2','OESTE DE SC · PREVISTO TER 24/11',93.5,'MM','93','Chuva em um dia · grade 1,5°'),
 painel('f3',f'OESTE DO PR · PREVISTO {SEM}',162.8,'MM','162','Acumulado · pico domingo 22/11'),
 painel('f4','VITÓRIA · PREVISTO SEX 27/11',65.6,'MM','65','Atenção aos alagamentos'),
 painel('f5','FLORIANÓPOLIS · PREVISTO QUI 26/11',79.9,'KM/H','79','Carro longe de árvores','#ffd23f'),
 {'ini':ini('f6'),'fim':fim('f6'),'k':'NORTE / CENTRO-OESTE · SÁB 21/11','itens':[{'t':ini('f6'),'txt':'Pancadas com trovoadas'},{'t':em('f6','Tocantins'),'txt':'TO · AM · MT · GO'}],'borda':'#ff8c1a'},
 painel('f7','SERRA GAÚCHA · PREVISTO QUI/SEX',9.5,'°C','9','26 e 27/11 · separe roupa de frio'),
 {'ini':ini('f8'),'fim':fim('f8'),'k':'INMET · SÁB 21 A SEG 23/11','itens':[{'t':ini('f8'),'txt':'AVISOS AMARELOS'},{'t':em('f8','granizo'),'txt':'Risco de granizo'}],'borda':'#ffd23f'},
 {'ini':ini('f9'),'fim':fim('f9'),'k':'SE PREPARE','itens':[{'t':ini('f9'),'txt':'Beba água no calor'},{'t':em('f9','atravesse'),'txt':'Não atravesse rua alagada'}]},
 {'ini':ini('f10'),'fim':fim('f10'),'k':'COMENTA AQUI','itens':[{'t':ini('f10'),'txt':'De que cidade você é?'},{'t':em('f10','tempo'),'txt':'Como está o tempo aí?'}]}
]
cta={'ini':ini('f11'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f11','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
OM=f'<b>Open-Meteo</b>, previsão lida em {DATA}'
fontes=[{'ini':-1,'fim':ini('f6'),'html':f'{OM} · 21 a 27/11 · valores locais'},
 {'ini':ini('f6'),'fim':ini('f7'),'html':f'<b>INMET</b> · previsão de 19/11 · lida {DATA}'},
 {'ini':ini('f7'),'fim':ini('f8'),'html':f'{OM} · mínima local prevista'},
 {'ini':ini('f8'),'fim':ini('f9'),'html':f'<b>INMET</b> · avisos 56462/56466 · lidos {DATA}'},
 {'ini':ini('f9'),'fim':ini('f10'),'html':'<b>INMET</b> · orientações de proteção nos avisos'}]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "alagada": "#5ec8ff", "rajadas": "#ffd23f", "atingir": "#ffd23f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "pior": "#ff2a1f", "comenta": "#ffd23f", "arvores": "#5ec8ff", "encosta": "#ff8c1a", "rio": "#5ec8ff"}
LUGAR = {"sao", "paulo", "espirito", "santo", "goias", "belo", "horizonte", "brasilia", "centronorte", "norte", "sul", "grande",
         "cuiaba", "goiania", "piaui", "inemaclub", "cidade", "regiao", "cidades", "quinta", "domingo", "terca", "sexta", "inmet"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        # Texto largo não cabe só pelo limite de três palavras (ex.: CTA).
        if bloco and len(" ".join(x["w"] for x in bloco) + " " + w) > 20:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["t"], "palavras": bloco})
            bloco = []
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])


C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "padding_topo": 540,
 "duracao": DUR,"marca":"INEMA · ALERTA DA SEMANA","selo":f"ALERTA · {SEM}","camera":camera,"sat":SAT,"estados":estados,"colunas":colunas,"pinos":pinos,"hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(CS)} colunas; previsão 21–27/11")
