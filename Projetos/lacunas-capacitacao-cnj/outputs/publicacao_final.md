# Modelo de priorização de capacitações para escolas judiciais a partir de evidências documentais do CNJ

## 1. Resumo executivo

Este documento apresenta uma proposta técnica para identificar lacunas de capacitação em produções do CNJ, distinguir gaps observados de competências requeridas por normas e ofertas formativas existentes, e converter esse diagnóstico em um plano de aprofundamento analítico. O produto combina coleta documental, expansão multibase, identificação automatizada de evidências, score composto, matriz de priorização, alertas de risco e plano de validação.

**Status da entrega:** PROPOSTA TÉCNICA - priorização automatizada com amostra de calibração estruturada.

## 2. Corpus e alcance

A linha de base `baseline-2026-05-31` considera a fotografia editorial de `2026-05-31` do portal de Pesquisas Judiciárias do CNJ. O corpus processado contém `84` documentos e 3100 evidências únicas em 5034 linhas evidência-eixo consideradas para a etapa de síntese.

O estudo não mede demanda de cursistas, orçamento, capacidade operacional das escolas ou prioridade política. Ele organiza sinais documentais para apoiar decisão pedagógica posterior.

## 3. Método utilizado e justificativa da escolha

### 3.1. Problema metodológico enfrentado

A pergunta de pesquisa não é simplesmente "quais palavras aparecem nos documentos do CNJ?". O desafio é identificar, em um conjunto heterogêneo de fontes, sinais que possam indicar necessidade de desenvolvimento de competências no Poder Judiciário. Isso exige separar três coisas que costumam aparecer misturadas no texto institucional:

- `gap_observado`: relatórios, diagnósticos ou pesquisas apontam dificuldade, ausência, carência, baixa adesão, insuficiência, falta de padronização ou necessidade de capacitação.
- `competencia_requerida`: resoluções, portarias, programas, guias ou manuais estabelecem uma capacidade esperada, uma obrigação de implementação ou uma competência institucional a desenvolver.
- `oferta_formativa`: notícias, páginas de cursos e capacitações indicam uma resposta já existente, que pode reduzir ou cobrir parcialmente uma lacuna, mas não prova sozinha que a lacuna exista.

Sem essa separação, o relatório poderia cometer dois erros: tratar toda norma como evidência de lacuna ou tratar toda oferta de curso como prova de que há demanda não atendida. A metodologia escolhida evita esses atalhos.

### 3.2. Por que o corpus original foi expandido

A primeira linha de base era tecnicamente consistente, mas estreita: partia de uma página específica de Pesquisas Judiciárias e privilegiava relatórios de pesquisa. Esse recorte era adequado para um piloto, mas insuficiente para uma leitura ampla da agenda de capacitação do CNJ. Por isso, o universo documental foi ampliado para incluir atos normativos, páginas de programas, publicações, notícias, ofertas formativas e fontes associadas ao CNJ.

Na execução atual, o corpus analisável contém `84` documentos e 3100 evidências únicas em 5034 linhas evidência-eixo consideradas. A distribuição por tipo de fonte é:

| Tipo de fonte | Documentos |
| --- | --- |
| relatorio_diagnostico_pesquisa | 39 |
| ato_normativo | 36 |
| oferta_formativa | 4 |
| pagina_programa | 4 |
| noticia_cnj | 1 |

### 3.3. Unidade de análise

A unidade primária de análise é o trecho textual rastreável. Para PDFs, o trecho preserva documento, página, URL, `doc_id`, hash e metadados do catálogo. Para HTML, o trecho preserva URL, tipo de fonte, origem da descoberta e texto extraído da página. O uso do trecho como unidade permite citar evidências, revisar falsos positivos e auditar a decisão sem depender de uma interpretação global opaca do documento.

O pipeline gera segmentos por página, parágrafo e janela deslizante. A detecção prioriza janelas textuais porque elas capturam coocorrências que podem ficar separadas artificialmente por quebras de página, cabeçalhos, tabelas ou parágrafos curtos. Essa escolha aumenta sensibilidade, mas também exige alertas de risco e calibração amostral para reduzir ambiguidade.

### 3.4. Descoberta, extração e rastreabilidade

O método usa descoberta multibase a partir de fontes configuradas em `config/sources.yml`. Cada item recebe `fonte_tipo`, `peso_fonte`, `forca_probatoria` e `uso_metodologico`. Esses campos tornam explícita a diferença entre diagnóstico, norma, guia, notícia, curso e painel.

O fluxo operacional é:

1. Descobrir fontes e links relacionados nos domínios CNJ permitidos.
2. Classificar cada item por tipo de fonte e uso metodológico.
3. Extrair texto de PDFs e HTML quando houver conteúdo analisável.
4. Segmentar o texto com identificadores estáveis.
5. Aplicar critérios lexicais e contextuais de lacuna, competência requerida e oferta formativa.
6. Priorizar evidências por score composto, recorrência, distribuição documental e valor institucional.
7. Gerar matrizes de lacunas, competências normativas, oferta versus lacuna e dossiê de evidências.

### 3.5. Strings de busca para formação do corpus

A formação do corpus expandido partiu de páginas-semente configuradas, e não de uma busca livre na internet. O crawler visitou as fontes abaixo e, a partir delas, seguiu links internos quando a URL, o texto da âncora, o título ou o início do conteúdo continham termos de descoberta relacionados a capacitação, competência, publicações, normativos, programas ou notícias.

| Fonte | Tipo | Prioridade | URL |
| --- | --- | --- | --- |
| atos-normativos-cnj | normative_acts | high | https://www.cnj.jus.br/atos_normativos/ |
| biblioteca-digital-cnj | digital_library | high | https://bibliotecadigital.cnj.jus.br/ |
| ceajud-legislacao | normative_acts | high | https://www.cnj.jus.br/legislacao-ceajud/ |
| enaju-publicacoes | training | high | https://www.cnj.jus.br/cidadao/publicacoes/ |
| gestao-por-competencias | training | high | https://www.cnj.jus.br/formacao-e-capacitacao/gestao-por-competencias/ |
| justica-4-capacitacoes | justice_4_training | high | https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/justica-4-0/capacitacoes/ |
| pesquisas-judiciarias-justica-pesquisa | publications_research | high | https://www.cnj.jus.br/pesquisas-judiciarias/justica-pesquisa/publicacoes-justica-pesquisa/ |
| pesquisas-judiciarias-producao-interna | publications_research | high | https://www.cnj.jus.br/pesquisas-judiciarias/ |
| programas-e-acoes | program | high | https://www.cnj.jus.br/programas-e-acoes/ |
| publicacoes-cnj | publications | high | https://www.cnj.jus.br/publicacoes- |
| justica-em-numeros | publications_research | medium | https://www.cnj.jus.br/justica-em-numeros/ |
| pdpj-capacitacao | justice_4_training | medium | https://www.cnj.jus.br/capacitacao/ |
| politicas-programaticas | program | medium | https://www.cnj.jus.br/gestao-da-justica/politicas-judiciarias-nacionais-programaticas/eixos-estrategicos/ |
| relatorios-anuais-cnj | publications | medium | https://www.cnj.jus.br/relatorios-anuais-do-cnj/ |
| sistema-penal-publicacoes | publications | medium | https://www.cnj.jus.br/publicacoes-e-relatorios/ |
| noticias-cnj | news | low | https://www.cnj.jus.br/category/noticias/ |

Os domínios autorizados para descoberta foram: `cnj.jus.br`, `atos.cnj.jus.br`, `bibliotecadigital.cnj.jus.br`, `boaspraticas.cnj.jus.br`, `paineisanalytics.cnj.jus.br`. A janela metodológica configurada foi de `2021` até a data de execução; normas estruturantes antigas puderam ser preservadas quando descobertas por fonte institucional vigente.

As strings de descoberta usadas para formar o corpus foram:

`capacitacao`, `capacitações`, `capacitação`, `competencia`, `competência`, `formacao`, `formação`, `treinamento`, `curso`, `relatorio`, `relatório`, `diagnostico`, `diagnóstico`, `pesquisa`, `manual`, `guia`, `cartilha`, `publicacao`, `publicação`, `publicacoes`, `publicações`, `normativo`, `normativos`, `resolucao`, `resolução`, `portaria`, `recomendacao`, `recomendação`, `noticia`, `notícia`, `noticias`, `notícias`, `implementacao`, `implementação`, `politica`, `política`

Essas strings foram aplicadas de forma normalizada: o texto foi convertido para caixa baixa, com acentos removidos para comparação e espaços colapsados. Na descoberta de corpus, a presença de uma string funcionou como filtro de relevância para seguir links ou manter metadados; ela não significou, sozinha, que havia uma lacuna confirmada.

### 3.6. Strings usadas na análise dos gaps

Depois de formado o corpus, a análise textual usou outro conjunto de strings, mais específico, registrado em `config/criterios_analiticos.yml`. Diferentemente da descoberta de corpus, aqui as strings acionam grupos com pesos, classes de achado, eixos temáticos e hipóteses de competência.

As regras trabalham com correspondência literal normalizada, com fronteiras de palavra e espaços flexíveis em expressões compostas. Isso significa que `falta de` e `necessidade de`, por exemplo, são buscadas como expressões textuais rastreáveis, não como inferência semântica livre. A decisão foi manter regras auditáveis e reprodutíveis antes de introduzir classificação assistida por modelo.

#### Grupos analíticos e pesos

| Grupo | Peso | Strings |
| --- | --- | --- |
| A_lacuna_direta | 3 | `lacuna`, `gargalo`, `deficiencia`, `insuficiencia`, `fragilidade`, `carencia`, `ausencia`, `falta de`, `necessidade de`, `desafio`, `desafios`, `dificuldade`, `dificuldades`, `limitacao`, `limitacoes`, `obstaculo`, `entrave` |
| B_necessidade_formativa | 2 | `capacitacao`, `formacao`, `aperfeicoamento`, `treinamento`, `qualificacao`, `desenvolvimento de competencias`, `gestao por competencias`, `educacao corporativa`, `formacao continuada`, `trilha formativa`, `aprendizagem`, `desenvolvimento gerencial` |
| C_problema_organizacional | 1 | `baixa adesao`, `baixa participacao`, `pouca participacao`, `desconhecimento`, `falta de conhecimento`, `uso insuficiente`, `baixo uso`, `ausencia de protocolo`, `ausencia de fluxo`, `falta de padronizacao`, `heterogeneidade`, `assimetria`, `nao implementacao`, `implementacao parcial`, `inexistencia`, `subnotificacao`, `baixa cobertura`, `insuficiencia de pessoal`, `equipe reduzida`, `estrutura insuficiente`, `governanca`, `monitoramento`, `avaliacao`, `indicadores` |
| D_tecnologia_dados_inovacao | 1 | `qualidade dos dados`, `saneamento de dados`, `datajud`, `inteligencia artificial`, `ia generativa`, `transformacao digital`, `inovacao`, `laboratorio`, `automacao`, `analitica`, `ciencia de dados` |
| E_inclusao_direitos_relacoes | 1 | `acessibilidade`, `assedio`, `discriminacao`, `equidade`, `racial`, `genero`, `pessoas com deficiencia`, `saude mental`, `violencia` |
| F_competencia_requerida | 2 | `devera promover`, `devera garantir`, `compete ao tribunal`, `compete aos tribunais`, `fica instituida`, `fica instituido`, `politica nacional`, `plano nacional`, `programa nacional`, `implementar politica`, `assegurar capacitacao`, `promover capacitacao`, `desenvolver competencias`, `mapeamento de competencias`, `gestao por competencias` |
| G_oferta_formativa | 1 | `curso`, `cursos`, `webinar`, `capacitações`, `capacitacoes`, `autoinstrucional`, `ead`, `carga horaria`, `publico-alvo`, `publico alvo`, `inscricoes`, `certificacao` |
| H_implementacao_politica | 1 | `implementacao`, `implantação`, `implantacao`, `plano de acao`, `plano de ação`, `monitoramento da politica`, `acompanhamento da politica`, `relatorio anual`, `prestação de contas`, `prestacao de contas` |

#### Bônus de coocorrência e verbos de ação

- Coocorrência entre lacuna direta e necessidade formativa: peso `2`.
- Verbos de ação que reforçam orientação para desenvolvimento: `aprimorar`, `fortalecer`, `desenvolver`, `qualificar`.

#### Strings de classificação por eixo

| Eixo | Strings |
| --- | --- |
| dados_e_tecnologia | `dados`, `datajud`, `saneamento`, `analitica`, `automacao`, `inteligencia artificial` |
| gestao_e_governanca | `gestao`, `governanca`, `protocolo`, `fluxo`, `padronizacao`, `institucionalizacao` |
| formacao_de_liderancas | `lideranca`, `liderancas`, `gerencial`, `chefia`, `gestor`, `gestores` |
| saude_e_bem_estar | `saude mental`, `saude`, `bem-estar`, `adoecimento`, `qualidade de vida` |
| direitos_humanos_e_inclusao | `direitos humanos`, `discriminacao`, `equidade`, `racial`, `genero`, `violencia`, `assedio` |
| atendimento_e_servicos_judiciarios | `atendimento`, `servico`, `jurisdicionado`, `acesso a justica`, `prestacao jurisdicional` |
| inovacao_e_transformacao | `inovacao`, `laboratorio`, `transformacao digital`, `ia generativa` |
| avaliacao_e_monitoramento | `avaliacao`, `monitoramento`, `indicador`, `indicadores`, `cobertura` |
| comunicacao_e_acessibilidade | `comunicacao`, `acessibilidade`, `linguagem simples`, `pessoas com deficiencia` |
| equipes_multidisciplinares | `equipe multidisciplinar`, `equipes multidisciplinares`, `equipe reduzida`, `pessoal` |

#### Gatilhos para hipóteses de competência

| Hipótese de competência | Gatilhos textuais |
| --- | --- |
| governanca e qualidade de dados | `saneamento de dados`, `qualidade dos dados`, `datajud` |
| prevencao, acolhimento e encaminhamento institucional | `assedio`, `discriminacao`, `fluxo`, `protocolo` |
| gestao da inovacao e transformacao organizacional | `inovacao`, `laboratorio`, `transformacao digital` |
| acessibilidade e comunicacao inclusiva | `acessibilidade`, `pessoas com deficiencia`, `comunicacao` |
| estruturacao e atuacao de equipes multidisciplinares | `equipe multidisciplinar`, `equipes multidisciplinares`, `equipe reduzida` |

#### Peso metodológico por tipo de fonte

Nem toda string tem a mesma força conforme a fonte. Por isso, depois da detecção textual, o achado é ponderado por tipo de documento:

| Tipo de fonte | Força probatória | Peso | Uso metodológico |
| --- | --- | --- | --- |
| relatorio_diagnostico_pesquisa | alta | 1.0 | gap_observado |
| ato_normativo | alta_normativa | 0.85 | competencia_requerida |
| manual_guia_cartilha | media | 0.7 | competencia_requerida |
| noticia_cnj | contextual | 0.45 | evidencia_contextual |
| oferta_formativa | oferta | 0.4 | oferta_formativa |
| pagina_programa | contextual | 0.6 | competencia_requerida |
| painel_dados | metadado | 0.3 | metadado |
| base_dados | metadado | 0.3 | metadado |

Em termos práticos: relatórios e diagnósticos pesam mais para `gap_observado`; atos normativos pesam mais para `competencia_requerida`; cursos e notícias entram como contexto ou oferta formativa, com menor peso para não dominar a priorização.


### 3.7. Regras de detecção

A detecção combina grupos de termos e contexto. Termos de lacuna direta recebem maior peso; sinais formativos, problemas organizacionais, tecnologia/dados, inclusão, competência requerida, oferta formativa e implementação de política entram como camadas complementares. A classificação automática não decide sozinha a validade institucional do achado: ela identifica candidatos, explica quais termos acionaram a regra e registra o tipo de evidência.

As classes observadas nesta execução foram:

| Classe de achado | Evidências | Documentos |
| --- | --- | --- |
| gap_observado | 2778 | 53 |
| competencia_requerida | 178 | 52 |
| oferta_formativa | 144 | 30 |

### 3.8. Priorização e score composto

A priorização usa o score composto:

`score_final = 0,45 * score_textual_norm + 0,30 * consistencia_evidencial + 0,25 * valor_institucional`

- `score_textual_norm`: mede a intensidade lexical e contextual do trecho, limitada a 1,0 e ponderada pelo peso da fonte.
- `consistencia_evidencial`: mede se o eixo aparece de forma recorrente e distribuída em documentos distintos.
- `valor_institucional`: representa relevância estratégica configurada por eixo temático.
- faixas de decisão: alta (`>= 0,75`), média (`>= 0,50`) e baixa (`< 0,50`).

O score textual bruto utiliza escala própria de detecção lexical; o score final é normalizado entre 0 e 1 após ponderação por consistência evidencial e valor institucional. Essa distinção evita comparar diretamente números que pertencem a escalas diferentes.

O score não é uma medida absoluta de urgência pedagógica. Ele é um instrumento de ordenação para decidir onde aprofundar a análise humana. Esse ponto é central: o método não transforma contagem de menções em decisão de curso; ele transforma evidência documental em uma fila priorizada de investigação.

### 3.9. Justificativa da escolha metodológica

Foram rejeitadas duas alternativas extremas. A primeira seria revisar manualmente todo o universo documental antes de qualquer síntese. Embora rigorosa, essa alternativa é lenta, cara e pouco escalável para ciclos periódicos de planejamento. A segunda seria usar apenas automação lexical e publicar os resultados como conclusão. Essa alternativa é rápida, mas frágil, porque termos como "capacitação", "desafio" ou "competência" podem ter sentidos muito diferentes conforme a fonte.

A escolha adotada é intermediária e mais defensável: automação rastreável para ampliar cobertura, pesos por tipo de fonte para reduzir viés, score composto para ordenar prioridades, alertas de risco para explicitar incerteza e calibração amostral para orientar revisão humana. Assim, o trabalho ganha escala sem abrir mão de auditabilidade.

### 3.10. Estado da calibração

Arquivo de calibração analítica existe, mas não contém decisões revisadas. A ausência de decisões revisadas não invalida a publicação técnica, mas limita seu uso: ela deve orientar uma etapa seguinte de análise robusta, e não ser tratada como validação institucional conclusiva.


## 4. Expansão do universo documental

O corpus expandido separa documentos de diagnóstico, atos normativos, guias/manuais, notícias e ofertas formativas. Essa separação evita que comunicação institucional ou oferta de curso tenha o mesmo peso probatório de pesquisa ou diagnóstico.

### Distribuição por origem e tipo de fonte

| Origem | Tipo de fonte | Documentos |
| --- | --- | --- |
| expanded_html | ato_normativo | 36 |
| baseline_pdf | relatorio_diagnostico_pesquisa | 35 |
| expanded_html | oferta_formativa | 4 |
| expanded_html | pagina_programa | 4 |
| expanded_html | relatorio_diagnostico_pesquisa | 4 |
| expanded_html | noticia_cnj | 1 |

### Lacunas por tipo de fonte

| Tipo de fonte | Classe | Eixo | Evidências | Documentos |
| --- | --- | --- | --- | --- |
| relatorio_diagnostico_pesquisa | gap_observado | dados_e_tecnologia | 927 | 34 |
| relatorio_diagnostico_pesquisa | gap_observado | direitos_humanos_e_inclusao | 789 | 33 |
| relatorio_diagnostico_pesquisa | gap_observado | avaliacao_e_monitoramento | 600 | 29 |
| relatorio_diagnostico_pesquisa | gap_observado | inovacao_e_transformacao | 448 | 19 |
| relatorio_diagnostico_pesquisa | gap_observado | atendimento_e_servicos_judiciarios | 383 | 34 |
| relatorio_diagnostico_pesquisa | gap_observado | nao_classificado | 330 | 27 |
| relatorio_diagnostico_pesquisa | gap_observado | gestao_e_governanca | 295 | 30 |
| relatorio_diagnostico_pesquisa | gap_observado | comunicacao_e_acessibilidade | 267 | 24 |
| relatorio_diagnostico_pesquisa | gap_observado | saude_e_bem_estar | 194 | 23 |
| relatorio_diagnostico_pesquisa | gap_observado | equipes_multidisciplinares | 85 | 19 |
| relatorio_diagnostico_pesquisa | gap_observado | formacao_de_liderancas | 72 | 22 |
| ato_normativo | competencia_requerida | gestao_e_governanca | 55 | 13 |

### Competências requeridas por normas, guias e programas

| Eixo | Competência | Fonte | Evidências | Documentos |
| --- | --- | --- | --- | --- |
| gestao_e_governanca | competencia_a_qualificar | ato_normativo | 40 | 6 |
| avaliacao_e_monitoramento | competencia_a_qualificar | ato_normativo | 34 | 4 |
| avaliacao_e_monitoramento | competencia_a_qualificar | relatorio_diagnostico_pesquisa | 19 | 9 |
| comunicacao_e_acessibilidade | acessibilidade e comunicacao inclusiva | ato_normativo | 18 | 11 |
| dados_e_tecnologia | competencia_a_qualificar | relatorio_diagnostico_pesquisa | 17 | 9 |
| atendimento_e_servicos_judiciarios | competencia_a_qualificar | ato_normativo | 17 | 7 |
| direitos_humanos_e_inclusao | competencia_a_qualificar | relatorio_diagnostico_pesquisa | 15 | 8 |
| dados_e_tecnologia | competencia_a_qualificar | ato_normativo | 15 | 4 |
| nao_classificado | competencia_a_qualificar | ato_normativo | 13 | 3 |
| nao_classificado | competencia_a_qualificar | relatorio_diagnostico_pesquisa | 12 | 8 |

### Mapa oferta versus lacuna

A coluna de leitura estratégica diferencia lacunas fortes com oferta parcial, lacunas sem oferta mapeada, competências normativas sem diagnóstico, ofertas sem gap demonstrado e evidências que ainda exigem revisão temática.

| Eixo | Gaps | Competências | Ofertas | Leitura |
| --- | --- | --- | --- | --- |
| dados_e_tecnologia | 932 | 50 | 47 | lacuna forte com oferta parcial |
| direitos_humanos_e_inclusao | 795 | 34 | 19 | lacuna forte com oferta parcial |
| avaliacao_e_monitoramento | 608 | 74 | 17 | lacuna forte com oferta parcial |
| inovacao_e_transformacao | 449 | 20 | 15 | lacuna forte com oferta parcial |
| atendimento_e_servicos_judiciarios | 390 | 28 | 17 | lacuna forte com oferta parcial |
| nao_classificado | 333 | 23 | 50 | revisão temática pendente |
| gestao_e_governanca | 304 | 69 | 21 | lacuna forte com oferta parcial |
| comunicacao_e_acessibilidade | 275 | 24 | 21 | lacuna forte com oferta parcial |
| saude_e_bem_estar | 199 | 8 | 7 | lacuna forte com oferta parcial |
| equipes_multidisciplinares | 87 | 21 | 5 | lacuna moderada com oferta existente |

## 5. Resultados priorizados

| Faixa | Proposta | Evidências | Documentos | Score final |
| --- | --- | --- | --- | --- |
| media | Capacitação em dados, tecnologia e inteligência institucional | 1029 | 46 | 0.6656 |
| media | Capacitação em direitos humanos, inclusão e acessibilidade | 848 | 48 | 0.6411 |
| media | Capacitação em comunicação e acessibilidade | 320 | 42 | 0.591 |
| media | Trilha de avaliação, monitoramento e planejamento estratégico | 699 | 44 | 0.5736 |
| media | Trilha de gestão, governança e liderança | 394 | 51 | 0.5709 |
| media | Trilha de atendimento e serviços ao cidadão | 435 | 45 | 0.5567 |
| media | Trilha de inovação e transformação digital | 484 | 27 | 0.5157 |
| baixa | Capacitação em saúde e bem-estar institucional | 214 | 31 | 0.4448 |
| baixa | Trilha de formação de lideranças | 92 | 25 | 0.4443 |
| baixa | Capacitação para estruturação e atuação de equipes multidisciplinares | 113 | 24 | 0.4367 |

## 6. Portfólio preliminar para validação

| Prioridade | Proposta | Público prioritário | Carga horária | Modalidade |
| --- | --- | --- | --- | --- |
| media | Capacitação em dados, tecnologia e inteligência institucional | gestores, analistas e equipes de dados | 12h a 20h | curso curto com laboratório aplicado |
| media | Capacitação em direitos humanos, inclusão e acessibilidade | servidores, gestores e equipes de políticas públicas | 12h a 16h | curso com oficina de aplicação |
| media | Capacitação em comunicação e acessibilidade | equipes de comunicação, atendimento e gestão de conteúdo | 8h a 12h | oficina prática |
| media | Trilha de avaliação, monitoramento e planejamento estratégico | gestores e formuladores de políticas | 16h a 24h | trilha curta com mentoria |
| media | Trilha de gestão, governança e liderança | gestores, chefias e equipes de governança | 16h a 24h | trilha aplicada |
| media | Trilha de atendimento e serviços ao cidadão | equipes de atendimento, comunicação e gestão de serviços | 12h a 18h | curso com simulação |
| media | Trilha de inovação e transformação digital | coordenadores e equipes de inovação | 16h a 20h | trilha com projeto piloto |
| baixa | Capacitação em saúde e bem-estar institucional | gestores de pessoas, magistrados e equipes de apoio institucional | 12h a 16h | curso com estudo de caso |
| baixa | Trilha de formação de lideranças | lideranças atuais e potenciais gestores | 20h a 30h | trilha com atividades reflexivas e práticas |
| baixa | Capacitação para estruturação e atuação de equipes multidisciplinares | equipes técnicas, gestores e unidades de apoio psicossocial | 12h a 20h | curso com oficina de fluxo |

## 7. Evidências rastreáveis

| Proposta | Documento | Página | Score final | Aderência | Nota de curadoria | Evidência rastreável |
| --- | --- | --- | --- | --- | --- | --- |
| Capacitação em dados, tecnologia e inteligência institucional | Relatório de Diagnóstico dos Tribunais nas Atividades de Saneamento de Dados do Datajud | 15 | 0.9278 | 7.5 | aderência temática suficiente para dossiê | Em dezembro de 2020, o CNJ e o Programa das Nações Unidas para o Desenvolvimento (PNUD) assinaram o projeto de cooperação técnica internacional BRA/20/015 – Justiça 4.0: Inovação e Efetividade na Realização da Justiça para Todos com o objetivo de promover o acesso à Justiça por meio de ações e projetos desenvolvidos para o uso colaborativo de produtos que empregam novas tecnologias e inteligência artificial. Um dos eixos do Programa Justiça 4.0 dedica-se especificamente a auxiliar os tribunais no aprimoramento dos registros processuais primários e na consolidação, implantação, tutoria, treina |
| Trilha de avaliação, monitoramento e planejamento estratégico | Avaliação sobre a aplicação das Medidas Protetivas de Urgência da Lei Maria da Penha | 144 | 0.8163 | 8.0 | aderência temática suficiente para dossiê |  justiça e de segurança pública, para avaliar a implementação do Formulário Nacional de Avaliação de Risco e apresentar soluções para as dificuldades mapeadas e explicitadas nos workshops. Entre os aspectos a serem abordados recomenda-se também a revisão do formulário nacional a fim de contemplar parâmetros para classificação, avaliação e gestão do risco; 2) elabore ferramentas para monitorar a aplicação do formulário pelo Poder Judiciário, incluindo indicadores de utilização do formulário na apreciação das medidas protetivas de urgência; 3) desenvolva ferramenta e metodologia que auxilie o Po |
| Capacitação em comunicação e acessibilidade | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 43 | 0.8152 | 8.0 | aderência temática suficiente para dossiê | com frequência significativa (36,0%). Outros desafios mencionados incluem a falta de infraestrutura acessível e a inexistência de mecanismos efetivos de monitoramento e avaliação das ações. Esses resultados evidenciam a complexidade do cenário enfrentado e reforçam a necessidade de ações integradas para superar tais barreiras (Figura 14). Figura 14 - Percentual de respondentes sobre os desafios de implementar ações para acessibilidadeo gráfico apresenta nove barras horizontais, cada uma representando a frequência percentual dos desafios enfrentados na gestão de iniciativas de acessibilidade, c |
| Capacitação em comunicação e acessibilidade | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 44 | 0.8152 | 8.0 | aderência temática suficiente para dossiê | A dificuldade em encontrar profissionais qualificados para atender a pessoas com deficiência foi um dos principais desafios relatados nos formulários. Pouco mais da metade dos(as) respondentes destacou essa questão, sugerindo que há uma escassez de mão de obra especializada, especialmente no contexto judiciário (Figura 14). Isso é agravado pela falta de treinamento adequado para magistrados(as) e servidores(as) em temas de acessibilidade e inclusão. Embora os dados do Painel do Balanço da Sustentabilidade do CNJ indiquem um aumento considerável no investimento em capacitação de gestores(as) em |
| Trilha de inovação e transformação digital | Laboratórios de Inovação do Poder Judiciário - Diagnóstico sobre as formas de atuação | 81 | 0.8125 | 8.0 | aderência temática suficiente para dossiê | processos administrativos, e nas radicais, a partir de processos de transformação digital e por meio da adoção de produtos tecnológicos. Evidencia-se, portanto, que um dos desafios dos laboratórios é passar a atuar também na identificação e na resolução de problemas relacionados à área finalística do Poder Judiciário. • Os dados obtidos por meio da survey e das entrevistas revelaram a ausência de diretrizes e de planos para uma atuação sistemática dos laboratórios de inovação, de modo que se sugere o estímulo à elaboração de planos de ação desses espaços, que englobem suas atividades e levem e |
| Capacitação em direitos humanos, inclusão e acessibilidade | Discriminação e Violência Contra LGBTQIA+ | 44 | 0.7723 | 9.0 | aderência temática suficiente para dossiê | 3. REFERENCIAL TEÓRICO 44 Tal como abordado em tópicos anteriores, a violência contra a população LGBTQIA+ se caracteriza por compor um processo de discriminação a determinadas expres­ sões de gênero e sexualidade. Um dos as­ pectos mais complexos na caracterização dessa violência é a pluralidade de formas que ela pode ter. A Organização Mundial de Saúde (KRUG EG et al, 2002, p. 5) concei­ tua violência como o uso intencional de força física ou poder, real ou em ameaça, contra si mesmo(a), contra outra pessoa ou contra um grupo ou uma comunidade, que resulte ou tenha grande chance de resultar  |
| Trilha de avaliação, monitoramento e planejamento estratégico | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 108 | 0.7713 | 8.0 | aderência temática suficiente para dossiê | Sistemas integrados e simplificados: avançar no processo de padronização das interfaces dos sistemas em todos os estados e tribunais, facilitando a utilização e reduzindo a sobrecarga cognitiva causada por interfaces diferentes em cada localidade. 7.4.2. Monitoramento e auditoria Desenvolver estratégias que permitam o monitoramento contínuo do nível de acessibilidade dos sites e sistemas com identificação dos problemas. 7.5. MONITORAMENTO E AVALIAÇÃO CONSTANTES 7.5.1. Indicadores e Ferramentas de Avaliação Indicadores de desempenho: Estabelecer indicadores de desempenho e monitoramento para av |
| Capacitação em direitos humanos, inclusão e acessibilidade | Discriminação e Violência Contra LGBTQIA+ | 128 | 0.7273 | 9.0 | aderência temática suficiente para dossiê | (org.), Manual de educação LGBTI+, 2021. Disponível em: https://vtp.ifsp.edu. br/images/NUGS/manual_de_educao_gaylatino_2021_v_25_11_2021_-_WEB.pdf. Acesso em: 3 ago. 2022. RIOS, Roger Raupp. “Desenvolver os direitos sexuais – desafios e tendências na América Latina”. In: CORNWALL, Andrea & JOLLY, Susie (org.). Questões de sexualidade: ensaios transculturais. Rio de Janeiro, ABIA, 2008. RIOS, Roger Raupp. “Direitos humanos, direitos sexuais e homossexualidade”. In: POCAHY, Fernando (org.). Políticas de enfrentamento ao heterossexismo: corpo e prazer. Porto Alegre, Nuances, 2010. RIOS, Roger Ra |
| Trilha de avaliação, monitoramento e planejamento estratégico | Pesquisa sobre Percepção e Avaliação do Poder Judiciário Brasileiro | 17 | 0.7263 | 8.0 | aderência temática suficiente para dossiê | de indução e de monitoramento de políticas públicas para o setor, em caráter estruturante e perene. Essa proposta se insere no contexto da Estratégia Nacional do Poder Judiciário 2021-2026, prevista na Resolução n. 325/2020, que indica a adoção de instrumentos de monitoramento e avaliação como indicadores de desem­ penho, análise de resultados das Metas Nacionais e Específicas e a verificação da realização de programas, projetos ou ações implementadas pelos órgãos do Poder Judiciário. Para esse fim, este relatório apresenta o referencial teórico e metodológico utilizado para realização da pesq |
| Trilha de formação de lideranças | Pesquisa sobre Tendência Organizacional e a Capacidade Institucional dos Tribunais Brasileiros para a Inovação | 126 | 0.7169 | 4.0 | aderência temática suficiente para dossiê | 126 DOS TRIBUNAIS BRASILEIROS PARA A INOVAÇÃO PESQUISA SOBRE daquilo, ele não teve uma experiência com aquilo. E aí, então, essa ausência de experiência, né, aliado à tranquilidade que ele tem, fala, beleza, né? E não quero dizer com isso que as pessoas aqui não estão interessadas, ao contrário, tem muita gente que entra de outras áreas e querem aprender e fazem os cursos, mas isso não acontece com a maior parte das pessoas. (Entrevistado(a) 4) Então, eu acho que incluir as pessoas todas nos processos de inovação, algu­ mas lideranças, algumas pessoas específicas, e capacitá-las, me parece que |
| Trilha de formação de lideranças | Pesquisa sobre Tendência Organizacional e a Capacidade Institucional dos Tribunais Brasileiros para a Inovação | 79 | 0.7169 | 4.0 | aderência temática suficiente para dossiê | de temática que demanda maior atenção por parte das lideranças do Poder Judiciário, ainda mais quando 34% discordam totalmente ou parcialmente, valor que alcança 44% na Justiça Militar. As entrevistas indicaram que a falta de equipes exclusivas para essas unidades é uma das principais barreiras no nível organizacional. Também foi apontada a necessidade de profissionais da área de tecnologia da informação com competências específicas para atender as demandas por inovação tecnológica. Em uma análise mais geral dos tribunais, alguns(as) entrevistados(as) consideraram que a força de trabalho é pou |
| Capacitação em direitos humanos, inclusão e acessibilidade | Rota crítica da violência doméstica e familiar contra mulheres que atuam no Poder Judiciário brasileiro | 12 | 0.6823 | 10.0 | aderência temática suficiente para dossiê | as Recomendações Gerais n. 33 e n. 35 (esta última atualizan­ do a anterior) tratam, respectivamente, do acesso das mulheres ao sistema de justiça e da violência de gênero contra as mulheres. Há também o sistema regional de proteção aos direitos humanos, composto por três núcleos: o africano, o interamericano e o europeu, sendo o Brasil um componente do interamericano, parte da Organização dos Estados Americanos (OEA)3, estabelecida em 1948. Ainda no que se refere à proteção dos direitos humanos das mulheres, há importantes diplomas regionais, como a Convenção Interamericana para Prevenir, Pun |
| Trilha de inovação e transformação digital | Laboratórios de Inovação do Poder Judiciário - Diagnóstico sobre as formas de atuação | 33 | 0.6775 | 8.0 | aderência temática suficiente para dossiê | 33 Fonte: dados da pesquisa, 2023. Constata-se que predomina um bloco de experiências associadas à introdução de tecnologias da informação no processo de transformação digital do Poder Judiciário, representadas por: implementação de sistema (8%); balcão virtual (6%), associado ao Programa Justiça 4.0; inteligência artificial (6%); implementação de PJe (6%); processo eletrônico (6%); e audiências virtuais (4%). Tudo isso correspondendo, portanto, a 36% das menções. Nas entrevistas realizadas, tais iniciativas foram explicitadas, conforme falas a seguir: O Judiciário, como um todo, se viu no des |
| Capacitação para estruturação e atuação de equipes multidisciplinares | Relatório de Diagnóstico dos Tribunais nas Atividades de Saneamento de Dados do Datajud | 15 | 0.6671 | 8.0 | aderência temática suficiente para dossiê | Em dezembro de 2020, o CNJ e o Programa das Nações Unidas para o Desenvolvimento (PNUD) assinaram o projeto de cooperação técnica internacional BRA/20/015 – Justiça 4.0: Inovação e Efetividade na Realização da Justiça para Todos com o objetivo de promover o acesso à Justiça por meio de ações e projetos desenvolvidos para o uso colaborativo de produtos que empregam novas tecnologias e inteligência artificial. Um dos eixos do Programa Justiça 4.0 dedica-se especificamente a auxiliar os tribunais no aprimoramento dos registros processuais primários e na consolidação, implantação, tutoria, treina |
| Trilha de gestão, governança e liderança | Pesquisa sobre Tendência Organizacional e a Capacidade Institucional dos Tribunais Brasileiros para a Inovação | 48 | 0.6324 | 5.0 | aderência temática suficiente para dossiê | 48 DOS TRIBUNAIS BRASILEIROS PARA A INOVAÇÃO PESQUISA SOBRE Os Conselhos e Tribunais Superiores, por suas inserções na estrutura organizacional do Judiciário, são instâncias naturais de coordenação nacional das ações, da mesma forma que os Tribunais Regionais Federais são no âmbito regional. As entrevistas indicaram a existência de ações de coordenação, incluindo a atuação de grupos de trabalho. Por outro lado, também foi destacado que há diferenças de entendimentos na concepção de algumas inovações entre tribunais e conselhos superiores, além de uma atuação fragmentada do Poder Judiciário. A  |
| Trilha de atendimento e serviços ao cidadão | Pesquisa sobre Percepção e Avaliação do Poder Judiciário Brasileiro | 47 | 0.5758 | 8.5 | aderência temática suficiente para dossiê | 5 RESULTADOS: PERCEPÇÃO SOBRE O FUNCIONAMENTO DO PODER JUDICIÁRIO Nessa seção são apresentados os resultados referentes à percepção sobre o funcionamento do Poder Judiciário entre cidadãos(ãs) e entre operadores(as) do direito19. Entre os(as) cidadãos(ãs) foram coletados dados referentes ao último processo judicial, às audiências de conciliação, aos serviços prestados por servidores(as) e magistrados(as), aos meios de comunicação do fórum/ tribunal, às ferramentas de consulta utilizadas, aos custos envolvidos no pro­ cesso, à avaliação em relação ao acesso à Justiça, entre outros aspectos. Ent |
| Capacitação em dados, tecnologia e inteligência institucional | Relatório de Diagnóstico dos Tribunais nas Atividades de Saneamento de Dados do Datajud | 40 | 0.5678 | 7.5 | aderência temática suficiente para dossiê |  computacionais (por exemplo, inteligência artificial, fórmulas, expressões regulares etc.), mas a reclassificação depende da ação da unidade”. Essa resposta foi dada pelo Tribunal Regional Federal da 2ª Região, pelo Tribunal Regional Eleitoral do Espírito Santo e pelo Tribunal de Justiça de Rondônia. • • • • • 40 |
| Capacitação em dados, tecnologia e inteligência institucional | Relatório de Diagnóstico dos Tribunais nas Atividades de Saneamento de Dados do Datajud | 42 | 0.5678 | 7.5 | aderência temática suficiente para dossiê | 1 (4%) informou que “cada unidade judiciária adota seu próprio padrão e faz a reclassificação dos autos quando considera necessário”; e 1 (4%) informou que “a triagem é feita de forma automática, por sugestões de programas computacionais (por exemplo, inteligência artificial, fórmulas, expressões regulares etc.), mas a reclassificação depende da ação da unidade”. Justiça Estadual: dos 26 Tribunais de Justiça respondentes, 13 (50%) recomendam que seja feita triagem nas varas/unidades judiciárias, mas a ação depende da gestão do juiz ou do diretor de secretaria; 6 (23%) informaram que “cada unid |

## 8. Limitações e riscos

- 1550 trechos apresentam score textual bruto baixo (< 3); devem ser lidos como hipóteses técnicas.
- 7 evidências repetem o mesmo documento e trecho; a síntese consolida a mensagem para reduzir duplicidade.
- 1792 evidências foram classificadas como potenciais; elas apoiam recomendações, mas não constituem conclusões institucionais isoladas.
- O score textual bruto usa escala própria de detecção lexical; o score final é normalizado entre 0 e 1 após ponderação por consistência evidencial e valor institucional.

As evidências automatizadas devem ser lidas como subsídio técnico. A decisão final sobre oferta educacional, sequenciamento, carga horária e público prioritário deve considerar validação institucional, disponibilidade de instrutores, calendário e capacidade de execução.

## 9. Plano proposto para análise robusta dos gaps

### 9.1. Objetivo do plano

O objetivo da próxima etapa não é produzir imediatamente uma grade de cursos. O objetivo é transformar os sinais documentais priorizados em um diagnóstico robusto de gaps, capaz de responder a quatro perguntas:

1. Qual é exatamente a lacuna: conhecimento, habilidade, atitude, processo, tecnologia, governança, padronização ou capacidade institucional?
2. Quem é afetado: magistrados, servidores, gestores, equipes técnicas, escolas judiciais, unidades de atendimento ou áreas de tecnologia?
3. A lacuna já possui resposta formativa ou normativa mapeada?
4. Qual intervenção é mais adequada: curso, trilha, oficina, guia, mentoria, laboratório, comunidade de prática, protocolo ou apoio à implementação?

### 9.2. Eixos que devem abrir o aprofundamento

Os primeiros eixos a aprofundar são aqueles com maior combinação de volume documental, distribuição em documentos distintos e valor institucional:

| Eixo/proposta | Evidencias | Documentos | Score final | Faixa |
| --- | --- | --- | --- | --- |
| Capacitação em dados, tecnologia e inteligência institucional | 1029 | 46 | 0.6656 | media |
| Capacitação em direitos humanos, inclusão e acessibilidade | 848 | 48 | 0.6411 | media |
| Capacitação em comunicação e acessibilidade | 320 | 42 | 0.591 | media |
| Trilha de avaliação, monitoramento e planejamento estratégico | 699 | 44 | 0.5736 | media |
| Trilha de gestão, governança e liderança | 394 | 51 | 0.5709 | media |
| Trilha de atendimento e serviços ao cidadão | 435 | 45 | 0.5567 | media |
| Trilha de inovação e transformação digital | 484 | 27 | 0.5157 | media |

### 9.3. Leitura oferta versus lacuna

O mapa de oferta versus lacuna evita propor capacitações redundantes. Quando há muitos gaps e poucas ofertas, a prioridade é o desenho de nova resposta. Quando há gaps e ofertas ao mesmo tempo, a prioridade é avaliar adequação, cobertura e efetividade da oferta existente.

O eixo `nao_classificado` reúne evidências com sinais de lacuna ou oferta que não atingiram aderência suficiente aos eixos temáticos predefinidos. Na próxima etapa, essas evidências devem ser revisadas para reclassificação, descarte ou eventual criação de novo eixo.

| Eixo | Gaps | Competências | Ofertas | Leitura |
| --- | --- | --- | --- | --- |
| dados_e_tecnologia | 932 | 50 | 47 | lacuna forte com oferta parcial |
| direitos_humanos_e_inclusao | 795 | 34 | 19 | lacuna forte com oferta parcial |
| avaliacao_e_monitoramento | 608 | 74 | 17 | lacuna forte com oferta parcial |
| inovacao_e_transformacao | 449 | 20 | 15 | lacuna forte com oferta parcial |
| atendimento_e_servicos_judiciarios | 390 | 28 | 17 | lacuna forte com oferta parcial |
| nao_classificado | 333 | 23 | 50 | revisão temática pendente |
| gestao_e_governanca | 304 | 69 | 21 | lacuna forte com oferta parcial |
| comunicacao_e_acessibilidade | 275 | 24 | 21 | lacuna forte com oferta parcial |
| saude_e_bem_estar | 199 | 8 | 7 | lacuna forte com oferta parcial |
| equipes_multidisciplinares | 87 | 21 | 5 | lacuna moderada com oferta existente |

### 9.4. Etapa 1 - Curadoria qualificada da evidência

Selecionar uma amostra dirigida, não aleatória simples, combinando:

- as 30 evidências de maior score por eixo prioritário;
- todas as evidências que entraram no dossiê final;
- evidências oriundas de atos normativos classificadas como `competencia_requerida`;
- evidências de notícia e oferta formativa, para confirmar se são contexto, demanda ou resposta existente;
- trechos de baixo score que aparecem em muitos documentos, pois podem indicar linguagem institucional recorrente mas ambígua.

Cada evidência deve receber decisão: `confirmar gap`, `confirmar competencia requerida`, `confirmar oferta existente`, `reclassificar`, `descartar` ou `pedir leitura de documento completo`.

### 9.5. Etapa 2 - Triangulação por tipo de fonte

Para cada eixo prioritário, cruzar três matrizes:

- diagnósticos e relatórios que apontam problemas observados;
- normas, guias e programas que estabelecem competências ou obrigações;
- cursos, capacitações e notícias que indicam resposta formativa existente.

Essa triangulação permite separar quatro situações:

- `gap forte`: problema observado em relatório e competência exigida por norma, sem oferta suficiente mapeada.
- `gap com resposta parcial`: problema observado e oferta existente, mas ainda com evidência de dificuldade ou baixa cobertura.
- `competencia normativa sem diagnostico`: norma exige capacidade, mas o corpus ainda não demonstra lacuna empírica.
- `oferta sem gap demonstrado`: há curso ou notícia, mas sem evidência suficiente de necessidade não atendida.

### 9.6. Etapa 3 - Tradução pedagógica dos gaps

Cada gap confirmado deve ser convertido em ficha pedagógica contendo:

- descrição do gap em linguagem institucional;
- evidências documentais principais;
- público-alvo provável;
- competência central a desenvolver;
- tipo de resposta recomendado;
- carga de esforço estimada;
- indicadores de resultado;
- riscos de implementação;
- dependência normativa ou tecnológica.

Essa ficha é o ponto de passagem entre pesquisa documental e desenho de oferta educacional.

### 9.7. Etapa 4 - Validação institucional

Submeter as fichas a um ciclo curto de validação com ENAJU, escolas judiciais e áreas técnicas relacionadas ao eixo. A validação deve perguntar se o gap é reconhecível, se já há iniciativas equivalentes, qual público deve ser priorizado e que tipo de resposta tem maior chance de adesão.

### 9.8. Entregáveis da análise robusta

Ao final da etapa seguinte, produzir:

- matriz revisada de gaps confirmados;
- mapa de competências requeridas por eixo;
- mapa de oferta existente versus gap;
- dossiê de evidências validadas;
- fichas pedagógicas por gap prioritário;
- plano de intervenção formativa com ondas de implementação;
- critérios de monitoramento e avaliação.

### 9.9. Foco documental para a próxima rodada

As fontes que mais devem orientar a revisão qualificada são:

| Tipo de fonte | Classe | Eixo | Evidências | Documentos |
| --- | --- | --- | --- | --- |
| relatorio_diagnostico_pesquisa | gap_observado | dados_e_tecnologia | 927 | 34 |
| relatorio_diagnostico_pesquisa | gap_observado | direitos_humanos_e_inclusao | 789 | 33 |
| relatorio_diagnostico_pesquisa | gap_observado | avaliacao_e_monitoramento | 600 | 29 |
| relatorio_diagnostico_pesquisa | gap_observado | inovacao_e_transformacao | 448 | 19 |
| relatorio_diagnostico_pesquisa | gap_observado | atendimento_e_servicos_judiciarios | 383 | 34 |
| relatorio_diagnostico_pesquisa | gap_observado | nao_classificado | 330 | 27 |
| relatorio_diagnostico_pesquisa | gap_observado | gestao_e_governanca | 295 | 30 |
| relatorio_diagnostico_pesquisa | gap_observado | comunicacao_e_acessibilidade | 267 | 24 |
| relatorio_diagnostico_pesquisa | gap_observado | saude_e_bem_estar | 194 | 23 |
| relatorio_diagnostico_pesquisa | gap_observado | equipes_multidisciplinares | 85 | 19 |

As competências normativas mais relevantes para leitura dirigida são:

| Eixo | Competência | Fonte | Evidências | Documentos |
| --- | --- | --- | --- | --- |
| gestao_e_governanca | competencia_a_qualificar | ato_normativo | 40 | 6 |
| avaliacao_e_monitoramento | competencia_a_qualificar | ato_normativo | 34 | 4 |
| avaliacao_e_monitoramento | competencia_a_qualificar | relatorio_diagnostico_pesquisa | 19 | 9 |
| comunicacao_e_acessibilidade | acessibilidade e comunicacao inclusiva | ato_normativo | 18 | 11 |
| dados_e_tecnologia | competencia_a_qualificar | relatorio_diagnostico_pesquisa | 17 | 9 |
| atendimento_e_servicos_judiciarios | competencia_a_qualificar | ato_normativo | 17 | 7 |
| direitos_humanos_e_inclusao | competencia_a_qualificar | relatorio_diagnostico_pesquisa | 15 | 8 |
| dados_e_tecnologia | competencia_a_qualificar | ato_normativo | 15 | 4 |

### 9.10. Critério de encerramento

Um gap só deve virar proposta de plano formativo quando cumprir pelo menos três critérios: evidência documental rastreável, interpretação confirmada por curadoria, público-alvo plausível, relação clara com competência ou capacidade institucional, e ausência ou insuficiência demonstrada de oferta equivalente. Esse critério reduz o risco de converter todo problema organizacional em curso e preserva a qualidade da recomendação final.


## 10. Conclusão

O pacote produzido oferece uma base objetiva, rastreável e replicável para transformar produções do CNJ em uma agenda inicial de capacitação. A principal contribuição é criar um funil metodológico: primeiro identifica sinais documentais em escala, depois distingue a natureza da evidência, em seguida prioriza e, por fim, direciona uma análise humana mais robusta apenas para os gaps de maior relevância, risco ou potencial de decisão.
