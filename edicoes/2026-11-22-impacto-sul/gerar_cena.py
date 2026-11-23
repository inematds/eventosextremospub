#!/usr/bin/env python3
"""Impacto Sul 22/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "22/11/2026"
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



# Avisos da coleta atual, com contagem de municípios única por estado.
from collections import Counter
from scipy.optimize import linear_sum_assignment
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56475)=={'41':399,'42':295,'43':351}
assert cidades(56477)=={'41':371,'42':114,'43':1}
assert cidades(56476)=={'41':399,'42':52}
assert cidades(56480)=={'41':399,'42':295,'43':401}
assert aviso[56477]['fim']=='2026-11-22 23:59'
assert aviso[56476]['inicio']=='2026-11-23 00:00'
assert aviso[56480]['inicio']=='2026-11-24 00:00'
assert '100 mm/dia' in aviso[56477]['riscos'][0]
END=FIM_VIDEO if AVATAR else DUR
DUR=END; CAPA=3.0
MAP0=ini('f5'); MAP1=MAP0+3.0
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.ceil((b-a)/2.9)
    assert num>0 and (b-a)/num>=2.5,('intervalo insuficiente',a,b,num)
    for k in range(num):slots.append((a+k*(b-a)/num,a+(k+1)*(b-a)/num))
clipes=json.loads((AQUI/'pesquisa/clipes.json').read_text())
assert len(slots)>=len(clipes),'Faltam janelas para todas as cenas fortes'
preferidos=[]
for x in clipes:
    fid=x['fala'];siblings=[c for c in clipes if c['fala']==fid];idx=siblings.index(x)
    preferidos.append(ini(fid)+(idx+.5)*(fim(fid)-ini(fid))/len(siblings))
def custo(x, target, a, b):
    mid=(a+b)/2
    fid=next((t['id'] for t in T if t['ini']<=mid<t['fim']), 'f11')
    permitido={'f2':('v4',),'f3':('v1','v2'),'f4':('v3',)}
    penal=10000 if fid in permitido and x['video'] not in permitido[fid] else 0
    return abs(mid-target)+penal
# Reservar as imagens do fenômeno para as palavras correspondentes.
# As demais tomadas obrigatórias entram nos trechos próximos, sempre localizadas.
selected={}
for fid, indices in [('f2',[15,16,17,18]),('f3',[5,6,8]),('f4',[12,13,14])]:
    js=[j for j,(a,b) in enumerate(slots) if ini(fid)<=(a+b)/2<fim(fid)]
    if len(js)<len(indices):
        # No canto mais rápido, prioriza granizo, enxurrada e destelhamento;
        # todas as demais tomadas continuam na atribuição global abaixo.
        indices=indices[:len(js)]
    for j,k in zip(js,indices):selected[j]=k
rest_clipes=[k for k in range(len(clipes)) if k not in selected.values()]
rest_slots=[j for j in range(len(slots)) if j not in selected]
rows,cols=linear_sum_assignment([[custo(clipes[k],preferidos[k],*slots[j]) for j in rest_slots] for k in rest_clipes])
selected.update({rest_slots[int(c)]:rest_clipes[int(r)] for r,c in zip(rows,cols)})
def nearest(mid):
    fid=next((t['id'] for t in T if t['ini']<=mid<t['fim']),'f11')
    candidates=[k for k,x in enumerate(clipes) if x['fala']==fid]
    # Durante previsão, evitar coluna de vento como se fosse previsão de novo tornado.
    if fid in ('f1','f2','f7'):candidates=[15,16,17,18]
    if fid=='f4':candidates=[12,13,14]
    if not candidates:candidates=[0,5,6,7,8,12,13,14,15,16,17,18]
    return candidates[int(mid/3)%len(candidates)]
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':0}]
visual=[]
for j,(a,b) in enumerate(slots):
    k=selected.get(j,nearest((a+b)/2));x=clipes[k]
    q=sorted((AQUI/x['usado']).glob('*.jpg'))
    assert b-a<=len(q)/30+.001,(k,b-a,len(q)/30)
    telas.append({'seq':[str(z.relative_to(AQUI)) for z in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':.02})
    visual.append({'ini':a,'fim':b,'lugar':x['rotulo']})
assert all(t['fim']-t['ini']>=2.5 for t in telas)
assert all(any(t.get('seq',[''])[0].startswith(c['usado']+'/') for t in telas) for c in clipes)
SUL={'lon':-51.5,'lat':-27.8,'zoom':5.25,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}];SAT=None
estados=[{'id':uf,'ini':MAP0,'fim':MAP1,'ufs':[uf],'cor':cor,'alfa':.28} for uf,cor in [('RS',AMA),('SC',LAR),('PR',LAR)]]
alertas=[{'id':56477,'ini':MAP0,'fim':MAP1,'geocodes':[c for c in aviso[56477]['geocodes'].split(',') if c[:2] in ('41','42','43')],'cor':LAR}]
pinos=[{'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0,'fim':MAP1,'h':1 if nome=='Norte do RS' else 25} for nome,sub,lon,lat in [
('Altônia / PR','Enxurrada hoje',-53.9,-23.87),('Oeste de SC','Risco de granizo',-53.0,-26.8),('Norte do RS','Chuva prevista',-53.0,-28.4)]]
def painel(fid,k,linhas,contador=None):
    a,b=ini(fid),fim(fid);z={'fid':fid,'ini':a,'fim':b,'k':k,'borda':'rgba(255,42,31,.8)'}
    if contador:
        valor,palavra,unid=contador;z['ini']=max(a,em(fid,palavra)-1)
        z.update(contador={'de':0,'ate':valor,'ini':em(fid,palavra)-1,'dur':1,'cor':'#FACC15','unid':unid},l=' · '.join(linhas))
    else:z['itens']=[{'t':a+i*.25,'txt':txt} for i,txt in enumerate(linhas)]
    return z
paineis=[
painel('f1','PARANÁ · HOJE · PREVISÃO',['Até 100 mm no dia','Áreas em aviso laranja']),
painel('f2','ALTÔNIA / PR · HOJE',['Ruas tomadas pela água','Casas e comércio atingidos']),
painel('f3','NORTE E NOROESTE / RS',['Granizo grande · noite passada','Sertão: telhados atingidos']),
painel('f4','SARANDI / RS · HOJE CEDO',['Casas destelhadas','Árvores quebradas']),
painel('f5','NORTE DO RS · ESTA NOITE',['Limite diário do aviso · previsão'],(50,'50','mm / DIA · ATÉ')),
painel('f6','SC · ESTA NOITE · PREVISÃO',['Nas áreas em aviso laranja'],(100,'100','mm / DIA · ATÉ')),
painel('f7','PR · AMANHÃ · PREVISÃO',['Até 50 mm no dia · áreas avisadas'],(60,'60','km/h · ATÉ')),
painel('f8','TERÇA · NOVA INTENSIFICAÇÃO',['Segunda: menos chuva prevista','Terça: pode voltar forte']),
painel('f9','ATENÇÃO NAS ÁREAS ATINGIDAS',['Árvores instáveis e fios caídos','Acompanhe a Defesa Civil']),
painel('f10','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
paineis[0]['ini']=CAPA
for fid,txt in [('f5','Chuva prevista no norte gaúcho'),('f6','Chuva e risco de granizo em SC'),('f7','Segunda com aviso no Paraná')]:
 z=next(p for p in paineis if p['fid']==fid)
 paineis.append({'fid':fid+'-intro','ini':ini(fid),'fim':z['ini'],'k':z['k'],'itens':[{'t':ini(fid),'txt':txt}]})
paineis.sort(key=lambda p:p['ini'])
for a,b in zip(paineis,paineis[1:]):a['fim']=min(a['fim'],b['ini'])
fontes=[{'ini':0,'fim':CAPA,'html':f'<b>INMET · aviso 56477 · PREVISÃO</b> · {DATA} · Registro de hoje: Altônia / PR'}]
for v in visual:fontes.append({'ini':v['ini'],'fim':v['fim'],'html':f"<b>{v['lugar']}</b> · {MET}"})
for v in visual:
    mid=(v['ini']+v['fim'])/2
    fid=next((t['id'] for t in T if t['ini']<=mid<t['fim']),'f11')
    if fid in ('f1','f5','f6','f7'):
        fontes.insert(0,{'ini':v['ini'],'fim':v['fim'],'html':f"<b>INMET · {DATA} · PREVISÃO</b> · imagens: {v['lugar']}"})
fontes.insert(0,{'ini':MAP0,'fim':MAP1,'html':f'<b>INMET · {DATA}</b> · áreas avisadas · PREVISÃO'})
cta={'ini':ini('f11'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f11','inema'),'fim':DUR,'a':'inema.club','b':'aprenda de graça · inteligência artificial'}

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


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"22/11/2026 · INMET","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"alertas":alertas,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; {len(clipes)} clipes fortes; mapa {MAP0:.2f}–{MAP1:.2f} s')
