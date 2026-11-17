#!/usr/bin/env python3
"""Impacto Sul 16/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/11/2026"
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



# Avisos desta edição: contagens únicas por UF, não somar áreas sobrepostas.
from collections import Counter
from scipy.optimize import linear_sum_assignment
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56425)=={'43':70,'42':24}
assert cidades(56428)=={'43':270,'42':96,'41':158}
assert cidades(56433)=={'43':369,'42':171,'41':118}
assert sum(cidades(56433).values())==658
assert aviso[56425]['fim']=='2026-11-17 23:59'
assert aviso[56433]['inicio']=='2026-11-18 00:00'
assert '60-100 km/h' in aviso[56433]['riscos'][0]
END=FIM_VIDEO if AVATAR else DUR
DUR=END
CAPA=2.8
# Um único mapa estático localiza juntos os estados, em área de leitura livre.
MAP0=ini('f5'); MAP1=MAP0+3.0
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.ceil((b-a)/3.10)
    assert (b-a)/num>=2.5, ('intervalo insuficiente',a,b,num)
    for k in range(num): slots.append((a+k*(b-a)/num,a+(k+1)*(b-a)/num))
preferidos={1:ini('f1')+3,2:em('f2','enxurradas'),3:em('f2','telhados'),
4:em('f3','granizo'),5:em('f3','enxurrada'),6:ini('f2')+2,
7:ini('f4'),8:em('f4','chuva'),9:em('f3','lavouras')+2,
10:ini('f9'),11:em('f9','bloqueios')+3,12:em('f3','granizo')+3}
assert len(slots)>=12
rows,cols=linear_sum_assignment([[abs((a+b)/2-preferidos[k]) for a,b in slots] for k in range(1,13)])
selected={int(c):int(r)+1 for r,c in zip(rows,cols)}
def nearest(mid):
    if mid<ini('f3'):return 3
    if mid<ini('f4'):return 4
    if mid<ini('f5'):return [7,8,4][int(mid/3)%3]
    if mid<ini('f9'):return [1,6,4,8][int(mid/3)%4]
    return [10,11,2,9][int(mid/3)%4]
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':.02}]
for j,(a,b) in enumerate(slots):
    k=selected.get(j,nearest((a+b)/2));name=f'clip-{k:02d}'
    q=sorted((AQUI/'cenas'/name).glob('*.jpg'))
    assert b-a<=len(q)/30+.03,(name,b-a,len(q)/30)
    telas.append({'seq':[str(x.relative_to(AQUI)) for x in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':.02})
assert all(t['fim']-t['ini']>=2.5 for t in telas)
SUL={'lon':-51.5,'lat':-27.8,'zoom':5.25,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}]
SAT=None  # há registros reais suficientes; nenhum satélite de preenchimento
# Cores leves localizam estados: os textos informam o recorte municipal do aviso.
estados=[{'id':uf,'ini':MAP0-.6,'fim':MAP1+.6,'ufs':[uf],'cor':AMA,'alfa':.28} for uf in ('RS','SC','PR')]
pinos=[{'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0-.6,'fim':MAP1+.6,'h':55} for nome,sub,lon,lat in [
('Paraná','158 cidades · terça',-51.2,-24.6),
('Santa Catarina','24 cidades · vento',-49.9,-27.1),
('Rio Grande do Sul','70 cidades · vento',-53.5,-30.1)]]
def painel(fid,k,linhas,contador=None):
    a,b=ini(fid),fim(fid)
    z={'fid':fid,'ini':a,'fim':b,'k':k,'borda':'rgba(255,42,31,.8)'}
    if contador:
        valor,palavra,unid=contador
        z['ini']=min(a,em(fid,palavra)-1)
        z.update(contador={'de':0,'ate':valor,'ini':em(fid,palavra)-1,'dur':1,'cor':'#FACC15','unid':unid},l=' · '.join(linhas))
    else:z['itens']=[{'t':a+i*.25,'txt':txt} for i,txt in enumerate(linhas)]
    return z
paineis=[
painel('f1','INMET · ESTA NOITE · PREVISÃO',['aviso de vento até terça, 23h59'],(70,'70','CIDADES / RS')),
painel('f2','HOJE · AVALIAÇÃO DOS ESTRAGOS',['SC e PR','Tempestades de domingo']),
painel('f3','REGISTROS · SANTA CATARINA / PR',['Granizo e lavoura danificada','Enxurrada e vias atingidas']),
painel('f4','SEMANA · PREVISÃO',['Novas tempestades','Chuva, vento e granizo']),
painel('f5','INMET · RS · HOJE E TERÇA',['Vento previsto','70 cidades no aviso'],(60,'60','km/h · ATÉ')),
painel('f6','INMET · SC · PREVISÃO',['Vento até terça','Tempestade em outras áreas amanhã'],(24,'24','CIDADES')),
painel('f7','INMET · PR · TERÇA',['aviso de tempestade'],(158,'158','CIDADES')),
painel('f8','INMET · QUARTA · PREVISÃO',['369 RS + 171 SC + 118 PR','aviso laranja de tempestade'],(658,'658','CIDADES')),
painel('f9','ATENÇÃO NA ESTRADA',['Confira bloqueios','Evite água e fios caídos']),
painel('f10','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
# Cada número de previsão só chega quando a palavra correspondente é dita.
for fid,valor,unid,rotulo in [('f7',50,'mm/dia · ATÉ','INMET · PR · CHUVA PREVISTA'),('f8',100,'km/h · ATÉ','INMET · QUARTA · VENTO PREVISTO')]:
    troca=em(fid,str(valor))-1
    atual=next(p for p in paineis if p['fid']==fid)
    atual['fim']=troca
    z=painel(fid,rotulo,['previsão; não é medição observada'],(valor,str(valor),unid))
    z['ini']=troca
    paineis.append(z)
paineis[0]['ini']=CAPA
paineis.sort(key=lambda p:p['ini'])
for a,b in zip(paineis,paineis[1:]):a['fim']=min(a['fim'],b['ini'])
fontes=[{'ini':0,'fim':ini('f2'),'html':'<b>INMET · 16/11/2026</b> · aviso 56425 · previsão'},
{'ini':ini('f2'),'fim':ini('f4'),'html':f'<b>{MET}</b> · estragos de domingo avaliados hoje'},
{'ini':ini('f4'),'fim':ini('f5'),'html':f'<b>{MET}</b> · previsão da semana'},
{'ini':ini('f5'),'fim':ini('f8'),'html':'<b>INMET · 16/11/2026</b> · avisos 56425 / 56428 · previsão'},
{'ini':ini('f8'),'fim':ini('f9'),'html':'<b>INMET · 16/11/2026</b> · aviso 56433 · previsão'},
{'ini':ini('f9'),'fim':DUR,'html':f'<b>{MET}</b> · imagens dos estragos anteriores'}]
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


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"16/11 · INMET","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; todas as 11 cenas fortes em 12 clipes; mapa parado: {MAP0:.2f}–{MAP1:.2f} s')

