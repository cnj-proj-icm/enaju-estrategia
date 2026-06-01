# Ficha de Projeto - Lacunas de Capacitacao em Producoes do CNJ

## Identificacao

| Campo | Preencher |
| --- | --- |
| Nome do projeto | Lacunas de Capacitacao em Producoes do CNJ |
| Eixo | Pesquisa aplicada / Inteligencia educacional / Dados |
| Responsavel | A definir |
| Pessoas envolvidas | A definir |
| Status | Planejado |
| Data de inicio | 2026-05-31 |
| Proximo marco | Implementar o catalogo piloto de PDFs e validar o recorte |

## Problema

As producoes do CNJ registram diagnosticos, dificuldades, assimetrias e
recomendacoes relevantes para o planejamento educacional. Essas evidencias
estao dispersas em PDFs e ainda nao formam um corpus estruturado que permita
identificar lacunas de capacitacao de modo rastreavel.

## Objetivo

Construir um pipeline local e reproduzivel para coletar PDFs do portal de
Pesquisas Judiciarias do CNJ, extrair texto, localizar evidencias de lacunas
formativas e consolidar os achados em tabelas adequadas para revisao humana e
analise institucional.

## Publico-alvo

- ENAJU
- escolas judiciais e escolas de servidores
- unidades de gestao de pessoas
- unidades de inovacao, dados e tecnologia
- equipes responsaveis por politicas judiciarias

## Entregaveis

| Entregavel | Formato | Pasta de destino | Status |
| --- | --- | --- | --- |
| Desenho metodologico | Markdown | `docs/` | Concluido |
| Arquitetura do pipeline | Markdown e YAML | `docs/` e `config/` | Concluido |
| Catalogo rastreavel de PDFs | CSV | `data/processed/` | Pendente |
| Corpus textual limpo | TXT, CSV e Parquet | `data/text/` e `data/processed/` | Pendente |
| Dataset de evidencias | CSV e Parquet | `data/processed/` | Pendente |
| Resumos analiticos | CSV e Markdown | `outputs/` | Pendente |
| Relatorio de validacao | Markdown | `outputs/` | Pendente |

## Insumos

| Insumo | Local | Observacao |
| --- | --- | --- |
| Portal Pesquisas Judiciarias | `https://www.cnj.jus.br/pesquisas-judiciarias/` | Fonte oficial prioritaria |
| Briefing inicial | Conversa de criacao do projeto | Incorporado ao desenho em 2026-05-31 |
| Taxonomia inicial | `config/criterios_analiticos.yml` | Deve ser calibrada no piloto |

## Plano de Trabalho

| Etapa | Descricao | Responsavel | Prazo | Status |
| --- | --- | --- | --- | --- |
| 1 | Aprovar desenho e criterios do piloto | A definir | A definir | Pendente |
| 2 | Implementar coleta e catalogo | A definir | A definir | Pendente |
| 3 | Validar inclusoes, exclusoes e relacoes documentais | A definir | A definir | Pendente |
| 4 | Baixar PDFs e extrair texto | A definir | A definir | Pendente |
| 5 | Limpar, segmentar e detectar candidatos | A definir | A definir | Pendente |
| 6 | Validar amostra e calibrar regras | A definir | A definir | Pendente |
| 7 | Gerar datasets e sinteses | A definir | A definir | Pendente |

## Decisoes

| Data | Decisao | Motivo |
| --- | --- | --- |
| 2026-05-31 | Criar o projeto em `Projetos/lacunas-capacitacao-cnj/` | A iniciativa ainda esta em estruturacao |
| 2026-05-31 | Registrar `ano_url` e `ano_documento` separadamente | A pasta de upload pode divergir do ano informado no titulo |
| 2026-05-31 | Preservar documentos excluidos no catalogo | Garantir auditoria de traducoes, sumarios e duplicatas |

## Riscos e Pendencias

| Item | Impacto | Encaminhamento |
| --- | --- | --- |
| Mudancas na estrutura HTML do portal | Pode interromper a coleta | Salvar HTML bruto e testar seletores |
| Ano de upload diferente do ano do documento | Pode distorcer o recorte | Registrar ambos e revisar divergencias |
| PDFs digitalizados ou corrompidos | Pode reduzir cobertura textual | Registrar falha e aplicar OCR somente por excecao |
| Falsos positivos por palavras isoladas | Pode inflar achados | Aplicar regras de tipo de gap e validacao humana |
| Responsavel ainda nao definido | Pode atrasar o piloto | Designar responsavel antes da implementacao |
