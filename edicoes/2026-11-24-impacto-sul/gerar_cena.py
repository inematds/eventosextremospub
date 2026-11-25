#!/usr/bin/env python3
"""Impacto Sul 24/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "24/11/2026"
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
        if (n(palavra)==n(p["w"]) if len(n(palavra))<=2 else n(palavra) in n(p["w"])):
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



# Avisos da coleta atual: contagens congeladas da edição.
from collections import Counter
from scipy.optimize import linear_sum_assignment
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56492)=={'41':287,'42':139,'43':214}
assert cidades(56499)=={'41':399,'42':280,'43':164}
assert cidades(56501)=={'41':398,'42':24}
assert cidades(56502)=={'41':399,'42':92}
assert aviso[56492]['fim']=='2026-11-24 23:59'
assert aviso[56499]['inicio']=='2026-11-25 00:00'
assert aviso[56501]['inicio']=='2026-11-25 00:00'
assert '100 mm/dia' in aviso[56501]['riscos'][0]
END=FIM_VIDEO if AVATAR else DUR
DUR=END
# Manchete imóvel até terminar o fato principal, antes da identificação da edição.
CAPA=max(3.0, em('f1','É'))
MAP0=ini('f5'); MAP1=MAP0+3.0
clipes=json.loads((AQUI/'pesquisa/clipes.json').read_text())
# Cada clipe tem 2.86+ s; janelas de 2.5–2.8 s deixam folga no canto.
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.floor((b-a)/2.5)
    assert num>0 and 2.5<=(b-a)/num<=2.95,('intervalo insuficiente',a,b,num)
    slots += [(a+k*(b-a)/num,a+(k+1)*(b-a)/num) for k in range(num)]
assert len(slots)>=len(clipes), 'Faltam janelas para todas as cenas fortes'
# Atribuição mínima preserva todas as cenas. Penaliza trocas de cidade na fala factual;
# restantes entram na previsão, pergunta e CTA, sempre com rótulo geográfico do registro.
def slotfid(a,b):
    return next((t['id'] for t in T if t['ini']<=(a+b)/2<t['fim']),'f11')
def custo(x,a,b):
    fid=slotfid(a,b); mid=(a+b)/2
    target=(ini(x['fala'])+fim(x['fala']))/2
    penalty=0
    if fid=='f3' and x['video']!='v5':penalty=1000
    if fid=='f4' and x['video']!='v2':penalty=1000
    if fid in ('f1','f2') and x['video'] not in ('v3','v4'):penalty=1000
    return abs(mid-target)+penalty
rows,cols=linear_sum_assignment([[custo(x,a,b) for a,b in slots] for x in clipes])
selected={int(j):int(i) for i,j in zip(rows,cols)}
def nearest(a,b):
    fid=slotfid(a,b)
    candidates=[i for i,x in enumerate(clipes) if x['fala']==fid]
    if not candidates:
        candidates=[i for i,x in enumerate(clipes) if x['video'] in ('v3','v4')]
    return candidates[int(a/2.7)%len(candidates)]
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':0}]
visual=[]
for j,(a,b) in enumerate(slots):
    x=clipes[selected.get(j,nearest(a,b))]
    q=sorted((AQUI/x['usado']).glob('*.jpg'))
    assert b-a<=len(q)/30+.001,(x['usado'],b-a,len(q)/30)
    telas.append({'seq':[str(z.relative_to(AQUI)) for z in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':0})
    visual.append({'ini':a,'fim':b,'lugar':x['rotulo']})
assert all(t['fim']-t['ini']>=2.5 for t in telas)
assert all(any(t.get('seq',[''])[0].startswith(c['usado']+'/') for t in telas) for c in clipes)
SUL={'lon':-51.5,'lat':-27.8,'zoom':5.25,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}];SAT=None
estados=[{'id':uf,'ini':MAP0,'fim':MAP1,'ufs':[uf],'cor':cor,'alfa':.28} for uf,cor in [('RS',AMA),('SC',LAR),('PR',VERM)]]
alertas=[]
# Primeiro amarelo, depois laranja e vermelho, mantendo o maior risco visível.
for id,cor in [(56497,AMA),(56494,LAR),(56492,VERM)]:
    alertas.append({'id':id,'ini':MAP0,'fim':MAP1,'ids':[c for c in aviso[id]['geocodes'].split(',') if c[:2] in ('41','42','43')],'cor':cor,'alfa':.5,'varredura':0})
pinos=[{'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0,'fim':MAP1,'h':130 if nome=='Verê / PR' else 1} for nome,sub,lon,lat in [
('Verê / PR','Enxurrada hoje',-52.9,-25.88),('Oeste / SC','Chuva persistente',-53.1,-26.9),('Ijuí / RS','Estradas atingidas',-53.91,-28.39)]]
def painel(fid,k,linhas,contador=None):
    a,b=ini(fid),fim(fid);z={'fid':fid,'ini':a,'fim':b,'k':k,'borda':'rgba(255,42,31,.8)'}
    if contador:
        valor,palavra,unid=contador
        # Contador termina exatamente na palavra do número, mesmo se começar antes da fala.
        z['ini']=em(fid,palavra)-1
        z.update(contador={'de':0,'ate':valor,'ini':em(fid,palavra)-1,'dur':1,'cor':'#FACC15','unid':unid},l=' · '.join(linhas))
    else:z['itens']=[{'t':a+i*.25,'txt':txt} for i,txt in enumerate(linhas)]
    return z
paineis=[
painel('f1','SUDOESTE / PR · HOJE',['Mais de 200 mm','Em pouco mais de 1 hora']),
painel('f2','VERÊ E ITAPEJARA / PR',['Casas e comércio atingidos','Veículos cercados pela água']),
painel('f3','PALMAS / PR · ESTIMATIVA',['Possivelmente acima de 90 km/h'],(90,'90','km/h · POSSIVELMENTE ACIMA')),
painel('f4','NOROESTE / RS · HOJE',['Mais de 150 mm desde a manhã'],(150,'150','mm · MAIS DE')),
painel('f5','SUL · SISTEMA QUASE PARADO',['Calor + umidade','Tempestades persistentes']),
painel('f6','RS · AMANHÃ · PREVISÃO',['Nas áreas em aviso amarelo'],(50,'50','mm / DIA · ATÉ')),
painel('f7','SC · AMANHÃ · PREVISÃO',['Nas áreas em aviso laranja'],(100,'100','mm / DIA · ATÉ')),
painel('f8','PR · AMANHÃ · PREVISÃO',['Quarta e quinta: chuva pode persistir'],(100,'100','mm / DIA · ATÉ')),
painel('f9','ATENÇÃO NAS ÁREAS ATINGIDAS',['Evite ruas alagadas','Mantenha distância de fios caídos']),
painel('f10','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
paineis[0]['ini']=CAPA
# Retirar o painel durante o mapa: deixa os três pinos livres.
paineis[4]['ini']=MAP1
for fid in ['f3','f4','f6','f7','f8']:
 z=next(x for x in paineis if x['fid']==fid)
 if z['ini']-ini(fid)>.2:
  paineis.append({'fid':fid+'-intro','ini':ini(fid),'fim':z['ini'],'k':z['k'],'itens':[{'t':ini(fid),'txt':{'f3':'Árvores derrubadas · telhados atingidos','f4':'Estradas cedem perto de Ijuí','f6':'Atenção no norte gaúcho nesta noite','f7':'Oeste: chuva pode persistir','f8':'Risco continua no sudoeste'}[fid]}]})
paineis.sort(key=lambda p:p['ini'])
for a,b in zip(paineis,paineis[1:]):a['fim']=min(a['fim'],b['ini'])
fontes=[{'ini':0,'fim':CAPA,'html':f'<b>Sudoeste / PR · hoje</b> · {MET} · imagem: Itapejara / PR'}]
for v in visual:
 fid=slotfid(v['ini'],v['fim'])
 official=f'<b>INMET · {DATA} · PREVISÃO</b>' if fid in ('f6','f7','f8') else f'<b>{MET}</b>'
 fontes.append({'ini':v['ini'],'fim':v['fim'],'html':f"{official} · registro: {v['lugar']}"})
fontes.insert(0,{'ini':MAP0,'fim':MAP1,'html':f'<b>INMET · {DATA}</b> · hoje · risco em partes dos estados'})
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


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"INMET · 24/11/2026","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"alertas":alertas,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; {len(clipes)} clipes fortes; mapa {MAP0:.2f}–{MAP1:.2f} s')
