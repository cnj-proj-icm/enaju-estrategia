# Plano de Execucao

## 1. Estrategia

Implementar em ciclos curtos. O primeiro resultado util nao e o dataset final,
mas um catalogo auditavel que permita validar o universo documental.

## 2. Fases

| Fase | Resultado | Criterio de conclusao |
| --- | --- | --- |
| 0. Desenho | Protocolo, arquitetura, schemas e configuracao | Documentos revisados |
| 1. Catalogo piloto | Links coletados, classificados e deduplicados por URL | Catalogo revisavel gerado |
| 2. Curadoria documental | Inclusoes, exclusoes e relacoes aprovadas | Catalogo congelado para o ciclo |
| 3. Corpus | PDFs baixados, hashes e TXT gerados | Cobertura e falhas conhecidas |
| 4. Processamento | Texto limpo e segmentos produzidos | Amostra reconstruivel por pagina |
| 5. Deteccao | Candidatos classificados e ordenados | Dataset preliminar gerado |
| 6. Calibracao | Amostra revisada e risco estimado | Versao dos criterios congelada |
| 7. Priorizacao | Score composto e matriz de lacunas | Lacunas ordenadas por evidencia, consistencia e valor |
| 8. Expansao do corpus | Fontes CNJ expandidas, HTML e normativos | Universo documental ampliado e separado por tipo de fonte |
| 9. Sintese publicavel | Publicacao, portfolio e anexos CSV | Entregaveis prontos para leitura institucional |

## 3. Ordem de implementacao

1. Criar ambiente Python e lock de dependencias.
2. Implementar utilitarios de configuracao, logs, caminhos e IDs.
3. Implementar `01_scrape_portal.py`.
4. Implementar `02_classify_catalog.py`.
5. Rodar o catalogo piloto e interromper para curadoria.
6. Implementar download, extracao e limpeza.
7. Implementar segmentacao, deteccao e consolidacao.
8. Criar testes unitarios e um teste integrado com pequena amostra fixa.
9. Implementar importacao de calibracao, priorizacao e publicacao final.
10. Implementar descoberta multibase e corpus expandido.
11. Gerar notebook exploratorio somente depois do dataset preliminar.

## 4. Decisoes antes do piloto

| Decisao | Proposta inicial | Quem valida |
| --- | --- | --- |
| Fonte | Pagina de Pesquisas Judiciarias do CNJ | Responsavel da pesquisa |
| Secao | Priorizar `Producao Interna`, sem apagar demais contextos | Responsavel da pesquisa |
| Janela | Desde 2022 ate a data da execucao | Responsavel da pesquisa |
| Corpus principal | PDFs completos em portugues | Responsavel da pesquisa |
| OCR | Excecao, desabilitado por padrao | Responsavel tecnico |
| Score | Termos distintos no trecho | Equipe de pesquisa apos piloto |
| Validacao | Revisao humana estratificada | Equipe de pesquisa |

## 5. Checklist do primeiro ciclo

- [ ] Designar responsavel.
- [ ] Aprovar o protocolo.
- [ ] Criar ambiente local.
- [ ] Gerar lock de dependencias testado.
- [ ] Implementar coleta.
- [ ] Salvar snapshot HTML.
- [ ] Gerar catalogo piloto.
- [ ] Revisar divergencias de ano.
- [ ] Revisar traducoes, sumarios e apresentacoes.
- [ ] Congelar catalogo do ciclo.
- [ ] Baixar PDFs aprovados.
- [ ] Extrair e limpar textos.
- [ ] Segmentar corpus.
- [ ] Detectar candidatos.
- [ ] Revisar amostra.
- [ ] Calibrar configuracao.
- [ ] Gerar matriz de lacunas priorizadas.
- [ ] Executar descoberta multibase CNJ.
- [ ] Gerar corpus expandido HTML/PDF e matrizes por tipo de fonte.
- [ ] Gerar publicacao final, portfolio e anexos CSV.

## 6. Evolucoes posteriores

- ampliar fontes do CNJ com rastreabilidade separada;
- incorporar classificacao assistida por modelos de linguagem apos formar
  amostra revisada;
- cruzar evidencias com catalogos de cursos;
- priorizar competencias por recorrencia, criticidade e cobertura formativa;
- gerar relatorios executivos periodicos para a ENAJU.

## 7. Estado da execucao `baseline-2026-05-31`

| Fase | Estado |
| --- | --- |
| Snapshot editorial | Concluido |
| Catalogo e relacoes documentais | Concluido automaticamente; curadoria pendente |
| Download, hash e corpus | Concluido |
| Extracao, limpeza e segmentacao | Concluido; sem OCR pendente |
| Deteccao deterministica | Concluida com criterios `0.1.0` |
| Amostra de calibracao | Gerada; revisao humana pendente |
| Fila de evidencias | Gerada; revisao e auditoria pendentes |
| Priorizacao automatizada | Implementada como etapa `prioritize` |
| Expansao do corpus | Implementada com `discover-sources` e `expanded-corpus` |
| Sintese | Publicacao final integrada ao pipeline, com secao de expansao documental |
