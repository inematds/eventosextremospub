"""Recupera lacunas internas do Whisper com contexto anterior, sem inventar palavras."""
from pathlib import Path
import subprocess


def maior_buraco(pal):
    return max((b['start']-a['end'] for a,b in zip(pal,pal[1:])), default=0)


def recuperar(wav, pal, tdir, transcrever, buraco=8.0):
    for tentativa in range(3):
        i=next((k for k in range(len(pal)-1) if pal[k+1]['start']-pal[k]['end']>buraco),None)
        if i is None: return pal
        # Recortar exatamente no buraco repetia a omissão. Incluir fala anterior dá contexto.
        alvo=max(0,pal[i]['end']-15*(tentativa+1))
        inicio=next((k for k,p in enumerate(pal) if p['start']>=alvo),0)
        ini=pal[inicio]['start']
        pasta=Path(tdir);pasta.mkdir(parents=True,exist_ok=True)
        tr=pasta/f'contexto-{tentativa}-{ini:.2f}.wav'
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(ini),'-i',str(wav),str(tr)],check=True)
        novo=transcrever(tr,pasta/f'contexto-{tentativa}',palavras=True)
        if not novo: continue
        candidato=pal[:inicio]+[{**p,'start':p['start']+ini,'end':p['end']+ini} for p in novo]
        # Não substituir um trecho bom por transcrição com lacuna igual ou maior.
        if maior_buraco(candidato)<maior_buraco(pal): pal=candidato
    return pal
