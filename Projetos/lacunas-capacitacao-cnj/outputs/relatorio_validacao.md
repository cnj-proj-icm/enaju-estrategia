# Relatorio de Validacao

## Status

**PROPOSTA TECNICA - priorizacao automatizada com amostra de calibracao estruturada**

## Linha de base

- `run_id`: `baseline-2026-05-31`
- data de corte editorial: `2026-05-31`
- fonte analitica usada nos outputs: `evidencias_priorizadas`
- documentos no corpus processado: `84`
- evidencias consideradas: `3100 evidencias unicas em 5034 linhas evidencia-eixo`

## Calibracao amostral

Arquivo de calibracao analitica existe, mas nao contem decisoes revisadas.

- decisoes revisadas: `0`
- pendencias registradas: `130`
- taxa de falso positivo estimada: ``

## Alertas de risco

- 1550 trechos apresentam score textual baixo (< 3); devem ser lidos como hipoteses tecnicas.
- 7 evidencias repetem o mesmo documento e trecho; a sintese consolida a mensagem para reduzir duplicidade.
- 1792 evidencias foram classificadas como potenciais; elas apoiam recomendacoes, mas nao constituem conclusoes institucionais isoladas.

## Criterios de aceite

- snapshot e hash registrados em `data/processed/manifest_run.json`;
- PDFs, textos e segmentos rastreaveis por `doc_id`;
- classificacao automatica identificada pela versao dos criterios;
- score composto documentado em `config/criterios_analiticos.yml`;
- resultados apresentados como proposta tecnica, nao como deliberacao institucional final.
