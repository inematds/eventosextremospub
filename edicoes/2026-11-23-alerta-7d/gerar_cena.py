#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 23/11/2026 (segunda) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 24/11 a 30/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "23/11/2026"
SEM = "24 A 30/11"
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

# Janela exclusiva 24–30/11. Grade: valores locais, não cobertura uniforme por UF.
R=json.loads((AQUI/'om/prev15_resumo.json').read_text())
G=json.loads((AQUI/'om/prev15_grade.json').read_text())['pts']
CAP=json.loads((AQUI/'om/prev15_capitais.json').read_text())['capitais']
gs=R['grade']['semana'];pu=gs['por_uf']
assert R['inicio']=='2026-11-24' and gs['dias']=='2026-11-24 a 2026-11-30'
pt=lambda xy:next(q for q in G if q['p']==xy)
cap=lambda nome:next(q for q in CAP if q['cap']==nome)
soma=lambda v:round(sum(x or 0 for x in v),1)
assert soma(pt([-46.5,-24])['chuva'][:7])==198.3
assert pt([-46.5,-24])['chuva'][2]==93.5
assert pt([-52.5,-27])['chuva'][0]==48.6
assert pt([-54,-25.5])['chuva'][:7].index(max(pt([-54,-25.5])['chuva'][:7]))==1
assert cap('Rio de Janeiro')['raj'][2]==68.8
assert cap('Manaus')['chuva'][:7].index(max(cap('Manaus')['chuva'][:7]))==5
assert cap('Cuiabá')['chuva'][:7].index(max(cap('Cuiabá')['chuva'][:7]))==4
assert pt([-42,-6])['tmax'][2]==41.2
assert pt([-51,-28.5])['tmin'][3]==11.1
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
red=next(a for a in AV['futuro'] if a['id']==56492)
mun=re.findall(r'([^,]+) - ([A-Z]{2}) \((\d{7})\)',red['municipios'])
assert len(set(c for a,b,c in mun if b=='PR'))==287
assert red['inicio']=='2026-11-24 00:00' and red['fim']=='2026-11-24 23:59'
views=[(-51,-25,4.5),(-52,-26,4.2),(-46.5,-24,4.4),(-43.2,-22.9,4.5),(-53,-26,4.3),(-59,-10,3.6),(-42,-6,4.2),(-51,-28.5,4.5),(-51,-14,3.6),(-51,-14,3.6),(-51,-14,3.6)]
K=lambda t,lon,lat,z:{'t':round(t,3),'lon':lon,'lat':lat,'zoom':z,'pitch':28,'bearing':0}
camera=[]
for i,v in enumerate(views,1):
 fid=f'f{i}'
 camera.extend([K(0 if i==1 else ini(fid)+.4,*v),K(fim(fid)-.35,*v)])
if CANTO:
 # Desloca o foco da abertura abaixo do hero; preserva mapa cheio e avatar no canto.
 camera[0].update(lat=-19,zoom=4.1);camera[1].update(lat=-19,zoom=4.1)
camera.append(K(DUR,*views[-1]));camera.sort(key=lambda x:x['t'])
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
SAT={}
estados=[{'id':'abertura','ini':-1,'fim':fim('f1'),'ufs':['PR'],'cor':VERM,'alfa':.9}]
for fid,ufs,cor in [('f2',['PR','SC','RS','MS'],VERM),('f3',['SP'],AZUL),('f4',['RJ'],AMAR),('f5',['PR','SC'],AZUL),('f6',['AM','MT'],AZUL),('f7',['PI','CE','RN','PB','PE','AL','SE','BA','MA'],LARANJA),('f8',['RS'],AZUL)]:
 assert all(uf in pu for uf in ufs)
 estados.append({'id':fid,'ini':ini(fid),'fim':fim(fid),'ufs':ufs,'cor':cor,'alfa':.75})
estados.append({'id':'chuvaBR','ini':ini('f9'),'fim':DUR,'ufs':[uf for uf,v in pu.items() if v['chuva_max']>=60],'cor':AZUL,'alfa':.35})
CS=[{'id':f'c{i}','p':q['p'],'v':soma(q['chuva'][:7]),'cor':AZUL} for i,q in enumerate(G) if soma(q['chuva'][:7])>=40]
assert max(d['v'] for d in CS)==198.3
colunas=[{'id':'chuva','ini':ini('f3'),'fim':fim('f3'),'dados':CS,'escala':450,'raio':18000,'cor':AZUL,'ordem':{},'varredura':0}]
pinos=[]
for fid,nome,sub,lon,lat in [('f1','PARANÁ','Áreas em vermelho · terça 24/11',-51,-25),('f3','Litoral paulista','198,3 mm previstos · 24–30/11',-46.5,-24),('f4','Rio de Janeiro','68,8 km/h previstos · qui 26/11',-43.2,-22.9),('f5','Oeste de SC','48,6 mm previstos · ter 24/11',-52.5,-27),('f7','Piauí','41,2 °C previstos · qui 26/11',-42,-6),('f8','Serra gaúcha','11,1 °C previstos · sex 27/11',-51,-28.5)]:
 pinos.append({'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':-1 if fid=='f1' else ini(fid)+.5,'fim':fim(fid),'h':95})
pinos.extend([
 {'nome':'Manaus','sub':'Pico de chuva previsto · dom 29/11','lon':-60.02,'lat':-3.1,'ini':ini('f6')+.4,'fim':em('f6','Centro-Oeste'),'h':95},
 {'nome':'Cuiabá','sub':'Pico de chuva previsto · sáb 28/11','lon':-56.1,'lat':-15.6,'ini':em('f6','Cuiabá'),'fim':fim('f6'),'h':95}
])
hero=[{'ini':-1,'fim':fim('f1'),'html':f'''<div style="font:400 108px/1 'Archivo Black';margin-bottom:16px">{DATA}</div><div class="dt" style="background:#ff2a1f;color:white;font-size:36px">ALERTA · PRÓXIMOS 7 DIAS</div><div class="t1" style="font-size:130px;color:#ffd23f">287 CIDADES</div><div style="font:900 66px/1.05 Inter">PARANÁ EM VERMELHO</div><div style="font:900 48px/1.12 Inter;margin-top:12px">AMANHÃ · TERÇA 24/11</div><div style="font:400 98px/1 'Archivo Black';color:#ff5147;margin-top:22px">SE PREPARE</div>'''}]
def painel(fid,k,valor,unid,palavra,l,cor='#5ec8ff'):
 return {'ini':ini(fid),'fim':fim(fid),'k':k,'contador':{'de':0,'ate':valor,'dec':0 if isinstance(valor,int) else 1,'ini':chega(fid,palavra),'dur':1.0,'cor':cor,'unid':unid},'l':l,'borda':cor}
paineis=[
 {'ini':ini('f2'),'fim':fim('f2'),'k':'INMET · TER 24/11 · ÁREAS SOB AVISO','itens':[{'t':ini('f2'),'txt':'VERMELHO · GRANDE PERIGO'},{'t':em('f2','granizo'),'txt':'Vento superior a 100 km/h + granizo'}],'borda':'#ff2a1f'},
 painel('f3','LITORAL DE SP · PREVISTO 24–30/11',198.3,'MM','198','Pico: qui 26/11 · 93,5 mm previstos'),
 painel('f4','RIO DE JANEIRO · PREVISTO QUI 26/11',68.8,'KM/H','68','Rajadas previstas · evite árvores','#ffd23f'),
 painel('f5','OESTE DE SC · PREVISTO TER 24/11',48.6,'MM','48','Oeste do PR: pico de chuva qua 25/11'),
 {'ini':ini('f6'),'fim':fim('f6'),'k':'PICOS DE CHUVA · PREVISÃO 24–30/11','itens':[{'t':ini('f6'),'txt':'Manaus · domingo 29/11'},{'t':em('f6','Cuiabá'),'txt':'Cuiabá · sábado 28/11'}],'borda':'#5ec8ff'},
 painel('f7','PIAUÍ · PREVISTO QUI 26/11',41.2,'°C','41','INMET: ar seco no NE até qua 25/11','#ff5147'),
 painel('f8','SERRA GAÚCHA · PREVISTO SEX 27/11',11.1,'°C','11','Mínima local prevista · roupa de frio'),
 {'ini':ini('f9'),'fim':fim('f9'),'k':'SE PREPARE','itens':[{'t':ini('f9'),'txt':'Procure abrigo seguro'},{'t':em('f9','carro'),'txt':'Carro longe de árvores'},{'t':em('f9','atravesse'),'txt':'Evite rua alagada'}]},
 {'ini':ini('f10'),'fim':fim('f10'),'k':'COMENTA AQUI','itens':[{'t':ini('f10'),'txt':'De que cidade você é?'},{'t':em('f10','tempo'),'txt':'Como está o tempo aí?'}]}
]
cta={'ini':ini('f11'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f11','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
OM=f'<b>Open-Meteo</b>, previsão lida em {DATA}'
fontes=[{'ini':-1,'fim':ini('f3'),'html':f'<b>INMET 56492</b> · lido {DATA} · áreas sob aviso'},
 {'ini':ini('f3'),'fim':ini('f7'),'html':f'{OM} · 24 a 30/11 · valores locais'},
 {'ini':ini('f7'),'fim':ini('f8'),'html':f'{OM} · <b>INMET 56481</b> · áreas sob aviso'},
 {'ini':ini('f8'),'fim':ini('f9'),'html':f'{OM} · valor local previsto'},
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
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(CS)} colunas; previsão 24–30/11")
