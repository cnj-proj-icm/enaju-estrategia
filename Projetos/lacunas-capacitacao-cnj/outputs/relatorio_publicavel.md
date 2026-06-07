# Relatório Automatizado Publicável - ENAJU/CNJ

## Status executivo

**PROPOSTA TÉCNICA - priorização automatizada com amostra de calibração estruturada**

Este produto organiza uma proposta técnica de priorização de lacunas de capacitação com base em evidências documentais rastreáveis, score composto e alertas de risco. A leitura correta é de apoio à decisão, sem substituir a deliberação institucional da ENAJU ou das escolas judiciais.

## Resumo operacional

- run_id: `baseline-2026-05-31`
- data de corte editorial: `2026-05-31`
- documentos no corpus: `84`
- evidências consideradas: `3100 evidências únicas em 5034 linhas evidência-eixo`
- score textual médio: `3.51`
- score final médio: `0.5689`
- calibração: `calibracao_sem_decisoes`

## Lacunas priorizadas

- Capacitação em dados, tecnologia e inteligência institucional: score final `0.6656`, faixa `media`, 1029 evidências em 46 documentos.
- Capacitação em direitos humanos, inclusão e acessibilidade: score final `0.6411`, faixa `media`, 848 evidências em 48 documentos.
- Capacitação em comunicação e acessibilidade: score final `0.591`, faixa `media`, 320 evidências em 42 documentos.
- Trilha de avaliação, monitoramento e planejamento estratégico: score final `0.5736`, faixa `media`, 699 evidências em 44 documentos.
- Trilha de gestão, governança e liderança: score final `0.5709`, faixa `media`, 394 evidências em 51 documentos.
- Trilha de atendimento e serviços ao cidadão: score final `0.5567`, faixa `media`, 435 evidências em 45 documentos.
- Trilha de inovação e transformação digital: score final `0.5157`, faixa `media`, 484 evidências em 27 documentos.
- Capacitação em saúde e bem-estar institucional: score final `0.4448`, faixa `baixa`, 214 evidências em 31 documentos.
- Trilha de formação de lideranças: score final `0.4443`, faixa `baixa`, 92 evidências em 25 documentos.
- Capacitação para estruturação e atuação de equipes multidisciplinares: score final `0.4367`, faixa `baixa`, 113 evidências em 24 documentos.

## Eixos documentais

- `direitos_humanos_e_inclusao`: 473 evidências em 24 documentos (Producao Interna)
- `avaliacao_e_monitoramento`: 413 evidências em 20 documentos (Producao Interna)
- `dados_e_tecnologia`: 339 evidências em 25 documentos (Producao Interna)
- `nao_classificado`: 229 evidências em 20 documentos (Producao Interna)
- `dados_e_tecnologia`: 228 evidências em 7 documentos (Parcerias Institucionais)
- `inovacao_e_transformacao`: 227 evidências em 5 documentos (Parcerias Institucionais)
- `direitos_humanos_e_inclusao`: 172 evidências em 16 documentos (Producao Interna)
- `atendimento_e_servicos_judiciarios`: 146 evidências em 24 documentos (Producao Interna)
- `dados_e_tecnologia`: 146 evidências em 19 documentos (Producao Interna)
- `inovacao_e_transformacao`: 126 evidências em 4 documentos (Parcerias Institucionais)

## Alertas de risco

- 1550 trechos apresentam score textual bruto baixo (< 3); devem ser lidos como hipóteses técnicas.
- 7 evidências repetem o mesmo documento e trecho; a síntese consolida a mensagem para reduzir duplicidade.
- 1792 evidências foram classificadas como potenciais; elas apoiam recomendações, mas não constituem conclusões institucionais isoladas.
- O score textual bruto usa escala própria de detecção lexical; o score final é normalizado entre 0 e 1 após ponderação por consistência evidencial e valor institucional.

## Recomendação de uso

- Usar como proposta técnica para planejamento de capacitações e trilhas.
- Cruzar os achados com prioridades pedagógicas, capacidade operacional e agenda institucional.
- Registrar qualquer decisão final em ata, parecer ou documento institucional próprio.
