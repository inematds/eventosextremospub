#!/usr/bin/env python3
"""Impacto Sul 17/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "17/11/2026"
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



# INMET: avisos desta coleta; geocódigos únicos por UF.
from collections import Counter
from scipy.optimize import linear_sum_assignment
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56434)=={'43':497,'42':283,'41':363}
assert cidades(56442)=={'43':468,'42':277,'41':294}
assert sum(cidades(56442).values())==1039
assert aviso[56442]['inicio']=='2026-11-18 00:00'
assert aviso[56442]['fim']=='2026-11-18 23:59'
assert '60-100 km/h' in aviso[56442]['riscos'][0]
END=FIM_VIDEO if AVATAR else DUR
DUR=END
CAPA=2.8
MAP0=ini('f5'); MAP1=MAP0+3.0
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.ceil((b-a)/3.05)
    assert (b-a)/num>=2.5, ('intervalo insuficiente',a,b,num)
    for k in range(num): slots.append((a+k*(b-a)/num,a+(k+1)*(b-a)/num))
# Toda cena forte entra; o algoritmo só escolhe a janela temporal mais próxima.
preferidos={1:ini('f4')+3,2:ini('f4')+6,3:em('f4','granizo'),
4:ini('f3'),5:ini('f3')+3,6:ini('f3')+6,7:ini('f3')+9,
8:em('f3','chuva'),9:ini('f6')+3,
10:ini('f2'),11:ini('f9'),12:ini('f5')+4,
13:em('f2','Mercedes'),14:em('f2','telhados'),
15:ini('f1')+3,16:ini('f1')+6,17:em('f2','árvores'),18:ini('f8'),
19:ini('f8')+3,20:ini('f7')+3,21:ini('f9')+3,22:ini('f5')+7}
assert len(slots)>=22,('sem espaço para cenas fortes',len(slots))
# Reserve primeiro os registros argentinos na explicação do sistema.
# Isso impede que a compressão do avatar os desloque para a previsão brasileira.
arg_slots=[j for j,(a,b) in enumerate(slots) if (a+b)/2>=ini('f4') and (a+b)/2<=fim('f4')]
if len(arg_slots)<3:
    centro=(ini('f4')+fim('f4'))/2
    arg_slots=sorted(range(len(slots)),key=lambda j:abs((slots[j][0]+slots[j][1])/2-centro))[:3]
# Granizo permanece na tela durante a palavra, com prioridade sobre outras imagens.
granizo=em('f4','granizo')
jg=min(range(len(slots)),key=lambda j:0 if slots[j][0]<=granizo<slots[j][1] else abs((slots[j][0]+slots[j][1])/2-granizo))
selected={jg:3}
posteriores=[j for j in range(jg+1,len(slots)) if (slots[j][0]+slots[j][1])/2<=fim('f4')]
for k in (1,2):
    candidatos=[j for j in posteriores if j not in selected]
    if not candidatos:
        candidatos=sorted((j for j in range(len(slots)) if j not in selected),key=lambda j:abs((slots[j][0]+slots[j][1])/2-(ini('f4')+fim('f4'))/2))
    selected[candidatos[0]]=k
livres=[j for j in range(len(slots)) if j not in selected]
rows,cols=linear_sum_assignment([[abs((slots[j][0]+slots[j][1])/2-preferidos[k]) for j in livres] for k in range(4,23)])
selected.update({livres[int(c)]:int(r)+4 for r,c in zip(rows,cols)})
def nearest(mid):
    if mid<ini('f2'):return [15,18,16][int(mid/3)%3]
    if mid<ini('f3'):return [10,13,14,17][int(mid/3)%4]
    if mid<ini('f4'):return [4,7,8,9][int(mid/3)%4]
    if mid<ini('f5'):return 12  # Argentina só nos três trechos explicitamente identificados
    if mid<ini('f6'):return [12,20,22][int(mid/3)%3]
    if mid<ini('f7'):return [4,7,8,9][int(mid/3)%4]
    return [16,17,18,19,21,13,14][int(mid/3)%7]
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':.02}]
visual=[]
for j,(a,b) in enumerate(slots):
    k=selected.get(j,nearest((a+b)/2));name=f'clip-{k:02d}'
    q=sorted((AQUI/'cenas'/name).glob('*.jpg'))
    assert b-a<=len(q)/30+.03,(name,b-a,len(q)/30)
    telas.append({'seq':[str(x.relative_to(AQUI)) for x in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':.02})
    lugar='ARGENTINA · NOITE ANTERIOR' if k<=3 else 'MISSÕES / RS · HOJE' if k<=9 else 'PARANÁ · HOJE' if k in (12,20,22) else 'MERCEDES / PR · HOJE' if k<=14 else 'MARECHAL CÂNDIDO RONDON / PR · HOJE'
    visual.append({'ini':a,'fim':b,'lugar':lugar})
assert all(t['fim']-t['ini']>=2.5 for t in telas)
SUL={'lon':-51.5,'lat':-27.8,'zoom':5.25,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}]
SAT=None
# Estados com municípios no aviso 56442; o painel informa o recorte municipal.
estados=[{'id':uf,'ini':MAP0,'fim':MAP1,'ufs':[uf],'cor':AMA,'alfa':.23} for uf in ('RS','SC','PR')]
pinos=[{'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0,'fim':MAP1,'h':35} for nome,sub,lon,lat in [
('Paraná','294 cidades · quarta',-51.2,-24.6),
('Santa Catarina','277 cidades · quarta',-49.9,-27.1),
('Rio Grande do Sul','468 cidades · quarta',-53.5,-30.1)]]
def painel(fid,k,linhas,contador=None):
    a,b=ini(fid),fim(fid)
    z={'fid':fid,'ini':a,'fim':b,'k':k,'borda':'rgba(255,42,31,.8)'}
    if contador:
        valor,palavra,unid=contador
        z['ini']=em(fid,palavra)-1
        z.update(contador={'de':0,'ate':valor,'ini':em(fid,palavra)-1,'dur':1,'cor':'#FACC15','unid':unid},l=' · '.join(linhas))
    else:z['itens']=[{'t':a+i*.25,'txt':txt} for i,txt in enumerate(linhas)]
    return z
paineis=[
painel('f1','INMET · AMANHÃ · PREVISÃO',['Paraná · aviso laranja'],(294,'294','CIDADES / PR')),
painel('f2','HOJE · OESTE DO PARANÁ',['Mercedes e Marechal Cândido Rondon','Árvores, postes e telhados atingidos']),
painel('f3','HOJE · MISSÕES / RS',['Nuvens prateleira','Chuva forte e rajadas']),
painel('f4','SISTEMA DE TEMPESTADES',['Ar quente alimenta o temporal','Reforço vindo do Paraguai']),
painel('f5','PARANÁ · PREVISÃO',['Noite: chuva cruza o estado','Quarta: granizo no aviso'],(294,'294','CIDADES')),
painel('f6','RS · QUARTA · PREVISÃO',['Aviso laranja'],(468,'468','CIDADES')),
painel('f7','SC · QUARTA · PREVISÃO',['Novas chuvas podem voltar'],(277,'277','CIDADES')),
painel('f8','SUL · QUARTA · PREVISÃO',['468 RS + 277 SC + 294 PR'],(1039,'1.039','CIDADES')),
painel('f9','PROTEJA-SE',['Evite fios e árvores','Não atravesse água']),
painel('f10','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
for fid,valor,unid,rotulo in [('f6',100,'mm/dia · ATÉ','INMET · RS · CHUVA PREVISTA'),('f8',100,'km/h · ATÉ','INMET · SUL · VENTO PREVISTO')]:
    troca=em(fid,str(valor))-1
    atual=next(p for p in paineis if p['fid']==fid);atual['fim']=troca
    z=painel(fid,rotulo,['Nas áreas do aviso laranja'],(valor,str(valor),unid));z['ini']=troca;paineis.append(z)
troca_pr=em('f5','294')-1
paineis.append({'fid':'f5-intro','ini':ini('f5'),'fim':troca_pr,'k':'PARANÁ · ESTA NOITE · PREVISÃO','itens':[{'t':ini('f5'),'txt':'Instabilidade cruza o estado'}]})
paineis[0]['ini']=CAPA
paineis.sort(key=lambda p:p['ini'])
for a,b in zip(paineis,paineis[1:]):a['fim']=min(a['fim'],b['ini'])
fontes=[{'ini':0,'fim':CAPA,'html':'<b>INMET · 17/11/2026</b> · previsão de quarta; foto: estragos de hoje em Rondon / PR'}]
for v in visual:
    prev= v['ini']<ini('f2') or v['ini']>=ini('f5') and v['ini']<ini('f9')
    fontes.append({'ini':v['ini'],'fim':v['fim'],'html':f"<b>{v['lugar']}</b> · {MET}"+ (' · números: INMET / previsão' if prev else '')})
fontes.append({'ini':MAP0,'fim':MAP1,'html':'<b>INMET · 17/11/2026</b> · aviso 56442 · previsão quarta 18/11'})
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


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"17/11 · INMET","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; 22 clipes fortes; mapa {MAP0:.2f}–{MAP1:.2f} s')
