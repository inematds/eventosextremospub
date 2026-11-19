#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 19/11/2026 (quinta) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 20/11 a 26/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "19/11/2026"
SEM = "20 A 26/11"
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

# Janela exclusiva 20–26/11; máximos são locais, não totais estaduais.
R=json.loads((AQUI/'om/prev15_resumo.json').read_text())
G=json.loads((AQUI/'om/prev15_grade.json').read_text())['pts']
CAP=json.loads((AQUI/'om/prev15_capitais.json').read_text())['capitais']
gs=R['grade']['semana']; pu=gs['por_uf']
assert R['inicio']=='2026-11-20' and gs['dias']=='2026-11-20 a 2026-11-26'
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
av=next(a for a in AV['futuro'] if a['id']==56457)
assert av['inicio']=='2026-11-20 09:16' and av['severidade']=='Perigo'
soma=lambda v:round(sum(x or 0 for x in v),1)
pt=lambda xy:next(q for q in G if q['p']==xy)
assert soma(pt([-54,-25.5])['chuva'][:7])==289.4
assert pt([-52.5,-27])['chuva'][0]==102.9
assert next(q for q in CAP if q['cap']=='Belo Horizonte') and soma(next(q for q in CAP if q['cap']=='Belo Horizonte')['chuva'][:7])==87.4
assert pt([-42,-4.5])['tmax'][3]==41.8
assert next(q for q in CAP if q['cap']=='Manaus')['chuva'][6]==64.2
assert pt([-48,-24])['raj'][6]==70.6
assert pt([-51,-28.5])['tmin'][6]==9.8
views=[(-54,-25.5,5),(-52.5,-27,5),(-52,-26,4.2),(-44,-19.9,4.3),(-42,-4.5,4.8),(-60.02,-3.12,4.8),(-48,-24,4.8),(-51,-28.5,5),(-51,-14,3.7),(-51,-14,3.7),(-51,-14,3.7)]
K=lambda t,lon,lat,z:{'t':round(t,3),'lon':lon,'lat':lat,'zoom':z,'pitch':28,'bearing':0}
camera=[]
for i,v in enumerate(views,1):
 fid=f'f{i}'
 camera.extend([K(0 if i==1 else ini(fid)+.4,*v),K(fim(fid)-.35,*v)])
if CANTO:
 camera[0].update(lat=-16,zoom=4.5);camera[1].update(lat=-16,zoom=4.5)
camera.append(K(DUR,*views[-1]));camera.sort(key=lambda x:x['t'])
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},'base':'sat/web/geocolor.jpg','bbox':[-76,-35,-33,7],'tint':[170,170,175]}
estados=[{'id':'abertura','ini':-1,'fim':ini('f2'),'ufs':['PR'],'cor':VERM,'alfa':.85}]
for fid,ufs,cor in [('f2',['SC'],AZUL),('f3',['RS','SC','PR'],LARANJA),('f4',['MG','GO','MS','MT','SP','RJ','ES'],AZUL),('f5',['PI'],VERM),('f6',['AM'],AZUL),('f7',['SP'],AMAR),('f8',['RS'],AZUL)]:
 assert all(uf in pu for uf in ufs)
 estados.append({'id':fid,'ini':ini(fid),'fim':fim(fid),'ufs':ufs,'cor':cor,'alfa':.7})
estados.append({'id':'chuvaBR','ini':ini('f9'),'fim':DUR,'ufs':[uf for uf,v in pu.items() if v['chuva_max']>=90],'cor':AZUL,'alfa':.35})
cor_mm=lambda v:[255,255,255] if v>=200 else [94,200,255] if v>=120 else AZUL
CS=[{'id':f'c{i}','p':q['p'],'v':soma(q['chuva'][:7]),'cor':cor_mm(soma(q['chuva'][:7]))} for i,q in enumerate(G) if soma(q['chuva'][:7])>=40]
assert max(d['v'] for d in CS)==289.4
colunas=[{'id':'chuva','ini':ini('f2'),'fim':fim('f4'),'dados':CS,'escala':600,'raio':22000,'cor':AZUL,'ordem':{},'varredura':0}]
pinos=[]
for fid,nome,sub,lon,lat in [('f1','Oeste do Paraná','289,4 mm previstos · 20–26/11',-54,-25.5),('f2','Oeste de SC','102,9 mm previstos · sex 20/11',-52.5,-27),('f4','Belo Horizonte','87,4 mm previstos · 20–26/11',-43.94,-19.92),('f5','Piauí','41,8 °C previstos · seg 23/11',-42,-4.5),('f6','Manaus','64,2 mm previstos · qui 26/11',-60.02,-3.12),('f7','Interior de SP','70,6 km/h previstos · qui 26/11',-48,-24),('f8','Serra gaúcha','9,8 °C previstos · qui 26/11',-51,-28.5)]:
 pinos.append({'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':-1 if fid=='f1' else ini(fid)+.5,'fim':fim(fid),'h':160})
hero=[{'ini':-1,'fim':fim('f1'),'html':f'''<div style="font:400 112px/1 'Archivo Black';margin-bottom:16px">{DATA}</div><div class="dt" style="background:#ff2a1f;color:white;font-size:38px">ALERTA · PRÓXIMOS 7 DIAS</div><div class="t1" style="font-size:170px;color:#ffd23f">ATÉ 289,4</div><div style="font:900 68px/1.05 Inter">MM · OESTE DO PARANÁ</div><div style="font:900 44px/1.12 Inter;margin-top:12px">PREVISTOS · SEX 20 A QUI 26/11</div><div style="font:400 104px/1 'Archivo Black';color:#ff5147;margin-top:22px">SE PREPARE</div>'''}]
def painel(fid,k,valor,unid,palavra,l,cor='#5ec8ff'):
 return {'ini':ini(fid),'fim':fim(fid),'k':k,'contador':{'de':0,'ate':valor,'dec':0 if isinstance(valor,int) else 1,'ini':chega(fid,palavra),'dur':1.0,'cor':cor,'unid':unid},'l':l,'borda':cor}
paineis=[
 painel('f2','OESTE DE SC · PREVISTO SEX 20/11',102.9,'MM','102','Valor local · grade 1,5°'),
 {'ini':ini('f3'),'fim':fim('f3'),'k':'INMET · SEXTA 20/11','itens':[{'t':ini('f3'),'txt':'AVISO LARANJA · TEMPESTADE'},{'t':em('f3','granizo'),'txt':'Granizo e alagamentos'}],'borda':'#ff8c1a'},
 painel('f4',f'BELO HORIZONTE · PREVISTO {SEM}',87.4,'MM','87','Acumulado de sexta até quinta'),
 painel('f5','PIAUÍ · PREVISTO SEG 23/11',41.8,'°C','41','Evite esforço sob sol forte','#ff5147'),
 painel('f6','MANAUS · PREVISTO QUI 26/11',64.2,'MM','64','Atenção aos alagamentos'),
 painel('f7','INTERIOR DE SP · PREVISTO QUI 26/11',70.6,'KM/H','70','Carro longe de árvores','#ffd23f'),
 painel('f8','SERRA GAÚCHA · PREVISTO QUI 26/11',9.8,'°C','9','Mínima · separe roupa de frio'),
 {'ini':ini('f9'),'fim':fim('f9'),'k':'SE PREPARE','itens':[{'t':ini('f9'),'txt':'Não atravesse rua alagada'},{'t':em('f9','Defesa'),'txt':'Acompanhe a Defesa Civil'}]},
 {'ini':ini('f10'),'fim':fim('f10'),'k':'COMENTA AQUI','itens':[{'t':ini('f10'),'txt':'De que cidade você é?'},{'t':em('f10','tempo'),'txt':'Como está o tempo aí?'}]}
]
cta={'ini':ini('f11'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f11','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
OM=f'<b>Open-Meteo</b>, previsão lida em {DATA}'
fontes=[{'ini':-1,'fim':ini('f3'),'html':f'{OM} · 20 a 26/11 · valores locais'},
 {'ini':ini('f3'),'fim':ini('f4'),'html':f'<b>INMET</b> · aviso 56457 · sex 20/11 · lido {DATA}'},
 {'ini':ini('f4'),'fim':ini('f5'),'html':f'{OM} · INMET 56456/56457 · feriado'},
 {'ini':ini('f5'),'fim':ini('f9'),'html':f'{OM} · valores locais previstos'},
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
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(CS)} colunas; previsão 20–26/11")
