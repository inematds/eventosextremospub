#!/usr/bin/env python3
"""Clima do DIA 16/11/2026. Boletim como fonte da previsão; --canto usa tempos do avatar."""
import os
import difflib, json, re, sys, unicodedata
from collections import Counter
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
        if n(palavra) == n(p["w"]) or (len(n(palavra)) > 3 and n(palavra) in n(p["w"])):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# Avisos de risco, independentes da previsão do boletim.
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
UFCOD = {"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
def conjunto(ids, data, quantidades):
    total=set()
    for id, quantidade in zip(ids,quantidades):
        a=aviso[id]
        assert a['descricao']=='Tempestade' and a['inicio'].startswith(data)
        cod=set(a['geocodes'].split(',')); assert len(cod)==quantidade
        total |= cod
    return total
HOJE=conjunto([56422,56423],'2026-11-16',[2645,464])
AMANHA=conjunto([56428,56429,56430],'2026-11-17',[2323,282,569])
ufs=lambda cs: sorted(set(UFCOD[c[:2]] for c in cs))
# Uma viagem de câmera e um card por assunto; mapa inteiro no quadro nacional.
regioes=[(-46,-22,4.5),(-50,-24,4.1),(-51,-15,3.6),(-51,-28,4.5),(-45,-12,4.1),(-59,-4,3.9),(-49,-23,4.3),(-48,-25,4.1),(-42,-7,4.5),(-52,-29,4.4),(-53,-14,3.6),(-53,-14,3.6)]
camera=[]
for i,(lon,lat,zoom) in enumerate(regioes,1):
    fid=f'f{i}'; pitch=24 if i in (4,8,10) else 0
    for t,z,b in [(ini(fid)+(.5 if i>1 else 0),zoom,-5),(fim(fid)-.1,zoom+.08,5)]:
        camera.append(dict(t=t,lon=lon,lat=lat,zoom=z,pitch=pitch,bearing=b))
camera.append({**camera[-1],'t':DUR})
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
from PIL import Image,ImageStat
TS=json.loads((AQUI/'sat/web/ir_tempos.json').read_text())
BONS=[i for i in range(len(TS)) if 90<ImageStat.Stat(Image.open(AQUI/f'sat/web/ir{i:02d}.jpg').convert('L')).mean[0]<130]
assert len(BONS)>=24, len(BONS)
def brt(z):
    d=datetime.strptime(z,'%Y-%m-%dT%H:%M:%SZ')-timedelta(hours=3)
    return d.strftime('%d/%m %Hh%M')
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},'base':'sat/web/geocolor.png','bbox':[-76,-35,-33,7],'tint':[170,170,175],
'ir':{'frames':[f'sat/web/ir{i:02d}.png' for i in BONS],'tempos':[brt(TS[i]) for i in BONS],'ini':ini('f2'),'fim':ini('f3'),'dur':fim('f2')-ini('f2'),'alfa':.9,'rotulo':'GOES-19 · observado · últimas 24 h'}}
GRA=em('f4','granizo')
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':2,'fade':0,'zoom':.03}, {'src':'capa-dia/granizo.png','ini':GRA,'fim':fim('f4'),'fade':.15,'zoom':.04,'selo':'ilustração'}]
imagens=[]; colunas=[]; hero=[]
estados=[]
def estado(id, fid, us, cor):
    estados.append(dict(id=id,ini=max(2,ini(fid)),fim=fim(fid),ufs=us,cor=cor,alfa=.3))
estado('risco-hoje','f1',ufs(HOJE),LAR)
estado('sudeste','f3',['SP','RJ','ES','MG'],AZUL)
estado('risco-amanha','f4',[u for u in ufs(AMANHA) if u in ['RS','SC','PR']],LAR)
estado('chuva-terca','f5',['GO','TO','MG','MA','PI','BA'],AZUL)
estado('norte-irregular','f6',['RR','AP','PA'],AMA)
estado('quarta','f7',['SP','MS'],AZUL)
estado('calor-sabado','f9',['PI'],VERM)
estado('tendencia-frio','f10',['RS','SC','PR'],FRIO)
pinos=[]
def pin(fid,palavra,nome,sub,lon,lat):
    pinos.append(dict(nome=nome,sub=sub,lon=lon,lat=lat,ini=em(fid,palavra),fim=fim(fid),h=150))
pin('f1','instabilidade','Sudeste','pancadas hoje',-45,-22)
pin('f5','Bahia','Bahia','terça: pancadas previstas',-42,-13)
pin('f6','Roraima','Roraima','terça: pouca chuva',-61,2.8)
pin('f7','aumentar','São Paulo','quarta: pancadas aumentam',-49,-23)
pin('f8','serras','Áreas altas do Sul','terça: mínima de 10 a 15 °C',-50,-28)
pin('f9','40','Piauí','sábado: pode superar 40 °C',-42,-7)
paineis=[]
def painel(fid,k,linhas,l='previsão · '+MET):
    paineis.append(dict(ini=max(2,ini(fid)),fim=fim(fid),k=k,itens=[dict(t=em(fid,pal),txt=txt) for pal,txt in linhas],l=l,borda='rgba(60,150,255,.8)'))
painel('f1','HOJE · 16/11/2026',[('instabilidade','SÃO PAULO E RIO · INSTABILIDADE')], 'INMET · risco de tempestade nas áreas pintadas')
painel('f2','CHUVA IRREGULAR',[('distribuída','pancadas mal distribuídas'),('marítima','litoral sul: circulação marítima')], 'GOES-19 observado · '+brt(TS[BONS[0]])+' a '+brt(TS[BONS[-1]]))
painel('f3','HOJE · BRASIL',[('Sudeste','Sudeste com pancadas')])
num=em('f3','33'); paineis[-1]['contador']=dict(de=28,ate=33,ini=num-1,dur=1,dec=0,cor='#ff8c1a',unid='°C · MÁXIMAS DE 28 A 33')
painel('f4','SUL · HOJE → AMANHÃ',[('isoladas','hoje: pancadas isoladas'),('Amanhã','terça: tarde e noite')], 'Meteorologia · 16/11/2026 · INMET 17/11')
paineis[-1]['fim']=GRA
painel('f5','TERÇA · CHUVA PREVISTA',[('Goiás','GOIÁS · TOCANTINS · NORTE MG'),('Nordeste','NORDESTE · MA / PI / BA')])
painel('f6','NORTE · TERÇA',[('irregular','CHUVA IRREGULAR'),('pouca','RR · AP · CENTRO-NORTE PA')])
painel('f7','QUARTA · MUDANÇA',[('aumentar','MAIS PANCADAS: SP E MS'),('redução','REDUÇÃO: RJ E ES')])
painel('f8','TERÇA · AMANHECER',[('frias','ÁREAS MAIS FRIAS'),('15','10 A 15 °C · SUL MG E SERRAS')])
painel('f9','SÁBADO · PREVISÃO',[('Piauí','PIAUÍ · CALOR ONDE CHOVE MENOS')])
num=em('f9','40'); paineis[-1]['contador']=dict(de=30,ate=40,ini=num-1,dur=1,dec=0,cor='#ff2a1f',unid='°C · PODE PASSAR DESTE VALOR')
painel('f10','PRÓXIMA SEMANA · TENDÊNCIA',[('queda','QUEDA DA TEMPERATURA NO SUL')])
painel('f11','COMENTA AQUI',[('onde','DE ONDE VOCÊ É?'),('tempo','COMO ESTÁ AÍ?')],MET)
cta={'ini':ini('f12'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f12','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
fontes=[dict(ini=2,fim=ini('f2'),html=MET+' · INMET 16/11'),dict(ini=ini('f2'),fim=ini('f3'),html=MET+' · NOAA/GOES-19 via NASA GIBS'),dict(ini=ini('f3'),fim=ini('f4'),html=MET),dict(ini=ini('f4'),fim=GRA,html=MET+' · INMET 17/11'),dict(ini=GRA,fim=fim('f4'),html=MET+' · risco pontual previsto · ilustração'),dict(ini=ini('f5'),fim=DUR,html=MET)]
# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "umidade": "#5ec8ff", "pancadas": "#5ec8ff", "pancadao": "#5ec8ff", "toro": "#5ec8ff",
         "frio": "#96d2ff", "amanhecer": "#96d2ff", "graus": "#ff2a1f", "granizo": "#ff2a1f", "tempestade": "#ff2a1f", "sobe": "#ff2a1f",
         "alerta": "#ff8c1a", "vento": "#ff8c1a", "calor": "#ff8c1a", "acima": "#ff2a1f", "abaixo": "#ff8c1a", "baixa": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "sao", "paulo", "minas", "brasil", "nordeste", "piaui", "serra", "curitiba", "porto", "alegre", "oeste", "paulista",
         "rio", "sertao", "maranhao", "pernambuco", "paraiba", "bahia", "amazonia", "pais", "inemaclub", "onde"}
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

C = {'layout':'canto' if CANTO else 'avatar' if AVATAR else 'cheio','padding_baixo':640 if CANTO else 820,'padding_topo':520,'duracao':DUR,
'marca':'INEMA · CLIMA DO DIA','selo':'16/11 · INMET · NOAA', 'camera':camera,'sat':SAT,'imagens':imagens,'colunas':colunas,'telas':telas,'estados':estados,'pinos':pinos,'hero':hero,'paineis':paineis,'cta':cta,'club':club,'fontes':fontes,'legenda':legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js ok · {DUR}s · {len(BONS)} quadros IR · avisos hoje {len(HOJE)} / amanhã {len(AMANHA)}')
