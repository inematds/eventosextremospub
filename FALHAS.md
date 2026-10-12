# Falhas

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-10-12 | publicar.sh do Amazônia e o mundo rodado por `systemd-run --user` usou `/usr/bin/codex` (0.116) → "unknown variant `default`" no config.toml, nada publicado e aviso "não publicado" no inemaytbot | serviço systemd com `--setenv=PATH=$PATH` (ou export PATH com ~/.npm-global/bin no script) | infra |
| 11/10/2026 | fala com "tu/teu" ("Tua cidade") e CTA "Segue o canal" (o Nei quer só inema.club) | roteiro.md pede "você" e CTA só inema.club; rodar.sh reprova tu/segue o canal antes do avatar | prompt |
| 10/10/2026 | voz do Chatterbox repetiu o fim da fala ("Medianeira, quase 90. Oco, quase 90.") e a conferência por transcrição do cardshorts aceitou; vista larga do Brasil (zoom 3,75) mostrava a borda do satélite | refazer só a fala com texto levemente mudado ("E Medianeira teve quase noventa"); conferir no narrar.log se a transcrição tem palavra a mais; BR com zoom ≥4,2 centrado em -54,5 e pitch 0 | infra (TTS) + prompt (câmera) |
| 10/10/2026 | download do avatar do clima 24h desistiu após 2 h com o HeyGen em 0% (fila cheia de outras sessões) | esperar até 4 h (`--minutos 240`) no clima diário | infra |
| 09/10/2026 | drawtext do ffmpeg local corta 1 letra do fim por caractere acentuado ("PRÉVIA" saía "PRÉVI") | pôr 1 espaço no fim do texto por letra acentuada | infra |
| 09/10/2026 | Whisper troca "El Niño" por "o ninho" e "40199" por "40 .199" nas legendas | legenda alinhada ao roteiro (`roteiro()` no gerar_cena do El Niño, campo `legenda` no falas.json) | infra |
