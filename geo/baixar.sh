#!/usr/bin/env bash
# Base geográfica pública (municípios IBGE via tbrugz/geodata-br, estados, Natural Earth, coordenadas kelvins).
set -e; cd "$(dirname "$0")"
for c in 41 42 43 11 12 13 14 15 16 17 21 22 23 24 25 26 27 28 29; do [ -s mun$c.json ] || curl -sSL -o mun$c.json "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-$c-mun.json"; done
curl -sSL -o uf.json "https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json"
curl -sSL -o paises.geojson "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
curl -sSL -o rios.geojson "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_rivers_lake_centerlines.geojson"
curl -sSL -o municipios.csv "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
echo "ok — agora: python3 motor/prep_geo.py"
