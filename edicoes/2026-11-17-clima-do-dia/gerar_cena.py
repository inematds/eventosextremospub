#!/usr/bin/env python3
"""Clima do DIA 17/11/2026. Boletim como fonte da previsão; --canto usa tempos do avatar."""
import os
import difflib, json, re, sys, unicodedata
from collections import Counter
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
HOJE=conjunto([56434,56430],'2026-11-17',[3438,569])
AMANHA=conjunto([56432,56433,56438],'2026-11-18',[387,658,4216])
ufs=lambda cs: sorted(set(UFCOD[c[:2]] for c in cs))
# Volumes registrados em BA; projeções regionais sem números fabricados.
regioes=[(-43,-14,4.8),(-43,-14,5.1),(-53,-14,3.6),(-49,-19,4.0),(-52,-28,4.3),(-44,-10,4.0),(-60,-6,3.8),(-51,-21,3.8),(-52,-28,4.3),(-53,-14,3.6),(-53,-14,3.6),(-53,-14,3.6)]
camera=[]
for i,(lon,lat,zoom) in enumerate(regioes,1):
    fid=f'f{i}'; pitch=55 if i==2 else 15 if i in (4,5,9) else 0
    for t,z,bearing in [(ini(fid)+(.35 if i>1 else 0),zoom,-12 if i==2 else -4),(fim(fid)-.1,zoom+.06,12 if i==2 else 4)]:
        camera.append(dict(t=t,lon=lon,lat=lat,zoom=z,pitch=pitch,bearing=bearing))
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
'ir':{'frames':[f'sat/web/ir{i:02d}.png' for i in BONS],'tempos':[brt(TS[i]) for i in BONS],'ini':ini('f3'),'fim':em('f3','previsão'),'dur':max(1,em('f3','previsão')-ini('f3')),'alfa':.9,'rotulo':'GOES-19 · observado · últimas 24 h'}}
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':2,'fade':0,'zoom':.03}]
imagens=[]; hero=[]
colunas=[dict(id='guanambi-registro',ini=ini('f2'),fim=fim('f2'),dados=[dict(id='guanambi',p=[-42.78,-14.22],v=200)],cor=AZUL,raio=16000,escala=1800,varredura=0,ordem={})]
estados=[]
def estado(id, fid, us, cor):
    estados.append(dict(id=id,ini=max(2,ini(fid)),fim=fim(fid),ufs=us,cor=cor,alfa=.3))
estado('registro-bahia','f1',['BA'],AZUL)
estado('registro-bahia-3d','f2',['BA'],AZUL)
estado('co-se','f4',['MT','MS','GO','DF','SP','RJ','ES','MG'],AZUL)
estado('sul','f5',['RS','SC','PR'],AZUL)
estado('nordeste','f6',['BA','MA','PI'],AZUL)
estado('norte-irregular','f7',['PA','AM','RO','AC','TO'],AMA)
estado('termica','f8',['RS','SC','PR','SP','MS','MG','GO'],FRIO)
estado('risco-hoje','f9',[u for u in ufs(HOJE) if u in ['RS','SC','PR']],LAR)
pinos=[]
def pin(fid,palavra,nome,sub,lon,lat):
    pinos.append(dict(nome=nome,sub=sub,lon=lon,lat=lat,ini=em(fid,palavra),fim=fim(fid),h=150))
pin('f1','Guanambi','Guanambi · BA','registro do fim de semana',-42.78,-14.22)
pin('f2','milímetros','Guanambi · BA','160–200 mm observados',-42.78,-14.22)
pin('f4','Centro-Oeste','Centro-Oeste','previsão até 30/11',-53,-16)
pin('f5','Campanha','Campanha · RS','previsão até 30/11',-55,-30)
pin('f6','Bahia','Bahia','chuva nas próximas semanas',-42,-13)
pin('f7','Pará','Pará','chuva irregular',-54,-5)
paineis=[]
def painel(fid,k,linhas,l='previsão · '+MET):
    paineis.append(dict(ini=max(2,ini(fid)),fim=fim(fid),k=k,itens=[dict(t=em(fid,pal),txt=txt) for pal,txt in linhas],l=l,borda='rgba(60,150,255,.8)'))
painel('f1','GUANAMBI · REGISTRO',[('Guanambi','FIM DE SEMANA · SUDOESTE DA BAHIA')],MET)
num=em('f1','200'); paineis[-1]['contador']=dict(de=0,ate=200,ini=num-1,dur=1,dec=0,cor='#5ec8ff',unid='mm · ATÉ / REGISTRADOS')
painel('f2','160 A 200 MM · OBSERVADOS',[('região','GUANAMBI E REGIÃO'),('30','SUPEROU A PREVISÃO DE 30 DIAS')],MET+' · fim de semana anterior')
painel('f3','BRASIL · CHUVA DESIGUAL',[('irregular','AGORA: DISTRIBUIÇÃO IRREGULAR'),('canal','DEZEMBRO: CANAL DE UMIDADE PREVISTO')],MET+' · GOES-19 observado')
painel('f4','ATÉ 30/11 · PREVISÃO',[('Centro-Oeste','CENTRO-OESTE E SUDESTE'),('expressivos','VOLUMES EXPRESSIVOS')])
painel('f5','SUL · ATÉ 30/11',[('frequente','CHUVA FREQUENTE PREVISTA'),('Campanha','AUMENTO TAMBÉM NA CAMPANHA')])
painel('f6','NORDESTE · PRÓXIMAS SEMANAS',[('Bahia','BAHIA: INDICAÇÃO DE CHUVA'),('irregular','MA / PI: DISTRIBUIÇÃO IRREGULAR')])
painel('f7','NORTE · IRREGULARIDADE',[('Pará','PA · AM · RO · AC · NORTE TO'),('repor','CHUVA DESIGUAL ENTRE AS ÁREAS')])
painel('f8','ATÉ DEZEMBRO · TEMPERATURA',[('Centro-Sul','CENTRO-SUL: NORMAL OU ABAIXO'),('Nordeste','NORDESTE: ACIMA DA MÉDIA')], 'tendência · '+MET)
painel('f9','SUL · RISCO',[('severo','FRIO + CALOR: RISCO DE TEMPO SEVERO'),('avisos','CONSULTE OS AVISOS LOCAIS')],MET+' · INMET 17/11')
painel('f10','DEZEMBRO · TENDÊNCIA',[('tendência','DETALHES PODEM MUDAR')],MET)
painel('f11','COMENTA AQUI',[('onde','DE ONDE VOCÊ É?'),('tempo','COMO ESTÁ AÍ?')],MET)
cta={'ini':ini('f12'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f12','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
fontes=[dict(ini=2,fim=ini('f3'),html=MET),dict(ini=ini('f3'),fim=em('f3','previsão'),html='NOAA/GOES-19 · '+brt(TS[BONS[0]])+' a '+brt(TS[BONS[-1]])),dict(ini=em('f3','previsão'),fim=ini('f9'),html=MET),dict(ini=ini('f9'),fim=ini('f10'),html=MET+' · INMET 17/11 · áreas de risco'),dict(ini=ini('f10'),fim=DUR,html=MET)]
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
'marca':'INEMA · CLIMA DO DIA','selo':'17/11 · Meteorologia · INMET', 'camera':camera,'sat':SAT,'imagens':imagens,'colunas':colunas,'telas':telas,'estados':estados,'pinos':pinos,'hero':hero,'paineis':paineis,'cta':cta,'club':club,'fontes':fontes,'legenda':legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js ok · {DUR}s · {len(BONS)} quadros IR · avisos hoje {len(HOJE)} / amanhã {len(AMANHA)}')
