#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 18/11/2026 (quarta) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 19/11 a 25/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "18/11/2026"
SEM = "19 A 25/11"
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

# Somente a janela 19–25/11; séries locais exatas.
R=json.loads((AQUI/'om/prev15_resumo.json').read_text())
G=json.loads((AQUI/'om/prev15_grade.json').read_text())['pts']
CAP=json.loads((AQUI/'om/prev15_capitais.json').read_text())['capitais']
gs=R['grade']['semana']; pu=gs['por_uf']
assert R['inicio']=='2026-11-19' and gs['dias']=='2026-11-19 a 2026-11-25'
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
for aid,dia in [(56446,'19'),(56447,'20')]:
 av=next(a for a in AV['futuro'] if a['id']==aid)
 assert av['inicio']==f'2026-11-{dia} 00:00' and av['severidade']=='Perigo Potencial'
soma=lambda v: round(sum(x or 0 for x in v),1)
pt=lambda xy:next(q for q in G if q['p']==xy)
assert next(q for q in CAP if q['cap']=='Florianópolis')['raj'][6]==84.6
assert soma(pt([-52.5,-27])['chuva'][:7])==283.6
assert pt([-52.5,-27])['chuva'][1]==59.2
assert soma(pt([-43.5,-16.5])['chuva'][:7])==139.1
assert pt([-42,-6])['tmax'][6]==42.2
assert pt([-55.5,-1.5])['tmax'][1]==39.8
assert pt([-51,-28.5])['tmin'][6]==8.1
views=[(-48.55,-27.59,5.0),(-52.5,-27,5.0),(-51,-27,4.5),(-43.5,-16.5,4.8),(-42,-6,4.8),(-55.5,-1.5,4.8),(-51,-28.5,5.0),(-51,-14,3.7),(-51,-14,3.7),(-51,-14,3.7)]
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
estados=[{'id':'abertura','ini':-1,'fim':ini('f2'),'ufs':['SC'],'cor':VERM,'alfa':.85}]
for fid,ufs,cor in [('f2',['SC'],AZUL),('f3',['RS','SC','PR'],AMAR),('f4',['MG','GO'],AZUL),('f5',['PI'],VERM),('f6',['PA'],VERM),('f7',['RS'],AZUL)]:
 assert all(uf in pu for uf in ufs)
 estados.append({'id':fid,'ini':ini(fid),'fim':fim(fid),'ufs':ufs,'cor':cor,'alfa':.7})
estados.append({'id':'chuvaBR','ini':ini('f8'),'fim':DUR,'ufs':[uf for uf,v in pu.items() if v['chuva_max']>=90],'cor':AZUL,'alfa':.35})
cor_mm=lambda v:[255,255,255] if v>=200 else [94,200,255] if v>=120 else AZUL
CS=[{'id':f'c{i}','p':q['p'],'v':soma(q['chuva'][:7]),'cor':cor_mm(soma(q['chuva'][:7]))} for i,q in enumerate(G) if soma(q['chuva'][:7])>=40]
assert max(d['v'] for d in CS)==283.6
colunas=[{'id':'chuva','ini':ini('f2'),'fim':fim('f4'),'dados':CS,'escala':600,'raio':22000,'cor':AZUL,'ordem':{},'varredura':0}]
pinos=[]
for fid,nome,sub,lon,lat in [('f1','Florianópolis','84,6 km/h previstos · qua 25/11',-48.55,-27.59),('f2','Oeste de SC','59,2 mm previstos · sex 20/11',-52.5,-27),('f4','Norte de Minas','139,1 mm previstos · 19–25/11',-43.5,-16.5),('f5','Piauí','42,2 °C previstos · qua 25/11',-42,-6),('f6','Oeste do Pará','39,8 °C previstos · sex 20/11',-55.5,-1.5),('f7','Serra gaúcha','8,1 °C previstos · qua 25/11',-51,-28.5)]:
 pinos.append({'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':-1 if fid=='f1' else ini(fid)+.5,'fim':fim(fid),'h':160})
hero=[{'ini':-1,'fim':fim('f1'),'html':f'''<div style="font:400 112px/1 'Archivo Black';margin-bottom:16px">{DATA}</div><div class="dt" style="background:#ff2a1f;color:white;font-size:38px">ALERTA · PRÓXIMOS 7 DIAS</div><div class="t1" style="font-size:180px;color:#ffd23f">ATÉ 84,6</div><div style="font:900 68px/1.05 Inter">KM/H · FLORIANÓPOLIS</div><div style="font:900 48px/1.12 Inter;margin-top:12px">RAJADAS PREVISTAS · QUA 25/11</div><div style="font:400 104px/1 'Archivo Black';color:#ff5147;margin-top:22px">SE PREPARE</div>'''}]
def painel(fid,k,valor,unid,palavra,l,cor='#5ec8ff'):
 return {'ini':ini(fid),'fim':fim(fid),'k':k,'contador':{'de':0,'ate':valor,'dec':0 if isinstance(valor,int) else 1,'ini':chega(fid,palavra),'dur':1.0,'cor':cor,'unid':unid},'l':l,'borda':cor}
# Acumulado e dia no mesmo painel; cada contador termina ao ouvir seu valor.
paineis=[
 painel('f2',f'OESTE DE SC · PREVISTO {SEM}',283.6,'MM EM 7 DIAS','283','Previsão local · grade 1,5°'),
 {'ini':ini('f3'),'fim':fim('f3'),'k':'INMET · QUINTA 19 E SEXTA 20/11','itens':[{'t':ini('f3'),'txt':'AVISO AMARELO · TEMPESTADE'},{'t':em('f3','granizo'),'txt':'Risco de granizo e alagamentos'}],'borda':'#ffd23f'},
 painel('f4',f'NORTE DE MG · PREVISTO {SEM}',139.1,'MM EM 7 DIAS','139','Chuva desde quinta · atenção em Goiás'),
 painel('f5','PIAUÍ · PREVISTO QUA 25/11',42.2,'°C','42','Evite esforço sob sol forte','#ff5147'),
 painel('f6','OESTE DO PA · PREVISTO SEX 20/11',39.8,'°C','39','Leve água ao trabalhar ao ar livre','#ff5147'),
 painel('f7','SERRA GAÚCHA · PREVISTO QUA 25/11',8.1,'°C MÍNIMA','8','Separe roupa de frio'),
 {'ini':ini('f8'),'fim':fim('f8'),'k':'SE PREPARE','itens':[{'t':em('f8','carro'),'txt':'Carro longe de árvores'},{'t':em('f8','alagada'),'txt':'Não atravesse rua alagada'},{'t':em('f8','Defesa'),'txt':'Acompanhe a Defesa Civil'}]},
 {'ini':ini('f9'),'fim':fim('f9'),'k':'COMENTA AQUI','itens':[{'t':ini('f9'),'txt':'De que cidade você é?'},{'t':em('f9','tempo'),'txt':'Como está o tempo aí?'}]}
]
tsexta=em('f2','sexta')
paineis[0]['fim']=tsexta
sex=painel('f2','OESTE DE SC · PREVISTO SEX 20/11',59.2,'MM NA SEXTA','59','283,6 mm previstos no ponto · 19 a 25/11');sex['ini']=tsexta
paineis.insert(1,sex)
cta={'ini':ini('f10'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f10','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
OM=f'<b>Open-Meteo</b>, previsão lida em {DATA}'
fontes=[{'ini':-1,'fim':ini('f3'),'html':f'{OM} · 19 a 25/11 · valores locais'},
 {'ini':ini('f3'),'fim':ini('f4'),'html':f'<b>INMET</b> · avisos 56446/56447 · qui/sex · lidos {DATA}'},
 {'ini':ini('f4'),'fim':ini('f8'),'html':f'{OM} · grade 1,5° · valores locais'},
 {'ini':ini('f8'),'fim':ini('f9'),'html':'<b>INMET</b> · orientações de proteção nos avisos'}]

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
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(CS)} colunas; previsão 19–25/11")
