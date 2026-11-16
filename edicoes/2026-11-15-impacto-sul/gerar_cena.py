#!/usr/bin/env python3
"""Impacto Sul 15/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/11/2026"
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
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
FIM_VIDEO = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(AQUI / "avatar/avatar.mp4")], capture_output=True, text=True).stdout or DUR) if AVATAR else DUR
FIM_VIDEO = min(FIM_VIDEO, DUR)   # o compor_avatar corta no fim do avatar: a última cena vale até aqui
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]
MIN_CENA, MIN_MAPA = 2.5, 3.0



# A duração usa o áudio real disponível; com --canto lê os tempos do avatar.
# Não elimina cenas fortes para encaixar: exige capacidade e distribui todas de novo.
from collections import Counter
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56412)=={'41':300,'42':153}, cidades(56412)
assert cidades(56419)=={'43':129,'41':102,'42':43}, cidades(56419)
assert cidades(56420)=={'42':10,'43':22}, cidades(56420)
assert aviso[56412]['fim']=='2026-11-15 23:59'
assert '40-60 km/h' in aviso[56412]['riscos'][0]
assert aviso[56420]['inicio'].startswith('2026-11-16')
# Há filmagem suficiente: o único mapa, parado, localiza RS/SC/PR e os avisos.
# Não se usa infravermelho só para preencher o tempo.
MAP0=ini('f8'); MAP1=MAP0+3.0
assert MAP1 < ini('f9')
END=FIM_VIDEO if AVATAR else DUR
DUR=END
from scipy.optimize import linear_sum_assignment
# Capa 2,8 s; demais telas entre 2,5 e 3,1 s, inclusive com a voz mais rápida do avatar.
CAPA=2.8
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.ceil((b-a)/3.06)
    assert (b-a)/num>=2.5, ('intervalo insuficiente',a,b,num)
    for k in range(num):slots.append((a+k*(b-a)/num,a+(k+1)*(b-a)/num))
# Alvos semânticos. Cenas adicionais de impacto entram na pergunta e no CTA.
preferidos={1:ini('f1')+3,2:ini('f2')+1,3:ini('f2')+4,4:ini('f10')+2,
5:ini('f11')+3,6:ini('f1')+7,7:em('f3','granizo'),8:em('f3','chão')+2,
9:ini('f10')+5,10:ini('f7')+1,11:em('f4','fios'),12:em('f3','Lages'),
13:ini('f4')+1,14:ini('f4')+4,15:ini('f5'),16:ini('f5')+3,17:ini('f5')+6,
18:ini('f6')+1,19:ini('f9')+2}
assert len(slots)>=19, f'{len(slots)} janelas: não cabem todas as 19 cenas fortes com mínimo de 2,5 s'
cost=[[abs((a+b)/2-preferidos[k]) for a,b in slots] for k in range(1,20)]
rows,cols=linear_sum_assignment(cost)
selected={int(col):int(row)+1 for row,col in zip(rows,cols)}
def nearest(mid):
    if mid<ini('f3'):return 2
    if mid<ini('f4'):return 8
    if mid<ini('f5'):return 13
    if mid<ini('f6'):return 16
    if mid<ini('f7'):return 18
    return 10

telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':.02}]
historicos=[]
for j,(a,b) in enumerate(slots):
    k=selected.get(j,nearest((a+b)/2)); name=f'clip-{k:02d}'
    q=sorted((AQUI/'cenas'/name).glob('*.jpg'))
    assert b-a<=len(q)/30+.04,(name,b-a,len(q)/30)
    telas.append({'seq':[str(x.relative_to(AQUI)) for x in q],'fps':30,'ini':a,'fim':b,'fade':.15,'zoom':.02})
    if k in (15,16,17):historicos.append((a,b))
assert all(t['fim']-t['ini']>=2.5 for t in telas)
SUL={'lon':-51.7,'lat':-27.5,'zoom':5.45,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}]
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75]},'base':'sat/web/geocolor.jpg','bbox':[-76,-35,-33,7],'tint':[170,170,175]}
estados=[{'id':uf,'ini':MAP0,'fim':MAP1,'ufs':[uf],'cor':cor,'alfa':.3} for uf,cor in [('PR',VERM),('SC',LAR),('RS',AMA)]]
pinos=[{'nome':nm,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0,'fim':MAP1,'h':55} for nm,sub,lon,lat in [('Paraná','300 cidades · esta noite',-51.6,-24.7),('Santa Catarina','10 cidades · vento amanhã',-50.2,-27.3),('Rio Grande do Sul','22 cidades · vento amanhã',-53.1,-30.0)]]
def painel(fid,k,linhas,contador=None):
    a,b=ini(fid),fim(fid)
    z={'ini':a,'fim':b,'k':k,'borda':'rgba(255,42,31,.8)'}
    if contador:
        valor,palavra,unid=contador
        # Um segundo de animação; chega ao valor na palavra do número.
        z.update(contador={'de':0,'ate':valor,'ini':em(fid,palavra)-1,'dur':1,'cor':'#FACC15','unid':unid},l=' · '.join(linhas))
    else:z['itens']=[{'t':a+i*.25,'txt':txt} for i,txt in enumerate(linhas)]
    return z
paineis=[
painel('f1','INMET · ESTA NOITE · PREVISÃO',['aviso de tempestade até 23h59'],(300,'300','CIDADES / PR')),
painel('f2','MALLET · PR · HOJE',['Vendaval e telhados danificados','Árvores e postes caídos']),
painel('f3','SANTA CATARINA · HOJE',['Santo Amaro da Imperatriz','Lages · chuva e granizo']),
painel('f4','JARAGUÁ DO SUL · SC · HOJE',['Estrutura de evento danificada','Feridos · atenção aos fios']),
painel('f5','IMAGENS DE SÁBADO · 14/11',['Norte do RS e Paraná','Árvores caídas ontem']),
painel('f6','PRÓXIMOS DIAS · PREVISÃO',['Calor + umidade','Pancadas à tarde e à noite']),
painel('f7','INMET · SC · ESTA NOITE',['153 cidades em aviso'],(60,'60','km/h · ATÉ')),
painel('f8','INMET · SEGUNDA · VENTO COSTEIRO',['RS: 22 cidades','SC: 10 cidades']),
painel('f9','RISCO DE TEMPESTADE · PREVISÃO',['Terça e quarta','Sexta: novo aumento do risco']),
painel('f10','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
# No quadro 0 a manchete completa está gravada dentro da imagem; o painel só entra depois.
paineis[0]['ini']=CAPA
# Não confundir aviso (cobertura prevista) com dano observado nem imagens de sábado com domingo.
fontes=[{'ini':0,'fim':ini('f2'),'html':'<b>INMET · 15/11/2026</b> · aviso 56412 · previsão; imagem: estragos de hoje'},
{'ini':ini('f2'),'fim':ini('f5'),'html':f'<b>{MET}</b> · registros de hoje'},
{'ini':ini('f5'),'fim':ini('f6'),'html':f'<b>{MET}</b> · imagens de sábado, 14/11'},
{'ini':ini('f6'),'fim':ini('f7'),'html':f'<b>{MET}</b> · previsão'},
{'ini':ini('f7'),'fim':ini('f9'),'html':'<b>INMET · 15/11/2026</b> · avisos 56412 e 56420 · previsão'},
{'ini':ini('f9'),'fim':ini('f10'),'html':f'<b>{MET}</b> · previsão'}]
# Etiqueta do próprio projeto permanece em cada reaparição de cena histórica.
for a,b in historicos:
    novo=[]
    for f in fontes:
        if f['fim']<=a or f['ini']>=b:novo.append(f);continue
        if f['ini']<a:novo.append({**f,'fim':a})
        if f['fim']>b:novo.append({**f,'ini':b})
    fontes=novo+[{'ini':a,'fim':b,'html':f'<b>{MET}</b> · IMAGENS DE SÁBADO · 14/11'}]
fontes.sort(key=lambda x:x['ini'])
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


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"15/11 · INMET · NOAA","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; todas as 19 cenas fortes; mapa parado: {MAP0:.2f}–{MAP1:.2f} s')

