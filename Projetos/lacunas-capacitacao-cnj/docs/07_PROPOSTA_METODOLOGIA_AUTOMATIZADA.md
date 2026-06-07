# Proposta de alternativa metodologica: lacunas priorizadas por evidencia e valor

## 1. Objetivo

Substituir a validação manual em larga escala por um modelo de priorização automatizada, rastreável e reproduzível, que devolva lacunas de capacitação com:

- evidencia textual citável;
- score de confianca calculado;
- peso de valor institucional;
- classificação em três níveis de prontidão para decisao.

A ideia e produzir uma proposta informada por evidencias, sem depender de revisor humano para revisar 1.807 trechos.

## 2. Principio central

Nao tratar toda mencao a capacitacao como lacuna. O sistema deve responder a tres perguntas:

1. O trecho realmente sinaliza um problema, ausencia ou necessidade?
2. Esse problema e relevante para competencias e formacao?
3. Ele tem valor estrategico suficiente para merecer prioridade institucional?

## 3. Novo desenho metodologico

### 3.1. Estrutura de decisao em tres camadas

1. Evidencia textual
   - trecho extraido com pagina, documento, secao e URL;
   - regra de gap explicito, implicito ou potencial;
   - termo(s), eixo tematico e score base.

2. Confiança analitica
   - recorrencia do mesmo padrao em varios documentos;
   - coocorrencia de termos fortes e contexto institucional;
   - consistencia entre score lexical e semantica;
   - taxa de falsos positivos estimada por amostragem pequena.

3. Valor para a instituicao
   - impacto esperado para o Judiciario;
   - urgencia de resposta formativa;
   - viabilidade de acao e relevancia estrategica;
   - grau de alinhamento com prioridades da ENAJU/CNJ.

## 4. Regra operacional de priorização

Cada evidencia recebe um score composto:

Score final = 0,45 × score_textual + 0,30 × consistencia_evidencial + 0,25 × valor_institucional

Onde:

- score textual: intensidade da sinalizacao de lacuna no trecho;
- consistencia evidencial: recorrencia, coocorrencia e robustez do padrao;
- valor institucional: peso associado a impacto, urgencia e relevancia estrategica.

### 4.1. Faixas de decisão

- Faixa alta: lacuna priorizada para proposta
  - score >= 0,75
  - evidencia robusta
  - contexto claro e repetido

- Faixa media: hipoteses de lacuna
  - score entre 0,50 e 0,74
  - necessita refinamento semantico ou consulta pontual

- Faixa baixa: descartar ou arquivar
  - score < 0,50
  - contexto fraco, ambíguo ou sem impacto claro

## 5. Metodo de calibracao automatica

Ao inves de revisar 1.807 trechos manualmente, usar um processo de calibracao em quatro passos:

1. Amostra pequena e estratificada
   - 100 a 150 trechos representativos por faixa de score;
   - incluir casos extremos e casos ambiguos.

2. Rotulagem de referencia por um pequeno grupo de especialistas
   - apenas para calibrar o modelo;
   - nao para revisar todo o corpus.

3. Ajuste de pesos e limiares
   - calibração dos pesos do score composto;
   - refinamento de termos e regras.

4. Validação por backtesting
   - medir estabilidade do ranking;
   - comparar os top N priorizados contra a amostra de referencia.

Esse procedimento substitui a revisão total por um ciclo de calibracao objetiva e reprodutível.

## 6. Saida proposta para a decisao

O sistema deve produzir, em vez de uma lista manual de evidencias, um pacote executivo com:

1. Matriz de lacunas priorizadas
   - lacuna;
   - eixo tematico;
   - documentos que sustentam a evidencia;
   - score final;
   - nivel de confianca.

2. Dossier de evidencia
   - trecho original;
   - pagina e documento;
   - criterio de gap aplicado;
   - motivo da classificacao.

3. Mapa de valor
   - impacto institucional;
   - urgencia formativa;
   - potencial de resposta educacional;
   - recomendação de intervenção.

4. Risco de erro
   - itens duvidosos;
   - casos de baixa confianca;
   - necessidade de verificação pontual apenas quando houver impacto alto.

## 7. Como isso reduz a dependência de revisão manual

A proposta preserva rigor metodologico porque:

- usa regras documentadas e reproduzíveis;
- separa evidencia, confianca e valor;
- evita classificação baseada em uma única palavra;
- limita revisão humana a casos de alto risco ou alto impacto;
- gera um ranking priorizado para decisao institucional.

## 8. Caminho de implementacao recomendado

### Fase 1 — consolidar a linha de base automatizada

- manter o pipeline atual como fonte de evidencia;
- exportar os trechos com metadados completos;
- criar uma tabela de score composto.

### Fase 2 — construir a priorização

- implementar um modulo de score composto;
- adicionar pesos de valor institucional;
- gerar top N por eixo e por documento.

### Fase 3 — validar com amostra pequena

- revisar apenas 100 a 150 trechos estratificados;
- ajustar thresholds;
- medir aderencia do ranking a evidencia real.

### Fase 4 — publicar proposta informada por evidencias

- gerar um relatório de lacunas priorizadas;
- incluir justificativas e rastreabilidade;
- usar como base para proposta de capacitacao ou programa institucional.

## 9. Recomendação final

A melhor alternativa para esse momento nao e continuar com a revisão manual completa. A melhor alternativa e construir uma metodologia de priorização automatizada, baseada em:

- evidencia textual rastreável;
- score composto e limiares explícitos;
- calibração com amostra pequena;
- valor institucional como criterio de escolha.

Esse caminho entrega uma proposta mais útil, mais defensável e menos dependente de curadoria manual massiva.
