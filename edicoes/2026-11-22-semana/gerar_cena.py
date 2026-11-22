#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana + 15 dias" de 22/11/2026 a partir de tempos.json (palavras da narração),
da previsão de 16 dias do Open-Meteo (om/prev15_*.json) e dos avisos do INMET (pesquisa/bruto).
Semana = 23/11 a 29/11 (previsto); dias 8 a 15 = 30/11 a 07/12 (tendência).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "22/11/2026"
SEM, TEND = "23 A 29/11", "30/11 A 07/12"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
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
chega = lambda fid, palavra: round(em(fid, palavra) - 1.0, 3)  # contador chega ao número quando a palavra é dita (Lesson 13/10)
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
AMAR, AZUL, VERM, LARANJA = [255, 210, 63], [60, 150, 255], [255, 42, 31], [255, 140, 26]

# Dados desta edição; asserts impedem renderizar outra coleta por engano.
R=json.loads((AQUI/'om/prev15_resumo.json').read_text())
G=json.loads((AQUI/'om/prev15_grade.json').read_text())['pts']
CAP={c['cap']:c for c in json.loads((AQUI/'om/prev15_capitais.json').read_text())['capitais']}
gs,gt=R['grade']['semana'],R['grade']['tendencia_8a15']
assert R['inicio']=='2026-11-23' and gs['dias']=='2026-11-23 a 2026-11-29' and gt['dias']=='2026-11-30 a 2026-12-07'
soma=lambda v:round(sum(x or 0 for x in v),1)
ponto=lambda x,y:next(p for p in G if p['p']==[x,y])
assert soma(ponto(-52.5,-27)['chuva'][:7])==246.3
assert ponto(-52.5,-27)['chuva'][2]==110.1
assert soma(ponto(-43.5,-22.5)['chuva'][:7])==212.0
assert soma(ponto(-49.5,-18)['chuva'][:7])==126.4
assert ponto(-42,-6)['tmax'][3]==42.3
assert soma(ponto(-60,-1.5)['chuva'][:7])==136.0
assert ponto(-48,-24)['raj'][3]==65.2 and ponto(-49.5,-28.5)['tmin'][5]==9.0
assert soma(ponto(-48,-21)['chuva'][7:15])==190.6
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
a=next(a for a in AV['hoje'] if a['id']==56477)
assert a['fim']=='2026-11-22 23:59' and a['severidade']=='Perigo'
assert len(set(a['geocodes'].split(',')))==655
UF={'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
ALERTA=sorted({UF[c[:2]] for c in a['geocodes'].split(',')})
pu_s,pu_t=gs['por_uf'],gt['por_uf']
CHUVA_S=sorted(u for u,v in pu_s.items() if v['chuva_max']>=100)
CALOR_S=sorted(u for u,v in pu_s.items() if v['tmax']>=38)
CHUVA_T=sorted(u for u,v in pu_t.items() if v['chuva_max']>=100)

def cam(lon,lat,z=4.8):return dict(lon=lon,lat=lat,zoom=z)
BR=cam(-53,-15,3.75)
regioes=[cam(-52.5,-27,4.5),cam(-52.5,-27,5.3),cam(-43.5,-22,5.0),cam(-49.5,-18,4.9),cam(-42,-6,5.0),cam(-60,-1.5,4.9),cam(-49,-26,4.5),BR,cam(-48,-21,4.7),cam(-48,-21,5.1),BR,BR]
camera=[]
for i,r in enumerate(regioes,1):
 fid=f'f{i}';camera.extend([dict(t=ini(fid),**r,pitch=20,bearing=0),dict(t=fim(fid)-.15,**{**r,'zoom':r['zoom']+.08},pitch=25,bearing=2)])
camera.append(dict(t=DUR,**BR,pitch=0,bearing=0))
camera.sort(key=lambda k:k['t'])
assert all(x['t']<y['t'] for x,y in zip(camera,camera[1:]))
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},'base':'sat/web/geocolor.jpg','bbox':[-76,-35,-33,7],'tint':[170,170,175]}
def est(id,fs,fe,ufs,cor):return dict(id=id,ini=fs,fim=fe,ufs=ufs,cor=cor,alfa=.42)
estados=[est('sul',-1,ini('f3'),['SC'],AZUL),est('chuvaS',ini('f3'),ini('f5'),CHUVA_S,AZUL),est('calorS',ini('f5'),ini('f6'),CALOR_S,VERM),est('norteS',ini('f6'),ini('f7'),['AM'],AZUL),est('vento',ini('f7'),ini('f8'),['SP','SC'],AMAR),est('inmet',ini('f8'),ini('f9'),ALERTA,LARANJA),est('chuvaT',ini('f9'),ini('f11'),CHUVA_T,AZUL)]
def col(a,b):
 return [dict(id=f'c{i}',p=p['p'],v=soma(p['chuva'][a:b]),cor=AZUL) for i,p in enumerate(G) if soma(p['chuva'][a:b])>=30]
CS,CT=col(0,7),col(7,15)
colunas=[dict(id='sem',ini=ini('f2'),fim=ini('f5'),dados=CS,escala=1100,raio=30000,cor=AZUL),dict(id='norte',ini=ini('f6'),fim=ini('f7'),dados=CS,escala=1100,raio=30000,cor=AZUL),dict(id='tend',ini=ini('f9'),fim=ini('f11'),dados=CT,escala=850,raio=30000,cor=AZUL)]
def pin(fid,nome,sub,lon,lat):
 return dict(nome=nome,sub=sub,lon=lon,lat=lat,ini=ini(fid)+.4,fim=fim(fid)-.1,h=90)
pinos=[pin('f2','Oeste catarinense','110,1 mm previstos · quarta 25/11',-52.5,-27),pin('f3','Interior fluminense','212 mm previstos · 23–29/11',-43.5,-22.5),pin('f4','Sul de Goiás','126,4 mm previstos · 23–29/11',-49.5,-18),pin('f5','Interior do Piauí','42,3 °C previstos · quinta 26/11',-42,-6),pin('f6','Amazonas','136 mm previstos · 23–29/11',-60,-1.5),pin('f7','Interior paulista','65,2 km/h previstos · quinta 26/11',-48,-24),pin('f10','Interior paulista','190,6 mm · TENDÊNCIA 30/11–07/12',-48,-21)]
hero=[dict(ini=0,fim=ini('f2')-.05,html=f'''<div style="font:400 112px/1 'Archivo Black';margin-bottom:14px">{DATA}</div>
<div class="dt" style="font-size:38px;background:#ff2a1f;color:#fff">ALERTA DA SEMANA + 15 DIAS</div>
<div class="t1" style="font-size:150px;color:#ff8c1a">ATÉ 246,3 MM</div>
<div class="t4" style="font-size:57px">OESTE CATARINENSE</div>
<div class="t4" style="font-size:38px">PREVISTO · SEMANA 23 A 29/11</div>
<div style="font:400 96px/1.03 'Archivo Black';margin-top:28px;color:#ffd23f">SUA RUA<br>AGUENTA?</div>''')]

def painel(fid,titulo,v,unid,palavra,desc,cor='#5ec8ff',dec=1):
 return dict(ini=ini(fid),fim=fim(fid),k=titulo,contador=dict(de=0,ate=v,dec=dec,ini=chega(fid,palavra),dur=1.0,cor=cor,unid=unid),l=desc,borda=cor)
paineis=[
 painel('f2','OESTE CATARINENSE · PREVISTO QUARTA 25/11',110.1,'MM','110','246,3 mm previstos na semana · ponto da grade'),
 painel('f3',f'INTERIOR FLUMINENSE · PREVISTO {SEM}',212,'MM','212','Zona da Mata mineira: atenção na quinta',dec=0),
 painel('f4',f'SUL DE GOIÁS · PREVISTO {SEM}',126.4,'MM','126','Acumulado pontual · confira sua cidade'),
 painel('f5','INTERIOR DO PIAUÍ · PREVISTO QUINTA 26/11',42.3,'°C','42','Beba água · evite esforço no sol','#ff2a1f'),
 painel('f6',f'AMAZONAS · PREVISTO {SEM}',136,'MM','136','Chuva concentrada no sábado · atenção aos igarapés',dec=0),
 painel('f7','INTERIOR PAULISTA · PREVISTO QUINTA 26/11',65.2,'KM/H','65','Serra catarinense: mínima prevista 9 °C sábado','#ffd23f'),
 dict(ini=ini('f8'),fim=fim('f8'),k='INMET · PERIGO · DOMINGO 22/11',itens=[dict(t=ini('f8'),txt='Aviso 56477 · tempestade · até 23h59'),dict(t=em('f8','Defesa'),txt='Acompanhe a Defesa Civil'),dict(t=em('f8','atravesse'),txt='Não atravesse alagamentos')],borda='#ff8c1a'),
 dict(ini=ini('f9'),fim=fim('f9'),k=f'TENDÊNCIA {TEND}',itens=[dict(t=ini('f9'),txt='DIAS 8 A 15 · PODE MUDAR'),dict(t=em('f9','paulista'),txt='Chuva no interior paulista · projeção')],borda='#ffd23f'),
 painel('f10',f'INTERIOR PAULISTA · TENDÊNCIA {TEND}',190.6,'MM','190','DIAS 8 A 15 · PODE MUDAR · incerteza maior','#ffd23f'),
 dict(ini=ini('f11'),fim=fim('f11'),k='COMENTA AQUI 👇',itens=[dict(t=em('f11','região'),txt='Sua região'),dict(t=em('f11','cidade'),txt='Sua cidade'),dict(t=em('f11','tempo'),txt='Como está o tempo aí?')],borda='#ffd23f')]
cta=dict(ini=ini('f12'),fim=DUR,a='APRENDA IA',b='inema.club')
club=dict(ini=em('f12','inema'),fim=DUR,a='inema.club',b='aprenda de graça sobre inteligência artificial')
OM=f'<b>Open-Meteo</b> · previsão lida em {DATA}'
fontes=[dict(ini=-.5,fim=ini('f8'),html=f'{OM} · previsto 23–29/11 · pontos da grade de 1,5° · não é média estadual'),dict(ini=ini('f8'),fim=ini('f9'),html='INMET · aviso 56477 · perigo · válido até 22/11, 23h59 · lido em 22/11/2026'),dict(ini=ini('f9'),fim=ini('f11'),html=f'{OM} · <b>TENDÊNCIA 30/11–07/12</b> · dias 8 a 15 · pode mudar')]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "frio": "#9fd8ff", "minima": "#9fd8ff", "maxima": "#9fd8ff", "despenca": "#9fd8ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f", "forte": "#ff2a1f",
         "disparar": "#5ec8ff", "acumulada": "#5ec8ff", "tendencia": "#ffd23f", "mudar": "#ffd23f", "comenta": "#ffd23f", "tregua": "#ff2a1f"}
LUGAR = {"brasil", "goias", "serra", "gaucha", "paulista", "nordeste", "piaui", "minas", "centrooeste", "parana", "mato", "grosso", "norte", "tocantins", "vitoria", "amazonia", "interior", "inemaclub", "cidade", "regiao", "cidades"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        # Três palavras longas podem ultrapassar 1080 px: quebrar antes de 16 caracteres.
        if bloco and sum(len(x["w"]) for x in bloco) + len(w) > 16:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": anterior_f + .12, "palavras": bloco})
            bloco = []
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        anterior_f = p["f"]
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])


C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio","padding_baixo":640 if CANTO else 820,"padding_topo":560,"duracao":DUR,"marca":"INEMA · ALERTA DA SEMANA","selo":f"PREVISÃO · {SEM}","camera":camera,"sat":SAT,"estados":estados,"colunas":colunas,"pinos":pinos,"hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js ok · {DUR}s · {len(legenda)} legendas · semana {SEM} · tendência {TEND} · {len(ALERTA)} UFs no aviso')
