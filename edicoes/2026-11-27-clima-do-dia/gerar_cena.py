#!/usr/bin/env python3
"""Clima do DIA 27/11/2026. Boletim como fonte da previsão; --canto usa tempos do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "27/11/2026"
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
LAR, AZUL = [255, 140, 26], [60, 150, 255]

# O aviso laranja abrange municípios já incluídos no aviso amarelo.
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
avisos = {a["id"]: a for a in AV["hoje"]}
UFCOD = {"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
         "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL",
         "28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR",
         "42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
codigos = {}
for aid, quantidade, severidade in [(56517, 1823, "Perigo Potencial"), (56515, 233, "Perigo")]:
    aviso = avisos[aid]
    assert aviso["descricao"] == "Chuvas Intensas" and aviso["severidade"] == severidade
    assert aviso["inicio"].startswith("2026-11-27")
    codigos[aid] = set(aviso["geocodes"].split(","))
    assert len(codigos[aid]) == quantidade
municipios = codigos[56517] | codigos[56515]
assert len(municipios) == 1823
ufs = {UFCOD[c[:2]] for c in municipios}
ufs_perigo = {UFCOD[c[:2]] for c in codigos[56515]}

regioes = [
    (-54.7, -28.8, 4.15, 5),   # oeste gaúcho e Sul no infravermelho
    (-53.2, -27.4, 3.85, 3),
    (-49.9, -27.45, 5.05, 9), # Serra Catarinense e litoral
    (-42.6, -8.4, 4.12, 8),
    (-66.0, -7.2, 3.93, 6),
    (-48.2, -16.7, 4.25, 9),
    (-49.6, -25.0, 4.25, 55),
    (-44.9, -22.7, 4.82, 9),
    (-44.3, -14.0, 3.55, 7),
    (-53.0, -14.3, 3.24, 0),
    (-53.0, -14.3, 3.24, 0),
]
camera = []

def chave(t, loc, bearing, zoom_extra=0):
    lon, lat, zoom, pitch = loc
    camera.append(dict(t=t, lon=lon, lat=lat, zoom=zoom + zoom_extra, pitch=pitch, bearing=bearing))

def fim_mapa(fid):
    return min(fim(fid) - .08, FALA[fid]["palavras"][-1]["f"] + .15)

for i, loc in enumerate(regioes, 1):
    fid = f"f{i}"
    inicio = 0 if i == 1 else max(0, ini(fid) - .16)
    ultima = max(inicio + .12, fim_mapa(fid) - .55)
    if i == 3:
        litoral = em(fid, "litoral")
        chave(inicio, loc, -3)
        chave(max(inicio + .1, litoral - .55), loc, 1)
        chave(max(litoral + .32, ultima), (-48.9, -27.0, 5.0, 8), 4)
    elif i == 7:
        sul = em(fid, "gaúcho")
        sp = (-47.8, -23.4, 4.48, 55)
        chave(inicio, sp, -15)
        chave(max(inicio + .1, sul - 1.05), sp, -2)
        chave(max(sul + .1, ultima), loc, 15)
    elif i == 9:
        chave(inicio, loc, -4)
        chave(ultima, (-42.6, -11.8, 3.62, 5), 7)
    else:
        chave(inicio, loc, -3)
        chave(ultima, loc, 4, .06 if i < 10 else 0)
chave(DUR, regioes[-1], 4)
assert all(a["t"] < b["t"] for a, b in zip(camera, camera[1:])), camera

from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
BONS = []
for i in range(len(TS)):
    with Image.open(AQUI / f"sat/web/ir{i:02d}.jpg") as img:
        if 90 < ImageStat.Stat(img.convert("L")).mean[0] < 130:
            BONS.append(i)
assert len(BONS) == len(TS) == 49

def brt(z):
    return (datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)).strftime("%d/%m %Hh%M")

IR_JANELA = f"{brt(TS[BONS[0]])} a {brt(TS[BONS[-1]])} (Brasília)"
CORTE_CAPA = 2
GRANIZO = em("f2", "granizo")
# A sequência começa no primeiro mapa e termina quando entra a ilustração.
SAT = dict(fundo=dict(src="sat/web/mundo.jpg", bbox=[-180,-60,180,75], tint=[170,170,175]),
           base="sat/web/geocolor-borda.png", bbox=[-76,-35,-33,7], tint=[170,170,175],
           ir=dict(frames=[f"sat/web/ir{i:02d}-borda.png" for i in BONS],
                   tempos=[brt(TS[i]) for i in BONS], ini=CORTE_CAPA, fim=GRANIZO,
                   dur=GRANIZO-CORTE_CAPA, alfa=.9, rotulo="GOES-19 · NUVENS FRIAS (IR)"))
telas = [
    dict(src="capa-dia/abertura.png", ini=0, fim=CORTE_CAPA, fade=0, zoom=0,
         selo=MET),
    dict(src="capa-dia/granizo.png", ini=GRANIZO, fim=min(GRANIZO+2.25, fim("f2")),
         fade=0, zoom=.035, selo="ILUSTRAÇÃO"),
]

def estado(id_, inicio, final, lista, cor=AZUL, alfa=.28):
    return dict(id=id_, ini=inicio, fim=final, ufs=sorted(lista), cor=cor, alfa=alfa)

estados = [
    estado("inmet-potencial", CORTE_CAPA, fim("f2"), ufs, [241,199,44], .27),
    estado("inmet-perigo", CORTE_CAPA, fim("f2"), ufs_perigo, LAR, .4),
    estado("serra", ini("f3"), fim("f3"), ["SC"]),
    estado("calor", ini("f4"), fim("f4"), ["PI"], LAR, .42),
    estado("amazonas", ini("f5"), fim("f5"), ["AC","AM","RO"]),
    estado("centro", ini("f6"), fim("f6"), ["DF","GO","MG"]),
    estado("sabado", ini("f7"), fim("f7"), ["RS","SC","PR","SP"]),
    estado("domingo", ini("f8"), fim("f8"), ["RJ"], AZUL, .43),
    estado("tendencia-dezembro", ini("f9"), fim_mapa("f9")+.4, ["MG","PB","PE","AL","CE","PI"]),
]

# Pontos de previsão de sexta a domingo nas faixas de chuva citadas no boletim.
om = json.loads((B / "openmeteo_capitais_3d.json").read_text())
capitais = [("Florianópolis",-48.55,-27.59), ("Curitiba",-49.27,-25.43),
            ("São Paulo",-46.64,-23.55)]
col = []
for nome, lon, lat in capitais:
    ponto = min(om, key=lambda d: (d["longitude"]-lon)**2 + (d["latitude"]-lat)**2)
    diaria = ponto["daily"]
    assert diaria["time"][:3] == ["2026-11-27","2026-11-28","2026-11-29"]
    col.append(dict(id=nome, p=[lon, lat], v=round(sum(diaria["precipitation_sum"][:3]), 1)))
assert [c["v"] for c in col] == [18.6, 9.8, 21.9]
OM = "Open-Meteo · previsão de 27 a 29/11"
colunas = [dict(id="chuva-ate-domingo", ini=ini("f7"), fim=fim("f7"),
                dados=col, cor=AZUL, escala=17000, raio=41000, varredura=.14,
                ordem={c["id"]: i for i,c in enumerate(col)})]

pinos = []
def pin(fid, palavra, nome, sub, lon, lat, fim_pin=None, h=58):
    instante = em(fid, palavra)
    fim_pin = fim(fid) if fim_pin is None else fim_pin
    assert instante < fim_pin
    pinos.append(dict(nome=nome, sub=sub, lon=lon, lat=lat, ini=instante, fim=fim_pin, h=h))

pin("f2","oeste","Oeste gaúcho","TROVOADAS NO RADAR",-55.7,-29.75,GRANIZO)
pin("f3","Serra","Serra Catarinense","FRIO PELA MANHÃ",-50.0,-28.0,em("f3","litoral"))
pin("f3","Itajaí","Vale do Itajaí","CHUVA MAIS TARDE",-49.07,-26.92)
pin("f4","Piauí","Piauí","MÁXIMA PREVISTA",-42.2,-7.8)
pin("f5","oeste","Oeste do Amazonas","PANCADAS MAIS FORTES",-67.6,-5.2,em("f5","Acre"))
pin("f5","Acre","Acre","PANCADAS MAIS FORTES",-68.3,-9.45,em("f5","Rondônia"))
pin("f5","Rondônia","Rondônia","PANCADAS MAIS FORTES",-63.1,-10.25)
pin("f6","Brasília","Brasília","PANCADAS NO RADAR",-47.88,-15.79,em("f6","Triângulo"))
pin("f6","Triângulo","Triângulo Mineiro","PANCADAS PREVISTAS",-48.3,-19.08)
pin("f7","Paulo","São Paulo","CHUVA GANHA FORÇA",-46.64,-23.55,em("f7","gaúcho"))
pin("f7","gaúcho","Norte gaúcho","PANCADAS NO SÁBADO",-52.35,-27.65,em("f7","Paraná"), h=28)
pin("f7","Paraná","Paraná","PANCADAS NO SÁBADO",-51.3,-24.7)
pin("f8","capital","Rio de Janeiro","RISCO DE CHUVA FORTE",-43.17,-22.91,em("f8","Região"))
pin("f8","Região","Região Serrana","RISCO DE CHUVA FORTE",-43.00,-22.36)

paineis = []
def painel(fid, k, linhas, inicio=None, fim_painel=None, l=MET):
    paineis.append(dict(ini=max(CORTE_CAPA, ini(fid)) if inicio is None else inicio,
                        fim=fim(fid) if fim_painel is None else fim_painel,
                        k=k, itens=[dict(t=em(fid,pal),txt=txt) for pal,txt in linhas],
                        l=l, borda="rgba(60,150,255,.8)"))

def contador(fid, palavra, ate, unid, cor="#ff8c1a", de=0):
    paineis[-1]["contador"] = dict(de=de, ate=ate, ini=em(fid,palavra)-1, dur=1,
                                    dec=0, cor=cor, unid=unid)

painel("f1","SUL · SEXTA",[("granizo","RISCO DE GRANIZO"),("vento","VENTO FORTE PONTUAL")])
painel("f2","OESTE GAÚCHO",[("trovoadas","TROVOADAS NO RADAR")],fim_painel=GRANIZO)
painel("f2","RISCO PONTUAL",[("granizo","GRANIZO E VENTO"),("Paraná","RS, SC E PR")],inicio=GRANIZO)
painel("f3","SERRA CATARINENSE · MÍNIMAS",[],fim_painel=em("f3","litoral"))
contador("f3","4",4,"°C · ENTRE 3 E 4","#96d2ff",de=3)
painel("f3","LITORAL E VALE DO ITAJAÍ",[("noite","CHUVA À NOITE")],inicio=em("f3","litoral"))
painel("f4","PIAUÍ · MÁXIMA PREVISTA",[])
contador("f4","40",40,"°C · APROX.")
painel("f5","NORTE · SEXTA",[("pancadas","PANCADAS MAIS FORTES"),("Acre","OESTE DO AM, AC E RO")])
painel("f6","CENTRO DO PAÍS · SEXTA",[("Brasília","PANCADAS EM BRASÍLIA"),("Triângulo","GO E TRIÂNGULO MINEIRO")])
painel("f7","SÁBADO",[("Paulo","CHUVA FORTE EM SP"),("gaúcho","NORTE DO RS, SC E PR")])
painel("f8","DOMINGO",[("capital","ATENÇÃO NO RIO"),("Serrana","CAPITAL E SERRA")])
painel("f9","INÍCIO DE DEZEMBRO",[("Minas","CHUVA EM MINAS"),("Nordeste","PANCADAS AVANÇAM NO NE")],
       fim_painel=fim_mapa("f9")+.4)
painel("f10","COMENTA AQUI",[("onde","DE ONDE VOCÊ É?"),("tempo","COMO ESTÁ AÍ?")],l="")
cta = dict(ini=ini("f11"),fim=DUR,a="APRENDA IA",b="inema.club")
club = dict(ini=em("f11","inema"),fim=DUR,a="inema.club",b="aprenda sobre inteligência artificial")

INMET = "INMET · estados com municípios sob aviso"
col_texto = " · ".join(f"{c['id']} {c['v']:g}".replace(".",",") for c in col)
fontes = [
    dict(ini=CORTE_CAPA,fim=GRANIZO,html="NOAA / GOES-19 · infravermelho realçado · "+IR_JANELA+"<br>"+INMET),
    dict(ini=GRANIZO,fim=fim("f2"),html=MET+" · risco pontual no Sul"),
    dict(ini=ini("f3"),fim=ini("f7"),html=MET),
    dict(ini=ini("f7"),fim=fim("f7"),html=OM+" · acumulados por ponto (mm)<br>"+col_texto),
    dict(ini=ini("f8"),fim=ini("f9"),html=MET+" · previsão de domingo"),
    dict(ini=ini("f9"),fim=fim_mapa("f9")+.4,html=MET+" · tendência para dezembro"),
]

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

C = {'layout':'canto' if CANTO else 'avatar' if AVATAR else 'cheio','padding_baixo':640 if CANTO else 820,'padding_topo':290,'duracao':DUR,
'marca':'INEMA · CLIMA DO DIA','selo':'27/11 · Meteorologia', 'camera':camera,'sat':SAT,'colunas':colunas,'telas':telas,'estados':estados,'pinos':pinos,'paineis':paineis,'cta':cta,'club':club,'fontes':fontes,'legenda':legenda}
# Ajuste local de composição: capa limpa durante os dois segundos iniciais.
# O motor compartilhado permanece intacto; --canto recebe o mesmo comportamento.
AJUSTE = """
window.addEventListener('load', () => {
  const render = window.render;
  const colunas = window.CENA.colunas[0];
  const vinheta = document.getElementById('vinheta');
  const camada = document.createElement('div');
  camada.style.cssText = 'position:absolute;inset:0 0 auto;height:220px;pointer-events:none;'
    + 'background:linear-gradient(#05080c 12%,rgba(5,8,12,.9) 45%,transparent)';
  vinheta.appendChild(camada);
  window.render = async function(t) {
    await render(t);
    for (const id of ['topo', 'leg']) {
      document.getElementById(id).style.opacity = t < 2 ? '0' : '1';
    }
    const entrada = Math.max(0, (t - colunas.ini + .5) * 2);
    const saida = Math.max(0, (colunas.fim + .5 - t) * 2);
    camada.style.opacity = Math.min(1, entrada, saida);
  };
});
"""
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';'+AJUSTE)
print(f'cena.js ok · {DUR}s · {len(BONS)} quadros IR · {len(municipios)} municípios INMET · {len(col)} colunas')
