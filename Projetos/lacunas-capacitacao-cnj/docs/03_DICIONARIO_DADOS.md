# Dicionario de Dados

## 1. Convencoes

- CSV em `utf-8-sig` para facilitar abertura local.
- Parquet para processamento e preservacao de tipos.
- Datas em ISO `YYYY-MM-DD`.
- Campos booleanos como `true` e `false`.
- Listas serializadas como JSON quando armazenadas em CSV.
- Todas as tabelas rastreaveis registram `run_id` e `as_of`.
- Tabelas analiticas registram `snapshot_sha256` e `versao_criterios`.

## 2. `catalogo_pdfs.csv`

Catalogo mestre. Inclui documentos mantidos, excluidos e pendentes.

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `doc_id` | string | Identificador estavel do registro |
| `url` | string | URL encontrada |
| `url_normalizada` | string | URL usada para deduplicacao |
| `nome_arquivo` | string | Nome inferido da URL |
| `texto_ancora` | string | Rotulo visivel associado ao link |
| `secao_portal` | string | Secao ou contexto DOM |
| `titulo_inferido` | string | Titulo documental normalizado |
| `categoria_inferida` | string | Categoria do portal ou inferida |
| `ano_url` | integer | Ano extraido da URL |
| `ano_documento` | integer | Ano indicado no titulo ou metadado |
| `ano_referencia` | integer | Ano tematico ou ano-base, se aplicavel |
| `idioma_inferido` | string | `pt`, `en`, `es` ou `indeterminado` |
| `tipo_documento` | string | `relatorio`, `diagnostico`, `pesquisa`, `sumario`, `apresentacao` ou `outro` |
| `familia_documental_id` | string | Grupo de versoes relacionadas |
| `status_corpus` | string | `incluir`, `excluir` ou `revisar` |
| `motivo_status` | string | Regra ou justificativa |
| `ocorrencias_html` | integer | Quantidade de aparicoes da URL na pagina |
| `coletado_em` | datetime | Momento da coleta |

## 3. `relacoes_documentos.csv`

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `doc_id_origem` | string | Documento relacionado |
| `doc_id_destino` | string | Documento principal ou comparado |
| `tipo_relacao` | string | `traducao_de`, `sumario_de`, `apresentacao_de`, `duplicata_de` ou `recurso_de` |
| `metodo` | string | `regra_exata`, `hash`, `similaridade_titulo` ou `revisao_humana` |
| `confianca` | float | Confianca entre `0` e `1` |
| `revisado_humano` | boolean | Confirmacao manual |

## 4. `download_status.csv`

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `doc_id` | string | Documento |
| `arquivo_pdf` | string | Caminho local |
| `http_status` | integer | Codigo HTTP |
| `content_type` | string | Tipo retornado |
| `bytes` | integer | Tamanho |
| `sha256` | string | Hash do arquivo |
| `status_download` | string | `sucesso`, `falha` ou `ignorado` |
| `erro` | string | Detalhe da falha |
| `baixado_em` | datetime | Momento do download |

## 5. `extracao_status.csv`

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `doc_id` | string | Documento |
| `metodo_extracao` | string | `pymupdf`, `pdfplumber`, `ocr` ou `falha` |
| `paginas_total` | integer | Total de paginas |
| `paginas_com_texto` | integer | Paginas com texto suficiente |
| `caracteres_extraidos` | integer | Total de caracteres |
| `arquivo_txt_raw` | string | Caminho do texto bruto |
| `arquivo_txt_clean` | string | Caminho do texto limpo |
| `status_extracao` | string | `sucesso`, `parcial`, `ocr_pendente` ou `falha` |
| `erro` | string | Detalhe da falha |

## 6. `corpus_documentos.csv`

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `doc_id` | string | Documento |
| `titulo` | string | Titulo para exibicao |
| `ano` | integer | Ano documental validado |
| `url` | string | Fonte |
| `tipo_documento` | string | Tipo |
| `categoria` | string | Categoria |
| `idioma` | string | Idioma |
| `sha256` | string | Hash |
| `arquivo_txt_clean` | string | Caminho do texto limpo |
| `paginas_total` | integer | Total de paginas |
| `incluido_em` | datetime | Momento da consolidacao |

## 7. `trechos_gaps.csv`

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `evidencia_id` | string | Identificador do candidato |
| `doc_id` | string | Documento |
| `titulo` | string | Titulo |
| `ano` | integer | Ano documental |
| `url` | string | Fonte |
| `pagina` | integer | Pagina inicial |
| `tipo_segmento` | string | `pagina`, `paragrafo` ou `janela` |
| `trecho` | string | Texto original |
| `termos_encontrados` | json | Termos acionados |
| `grupos_encontrados` | json | Grupos acionados |
| `eixos` | json | Um ou mais eixos |
| `tipo_gap` | string | `explicito`, `implicito` ou `potencial` |
| `hipotese_competencia` | string | Traducao preliminar para linguagem de competencia |
| `score` | integer | Score de priorizacao |
| `status_revisao` | string | `pendente`, `confirmado`, `ajustado` ou `descartado` |
| `nota_revisor` | string | Justificativa humana |
| `versao_criterios` | string | Versao da configuracao |

## 8. Resumos

`resumo_por_documento.csv` agrega quantidade de candidatos e evidencias
confirmadas por documento. `resumo_por_eixo.csv` agrega por eixo, tipo de gap e
status de revisao. Os resumos finais nao devem misturar candidatos pendentes com
evidencias confirmadas.

## 9. Filas de curadoria

`fila_curadoria_catalogo.csv` contem divergencias temporais, traducoes, sumarios,
apresentacoes e tipos documentais ambiguos dentro da janela de pesquisa.

`fila_revisao.csv` contem evidencias candidatas com os campos adicionais:

| Campo | Uso |
| --- | --- |
| `decisao_revisor` | `confirmado`, `ajustado`, `descartado` ou `pendente` |
| `tipo_gap_revisado` | Tipo validado quando houver ajuste |
| `eixos_revisados` | Lista JSON ou valores separados por `;` |
| `hipotese_competencia_revisada` | Redacao validada |
| `uso_relatorio` | Indica selecao para citacao |
| `nota_revisor` | Justificativa |
| `revisor_id` e `data_revisao` | Responsabilidade e data |
| `auditoria_status` | `aprovado`, `nao_selecionado` ou `pendente` |
| `conciliacao_status` | `conciliado`, `nao_necessaria` ou `pendente` |
