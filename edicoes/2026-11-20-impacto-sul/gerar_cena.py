#!/usr/bin/env python3
"""Impacto Sul 20/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "20/11/2026"
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



# Avisos locais da coleta de 20/11. Contagens de geocódigos únicos por UF.
from collections import Counter
from scipy.optimize import linear_sum_assignment
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56457)=={'43':400,'42':295,'41':399}
assert cidades(56462)=={'43':452,'42':295,'41':399}
assert cidades(56466)=={'43':324,'42':295,'41':399}
assert aviso[56457]['fim']=='2026-11-20 23:59'
assert aviso[56462]['inicio']=='2026-11-21 00:00'
assert '60-100 km/h' in aviso[56457]['riscos'][0]
assert '50 mm/dia' in aviso[56462]['riscos'][0]
END=FIM_VIDEO if AVATAR else DUR
DUR=END; CAPA=3.0
MAP0=ini('f6'); MAP1=MAP0+3.0
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.ceil((b-a)/3.0)
    assert num>0 and (b-a)/num>=2.5,('intervalo insuficiente',a,b,num)
    for k in range(num):slots.append((a+k*(b-a)/num,a+(k+1)*(b-a)/num))
clipes=json.loads((AQUI/'pesquisa/clipes.json').read_text())
assert len(slots)>=len(clipes),'Faltam janelas para todos os registros fortes'
preferidos=[]
for x in clipes:
    fid=x['fala'];siblings=[c for c in clipes if c['fala']==fid];idx=siblings.index(x)
    preferidos.append(ini(fid)+(idx+.5)*(fim(fid)-ini(fid))/len(siblings))
def custo(k,a,b,target):
    
    if abs(a-CAPA)<.001:return 1000000
    mid=(a+b)/2;fid=next((t['id'] for t in T if t['ini']<=mid<t['fim']),'f9')
    x=clipes[k];penalidade=0
    if fid in ('f1','f2','f3','f7') and x['video']=='v4':penalidade=1000
    if fid=='f4' and k not in (14,15):penalidade=10000
    if fid=='f5' and k not in (16,17):penalidade=10000
    return abs(mid-target)+penalidade
rows,cols=linear_sum_assignment([[custo(k,a,b,target) for a,b in slots] for k,target in enumerate(preferidos)])
selected={int(c):int(r) for r,c in zip(rows,cols)}
def nearest(mid):
    fid=next((t['id'] for t in T if t['ini']<=mid<t['fim']),'f9')
    candidates=[k for k,x in enumerate(clipes) if x['fala']==fid]
    if fid=='f4':candidates=[14,15]
    if fid=='f5':candidates=[16,17]
    if not candidates:candidates=[14,15,16,17] if fid in ('f6','f8') else [0,1,7,8,11]
    return candidates[int(mid/3)%len(candidates)]
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':0}]
visual=[]
for j,(a,b) in enumerate(slots):
    k=selected.get(j,nearest((a+b)/2));x=clipes[k]
    q=sorted((AQUI/x['usado']).glob('*.jpg'))
    assert b-a<=len(q)/30+.03,(k,b-a,len(q)/30)
    telas.append({'seq':[str(z.relative_to(AQUI)) for z in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':.02})
    visual.append({'ini':a,'fim':b,'lugar':x['rotulo']})
# A foto sem sobreposições é exibida integralmente após a capa.
telas[1]={'src':'cenas/real-caminhao.jpg','ini':slots[0][0],'fim':slots[0][1],'fade':0,'zoom':.025}
# Se o primeiro slot tinha uma cena exclusiva, desloca para slot livre, sem perder nenhuma cena forte.
if 0 in selected:
    spare=next(j for j in range(1,len(slots)) if j not in selected)
    x=clipes[selected[0]];a,b=slots[spare];q=sorted((AQUI/x['usado']).glob('*.jpg'))
    telas[spare+1]={'seq':[str(z.relative_to(AQUI)) for z in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':.02}
    visual[spare]={'ini':a,'fim':b,'lugar':x['rotulo']}
visual[0]['lugar']='Tupanciretã / RS'
assert all(t['fim']-t['ini']>=2.5 for t in telas)
SUL={'lon':-51.5,'lat':-27.8,'zoom':5.25,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}];SAT=None
estados=[{'id':uf,'ini':MAP0,'fim':MAP1,'ufs':[uf],'cor':LAR,'alfa':.28} for uf in ('RS','SC','PR')]
pinos=[{'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0,'fim':MAP1,'h':25} for nome,sub,lon,lat in [
('Paraná','Temporal previsto',-51.6,-24.7),('Santa Catarina','Temporal previsto',-50.8,-27.1),('Rio Grande do Sul','Áreas em aviso',-53.0,-30.2)]]
def painel(fid,k,linhas,contador=None):
    a,b=ini(fid),fim(fid);z={'fid':fid,'ini':a,'fim':b,'k':k,'borda':'rgba(255,42,31,.8)'}
    if contador:
        valor,palavra,unid=contador;z['ini']=max(a,em(fid,palavra)-1)
        z.update(contador={'de':0,'ate':valor,'ini':em(fid,palavra)-1,'dur':1,'cor':'#FACC15','unid':unid},l=' · '.join(linhas))
    else:z['itens']=[{'t':a+i*.25,'txt':txt} for i,txt in enumerate(linhas)]
    return z
paineis=[
painel('f1','TUPANCIRETÃ / RS · HOJE',['Destruição entre 3 e 4 horas','Madrugada de sexta']),
painel('f2','TUPANCIRETÃ / RS · ESTRAGOS',['Telhados e árvores ao chão','Veículos atingidos']),
painel('f3','CENTRO DO RS · O SISTEMA',['Supercélula: tempestade com rotação','Possível tornado · sob avaliação']),
painel('f4','FOZ DO IGUAÇU / PR · HOJE',['Nuvem em funil nesta tarde','Sem confirmação de toque no solo']),
painel('f5','LARANJEIRAS DO SUL / PR · HOJE',['Enxurrada e vento intenso','Árvores atingidas']),
painel('f6','SC E PR · ESTA NOITE · PREVISÃO',['Áreas em aviso laranja · INMET'],(100,'100','km/h · ATÉ')),
painel('f7','RS · AMANHÃ · PREVISÃO INMET',['Áreas em aviso amarelo'],(452,'452','MUNICÍPIOS')),
painel('f8','SC E PR · AMANHÃ · PREVISÃO',['Nas áreas avisadas · INMET'],(50,'50','mm / DIA · ATÉ')),
painel('f9','SUL · PRÓXIMOS DIAS',['Pico do risco: hoje','Domingo e segunda: instabilidade']),
painel('f10','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
paineis[0]['ini']=CAPA
for fid,txt in [('f6','Rajadas previstas nas áreas avisadas'),('f7','Possibilidade de granizo'),('f8','Chuva prevista nas áreas avisadas')]:
 z=next(p for p in paineis if p['fid']==fid)
 paineis.append({'fid':fid+'-intro','ini':ini(fid),'fim':z['ini'],'k':z['k'],'itens':[{'t':ini(fid),'txt':txt}]})
paineis.sort(key=lambda p:p['ini'])
for a,b in zip(paineis,paineis[1:]):a['fim']=min(a['fim'],b['ini'])
fontes=[{'ini':0,'fim':CAPA,'html':f'<b>Tupanciretã / RS · HOJE</b> · {MET}'}]
for v in visual:fontes.append({'ini':v['ini'],'fim':v['fim'],'html':f"<b>{v['lugar']}</b> · registro de hoje · {MET}"})
for fid,ident in [('f6',56457),('f7',56462),('f8',56462)]:fontes.insert(0,{'ini':ini(fid),'fim':fim(fid),'html':f'<b>INMET · {DATA} · aviso {ident}</b> · PREVISÃO · fundo: registros de hoje'})
fontes.insert(0,{'ini':MAP0,'fim':MAP1,'html':f'<b>INMET · {DATA}</b> · aviso 56457 · áreas em aviso nesta noite'})
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


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"20/11/2026 · INMET","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; {len(clipes)} clipes fortes; mapa {MAP0:.2f}–{MAP1:.2f} s')
