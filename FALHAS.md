# Falhas

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 09/10/2026 | drawtext do ffmpeg local corta 1 letra do fim por caractere acentuado ("PRÉVIA" saía "PRÉVI") | pôr 1 espaço no fim do texto por letra acentuada | infra |
| 09/10/2026 | Whisper troca "El Niño" por "o ninho" e "40199" por "40 .199" nas legendas | legenda alinhada ao roteiro (`roteiro()` no gerar_cena do El Niño, campo `legenda` no falas.json) | infra |
