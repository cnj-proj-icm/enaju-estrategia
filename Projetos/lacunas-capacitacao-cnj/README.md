# Lacunas de Capacitacao em Producoes do CNJ

Projeto de pesquisa aplicada para construir um corpus rastreavel das producoes do
portal de Pesquisas Judiciarias do CNJ e localizar evidencias textuais de lacunas
de capacitacao no Poder Judiciario.

## Estado atual

**Status:** pipeline implementado; linha de base preliminar gerada.

O pipeline automatizado foi executado para a linha de base
`baseline-2026-05-31`. Os resultados atuais sao preliminares: a fila de
curadoria humana ainda precisa ser revisada, auditada e importada antes de
qualquer uso institucional.

> **Acao imediata:** abrir
> [`ALERTA_PROXIMOS_PASSOS.md`](ALERTA_PROXIMOS_PASSOS.md) e iniciar a validacao
> por clique no checklist local.

## Pergunta orientadora

Quais lacunas de capacitacao, necessidades formativas e problemas
organizacionais com possivel traducao em competencias aparecem nas producoes do
CNJ publicadas desde 2022?

## Fonte prioritaria

- Portal oficial: <https://www.cnj.jus.br/pesquisas-judiciarias/>
- Secao prioritaria: `Producao Interna`
- Janela inicial: de `2022-01-01` ate a data de cada execucao

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
5. Submeter os achados automatizados a validacao humana antes de qualquer
   conclusao institucional.

## Produtos esperados

- `data/processed/catalogo_pdfs.csv`
- `data/processed/relacoes_documentos.csv`
- `data/processed/extracao_status.csv`
- `data/processed/corpus_documentos.csv`
- `data/processed/trechos_gaps.csv`
- `outputs/resumo_por_documento.csv`
- `outputs/resumo_por_eixo.csv`
- `outputs/relatorio_validacao.md`

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

## Proximo marco

Executar a curadoria descrita em
[`docs/06_GUIA_CURADORIA.md`](docs/06_GUIA_CURADORIA.md), importar as decisoes e
gerar a sintese executiva final.
