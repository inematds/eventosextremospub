# eventosextremospub

Vídeos curtos 9:16 sobre **eventos extremos do clima** no estilo "sala de crise": mapa animado com dados reais (alertas por município, satélite, vento, chuva prevista), cada número aparecendo no instante em que é dito, narração com a voz do Nei e, depois, avatar.

O projeto tem três partes:

1. **Notícias de fonte segura** (`coleta/`, `fontes-clima.md`): INMET (avisos por município), NASA GIBS / NOAA GOES-19 (satélite), Open-Meteo (previsão em grade), MetSul, Defesa Civil. Cada número leva fonte e horário, e o que já aconteceu fica separado da previsão.
2. **Animação que prende** (`motor/`): deck.gl no Chrome sem janela, quadro a quadro, pela GPU (Vulkan, ~0,1 s por quadro). Recursos:
   - municípios coloridos pelo nível do alerta;
   - colunas 3D;
   - timelapse do infravermelho das tempestades;
   - partículas de vento;
   - rios desenhados aos poucos;
   - pinos de cidade;
   - contadores e legenda palavra a palavra.
3. **Avatar** (a fazer): HeyGen com os dados do explicavideo.

## Regras de cada vídeo

- O quadro 0 já vem cheio: data **dd/mm/aaaa** e a manchete viral com o número mais forte que tenha fonte (ex.: "ATÉ 300 MM").
- Só números com fonte, e a fonte aparece na tela.
- A fala é no tom do Nei: direta, com "tu", pergunta ao espectador ("pra onde tu vai?"), preparação prática e o fecho no inema.club.

## Uso (uma edição)

```bash
geo/baixar.sh && python3 motor/prep_geo.py                       # base geográfica (1 vez)
E=edicoes/2026-10-09-alerta-sul
python3 coleta/inmet_avisos.py $E                                 # alertas por município
python3 coleta/satelite_gibs.py $E --base 2026-10-08T18:00 --de 2026-10-08T12:00 --ate 2026-10-09T05:00
python3 coleta/openmeteo.py $E --dia 2026-10-09                   # chuva 7 dias + vento
# escreva $E/falas.json (as falas) e $E/base.md (a pesquisa)
python3 $E/narrar.py                                              # voz do Nei, conferida por transcrição
python3 $E/gerar_cena.py                                          # linha do tempo → cena.js
node motor/render.mjs $E --quadros 0,10,30                        # prévia de quadros
motor/montar.sh $E $E/video.mp4                                   # vídeo final
```

A voz usa o motor do [cardshorts](https://github.com/inematds/cardshorts) (Chatterbox + Whisper locais).

## Edições

| Data | Edição | O que mostra |
|---|---|---|
| 09/10/2026 | `edicoes/2026-10-09-alerta-sul` | 529 cidades em vermelho (INMET), rajada de 109 km/h, 113 mm em São Borja, mapa do fim de semana, até 204 mm em 7 dias (Open-Meteo) |

Licença MIT. Dados de terceiros seguem as licenças das fontes (INMET, NASA/NOAA, Open-Meteo, IBGE, Natural Earth).
