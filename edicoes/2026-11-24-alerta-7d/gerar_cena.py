#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 24/11/2026 (terça) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 25/11 a 01/12) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "24/11/2026"
SEM = "25/11 A 01/12"
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

# Janela exclusiva 25/11–01/12 (dia 1 = amanhã). Grade: valores locais, não cobertura uniforme por UF.
R=json.loads((AQUI/'om/prev15_resumo.json').read_text())
G=json.loads((AQUI/'om/prev15_grade.json').read_text())['pts']
CAP=json.loads((AQUI/'om/prev15_capitais.json').read_text())['capitais']
gs=R['grade']['semana'];pu=gs['por_uf']
assert R['inicio']=='2026-11-25' and gs['dias']=='2026-11-25 a 2026-12-01'
pt=lambda xy:next(q for q in G if q['p']==xy)
cap=lambda nome:next(q for q in CAP if q['cap']==nome)
soma=lambda v:round(sum(x or 0 for x in v),1)
RJP=pt([-43.5,-22.5])
assert RJP['dias'][1]=='2026-11-26' and RJP['chuva'][1]==112.8 and soma(RJP['chuva'][:7])==188.1
rio=cap('Rio de Janeiro')
assert rio['tmax'][0]==36.3 and rio['tmax'][1]==25.7 and rio['chuva'][1]==69.9
assert soma(cap('Belo Horizonte')['chuva'][:7])==116.1
assert soma(pt([-51,-27])['chuva'][:7])==133.1
AMP=pt([-69,-1.5]);assert soma(AMP['chuva'][:7])==147.5 and max(AMP['chuva'][:7])==AMP['chuva'][5]==48.1
assert cap('Teresina')['tmax'][0]==40.5
AV={str(a['id']):a for a in json.loads((B/'inmet_avisos_ativos.json').read_text())['futuro']}
def nmun(i,uf=None):
 m=re.findall(r'([^,]+) - ([A-Z]{2}) \((\d{7})\)',AV[i]['municipios'])
 return len(set(c for a,b,c in m if uf is None or b==uf))
assert nmun('56503')==1278 and nmun('56503','RJ')==92 and AV['56503']['severidade']=='Perigo' and AV['56503']['inicio']=='2026-11-26 00:00'
assert nmun('56501')==1351 and AV['56501']['severidade']=='Perigo' and AV['56501']['inicio']=='2026-11-25 00:00'
UF503=['MG','SP','ES','MS','GO','RJ'];UF501=['PR','SP','MG','RJ','MS','ES','SC']
views=[(-43.4,-22.4,5.0),(-45.5,-20.5,4.2),(-43.2,-22.9,5.6),(-48,-22.5,4.0),(-47,-23.5,3.9),(-67,-3,4.4),(-42.8,-5.5,4.5),(-44,-21.5,4.2),(-51,-14,3.6),(-51,-14,3.6)]
K=lambda t,lon,lat,z:{'t':round(t,3),'lon':lon,'lat':lat,'zoom':z,'pitch':28,'bearing':0}
camera=[]
for i,v in enumerate(views,1):
 fid=f'f{i}'
 camera.extend([K(0 if i==1 else ini(fid)+.4,*v),K(fim(fid)-.35,*v)])
if CANTO:
 # Desloca o foco da abertura abaixo do hero; preserva mapa cheio e avatar no canto.
 camera[0].update(lat=-17.5,zoom=4.5);camera[1].update(lat=-17.5,zoom=4.5)
camera.append(K(DUR,*views[-1]));camera.sort(key=lambda x:x['t'])
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
SAT={}
estados=[{'id':'abertura','ini':-1,'fim':fim('f1'),'ufs':['RJ'],'cor':VERM,'alfa':.9},
 {'id':'abertura2','ini':-1,'fim':fim('f1'),'ufs':['MG','SP','ES'],'cor':LARANJA,'alfa':.55}]
for fid,ufs,cor in [('f2',UF503,LARANJA),('f3',['RJ'],VERM),('f4',UF501,LARANJA),('f5',['MG','SC'],AZUL),('f6',['AM'],AZUL),('f7',['PI','CE','RN','PB','PE','AL','SE','BA','MA'],LARANJA)]:
 assert all(uf in pu for uf in ufs)
 estados.append({'id':fid,'ini':ini(fid),'fim':fim(fid),'ufs':ufs,'cor':cor,'alfa':.75})
estados.append({'id':'chuvaBR','ini':ini('f8'),'fim':DUR,'ufs':[uf for uf,v in pu.items() if v['chuva_max']>=100],'cor':AZUL,'alfa':.35})
CQ=[{'id':f'q{i}','p':q['p'],'v':q['chuva'][1],'cor':AZUL} for i,q in enumerate(G) if (q['chuva'][1] or 0)>=15]
assert max(d['v'] for d in CQ)==112.8
CS=[{'id':f'c{i}','p':q['p'],'v':soma(q['chuva'][:7]),'cor':AZUL} for i,q in enumerate(G) if soma(q['chuva'][:7])>=40]
assert max(d['v'] for d in CS)==188.1
colunas=[{'id':'quinta','ini':-1.3,'fim':fim('f2'),'dados':CQ,'escala':700,'raio':18000,'cor':AZUL,'ordem':{},'varredura':0},
 {'id':'semana','ini':ini('f5'),'fim':fim('f6'),'dados':CS,'escala':450,'raio':18000,'cor':AZUL,'ordem':{},'varredura':0}]
pinos=[]
for fid,nome,sub,lon,lat in [('f1','Estado do RJ','112,8 mm previstos · qui 26/11',-43.5,-22.5),('f3','Rio de Janeiro','36,3 °C qua → 25,7 °C qui',-43.2,-22.9),('f6','Oeste do AM','147,5 mm previstos · 25/11–01/12',-69,-1.5),('f7','Teresina','40,5 °C previstos · qua 25/11',-42.8,-5.09)]:
 pinos.append({'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':-1 if fid=='f1' else ini(fid)+.5,'fim':fim(fid),'h':95})
pinos.extend([
 {'nome':'Belo Horizonte','sub':'116,1 mm previstos · semana','lon':-43.94,'lat':-19.92,'ini':ini('f5')+.4,'fim':em('f5','oeste'),'h':95},
 {'nome':'Oeste de SC','sub':'133,1 mm previstos · semana','lon':-51,'lat':-27,'ini':em('f5','oeste'),'fim':fim('f5'),'h':95}
])
hero=[{'ini':-1,'fim':fim('f1'),'html':f'''<div style="font:400 108px/1 'Archivo Black';margin-bottom:16px">{DATA}</div><div class="dt" style="background:#ff2a1f;color:white;font-size:36px">ALERTA · PRÓXIMOS 7 DIAS</div><div class="t1" style="font-size:150px;color:#ffd23f">112,8 MM</div><div style="font:900 62px/1.05 Inter">EM UM SÓ DIA NO RJ</div><div style="font:900 48px/1.12 Inter;margin-top:12px">NESTA QUINTA · 26/11</div><div style="font:400 98px/1 'Archivo Black';color:#ff5147;margin-top:22px">SE PREPARE</div>'''}]
def painel(fid,k,valor,unid,palavra,l,cor='#5ec8ff',kk=1):
 return {'ini':ini(fid),'fim':fim(fid),'k':k,'contador':{'de':0,'ate':valor,'dec':0 if isinstance(valor,int) else 1,'ini':round(em(fid,palavra,kk)-1.0,3),'dur':1.0,'cor':cor,'unid':unid},'l':l,'borda':cor}
paineis=[
 painel('f2','INMET · ALERTA LARANJA · QUI 26/11',1278,'CIDADES','1.278','Chuvas intensas · todas as 92 do RJ','#ff8c1a'),
 painel('f3','RIO DE JANEIRO · PREVISTO QUI 26/11',69.9,'MM','69,9','Máxima: 36,3 °C qua → 25,7 °C qui'),
 painel('f4','INMET · PERIGO DE TEMPESTADE · QUA 25/11',1351,'CIDADES','1.351','PR · SP · MG · RJ · MS · ES · SC','#ff8c1a'),
 {'ini':ini('f5'),'fim':fim('f5'),'k':'CHUVA PREVISTA · 25/11 A 01/12','itens':[{'t':ini('f5'),'txt':'Belo Horizonte · 116,1 mm'},{'t':em('f5','oeste'),'txt':'Oeste de SC · 133,1 mm'}],'borda':'#5ec8ff'},
 painel('f6','OESTE DO AMAZONAS · PREVISTO 25/11–01/12',147.5,'MM','147,5','Pico: seg 30/11 · 48,1 mm previstos'),
 painel('f7','TERESINA · PREVISTO QUA 25/11',40.5,'°C','40,5','INMET: ar seco no Nordeste','#ff5147'),
 {'ini':ini('f8'),'fim':fim('f8'),'k':'SE PREPARE','itens':[{'t':ini('f8'),'txt':'Carro longe de árvores'},{'t':em('f8','encostas'),'txt':'Distância das encostas'},{'t':em('f8','atravesse'),'txt':'Nunca atravesse rua alagada'}]},
 {'ini':ini('f9'),'fim':fim('f9'),'k':'COMENTA AQUI','itens':[{'t':ini('f9'),'txt':'De que cidade você é?'},{'t':em('f9','tempo'),'txt':'Como está o tempo aí?'}]}
]
cta={'ini':ini('f10'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f10','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
OM=f'<b>Open-Meteo</b>, previsão lida em {DATA}'
fontes=[{'ini':-1,'fim':ini('f2'),'html':f'{OM} · ponto de grade no RJ'},
 {'ini':ini('f2'),'fim':ini('f3'),'html':f'<b>INMET 56503</b> · lido {DATA}'},
 {'ini':ini('f3'),'fim':ini('f4'),'html':f'{OM} · capital'},
 {'ini':ini('f4'),'fim':ini('f5'),'html':f'<b>INMET 56501</b> · lido {DATA}'},
 {'ini':ini('f5'),'fim':ini('f7'),'html':f'{OM} · 25/11 a 01/12 · valores locais'},
 {'ini':ini('f7'),'fim':ini('f8'),'html':f'{OM} · <b>INMET 56481</b>'},
 {'ini':ini('f8'),'fim':ini('f9'),'html':'<b>INMET</b> · orientações do aviso 56503'}]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "alagada": "#5ec8ff", "rajadas": "#ffd23f", "atingir": "#ffd23f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "pior": "#ff2a1f", "comenta": "#ffd23f", "arvores": "#5ec8ff", "encosta": "#ff8c1a", "rio": "#5ec8ff"}
LUGAR = {"sao", "paulo", "espirito", "santo", "goias", "belo", "horizonte", "brasilia", "centronorte", "norte", "sul", "grande",
         "cuiaba", "goiania", "piaui", "rio", "janeiro", "teresina", "amazonas", "minas", "parana", "capital", "catarinense", "nordeste", "quarta", "segunda", "amanha", "semana", "inemaclub", "cidade", "regiao", "cidades", "quinta", "domingo", "terca", "sexta", "inmet"}
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
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(CQ)}+{len(CS)} colunas; previsão 25/11–01/12")
