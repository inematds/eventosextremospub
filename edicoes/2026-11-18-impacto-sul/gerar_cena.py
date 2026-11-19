#!/usr/bin/env python3
"""Impacto Sul 18/11/2026: material real inventariado, avisos novos e tempos adaptáveis ao canto."""
import os
import difflib, json, math, re, subprocess, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "18/11/2026"
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



# Avisos da coleta atual: quantidades municipais conferidas por geocódigo único.
from collections import Counter
from scipy.optimize import linear_sum_assignment
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
aviso={a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
def cidades(i):
    return Counter(c[:2] for c in set(aviso[i]['geocodes'].split(',')) if c[:2] in ('41','42','43'))
assert cidades(56443)=={'43':460,'42':295,'41':399}
assert cidades(56446)=={'43':83,'42':295,'41':399}
assert cidades(56447)=={'43':266,'42':295,'41':399}
assert aviso[56443]['fim']=='2026-11-18 23:59'
assert aviso[56446]['inicio']=='2026-11-19 00:00'
assert aviso[56447]['inicio']=='2026-11-20 00:00'
assert '40-60 km/h' in aviso[56443]['riscos'][0]
END=FIM_VIDEO if AVATAR else DUR
DUR=END
CAPA=2.8
MAP0=ini('f4'); MAP1=MAP0+3.0
slots=[]
for a,b in [(CAPA,MAP0),(MAP1,END)]:
    num=math.ceil((b-a)/3.0)
    assert (b-a)/num>=2.5,('intervalo insuficiente',a,b,num)
    for k in range(num):slots.append((a+k*(b-a)/num,a+(k+1)*(b-a)/num))
clipes=json.loads((AQUI/'pesquisa/clipes.json').read_text())
preferidos={1:ini('f3')+1,2:ini('f3')+5,3:ini('f4')+4,4:ini('f8')+5,5:ini('f4')+7,
6:ini('f5')+2,7:ini('f5')+5,8:ini('f2')+1,9:ini('f2')+4,10:ini('f1')+5,11:ini('f8')+2}
assert len(slots)>=11
# Todos os fortes têm uma janela exclusiva, mesmo com os tempos menores do avatar.
rows,cols=linear_sum_assignment([[abs((a+b)/2-preferidos[k])+(1000 if k in (1,2) and not ini('f3')<=a<fim('f3') else 0) for a,b in slots] for k in range(1,12)])
selected={int(c):int(r)+1 for r,c in zip(rows,cols)}
def nearest(mid):
    if ini('f3')<=mid<fim('f3'):return [1,2][int(mid/3)%2]
    return [10,8,9,7,11,6][int(mid/3)%6]
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':CAPA,'fade':0,'zoom':0}]
visual=[]
for j,(a,b) in enumerate(slots):
    k=selected.get(j,nearest((a+b)/2));x=clipes[k-1]
    if x['usado'].endswith('.jpg'):
        telas.append({'src':x['usado'],'ini':a,'fim':b,'fade':0,'zoom':.04})
    else:
        q=sorted((AQUI/x['usado']).glob('*.jpg'))
        assert b-a<=len(q)/30+.03,(k,b-a,len(q)/30)
        telas.append({'seq':[str(z.relative_to(AQUI)) for z in q],'fps':30,'ini':a,'fim':b,'fade':0,'zoom':.02})
    visual.append({'ini':a,'fim':b,'lugar':x['rotulo']})
assert all(t['fim']-t['ini']>=2.5 for t in telas)
SUL={'lon':-51.5,'lat':-27.8,'zoom':5.25,'pitch':0,'bearing':0}
camera=[{'t':0,**SUL},{'t':DUR,**SUL}]
SAT=None
estados=[{'id':uf,'ini':MAP0,'fim':MAP1,'ufs':[uf],'cor':AMA,'alfa':.28} for uf in ('RS','SC','PR')]
pinos=[{'nome':nome,'sub':sub,'lon':lon,'lat':lat,'ini':MAP0,'fim':MAP1,'h':35} for nome,sub,lon,lat in [
('Paraná','Sudoeste: avanço nesta noite',-51.2,-24.6),
('Santa Catarina','Oeste: chuva persistente',-49.9,-27.1),
('Rio Grande do Sul','Noroeste: retorno quinta',-53.5,-30.1)]]
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
painel('f1','SC · ESTA NOITE · INMET',['Tempestade · aviso amarelo'],(295,'295','CIDADES')),
painel('f2','SÃO MIGUEL DO OESTE / SC · HOJE',['Chuva muito forte','Rajadas no final da tarde']),
painel('f3','PARANÁ · REGISTROS DE TERÇA',['Árvore sobre veículo','Telhados atingidos']),
painel('f4','INSTABILIDADE VINDO DA ARGENTINA',['Chuva se repete na semana']),
painel('f5','OESTE DE SC · ESTA NOITE · PREVISÃO',['Chuva deve persistir'],(60,'60','km/h · ATÉ')),
painel('f6','PARANÁ · QUINTA · INMET',['Sudoeste: chuva avança nesta noite'],(399,'399','CIDADES')),
painel('f7','RS · QUINTA · INMET',['Extremo noroeste: chuva volta'],(83,'83','CIDADES')),
painel('f8','SEXTA · PICO PREVISTO DO RISCO',['Chuva no dia · nas áreas avisadas'],(50,'50','mm · ATÉ')),
painel('f9','COMENTA AQUI',['DE ONDE VOCÊ É?','COMO ESTÁ AÍ?'])]
# Painéis geográficos já no início da fala; contador só na palavra correspondente.
for fid,k,txt in [('f5','OESTE DE SC · PREVISÃO','Chuva persiste nas próximas horas'),('f6','SUDOESTE DO PARANÁ · PREVISÃO','Instabilidade avança nesta noite'),('f7','EXTREMO NOROESTE DO RS · PREVISÃO','Diminui na madrugada; volta quinta'),('f8','SEXTA-FEIRA · PREVISÃO','Maior risco de temporais no Sul')]:
    z=next(p for p in paineis if p['fid']==fid)
    paineis.append({'fid':fid+'-intro','ini':ini(fid),'fim':z['ini'],'k':k,'itens':[{'t':ini(fid),'txt':txt}]})
paineis[0]['ini']=max(CAPA,paineis[0]['ini'])
paineis.sort(key=lambda p:p['ini'])
for a,b in zip(paineis,paineis[1:]):a['fim']=min(a['fim'],b['ini'])
fontes=[{'ini':0,'fim':CAPA,'html':'<b>INMET · 18/11/2026</b> · aviso 56443 · previsão; imagem: São Miguel do Oeste hoje'}]
for v in visual:
    fontes.append({'ini':v['ini'],'fim':v['fim'],'html':f"<b>{v['lugar']}</b> · {MET}"})
# Identifica a fonte própria dos números oficiais sem atribuí-los às imagens.
for fid,aid in [('f1',56443),('f5',56443),('f6',56446),('f7',56446),('f8',56447)]:
    fontes.append({'ini':ini(fid),'fim':fim(fid),'html':f'<b>INMET · {DATA}</b> · aviso {aid} · PREVISÃO'})
fontes.insert(0,{'ini':MAP0,'fim':MAP1,'html':f'<b>INMET · {DATA}</b> · municípios em aviso nos três estados'})
# O motor mostra a primeira fonte ativa: números oficiais precedem os rótulos dos clipes.
fontes.sort(key=lambda f:0 if '<b>INMET' in f['html'] else 1)
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


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"duracao":DUR,"marca":"INEMA · IMPACTO SUL","selo":"18/11 · INMET","camera":camera,"sat":SAT,"imagens":[],"colunas":[],"telas":telas,"estados":estados,"pinos":pinos,"hero":[],"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js: {DUR:.2f} s; {len(telas)} telas; 11 clipes fortes; mapa {MAP0:.2f}–{MAP1:.2f} s')
