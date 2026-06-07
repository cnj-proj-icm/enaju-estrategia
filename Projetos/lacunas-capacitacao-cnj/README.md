# Lacunas de Capacitacao em Producoes do CNJ

Projeto de pesquisa aplicada para construir um corpus rastreavel das producoes do
portal de Pesquisas Judiciarias do CNJ e localizar evidencias textuais de lacunas
de capacitacao no Poder Judiciario.

## Estado atual

**Status:** pipeline implementado; linha de base preliminar gerada; expansao
metodologica CNJ integrada com descoberta multibase, corpus HTML/PDF e
priorizacao por tipo de fonte.

O pipeline automatizado foi executado para a linha de base
`baseline-2026-05-31`. Os resultados atuais sao preliminares: a fila de
curadoria humana ainda precisa ser revisada, auditada e importada antes de
qualquer uso institucional.

> **Acao imediata:** revisar a amostra de calibracao no checklist local,
> importar o CSV preenchido quando houver decisao humana e regenerar a
> priorizacao.

## Pergunta orientadora

Quais lacunas de capacitacao, necessidades formativas e problemas
organizacionais com possivel traducao em competencias aparecem nas producoes do
CNJ publicadas desde 2022?

## Fonte prioritaria

- Portal oficial: <https://www.cnj.jus.br/pesquisas-judiciarias/>
- Secao prioritaria: `Producao Interna`
- Janela inicial: de `2022-01-01` ate a data de cada execucao

## Fontes expandidas

A expansao metodologica usa janela `2021-2026` e varre fontes CNJ adicionais:

- atos normativos, resolucoes, portarias, provimentos e recomendacoes;
- programas, acoes, publicacoes, manuais, guias e cartilhas;
- ENAJU/CEAJUD, Justica 4.0, PDPJ, Justica em Numeros e relatorios anuais;
- Biblioteca Digital CNJ e noticias institucionais como evidencia contextual.

## Mapa da pasta

| Local | Conteudo |
| --- | --- |
| [ficha-projeto.md](ficha-projeto.md) | Registro institucional, entregaveis e riscos |
| [ALERTA_PROXIMOS_PASSOS.md](ALERTA_PROXIMOS_PASSOS.md) | Sequencia operacional imediata para concluir a validacao |
| [docs/01_PROTOCOLO_PESQUISA.md](docs/01_PROTOCOLO_PESQUISA.md) | Pergunta, recorte, criterios e regras analiticas |
| [docs/02_ARQUITETURA_PIPELINE.md](docs/02_ARQUITETURA_PIPELINE.md) | Desenho modular da automacao |
| [docs/03_DICIONARIO_DADOS.md](docs/03_DICIONARIO_DADOS.md) | Schemas dos arquivos produzidos |
| [docs/04_VALIDACAO_QUALIDADE.md](docs/04_VALIDACAO_QUALIDADE.md) | Testes, amostragem e criterios de aceite |
| [docs/05_PLANO_EXECUCAO.md](docs/05_PLANO_EXECUCAO.md) | Fases de implementacao e marcos |
| [docs/06_GUIA_CURADORIA.md](docs/06_GUIA_CURADORIA.md) | Passo a passo da revisao humana |
| [docs/07_PROPOSTA_METODOLOGIA_AUTOMATIZADA.md](docs/07_PROPOSTA_METODOLOGIA_AUTOMATIZADA.md) | Alternativa de priorizacao automatizada e evidenciada |
| [config/pipeline.yml](config/pipeline.yml) | Parametros operacionais da coleta e extracao |
| [config/criterios_analiticos.yml](config/criterios_analiticos.yml) | Termos, eixos e score inicial |
| [src/README.md](src/README.md) | Contrato dos modulos a implementar |

## Estrutura prevista

```text
lacunas-capacitacao-cnj/
|-- config/
|-- data/
|   |-- raw_html/
|   |-- raw_pdf/
|   |-- text/
|   |   |-- raw/
|   |   `-- clean/
|   |-- processed/
|   `-- logs/
|-- docs/
|-- notebooks/
|-- outputs/
|-- src/
|-- requirements.in
`-- requirements-ocr.in
```

## Principios

1. Preservar a fonte original e registrar a proveniencia de cada evidencia.
2. Separar coleta, extracao, limpeza, deteccao e consolidacao.
3. Nao interpretar toda mencao a capacitacao como lacuna.
4. Manter sumarios, traducoes e duplicatas no catalogo, mesmo quando nao entram
   no corpus principal.
5. Priorizar lacunas por evidencia, consistencia e valor institucional, usando
   calibracao amostral para estimar risco e revisao pontual em casos de alto
   impacto.

## Produtos esperados

- `data/processed/catalogo_pdfs.csv`
- `data/processed/relacoes_documentos.csv`
- `data/processed/extracao_status.csv`
- `data/processed/corpus_documentos.csv`
- `data/processed/trechos_gaps.csv`
- `outputs/resumo_por_documento.csv`
- `outputs/resumo_por_eixo.csv`
- `outputs/relatorio_validacao.md`
- `outputs/relatorio_publicavel.md`
- `outputs/matriz_lacunas_priorizadas.csv`
- `outputs/matriz_lacunas_por_tipo_fonte.csv`
- `outputs/matriz_normativos_competencias.csv`
- `outputs/mapa_oferta_vs_lacuna.csv`
- `outputs/dossie_evidencias.csv`
- `outputs/trilhas_capacitacoes_evidencias.csv`
- `outputs/portfolio_publicacao.md`
- `outputs/publicacao_final.md`
- `outputs/publicacao_final.docx`

## Execucao local

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe src\run_pipeline.py --step all-preliminary
```

Para retomar etapas isoladas:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py --step snapshot
.\.venv\Scripts\python.exe src\run_pipeline.py --step catalog
.\.venv\Scripts\python.exe src\run_pipeline.py --step corpus
.\.venv\Scripts\python.exe src\run_pipeline.py --step detect
.\.venv\Scripts\python.exe src\run_pipeline.py --step checklist
.\.venv\Scripts\python.exe src\run_pipeline.py --step prioritize
.\.venv\Scripts\python.exe src\run_pipeline.py --step outputs
```

Para ampliar o universo documental:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py --step discover-sources
.\.venv\Scripts\python.exe src\run_pipeline.py --step expanded-corpus
.\.venv\Scripts\python.exe src\run_pipeline.py --step detect
.\.venv\Scripts\python.exe src\run_pipeline.py --step prioritize
.\.venv\Scripts\python.exe src\run_pipeline.py --step outputs
```

Para importar a calibracao amostral preenchida:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py `
  --step import-calibration `
  --review-file data\processed\amostra_calibracao_preenchida.csv
.\.venv\Scripts\python.exe src\run_pipeline.py --step prioritize
.\.venv\Scripts\python.exe src\run_pipeline.py --step outputs
```

Para revisar por clique, sem abrir CSV:

```powershell
start outputs\checklist_validacao.html
```

## Estado da linha de base

| Indicador | Resultado preliminar |
| --- | --- |
| Snapshot editorial | `2026-05-31` |
| PDFs catalogados | `146` |
| PDFs na janela `2022-2026` | `52` |
| Downloads provisoriamente aprovados | `36` |
| PDFs unicos processados | `35` |
| Duplicatas por SHA-256 | `1` |
| Segmentos | `25.011` |
| Trechos candidatos | `2.826` |
| Itens na fila de revisao | `1.807` |

## Estado do corpus expandido

| Indicador | Resultado do piloto expandido |
| --- | --- |
| Fontes/links catalogados | `57` |
| Atos normativos identificados | `40` |
| Documentos no corpus expandido | `84` |
| Documentos HTML expandidos | `49` |
| Trechos candidatos expandidos | `3.100` |

## Proximo marco

Revisar a calibracao amostral descrita em
[`docs/06_GUIA_CURADORIA.md`](docs/06_GUIA_CURADORIA.md), importar as decisoes,
executar `prioritize` e gerar a publicacao final.
