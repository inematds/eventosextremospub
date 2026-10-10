#!/usr/bin/env python3
"""Clima no Brasil nas últimas 24 h (medido) + previsão 48 h nas capitais. Só APIs gratuitas liberadas.
uso: coleta/ultimas24h.py <pasta-bruto> [--fim 2026-10-10T06:00]   (fim em UTC; padrão = agora)
Grava JSON/CSV brutos e resumo.json na pasta. Cada fonte é independente: se falhar, vai para falhas[]."""
import argparse, csv, io, json, math, time, traceback, urllib.error, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"}
IBGE = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
        "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
        "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
CAP = {"Porto Velho": ("RO", -8.76, -63.90), "Rio Branco": ("AC", -9.97, -67.81), "Manaus": ("AM", -3.12, -60.02),
       "Boa Vista": ("RR", 2.82, -60.67), "Belém": ("PA", -1.46, -48.49), "Macapá": ("AP", 0.03, -51.07),
       "Palmas": ("TO", -10.18, -48.33), "São Luís": ("MA", -2.53, -44.30), "Teresina": ("PI", -5.09, -42.80),
       "Fortaleza": ("CE", -3.72, -38.54), "Natal": ("RN", -5.79, -35.21), "João Pessoa": ("PB", -7.12, -34.86),
       "Recife": ("PE", -8.05, -34.88), "Maceió": ("AL", -9.67, -35.74), "Aracaju": ("SE", -10.91, -37.07),
       "Salvador": ("BA", -12.97, -38.50), "Belo Horizonte": ("MG", -19.92, -43.94), "Vitória": ("ES", -20.32, -40.34),
       "Rio de Janeiro": ("RJ", -22.91, -43.17), "São Paulo": ("SP", -23.55, -46.63), "Curitiba": ("PR", -25.43, -49.27),
       "Florianópolis": ("SC", -27.60, -48.55), "Porto Alegre": ("RS", -30.03, -51.23), "Campo Grande": ("MS", -20.47, -54.62),
       "Cuiabá": ("MT", -15.60, -56.10), "Goiânia": ("GO", -16.68, -49.25), "Brasília": ("DF", -15.79, -47.88)}

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--fim", help="fim da janela em UTC, AAAA-MM-DDTHH:MM")
a = ap.parse_args()
dst = Path(a.pasta); dst.mkdir(parents=True, exist_ok=True)
fim = datetime.fromisoformat(a.fim).replace(tzinfo=timezone.utc) if a.fim else datetime.now(timezone.utc)
ini = fim - timedelta(hours=24)
R = {"janela_utc": [ini.isoformat(), fim.isoformat()], "coletado_utc": datetime.now(timezone.utc).isoformat(), "falhas": []}


def get(url, timeout=90):
    r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
    return r.status, r.read()


def etapa(nome):
    def deco(f):
        try:
            R[nome] = f()
        except Exception as e:
            R["falhas"].append({"fonte": nome, "erro": repr(e)[:400], "trace": traceback.format_exc()[-600:]})
            print("FALHA", nome, repr(e)[:200])
        return f
    return deco


@etapa("inmet_avisos")
def _():
    st, b = get("https://apiprevmet3.inmet.gov.br/avisos/ativos")
    (dst / "inmet_avisos_ativos.json").write_bytes(b)
    d = json.loads(b); out = {}
    for grupo in ("hoje", "futuro"):
        lst = []
        for av in d.get(grupo, []):
            ufs = Counter(IBGE.get(g[:2], g[:2]) for g in av["geocodes"].split(",") if g)
            lst.append({"id": av["id"], "desc": av["descricao"], "sev": av["severidade"], "inicio": av.get("inicio"),
                        "fim": av.get("fim"), "municipios": sum(ufs.values()), "ufs": dict(ufs)})
        por = Counter((x["desc"], x["sev"]) for x in lst)
        ufs_sev = defaultdict(set)
        for x in lst:
            for u in x["ufs"]:
                ufs_sev[x["sev"]].add(u)
        out[grupo] = {"n": len(lst), "por_tipo_sev": [[k[0], k[1], v] for k, v in por.most_common()],
                      "ufs_por_sev": {k: sorted(v) for k, v in ufs_sev.items()}, "avisos": lst}
    return out


@etapa("inmet_estacoes")
def _():
    tent = []
    h = ini.replace(minute=0, second=0, microsecond=0)
    while h <= fim:
        url = f"https://apitempo.inmet.gov.br/estacao/dados/{h:%Y-%m-%d}/{h:%H}00"
        try:
            st, b = get(url, 30); tent.append([url, st, len(b)])
        except Exception as e:
            tent.append([url, repr(e)[:120], 0])
        h += timedelta(hours=1)
    ok = [t for t in tent if t[1] == 200 and t[2] > 2]
    (dst / "inmet_estacoes_tentativas.json").write_text(json.dumps(tent, indent=0))
    if not ok:
        raise RuntimeError(f"apitempo.inmet.gov.br/estacao/dados/<dia>/<HH00>: {len(tent)} pedidos, todos sem dados "
                           f"(status {Counter(str(t[1]) for t in tent).most_common()}); sem token não sai dado de estação")
    return {"ok": len(ok)}


@etapa("cemaden")
def _():
    todos, erros = [], {}
    for uf in sorted(set(IBGE.values())):
        try:
            st, b = get(f"https://resources.cemaden.gov.br/graficos/interativo/getJson2.php?uf={uf}", 60)
            todos += json.loads(b) if b.strip() else []
        except Exception as e:
            erros[uf] = repr(e)[:120]
        time.sleep(0.5)
    (dst / "cemaden_getJson2_todas_ufs.json").write_text(json.dumps(todos, ensure_ascii=False))
    vivos = []
    for x in todos:
        try:
            t = datetime.strptime(x["datahoraUltimovalor"], "%d/%m/%y %H:%M").replace(tzinfo=timezone.utc)
            v = float(x["acc24hr"])
        except (TypeError, ValueError, KeyError):
            continue
        if fim - t < timedelta(hours=6):  # só estação que mandou dado recente
            vivos.append({"cidade": x["cidade"].title(), "uf": x["uf"], "estacao": x["nomeestacao"], "acc24": v,
                          "acc1": x.get("acc1hr"), "acc3": x.get("acc3hr"), "acc6": x.get("acc6hr"), "ultimo": x["datahoraUltimovalor"], "tipo": x.get("tipoestacao")})
    vivos.sort(key=lambda r: -r["acc24"])
    por_uf = defaultdict(float)
    for r in vivos:
        por_uf[r["uf"]] = max(por_uf[r["uf"]], r["acc24"])
    return {"estacoes_total": len(todos), "estacoes_recentes": len(vivos), "erros_uf": erros, "top": vivos[:25],
            "max_por_uf": dict(sorted(por_uf.items(), key=lambda k: -k[1])),
            "n_ge_50": sum(r["acc24"] >= 50 for r in vivos), "n_ge_100": sum(r["acc24"] >= 100 for r in vivos)}


@etapa("inpe_focos")
def _():
    B = "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/"
    linhas = []
    for d in sorted({ini.date(), fim.date()}):
        st, b = get(f"{B}focos_diario_br_{d:%Y%m%d}.csv", 120)
        (dst / f"inpe_focos_diario_br_{d:%Y%m%d}.csv").write_bytes(b)
        linhas += list(csv.DictReader(io.StringIO(b.decode("utf-8", "replace"))))
    jan = [r for r in linhas if ini <= datetime.fromisoformat(r["data_hora_gmt"]).replace(tzinfo=timezone.utc) < fim]
    ult = max((r["data_hora_gmt"] for r in linhas), default=None)
    ref = [r for r in jan if r["satelite"] == "AQUA_M-T"]

    def cont(rs, k):
        return Counter(r[k].title() for r in rs).most_common()
    return {"ultimo_foco_gmt": ult, "todos_sat": len(jan), "sat_ref_AQUA_M-T": len(ref),
            "por_satelite": Counter(r["satelite"] for r in jan).most_common(),
            "por_estado_todos": cont(jan, "estado")[:15], "por_bioma_todos": cont(jan, "bioma"),
            "por_estado_ref": cont(ref, "estado")[:15], "por_bioma_ref": cont(ref, "bioma"),
            "top_municipios_todos": [[f'{r[0][0].title()}/{r[0][1].title()}', r[1]] for r in
                                     Counter((x["municipio"], x["estado"]) for x in jan).most_common(10)]}


def ur(t, td):
    es = lambda x: math.exp(17.625 * x / (243.04 + x))
    return round(100 * es(td) / es(t))


@etapa("noaa_metar")
def _():
    # bbox devolve no máximo 400 linhas (só ~8 h): lista as estações e pede por ids, em lotes
    st, b = get("https://aviationweather.gov/api/data/stationinfo?bbox=-34,-74,6,-34&format=json", 120)
    ids = sorted({s["icaoId"] for s in json.loads(b) if s.get("country") == "BR" or str(s.get("icaoId", ""))[:2] in ("SB", "SW", "SN", "SD", "SI", "SJ", "SS")})
    todos = []
    for i in range(0, len(ids), 10):
        st, b = get("https://aviationweather.gov/api/data/metar?ids=" + ",".join(ids[i:i + 10]) + "&hours=26&format=json", 120)
        lote = json.loads(b) if b.strip() else []
        if len(lote) >= 400:
            print("aviso: lote METAR no teto de 400", ids[i:i + 10])
        todos += lote
        time.sleep(1)
    (dst / "noaa_metar_brasil_24h.json").write_text(json.dumps(todos))
    obs = [o for o in todos if o.get("icaoId", "")[:2] in ("SB", "SW", "SN", "SD", "SI", "SJ", "SS")
           and ini.timestamp() <= o.get("obsTime", 0) < fim.timestamp() + 1]
    est = defaultdict(list)
    for o in obs:
        est[o["icaoId"]].append(o)
    tmax, tmin, raj, umin = [], [], [], []
    for k, os_ in est.items():
        nome = os_[0].get("name", "")
        quando = lambda o: datetime.fromtimestamp(o["obsTime"], timezone.utc).strftime("%d/%m %H:%MZ")
        tt = [o for o in os_ if isinstance(o.get("temp"), (int, float))]
        if tt:
            m = max(tt, key=lambda o: o["temp"]); tmax.append([m["temp"], k, nome, quando(m)])
            m = min(tt, key=lambda o: o["temp"]); tmin.append([m["temp"], k, nome, quando(m)])
            uu = [(ur(o["temp"], o["dewp"]), o) for o in tt if isinstance(o.get("dewp"), (int, float))]
            if uu:
                m = min(uu, key=lambda p: p[0]); umin.append([m[0], k, nome, quando(m[1]), m[1]["temp"]])
        gg = [o for o in os_ if isinstance(o.get("wgst"), (int, float))]
        if gg:
            m = max(gg, key=lambda o: o["wgst"]); raj.append([round(m["wgst"] * 1.852), k, nome, quando(m), m["rawOb"]])
    return {"aeroportos": len(est), "obs": len(obs), "tmax_top": sorted(tmax, reverse=True)[:12],
            "tmin_top": sorted(tmin)[:10], "rajada_kmh_top": sorted(raj, reverse=True)[:12], "ur_min_top": sorted(umin)[:12],
            "trovoada": sorted({o["icaoId"] + " " + o.get("name", "") for o in obs if "TS" in (o.get("wxString") or "")})}


@etapa("openmeteo_capitais")
def _():
    nomes = list(CAP)
    d0 = (fim - timedelta(hours=3)).date()  # dia local de Brasília
    url = ("https://api.open-meteo.com/v1/forecast?latitude=" + ",".join(str(CAP[n][1]) for n in nomes) +
           "&longitude=" + ",".join(str(CAP[n][2]) for n in nomes) + "&timezone=America%2FSao_Paulo"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_gusts_10m_max,relative_humidity_2m_min"
           f"&start_date={d0}&end_date={d0 + timedelta(days=2)}")
    for t in range(5):
        try:
            st, b = get(url, 120); break
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(20 * (t + 1))
    (dst / "openmeteo_capitais_3d.json").write_bytes(b)
    res, ext = [], []
    for n, r in zip(nomes, json.loads(b)):
        dd = r["daily"]
        for i, dia in enumerate(dd["time"]):
            row = {"cap": n, "uf": CAP[n][0], "dia": dia, "tmax": dd["temperature_2m_max"][i], "tmin": dd["temperature_2m_min"][i],
                   "chuva": dd["precipitation_sum"][i], "raj": dd["wind_gusts_10m_max"][i], "urmin": dd["relative_humidity_2m_min"][i]}
            res.append(row)
            for k, cond in (("tmax", lambda v: v >= 38), ("chuva", lambda v: v >= 50), ("raj", lambda v: v >= 70), ("urmin", lambda v: v <= 20)):
                if row[k] is not None and cond(row[k]):
                    ext.append([k, n, CAP[n][0], dia, row[k]])
    return {"modelo": "Open-Meteo best_match", "linhas": res, "extremos": ext}


(dst / "resumo.json").write_text(json.dumps(R, ensure_ascii=False, indent=1))
print("→", dst / "resumo.json", "| falhas:", [f["fonte"] for f in R["falhas"]])
