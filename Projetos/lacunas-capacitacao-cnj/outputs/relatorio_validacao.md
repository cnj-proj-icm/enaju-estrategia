# Relatório de Validação

## Status

**PROPOSTA TÉCNICA - priorização automatizada com amostra de calibração estruturada**

## Linha de base

- `run_id`: `baseline-2026-05-31`
- data de corte editorial: `2026-05-31`
- fonte analítica usada nos outputs: `evidencias_priorizadas`
- documentos no corpus processado: `84`
- evidências consideradas: `3100 evidências únicas em 5034 linhas evidência-eixo`

## Calibração amostral

Arquivo de calibração analítica existe, mas não contém decisões revisadas.

- decisões revisadas: `0`
- pendências registradas: `130`
- taxa de falso positivo estimada: ``

## Alertas de risco

- 1550 trechos apresentam score textual bruto baixo (< 3); devem ser lidos como hipóteses técnicas.
- 7 evidências repetem o mesmo documento e trecho; a síntese consolida a mensagem para reduzir duplicidade.
- 1792 evidências foram classificadas como potenciais; elas apoiam recomendações, mas não constituem conclusões institucionais isoladas.
- O score textual bruto usa escala própria de detecção lexical; o score final é normalizado entre 0 e 1 após ponderação por consistência evidencial e valor institucional.

## Critérios de aceite

- snapshot e hash registrados em `data/processed/manifest_run.json`;
- PDFs, textos e segmentos rastreáveis por `doc_id`;
- classificação automática identificada pela versão dos critérios;
- score composto documentado em `config/criterios_analiticos.yml`;
- resultados apresentados como proposta técnica, não como deliberação institucional final.
