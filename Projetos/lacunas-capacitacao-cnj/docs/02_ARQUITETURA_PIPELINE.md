# Arquitetura do Pipeline

## 1. Visao geral

```mermaid
flowchart LR
    A[Portal CNJ] --> B[Snapshot HTML]
    B --> C[Catalogo de links]
    C --> D[Revisao do recorte]
    D --> E[Download PDFs]
    E --> F[Deduplicacao por hash e familia]
    F --> G[Extracao de texto]
    G --> H[Limpeza]
    H --> I[Segmentacao]
    I --> J[Deteccao e classificacao]
    J --> K[Validacao humana]
    K --> L[Datasets e sinteses]
```

## 2. Modulos planejados

| Modulo | Responsabilidade | Entrada principal | Saida principal |
| --- | --- | --- | --- |
| `pipeline/snapshot.py` | Salvar HTML e metadados da fonte | URL fonte | Snapshot e `manifest_run.json` |
| `pipeline/catalog.py` | Extrair cards, inferir metadados e aplicar regras documentais | Snapshot local | `catalogo_pdfs.csv`, `relacoes_documentos.csv` |
| `pipeline/corpus.py` | Baixar, validar, extrair, limpar e segmentar | Catalogo aprovado | PDFs, TXT, status e `segmentos.parquet` |
| `pipeline/detect.py` | Aplicar termos, score, eixos e hipoteses | Segmentos | Candidatos, amostra e fila de revisao |
| `pipeline/outputs.py` | Consolidar tabelas e resumos | Candidatos ou evidencias confirmadas | Arquivos em `outputs/` |

O orquestrador `src/run_pipeline.py` executa etapas isoladas ou o fluxo
preliminar completo e permite retomada sem baixar novamente artefatos validos.

## 3. Coleta robusta

O scraper deve:

1. salvar um snapshot datado do HTML antes de processar;
2. coletar inicialmente todos os links da pagina;
3. normalizar URLs absolutas e remover fragmentos;
4. preservar texto da ancora, secao, titulo do card e ordem no DOM;
5. identificar PDFs, ZIPs, paineis e paginas relacionadas;
6. deduplicar repeticoes exatas sem perder a contagem de ocorrencias;
7. registrar a regra que incluiu ou excluiu cada item.

O filtro por `/2022/`, `/2023/`, `/2024/`, `/2025/` e `/2026/` e util como
primeiro sinal, mas nao deve apagar registros antes da auditoria. O pipeline
deve manter `ano_url`, `ano_documento` e `ano_referencia` separadamente.

## 4. Identidade documental

Cada PDF deve receber:

- `doc_id` estavel baseado na URL normalizada antes do download;
- `sha256` depois do download;
- `familia_documental_id` para agrupar relatorio, sumario, apresentacao e
  traducoes;
- `status_corpus` com motivo explicito.

A deduplicacao acontece em camadas:

1. URL normalizada;
2. hash identico;
3. familia documental inferida por titulo normalizado, idioma, tipo e
   similaridade aproximada;
4. revisao humana das decisoes nao exatas.

## 5. Extracao e limpeza

Ordem de extracao:

1. `PyMuPDF`;
2. `pdfplumber`;
3. OCR apenas para excecoes registradas.

O TXT bruto nunca deve ser sobrescrito. A limpeza gera outro arquivo, remove
cabecalhos e rodapes repetidos, normaliza espacos, corrige hifenizacao por quebra
de linha e preserva `===PAGE_BREAK===`.

## 6. Segmentacao

Gerar tres visoes complementares:

| Tipo | Uso |
| --- | --- |
| Pagina | Rastreabilidade e citacao |
| Paragrafo | Leitura contextual |
| Janela deslizante | Captura de coocorrencias atravessando quebras artificiais |

Configuracao inicial da janela: `1000` caracteres com sobreposicao de `200`.

## 7. Deteccao e classificacao

A deteccao deve trabalhar sobre uma coluna normalizada, preservando o texto
original para leitura. Termos, pesos, eixos e hipoteses ficam fora do codigo em
[`config/criterios_analiticos.yml`](../config/criterios_analiticos.yml).

Toda classificacao automatica deve registrar:

- versao da configuracao;
- regra acionada;
- termos encontrados;
- score calculado;
- necessidade de revisao humana.

## 8. Logs e retomada

Cada etapa grava log datado em `data/logs/` e tabela de status quando aplicavel.
Falhas devem ser registradas por item, sem interromper todo o lote. Etapas
idempotentes pulam artefatos validos e podem ser reexecutadas com `--force`.

## 9. Contrato de execucao futuro

```powershell
python src/run_pipeline.py --step snapshot --as-of 2026-05-31
python src/run_pipeline.py --step catalog
python src/run_pipeline.py --step corpus
python src/run_pipeline.py --step detect
python src/run_pipeline.py --step outputs
python src/run_pipeline.py --step all-preliminary
```
