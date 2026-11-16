import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from recuperar_transcricao import recuperar

class Teste(unittest.TestCase):
 def test_recupera_omissao_com_contexto_e_preserva_inicio(self):
  pal=[{'word':f'inicio{k}','start':k,'end':k+1} for k in range(44)]+[{'word':'antes','start':44,'end':59},{'word':'fim','start':73,'end':74}]
  novo=[{'word':'antes','start':0,'end':15},{'word':'pergunta','start':15,'end':25},{'word':'fim','start':29,'end':30}]
  with tempfile.TemporaryDirectory() as d,patch('recuperar_transcricao.subprocess.run') as shell:
   r=recuperar('audio.wav',pal,d,lambda *a,**kw:novo)
  self.assertEqual(r[0],pal[0]);self.assertEqual(r[-2]['word'],'pergunta');self.assertEqual(r[-2]['start'],59)
  self.assertEqual(shell.call_args.args[0][5],'44')
 def test_lacuna_igual_nao_substitui_original(self):
  pal=[{'word':'antes','start':0,'end':1},{'word':'fim','start':20,'end':21}]
  with tempfile.TemporaryDirectory() as d,patch('recuperar_transcricao.subprocess.run'):
   r=recuperar('audio.wav',pal,d,lambda *a,**kw:pal)
  self.assertEqual(r,pal)
 def test_sem_lacuna_nao_transcreve(self):
  pal=[{'word':'bom','start':0,'end':1},{'word':'dia','start':1,'end':2}]
  r=recuperar('audio.wav',pal,'nunca-criar',lambda *a,**kw:self.fail('transcreveu'))
  self.assertEqual(r,pal)
if __name__=='__main__':unittest.main()
