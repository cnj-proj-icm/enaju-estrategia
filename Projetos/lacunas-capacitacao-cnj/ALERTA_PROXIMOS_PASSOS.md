# Alerta: Proximos Passos Imediatos

**Acao humana necessaria:** concluir a validacao da linha de base
`baseline-2026-05-31` antes de usar os resultados institucionalmente.

## Comecar agora

Abrir o checklist local:

```powershell
start outputs\checklist_validacao.html
```

O andamento fica salvo automaticamente no navegador. Antes de trocar de
computador ou limpar dados do navegador, clicar em `Baixar backup JSON`.

## Ordem de execucao

### 1. Catalogo: revisar 27 documentos

Na aba `Catalogo`, decidir por clique se cada documento entra ou sai do corpus.
Ao terminar, clicar em `Baixar CSV preenchido`, mover o arquivo para
`data/processed/` e executar:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py `
  --step import-catalog-review `
  --review-file data\processed\fila_curadoria_catalogo_preenchida.csv
.\.venv\Scripts\python.exe src\run_pipeline.py --step corpus
.\.venv\Scripts\python.exe src\run_pipeline.py --step detect
.\.venv\Scripts\python.exe src\run_pipeline.py --step checklist
```

### 2. Calibracao: revisar 130 itens

Na aba `Calibracao`, registrar gaps confirmados, falsos positivos e termos
ausentes. Depois, atualizar `config/criterios_analiticos.yml`, alterar a versao
dos criterios para `1.0.0` e reexecutar:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py --step detect
.\.venv\Scripts\python.exe src\run_pipeline.py --step checklist
```

### 3. Evidencias: revisar 1.807 trechos

Na aba `Evidencias`, o revisor principal confirma, ajusta ou descarta todos os
itens. O segundo revisor audita `20%` da amostra estratificada e todos os
trechos marcados para uso no relatorio.

Ao concluir, clicar em `Baixar CSV preenchido`, mover o arquivo para
`data/processed/` e executar:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py `
  --step import-review `
  --review-file data\processed\fila_revisao_preenchida.csv
.\.venv\Scripts\python.exe src\run_pipeline.py --step outputs
```

## Criterio de encerramento

Publicar a sintese somente depois de importar a fila final, concluir a
auditoria e conciliar divergencias.
