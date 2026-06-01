# Contrato dos Modulos

Esta pasta contem a implementacao Python do pipeline reproduzivel.

| Arquivo | Papel |
| --- | --- |
| `run_pipeline.py` | Orquestracao e retomada |
| `pipeline/snapshot.py` | Snapshot HTML e metadados da fonte |
| `pipeline/catalog.py` | Cards editoriais, recorte e familias documentais |
| `pipeline/corpus.py` | Download, hash, extracao, limpeza e segmentacao |
| `pipeline/detect.py` | Matches, score, eixos, amostra e fila de revisao |
| `pipeline/checklist.py` | Checklist HTML local para curadoria por clique |
| `pipeline/outputs.py` | CSV, Markdown e DOCX executivos |
| `pipeline/common.py` | Configuracao, caminhos, logs, IDs e utilitarios |

Testes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Regras detalhadas:
[`../docs/02_ARQUITETURA_PIPELINE.md`](../docs/02_ARQUITETURA_PIPELINE.md).
