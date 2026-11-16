#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 16/11/2026 (segunda) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 17/11 a 23/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/11/2026"
SEM = "17 A 23/11"
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

# Dados desta edição: janela exclusiva 17–23/11.
R = json.loads((AQUI/'om/prev15_resumo.json').read_text())
G = json.loads((AQUI/'om/prev15_grade.json').read_text())['pts']
gs = R['grade']['semana']; pu = gs['por_uf']
assert R['inicio']=='2026-11-17' and gs['dias']=='2026-11-17 a 2026-11-23'
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
av=next(a for a in AV['futuro'] if a['id']==56433)
cods=set(av['geocodes'].split(','))
assert av['inicio']=='2026-11-18 00:00' and av['fim']=='2026-11-18 23:59' and len(cods)==658
assert {uf:sum(c.startswith(prefix) for c in cods) for uf,prefix in [('RS','43'),('SC','42'),('PR','41')]}=={'RS':369,'SC':171,'PR':118}
soma=lambda v: round(sum(x or 0 for x in v),1)
pt=lambda xy:next(q for q in G if q['p']==xy)
assert soma(pt([-43.5,-16.5])['chuva'][:7])==142.3
assert pt([-49.5,-13.5])['chuva'][0]==54.4
assert pt([-54,-28.5])['chuva'][3]==90.1
assert pt([-52.5,-27])['raj'][3]==67.3
assert pt([-42,-4.5])['tmax'][6]==40.7
assert pt([-55.5,-1.5])['tmax'][1]==38.8
# Uma câmera por trecho; oeste do Pará ganha seu próprio enquadramento.
views=[(-52,-27.5,4.7),(-52,-27.5,4.8),(-43.5,-16.5,5.4),(-49.5,-13.5,5.4),(-54,-28.5,5.3),(-52.5,-27,5.5),(-42,-4.5,5.2),(-51,-14,3.7),(-51,-14,3.7),(-51,-14,3.7)]
K=lambda t,lon,lat,z:{'t':round(t,3),'lon':lon,'lat':lat,'zoom':z,'pitch':28,'bearing':0}
camera=[]
for i,v in enumerate(views,1):
 fid=f'f{i}'
 start=0 if i==1 else ini(fid)+.4
 end=fim(fid)-.35
 if i==7:
  para=em('f7','Pará')
  camera.extend([K(start,*v),K(para-.5,*v),K(para+.35,-55.5,-1.5,5.0),K(end,-55.5,-1.5,5.0)])
 else:
  camera.extend([K(start,*v),K(end,*v)])
if CANTO:
 # Desce o Sul abaixo do hero no layout com avatar no canto.
 camera[0].update(lat=-16,zoom=4.5)
 camera[1].update(lat=-16,zoom=4.5)
camera.append(K(DUR,*views[-1]));camera.sort(key=lambda x:x['t'])
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},'base':'sat/web/geocolor.jpg','bbox':[-76,-35,-33,7],'tint':[170,170,175]}
estados=[{'id':'sul0','ini':-1,'fim':ini('f3'),'ufs':['RS','SC','PR'],'cor':VERM,'alfa':.7}]
# A seleção é baseada em por_uf; as UFs indicam áreas, não cobertura uniforme.
for fid,ufs,cor in [('f3',['MG'],AZUL),('f4',['GO'],AZUL),('f5',['RS'],AZUL),('f6',['SC'],AMAR),('f7',['PI','PA'],VERM)]:
 assert all(uf in pu for uf in ufs)
 estados.append({'id':fid,'ini':ini(fid),'fim':fim(fid),'ufs':ufs,'cor':cor,'alfa':.65})
estados.append({'id':'chuvaBR','ini':ini('f8'),'fim':DUR,'ufs':[uf for uf,v in pu.items() if v['chuva_max']>=90],'cor':AZUL,'alfa':.35})
cor_mm=lambda v:[255,255,255] if v>=120 else [94,200,255] if v>=90 else AZUL
CS=[{'id':f'c{i}','p':q['p'],'v':soma(q['chuva'][:7]),'cor':cor_mm(soma(q['chuva'][:7]))} for i,q in enumerate(G) if soma(q['chuva'][:7])>=40]
assert max(d['v'] for d in CS)==142.3
colunas=[{'id':'chuva','ini':ini('f3'),'fim':ini('f6'),'dados':CS,'escala':900,'raio':28000,'cor':AZUL,'ordem':{},'varredura':0}]
pinos=[]
for fid,nome,sub,lon,lat in [('f3','Norte de Minas','142,3 mm previstos · 17–23/11',-43.5,-16.5),('f4','Norte de Goiás','54,4 mm previstos · ter 17/11',-49.5,-13.5),('f5','Noroeste do RS','90,1 mm previstos · sex 20/11',-54,-28.5),('f6','Oeste de SC','67,3 km/h previstos · sex 20/11',-52.5,-27)]:
 pinos.append({'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':ini(fid)+1,'fim':fim(fid),'h':160})
pinos += [{'nome':'Norte do Piauí','sub':'40,7 °C previstos · seg 23/11','lon':-42,'lat':-4.5,'ini':ini('f7'),'fim':para,'h':160},{'nome':'Oeste do Pará','sub':'38,8 °C previstos · qua 18/11','lon':-55.5,'lat':-1.5,'ini':para,'fim':fim('f7'),'h':160}]
hero=[{'ini':-1,'fim':ini('f2')-.05,'html':f'''<div style="font:400 112px/1 'Archivo Black';margin-bottom:16px">{DATA}</div><div class="dt" style="background:#ff2a1f;color:white;font-size:38px">ALERTA · PRÓXIMOS 7 DIAS</div><div class="t1" style="font-size:240px;color:#ffd23f">658</div><div style="font:900 64px/1.05 Inter">CIDADES DO SUL</div><div style="font:900 52px/1.12 Inter;color:#fff;margin-top:12px">EM ALERTA NA QUARTA 18/11</div><div style="font:400 104px/1 'Archivo Black';color:#ff5147;margin-top:22px">SE PREPARE</div>'''}]

def painel(fid,k,valor,unid,palavra,l,cor='#5ec8ff',ate=None):
 return {'ini':ini(fid),'fim':ate if ate is not None else fim(fid),'k':k,'contador':{'de':0,'ate':valor,'dec':0 if isinstance(valor,int) else 1,'ini':chega(fid,palavra),'dur':1.0,'cor':cor,'unid':unid},'l':l,'borda':cor}
paineis=[
 painel('f2','INMET · PERIGO · QUARTA 18/11',658,'CIDADES EM ALERTA','aviso','RS 369 · SC 171 · PR 118','#ff8c1a'),
 painel('f3',f'NORTE DE MINAS · PREVISTO {SEM}',142.3,'MM EM 7 DIAS','142','Chuva de terça 17 a segunda 23/11'),
 painel('f4','NORTE DE GOIÁS · PREVISTO TER 17/11',54.4,'MM NA TERÇA','54','Previsão por ponto da grade'),
 painel('f5','NOROESTE DO RS · PREVISTO SEX 20/11',90.1,'MM NA SEXTA','90','115,8 mm previstos de 17 a 23/11'),
 painel('f6','OESTE DE SC · PREVISTO SEX 20/11',67.3,'KM/H','67','Rajada prevista pelo Open-Meteo','#ffd23f'),
 painel('f7','NORTE DO PI · PREVISTO SEG 23/11',40.7,'°C','40','Calor aumenta até segunda 23/11','#ff5147',para),
 {'ini':para,'fim':fim('f7'),'k':'OESTE DO PA · PREVISTO QUA 18/11','contador':{'de':0,'ate':38.8,'dec':1,'ini':chega('f7','38'),'dur':1,'cor':'#ff5147','unid':'°C'},'l':'Hidrate-se e evite exposição ao sol forte'},
 {'ini':ini('f8'),'fim':fim('f8'),'k':'SE PREPARE','itens':[{'t':em('f8','água'),'txt':'Beba água'},{'t':em('f8','alagada'),'txt':'Não atravesse rua alagada'},{'t':em('f8','árvores'),'txt':'Fique longe de árvores'}]},
 {'ini':ini('f9'),'fim':fim('f9'),'k':'COMENTA AQUI','itens':[{'t':ini('f9'),'txt':'De que cidade você é?'},{'t':em('f9','tempo'),'txt':'Como está o tempo aí?'}]}
]
# O primeiro painel usa valor já apresentado: não anima desde zero.
paineis[0]['contador']['de']=658
cta={'ini':ini('f10'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f10','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
OM=f'<b>Open-Meteo</b>, previsão lida em {DATA}'
fontes=[{'ini':-1,'fim':ini('f3'),'html':f'<b>INMET</b> · aviso 56433 · válido qua 18/11 · lido em {DATA} · áreas das UFs'},
 {'ini':ini('f3'),'fim':ini('f5'),'html':f'{OM} · 17 a 23/11 · grade 1,5° · valores locais'},
 {'ini':ini('f5'),'fim':ini('f6'),'html':f'{OM} · MetSul 15/11 · risco até sexta'},
 {'ini':ini('f6'),'fim':ini('f8'),'html':f'{OM} · 17 a 23/11 · valores locais'},
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
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])


C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "padding_topo": 540,
 "duracao": DUR,"marca":"INEMA · ALERTA DA SEMANA","selo":f"ALERTA · {SEM}","camera":camera,"sat":SAT,"estados":estados,"colunas":colunas,"pinos":pinos,"hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(CS)} colunas; 658 cidades")
