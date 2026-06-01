# Validacao e Qualidade

## 1. Objetivo

Evitar que conveniencias tecnicas sejam confundidas com conclusoes de pesquisa.
Cada etapa possui verificacoes proprias e deixa rastros para auditoria.

## 2. Portas de qualidade

| Etapa | Verificacao minima | Criterio inicial de aceite |
| --- | --- | --- |
| Coleta | Snapshot HTML salvo e links rastreaveis ao contexto | Todos os links PDF visiveis catalogados |
| Catalogo | URLs normalizadas e repeticoes contadas | Nenhuma repeticao silenciosa |
| Recorte | Divergencias entre anos listadas | Casos divergentes revisados |
| Deduplicacao | URL, hash e familia documental registrados | Exclusoes com motivo |
| Download | HTTP, assinatura PDF, bytes e hash | Falhas explicitadas |
| Extracao | Paginas e caracteres contabilizados | PDFs sem texto sinalizados |
| Limpeza | Comparacao entre TXT bruto e limpo | Marcadores de pagina preservados |
| Segmentacao | Segmentos ligados a documento e pagina | Amostra reconstruivel |
| Deteccao | Termos, score e regra registrados | Score reproduzivel |
| Analise | Revisao humana separada da classificacao automatica | Resumos distinguem pendentes e confirmados |

## 3. Validacao do catalogo piloto

Antes do download completo:

1. gerar `catalogo_pdfs.csv`;
2. revisar todos os itens com `status_corpus = revisar`;
3. conferir traducoes, sumarios, apresentacoes e familias documentais;
4. verificar documentos com `ano_url != ano_documento`;
5. congelar uma versao do catalogo aprovada para o primeiro ciclo.

## 4. Validacao da extracao

Selecionar amostra estratificada por:

- metodo de extracao;
- faixa de tamanho do PDF;
- quantidade de paginas;
- categoria documental;
- status `parcial` ou `ocr_pendente`.

Comparar visualmente PDF e TXT em pelo menos paginas inicial, intermediaria e
final de cada documento amostrado.

## 5. Validacao analitica

### Amostra inicial

Revisar manualmente:

- os `50` trechos de maior score;
- uma amostra aleatoria de `50` candidatos restantes;
- uma amostra de `30` segmentos sem match para estimar falsos negativos
  visiveis;
- todos os casos usados em sinteses executivas.

### Registro da revisao

Cada candidato deve receber `status_revisao` e, quando ajustado ou descartado,
uma `nota_revisor`. A revisao deve distinguir:

- a existencia de problema;
- a pertinencia para capacitacao;
- o eixo tematico;
- a hipotese de competencia;
- a qualidade do trecho como evidencia.

### Calibracao

Depois da amostra:

1. revisar termos muito genericos;
2. incluir expressoes relevantes ausentes;
3. ajustar score, eixos e hipoteses;
4. versionar a configuracao;
5. executar novamente a deteccao.

## 6. Criterios para uso institucional

Um achado so pode aparecer como evidencia confirmada quando:

- o trecho e legivel e rastreavel ao PDF e pagina;
- a interpretacao foi revisada;
- o tipo de gap foi confirmado ou ajustado;
- a hipotese de competencia e apresentada como hipotese, salvo validacao
  institucional adicional.

## 7. Testes tecnicos previstos

- teste de normalizacao de URL;
- teste de inferencia de idioma e tipo documental;
- teste das regras de relacao entre versoes;
- teste de hash e deteccao de duplicata;
- teste de preservacao de `===PAGE_BREAK===`;
- teste de correcao de hifenizacao;
- teste de normalizacao sem acentos;
- teste deterministico do score;
- teste de serializacao CSV e Parquet.
