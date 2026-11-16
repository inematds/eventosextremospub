# Pesquisa do Clima no Mundo — cobertura e confirmação

Antes de concluir que não há eventos suficientes, execute esta sequência. Não
reduza o piso de impacto, não some episódios independentes e não invente fatos
para preencher a edição. A lista de ontem é uma pista, nunca o limite da busca.

1. **Descoberta ampla:** consulte separadamente seis regiões: Américas; Europa;
   África; Oriente Médio; Sul/Sudeste/Leste da Ásia; Oceania. Combine datas da
   janela e termos como flood, drought, cyclone, heatwave, wildfire, record,
   displaced, affected, inundaciones, sequía, enchentes e recorde. Procure também
   boletins de desastres e balanços de eventos em andamento. Abra páginas oficiais
   (não apenas os resultados indexados) de GDACS, ReliefWeb/OCHA, WMO, ECHO,
   IFRC, FAO e agências nacionais de meteorologia e defesa civil. Leitura pública
   de páginas/RSS é permitida; isso não autoriza APIs novas.
2. **Confirmação dirigida:** para cada candidato perto do piso, busque o nome do
   lugar + evento + órgão responsável + data. Siga a referência de uma notícia
   até o boletim original e tente a página do órgão local se o buscador não achar
   ReliefWeb. Não encerre só porque uma URL bloqueou: procure o título exato,
   a publicação original ou uma reprodução com autoria identificada. Registre o
   bloqueio e continue nas outras regiões.
3. **Fontes locais:** emissoras públicas nacionais (por exemplo ABC Austrália e
   CBC Canadá) e agências nacionais de notícias (por exemplo ANTARA) também
   podem fornecer pistas e confirmação quando identificam órgão, porta-voz,
   local e data. Abra o material e confronte o dado com boletim/série oficial
   ou uma segunda fonte editorial independente. Não exclua um fato apenas
   porque o nome do veículo não constava dos exemplos do prompt. Agregadores,
   sátira, fóruns e páginas sem autoria nunca confirmam um número para o vídeo.
4. **Comparação correta:** em recordes, confirme estação, duração, mês/ano e
   período da série. A tabela que já inclui o recorde novo não demonstra o valor
   anterior. Procure boletim do mês anterior, série histórica do mesmo posto ou
   relatório oficial que cite a marca superada. Não misture postos ou séries.
5. **Eventos em andamento:** um desastre iniciado antes da janela pode entrar
   se houver balanço oficial ou atualização factual na semana e evidência de que
   continua ativo. Diga o período acumulado e a data do balanço na fala. Uma
   página republicada sem dado novo não renova um desastre encerrado. Pessoas
   em risco não equivalem a atingidos; atendimentos não equivalem a pessoas.
6. **Auditoria antes de desistir:** grave `pesquisa/cobertura.md` com uma linha
   por região: buscas realizadas, páginas abertas, candidatos, confirmação ou
   motivo de exclusão. Grave `pesquisa/candidatos.json` como lista de objetos
   com local, evento, data_evento, data_balanco, numero, unidade, periodo,
   urls, elegivel e motivo. Cada região deve ter busca e leitura documentadas,
   mesmo se não houver candidato. Reexamine os candidatos pendentes em uma
   segunda passagem dirigida antes de escrever ERRO.txt. Se só dois eventos
   forem confirmados após isso, registre o limite honestamente e não produza
   uma seleção artificial de cinco.

Priorize o que mudou nas últimas 48 horas. Não reaproveite capa ou abertura de
ontem quando houver fato novo. O registro deve permitir distinguir falta de
eventos elegíveis de falta de acesso a fontes ou pesquisa incompleta.
