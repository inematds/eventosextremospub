# Falhas

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 10/10/2026 | download do avatar do clima 24h desistiu após 2 h com o HeyGen em 0% (fila cheia de outras sessões) | esperar até 4 h (`--minutos 240`) no clima diário | infra |
| 09/10/2026 | drawtext do ffmpeg local corta 1 letra do fim por caractere acentuado ("PRÉVIA" saía "PRÉVI") | pôr 1 espaço no fim do texto por letra acentuada | infra |
| 09/10/2026 | Whisper troca "El Niño" por "o ninho" e "40199" por "40 .199" nas legendas | legenda alinhada ao roteiro (`roteiro()` no gerar_cena do El Niño, campo `legenda` no falas.json) | infra |
