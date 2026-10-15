# Handoffs — trabalhos abertos

Cada linha é um assunto em andamento: leia o snapshot do assunto que for continuar. Gravado por handoff-grava.py.

<!-- handoff-indice:inicio -->
- `itaipu-ruptura` · handoffs/history/2026-10-15T120855Z-itaipu-ruptura.md · 15/10 09:08
- `previsao-do-dia` · handoffs/history/2026-10-15T100300Z-previsao-do-dia.md · 15/10 07:03
- `clima24h-2026-10-15` · handoffs/history/2026-10-15T095957Z-clima24h-2026-10-15.md · 15/10 06:59
<!-- handoff-indice:fim -->

---

Cópia integral do snapshot mais recente (handoffs/history/2026-10-15T120855Z-itaipu-ruptura.md):

# Handoff — 2026-10-15 — E se Itaipu rompesse? 16:9 com avatar → lives10 + bot v3

## Projeto e escopo
~/projetos/eventosextremospub. Nei pediu vídeo a partir do PDF Estudo_Risco_Rompimento_Itaipu.pdf: chamada viral, impacto, onde estão os riscos, chuva atual × 2024 e previsões; publicar no lives10 e mandar no bot.

## Objetivo atual
video-avatar.mp4 publicado no lives10, link no inemaytbot, arquivo 720p no bot v3. Pronto = linha "fim" em edicoes/2026-10-15-itaipu/AVATAR-STATUS.txt com "publicado no lives10".

## Estado aceito
- [confirmed] pesquisa (web.md, coletar.py, bruto/grade.json, resumo.txt), falas.json (11 falas, ~250 s), gerar_cena.py, 6 imagens Codex em capa/ — edicoes/2026-10-15-itaipu/
- [confirmed] prévia de quadros conferida (colunas de chuva, pinos, gráficos, capa) com tempos ESTIMADOS (estimar.py)
- [confirmed] commit 2c43bfd + push

## Proposto / tentado, não confirmado
- [?] avatar no estúdio HeyGen enviado 11:54 (EVX-itaipu-ruptura); download e retempo pendentes

## Decisões e restrições
- Formato 16:9 largo com avatar (molde queimadas-amazonia); GEO=geo.js (Sul) e DISPLAY=:99 (sem DISPLAY o render trava)
- Estudo tratado como hipotético; sem mancha de inundação desenhada; GloFAS não usado na tela

## Arquivos alterados
- `edicoes/2026-10-15-itaipu/*` — edição nova

## Memória e regras duráveis tocadas
- nenhuma

## Verificação
- Rodado: `python3 gerar_cena.py` → cena.js ok, 249,7 s; `node motor/render.mjs <ed> --quadros ...` com DISPLAY=:99 → quadros ok
- Não rodado: compor com avatar, LUFS, publicação — esperando avatar

## Estado em execução
- systemd user units: `itaipu-avatar` (auto/avatar.sh: estúdio + download + retempo), `itaipu-publica` (avatar-e-publica.sh: espera itaipu-avatar, gerar_cena --avatar, compor, LUFS, yt-pubx lives10, inemaytbot, bot v3). Parar: `systemctl --user stop <unit>`

## Perguntas abertas e adiados
- nenhuma

## Próxima ação exata
Acompanhar AVATAR-STATUS.txt; ao "fim", conferir quadros do video-avatar.mp4, commit da edição e avisar "Terminei:"/"Falhou:". Se falhar compor, retomar com PULA_RENDER=1 como na queimadas.

## Mapa de retomada
- `edicoes/2026-10-15-itaipu/AVATAR-STATUS.txt`
- `edicoes/2026-10-15-itaipu/avatar-e-publica.sh`
- `edicoes/2026-10-15-itaipu/base.md`

## Checagem de compartilhamento
- Sem segredos, tokens ou dados pessoais: sim
