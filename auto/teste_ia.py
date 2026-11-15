import copy, importlib.util, json, unittest
from pathlib import Path
from unittest.mock import patch
import ia_motor as ia
import intervalo
class Teste(unittest.TestCase):
 def test_agente_precisa_ferramentas_nao_api(self):
  d=copy.deepcopy(ia.carregar()); d['etapas']['roteiro_mundo'].update(tipo='api',motor='anthropic',modelo='claude-opus-5-5')
  with self.assertRaisesRegex(ValueError,'exige assinatura'):ia.validar(d)
 def test_claude_e_codex_agente(self):
  c=ia.carregar()['etapas']['roteiro_mundo']; cmd=ia.comando(c,agente=True,saida=Path('/tmp/saida'))
  self.assertIn('--dangerously-bypass-approvals-and-sandbox',cmd)
  c=dict(c,motor='claude',modelo='claude-opus-5-5'); cmd=ia.comando(c,agente=True)
  self.assertIn('bypassPermissions',cmd); self.assertIn('--model',cmd); self.assertIn('--effort',cmd)
 def test_so_conector_correto_e_leitura_na_agenda(self):
  c=ia.carregar()['etapas']['metricool_agenda']
  cmd=ia.comando(c,'mcp__metricool-inematds__getBrandSettings mcp__metricool-inematds__getScheduledPosts',True,Path('/tmp/saida'))
  self.assertIn('read-only',cmd); self.assertIn('mcp_servers.metricool-inematds.enabled=true',cmd)
  self.assertNotIn('createScheduledPost',' '.join(cmd))
 def test_intervalo_por_marca(self):
  self.assertEqual(intervalo.livre(10000,[10000,13600]),17200)
  self.assertEqual(intervalo.livre(10000,[6400]),10000)
 def test_setter_preserva_comentarios_e_outras_etapas(self):
  s=ia.CONFIG.read_text(); novo=ia.alterar_com_comentarios(s,'roteiro_sul',{'esforco':'high'})
  import yaml
  a=yaml.safe_load(s); b=yaml.safe_load(novo)
  self.assertEqual(b['etapas']['roteiro_sul']['esforco'],'high')
  for etapa in a['etapas']:
   if etapa!='roteiro_sul':self.assertEqual(a['etapas'][etapa],b['etapas'][etapa])
  self.assertEqual([x for x in s.splitlines() if x.lstrip().startswith('#')],[x for x in novo.splitlines() if x.lstrip().startswith('#')])
if __name__=='__main__':unittest.main()
