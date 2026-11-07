// Lista os últimos vídeos de um perfil do TikTok (o yt-dlp não lista perfil: "Unable to extract secondary user ID").
// Abre o perfil no Chromium sem janela e pega os links /video/<id> da grade; a data vem do próprio id (id >> 32 = segundos unix).
// uso: node auto/tiktok_lista.mjs <handle> [máx]   → linhas "id|aaaa-mm-dd hh:mm (local)|url"
import { chromium } from '../motor/node_modules/playwright/index.mjs';

const handle = (process.argv[2] || 'temponosul').replace(/^@/, '');
const max = Number(process.argv[3] || 30);
const navegador = await chromium.launch({ headless: true, args: ['--disable-blink-features=AutomationControlled'] });
const ctx = await navegador.newContext({
  userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
  locale: 'pt-BR', viewport: { width: 1280, height: 2000 },
});
const pag = await ctx.newPage();
const ids = new Set();
pag.on('response', async (r) => {  // a grade também chega pela chamada item_list da própria página
  if (!r.url().includes('/api/post/item_list')) return;
  try { for (const it of (await r.json()).itemList || []) ids.add(it.id); } catch {}
});
await pag.goto(`https://www.tiktok.com/@${handle}`, { waitUntil: 'domcontentloaded', timeout: 90000 });
for (let i = 0; i < 6 && ids.size < max; i++) {
  await pag.waitForTimeout(4000);
  const hrefs = await pag.$$eval('a[href*="/video/"]', (as) => as.map((a) => a.href));
  for (const h of hrefs) { const m = h.match(/\/video\/(\d{15,})/); if (m) ids.add(m[1]); }
  await pag.mouse.wheel(0, 1800);
}
await navegador.close();
const linhas = [...ids].map((id) => {
  const t = new Date(Number(BigInt(id) >> 32n) * 1000);
  const local = new Date(t.getTime() - t.getTimezoneOffset() * 60000).toISOString().slice(0, 16).replace('T', ' ');
  return { id, t, local };
}).sort((a, b) => b.t - a.t).slice(0, max);
if (!linhas.length) { console.error('nenhum vídeo achado no perfil'); process.exit(1); }
for (const l of linhas) console.log(`${l.id}|${l.local}|https://www.tiktok.com/@${handle}/video/${l.id}`);
