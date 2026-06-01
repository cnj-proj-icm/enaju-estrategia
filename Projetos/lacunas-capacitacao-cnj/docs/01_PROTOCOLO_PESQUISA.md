# Protocolo de Pesquisa

## 1. Finalidade

Construir uma base rastreavel de evidencias textuais que ajude a ENAJU a
identificar necessidades formativas e problemas institucionais com possivel
traducao em competencias.

O projeto gera candidatos para analise. Ele nao substitui leitura tecnica,
validacao institucional ou levantamento direto de necessidades junto aos
publicos envolvidos.

## 2. Pergunta de pesquisa

Quais lacunas de capacitacao, necessidades formativas e problemas
organizacionais aparecem nas producoes do CNJ publicadas desde 2022 e como
podem ser traduzidos, com cautela, em hipoteses de competencias?

## 3. Fonte e recorte

| Elemento | Regra inicial |
| --- | --- |
| Fonte | Portal oficial de Pesquisas Judiciarias do CNJ |
| URL | `https://www.cnj.jus.br/pesquisas-judiciarias/` |
| Secao prioritaria | `Producao Interna` |
| Inicio da janela | `2022-01-01` |
| Fim da janela | Data da execucao |
| Formato principal | PDF |
| Unidade documental | Documento PDF catalogado |
| Unidade analitica | Trecho textual associado a pagina e documento |

## 4. Observacoes da verificacao inicial do portal

A pagina oficial foi consultada em `2026-05-31`. O desenho considera quatro
caracteristicas observadas:

1. A pagina contem links diretos para PDFs, mas alguns aparecem repetidos no
   HTML por estarem associados a mais de um elemento visual.
2. O portal tambem oferece paineis, arquivos ZIP e bases de dados, que devem ser
   catalogados como referencias relacionadas quando forem relevantes, sem
   entrar automaticamente no corpus textual.
3. Ha relatorios completos, sumarios executivos, apresentacoes e traducoes.
4. O ano na pasta de upload pode divergir do ano informado no titulo do
   documento. Por isso, `ano_url` e `ano_documento` sao campos distintos.

## 5. Criterios de inclusao

Um PDF entra no catalogo inicial quando:

- aparece na pagina fonte ou em uma pagina interna explicitamente percorrida
  pelo coletor;
- possui URL normalizavel;
- apresenta `ano_url` desde 2022 ou requer revisao por divergencia temporal;
- pode ser associado a uma categoria e a um contexto de pagina.

Um PDF entra no corpus principal quando:

- e unico apos normalizacao de URL e hash;
- pertence a janela temporal validada;
- representa a versao principal do documento;
- esta em portugues quando houver versoes equivalentes em outros idiomas;
- possui texto extraivel ou pode ser tratado por OCR de excecao.

## 6. Exclusoes e relacoes documentais

| Situacao | Tratamento |
| --- | --- |
| Mesmo PDF repetido no HTML | Deduplicar por URL normalizada |
| Mesmo conteudo em URLs diferentes | Deduplicar por `sha256` |
| Traducao em ingles ou espanhol | Excluir do corpus se houver original em portugues e registrar relacao |
| Sumario executivo | Relacionar a versao completa; excluir do corpus principal quando houver relatorio completo |
| Apresentacao | Relacionar ao documento principal; analisar separadamente apenas se houver justificativa |
| ZIP, painel ou base | Registrar como recurso relacionado; nao extrair como PDF |
| PDF corrompido | Registrar falha; nao descartar silenciosamente |

## 7. Deteccao de candidatos

O texto e normalizado para busca sem distincao de maiusculas e minusculas e sem
acentos. Os termos iniciais estao em
[`config/criterios_analiticos.yml`](../config/criterios_analiticos.yml).

Cada trecho candidato recebe:

- termos encontrados;
- grupos ativados;
- um ou mais eixos tematicos;
- score inicial;
- tipo de gap proposto;
- hipotese de competencia;
- status de revisao humana.

## 8. Regras de interpretacao

### Gap explicito

Usar quando o trecho descreve falta, insuficiencia, ausencia, dificuldade,
necessidade ou fragilidade em contexto relevante para uma capacidade, processo
ou servico.

### Gap implicito

Usar quando o trecho descreve baixa cobertura, baixa adesao, assimetria,
estrutura reduzida, ausencia de fluxo, falha de governanca ou baixa
institucionalizacao, mesmo sem usar vocabulario formativo.

### Gap potencial

Usar quando ha sinal tematico ou mencao formativa, mas o trecho ainda nao
permite concluir que existe uma lacuna. Esse tipo serve para revisao, nao para
contagem final automatica.

## 9. Score inicial

O score serve para ordenar candidatos para leitura humana:

```text
+3 por termo distinto do Grupo A
+2 por termo distinto do Grupo B
+1 por termo distinto dos Grupos C, D ou E
+2 se houver coocorrencia entre A e B
+1 se houver verbo de acao configurado
```

A unidade inicial e o termo distinto no trecho, evitando que repeticoes da
mesma palavra dominem a priorizacao. Essa decisao deve ser calibrada no piloto.

## 10. Limites analiticos

- Uma mencao a `capacitacao` nao prova a existencia de uma lacuna.
- Uma recomendacao pode indicar aprimoramento desejavel sem revelar deficit.
- A ausencia de um termo configurado nao prova ausencia de necessidade.
- O corpus representa o portal e o recorte temporal adotado, nao todo o Poder
  Judiciario.
- As hipoteses de competencia devem ser revisadas por pessoas com dominio
  tematico antes de orientar oferta educacional.
