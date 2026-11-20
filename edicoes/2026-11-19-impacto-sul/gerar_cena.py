#!/usr/bin/env python3
"""Impacto Sul 19/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "19/11/2026"
MET = "Meteorologia · " + DATA
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / (os.environ.get("TEMPOS") or ("avatar/tempos.json" if AVATAR else "tempos.json"))).read_text())
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
DUR = round(fim(T[-1]["id"]), 3)
FIM_VIDEO = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(AQUI / "avatar/avatar.mp4")], capture_output=True, text=True).stdout or DUR) if AVATAR else DUR
FIM_VIDEO = min(FIM_VIDEO, DUR)   # o compor_avatar corta no fim do avatar: a última cena vale até aqui
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]
MIN_CENA, MIN_MAPA = 2.5, 3.0



# Avisos da coleta de 19/11; geocódigos únicos, sem somar áreas sobrepostas.
from collections import Counter
from scipy.optimize import linear_sum_assignment
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56453)=={'43':21,'42':194,'41':207}
assert cidades(56457)=={'43':400,'42':295,'41':399}
assert aviso[56457]['inicio']=='2026-11-20 09:16'
assert aviso[56457]['fim']=='2026-11-20 23:59'
assert '60-100 km/h' in aviso[56457]['riscos'][0]
assert '100 mm/dia' in aviso[56457]['riscos'][0]
END=FIM_VIDEO if AVATAR else DUR
DUR=END
CAPA=3.0
MAP0=ini('f5'); MAP1=MAP0+3.0
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.ceil((b-a)/3.0)
    assert num>0 and (b-a)/num>=2.5,('intervalo insuficiente',a,b,num)
    for k in range(num):slots.append((a+k*(b-a)/num,a+(k+1)*(b-a)/num))
clipes=json.loads((AQUI/'pesquisa/clipes.json').read_text())
assert len(slots)>=len(clipes),'Faltam janelas para todos os registros fortes'
# Cada cena forte recebe janela exclusiva. Não se perde nenhuma com --canto.
# Priorizamos o assunto da fala, preservando também os registros durante a pergunta/CTA.
preferidos=[]
for x in clipes:
    fid=x['fala'];siblings=[c for c in clipes if c['fala']==fid];idx=siblings.index(x)
    preferidos.append(ini(fid)+(idx+.5)*(fim(fid)-ini(fid))/len(siblings))
def custo(k,a,b,target):
    mid=(a+b)/2
    fid=next((t['id'] for t in T if t['ini']<=mid<t['fim']),'f8')
    x=clipes[k]
    penalidade=0
    if fid=='f3' and x['video']!='v3':penalidade=1000
    if fid=='f4' and k not in (10,17):penalidade=1000
    if fid=='f2' and x['video']=='v3':penalidade=1000
    if fid=='f1' and x['video']=='v3':penalidade=1000
    return abs(mid-target)+penalidade
rows,cols=linear_sum_assignment([[custo(k,a,b,target) for a,b in slots] for k,target in enumerate(preferidos)])
selected={int(c):int(r) for r,c in zip(rows,cols)}
def nearest(mid):
    fid=next((t['id'] for t in T if t['ini']<=mid<t['fim']),'f8')
    candidates=[k for k,x in enumerate(clipes) if x['fala']==fid]
    if not candidates:candidates=[6,7,8,10,15]
    return candidates[int(mid/3)%len(candidates)]
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':0}]
visual=[]
for j,(a,b) in enumerate(slots):
    k=selected.get(j,nearest((a+b)/2));x=clipes[k]
    q=sorted((AQUI/x['usado']).glob('*.jpg'))
    assert b-a<=len(q)/30+.03,(k,b-a,len(q)/30)
    telas.append({'seq':[str(z.relative_to(AQUI)) for z in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':.02})
    visual.append({'ini':a,'fim':b,'lugar':x['rotulo']})
assert all(t['fim']-t['ini']>=2.5 for t in telas)
SUL={'lon':-51.5,'lat':-27.8,'zoom':5.25,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}]
SAT=None
estados=[{'id':uf,'ini':MAP0,'fim':MAP1,'ufs':[uf],'cor':LAR,'alfa':.28} for uf in ('RS','SC','PR')]
pinos=[{'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0,'fim':MAP1,'h':25} for nome,sub,lon,lat in [
('Sudoeste do PR','Chuva prevista',-52.8,-25.6),
('Oeste de SC','Temporais previstos',-52.6,-27.0),
('Norte do RS','Chuva volumosa prevista',-52.4,-28.8)]]
def painel(fid,k,linhas,contador=None):
    a,b=ini(fid),fim(fid)
    z={'fid':fid,'ini':a,'fim':b,'k':k,'borda':'rgba(255,42,31,.8)'}
    if contador:
        valor,palavra,unid=contador
        z['ini']=max(a,em(fid,palavra)-1)
        z.update(contador={'de':0,'ate':valor,'ini':em(fid,palavra)-1,'dur':1,'cor':'#FACC15','unid':unid},l=' · '.join(linhas))
    else:z['itens']=[{'t':a+i*.25,'txt':txt} for i,txt in enumerate(linhas)]
    return z
paineis=[
painel('f1','LITORAL GAÚCHO · HOJE',['Imbé e Tramandaí','Granizo nesta tarde']),
painel('f2','TRAMANDAÍ / RS · HOJE',['Ruas alagadas','Calhas transbordaram']),
painel('f3','CAXIAS DO SUL / RS · HOJE',['Granizo e rajadas','Telhados atingidos']),
painel('f4','DIVISA RS / SC · HOJE',['Destelhamentos','Árvores e rede atingidas']),
painel('f5','SERRA, VALE E LITORAL · ESTA NOITE',['Calor e umidade','Alimentam instabilidades']),
painel('f6','RS · SEXTA · PREVISÃO INMET',['Até 100 mm/dia','Nas áreas em aviso laranja'],(100,'100','mm / DIA')),
painel('f7','SC · SEXTA · PREVISÃO INMET',['Rajadas de até 100 km/h','Nas áreas em aviso laranja'],(100,'100','km/h · ATÉ')),
painel('f8','SUDOESTE DO PARANÁ · PREVISÃO',['Chuva volumosa','Sexta e domingo']),
painel('f9','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
for fid,k,txt in [('f6','NORTE DO RS · SEXTA · PREVISÃO','Chuva volumosa nas áreas avisadas'),('f7','OESTE DE SC · SEXTA · PREVISÃO','Risco de temporais')]:
    z=next(p for p in paineis if p['fid']==fid)
    paineis.append({'fid':fid+'-intro','ini':ini(fid),'fim':z['ini'],'k':k,'itens':[{'t':ini(fid),'txt':txt}]})
paineis[0]['ini']=CAPA
paineis.sort(key=lambda p:p['ini'])
for a,b in zip(paineis,paineis[1:]):a['fim']=min(a['fim'],b['ini'])
fontes=[{'ini':0,'fim':CAPA,'html':f'<b>Granizo · litoral gaúcho · HOJE</b> · {MET}'}]
for v in visual:
    fontes.append({'ini':v['ini'],'fim':v['fim'],'html':f"<b>{v['lugar']}</b> · registro de hoje · {MET}"})
# Identifica separadamente previsão oficial e local da imagem real.
for fid in ('f6','f7'):
    fontes.insert(0,{'ini':ini(fid),'fim':fim(fid),'html':f'<b>INMET · {DATA}</b> · aviso 56457 · PREVISÃO para sexta · imagens: registros de hoje no Sul'})
fontes.insert(0,{'ini':MAP0,'fim':MAP1,'html':f'<b>INMET · {DATA}</b> · áreas dos três estados em aviso · previsão para sexta'})
cta={'ini':ini('f10'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f10','inema'),'fim':DUR,'a':'inema.club','b':'aprenda de graça · inteligência artificial'}

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "gelo": "#5ec8ff", "nino": "#5ec8ff",
         "calor": "#ff8c1a", "dispararam": "#ff8c1a", "graus": "#ff8c1a", "combustivel": "#ff8c1a", "arrancaram": "#ff2a1f",
         "tempestade": "#ff2a1f", "tempestades": "#ff2a1f", "granizo": "#ff2a1f", "estragos": "#ff2a1f", "telhados": "#ff2a1f",
         "vento": "#ff8c1a", "aviso": "#ff8c1a", "dispara": "#ff8c1a", "atencao": "#ff8c1a", "atento": "#ff8c1a", "comenta": AM,
         "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "rio", "grande", "oeste", "norte", "santa", "catarina", "parana", "paraguai", "inemaclub", "cidade"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and len(" ".join(b["w"] for b in bloco) + " " + w) > 19:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": t["palavras"][i - 1]["f"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"19/11 · INMET","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; 18 clipes fortes; mapa {MAP0:.2f}–{MAP1:.2f} s')
