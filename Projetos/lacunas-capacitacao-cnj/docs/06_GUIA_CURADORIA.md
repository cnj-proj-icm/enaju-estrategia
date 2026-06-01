# Guia de Curadoria Humana

## 1. Objetivo

Transformar os resultados automaticos da linha de base `baseline-2026-05-31`
em evidencias confirmadas para uso institucional. A interface recomendada e o
checklist HTML local: as decisoes sao feitas por clique e exportadas como CSV
compativel com o pipeline.

## 2. Abrir o checklist

Gerar ou atualizar o checklist sempre que as filas forem reprocessadas:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py --step checklist
start outputs\checklist_validacao.html
```

O arquivo possui tres abas:

- `Catalogo`: decisao de inclusao ou exclusao dos documentos ambiguos;
- `Calibracao`: validacao da amostra usada para ajustar as regras;
- `Evidencias`: confirmacao, ajuste ou descarte dos trechos candidatos.

O andamento e salvo automaticamente no navegador. Use `Baixar backup JSON`
antes de limpar os dados do navegador ou mudar de computador. Ao terminar cada
aba, use `Baixar CSV preenchido`.

## 3. Curadoria documental

Na aba `Catalogo`, revisar os itens da janela `2022-2026`. Confirmar ou ajustar:

- `status_corpus`: `incluir` ou `excluir`;
- `motivo_status`;
- relacoes entre relatorio completo, sumario, traducao e apresentacao;
- divergencias entre `ano_url` e `ano_documento`.

Baixar `fila_curadoria_catalogo_preenchida.csv`, colocar o arquivo em
`data/processed/` e importar:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py `
  --step import-catalog-review `
  --review-file data\processed\fila_curadoria_catalogo_preenchida.csv
```

Depois, reexecutar `corpus` e `detect`.

## 4. Calibracao analitica

Revisar a aba `Calibracao`, que contem:

- `50` maiores scores;
- `50` candidatos aleatorios;
- `30` segmentos sem match;
- seed reproduzivel `20260531`.

Registrar falsos positivos, termos ausentes e ajustes de taxonomia. Aplicar os
ajustes em `config/criterios_analiticos.yml`, alterar a versao para `1.0.0` e
reexecutar `detect`.

Baixar `amostra_calibracao_preenchida.csv` como registro da calibracao.

## 5. Revisao de evidencias

Na aba `Evidencias`, um revisor principal deve decidir todas as linhas. O
segundo revisor audita amostra estratificada de `20%` e todos os trechos
marcados para uso no relatorio.

Valores aceitos:

| Campo | Valores |
| --- | --- |
| `decisao_revisor` | `confirmado`, `ajustado`, `descartado`, `pendente` |
| `auditoria_status` | `aprovado`, `nao_selecionado`, `pendente` |
| `conciliacao_status` | `conciliado`, `nao_necessaria`, `pendente` |

Baixar `fila_revisao_preenchida.csv`, colocar o arquivo em `data/processed/` e
importar:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py `
  --step import-review `
  --review-file data\processed\fila_revisao_preenchida.csv
```

## 6. Sintese final

Gerar novamente os produtos:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py --step outputs
```

Quando `evidencias_confirmadas.csv` existir, os resumos deixam o modo
preliminar e passam a usar somente evidencias revisadas, auditadas e
conciliadas.
