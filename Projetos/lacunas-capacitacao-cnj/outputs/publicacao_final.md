# Modelo de priorizacao de capacitacoes para escolas judiciais a partir de evidencias documentais do CNJ

## 1. Resumo executivo

Este documento apresenta uma proposta tecnica para identificar lacunas de capacitacao em producoes do CNJ e converte-las em um portfolio inicial de trilhas e capacitacoes. O produto combina coleta documental, identificacao automatizada de evidencias, score composto, matriz de priorizacao e alertas de risco.

**Status da entrega:** PROPOSTA TECNICA - priorizacao automatizada com amostra de calibracao estruturada.

## 2. Corpus e alcance

A linha de base `baseline-2026-05-31` considera a fotografia editorial de `2026-05-31` do portal de Pesquisas Judiciarias do CNJ. O corpus processado contem `84` documentos e 3100 evidencias unicas em 5034 linhas evidencia-eixo consideradas para a etapa de sintese.

O estudo nao mede demanda de cursistas, orcamento, capacidade operacional das escolas ou prioridade politica. Ele organiza sinais documentais para apoiar decisao pedagogica posterior.

## 3. Metodo de priorizacao

A priorizacao usa um score composto:

`score_final = 0,45 * score_textual_norm + 0,30 * consistencia_evidencial + 0,25 * valor_institucional`

- `score_textual_norm`: intensidade lexical e contextual do trecho, limitada a 1,0.
- `consistencia_evidencial`: recorrencia do eixo e distribuicao em documentos distintos.
- `valor_institucional`: peso configurado por eixo tematico em `config/criterios_analiticos.yml`.
- faixas de decisao: alta (`>= 0,75`), media (`>= 0,50`) e baixa (`< 0,50`).

Calibracao: Arquivo de calibracao analitica existe, mas nao contem decisoes revisadas.

## 4. Expansao do universo documental

O corpus expandido separa documentos de diagnostico, atos normativos, guias/manuais, noticias e ofertas formativas. Essa separacao evita que comunicacao institucional ou oferta de curso tenha o mesmo peso probatorio de pesquisa ou diagnostico.

### Distribuicao por origem e tipo de fonte

| Origem | Tipo de fonte | Documentos |
| --- | --- | --- |
| expanded_html | ato_normativo | 36 |
| baseline_pdf | relatorio_diagnostico_pesquisa | 35 |
| expanded_html | oferta_formativa | 4 |
| expanded_html | pagina_programa | 4 |
| expanded_html | relatorio_diagnostico_pesquisa | 4 |
| expanded_html | noticia_cnj | 1 |

### Lacunas por tipo de fonte

| Tipo de fonte | Classe | Eixo | Evidencias | Documentos |
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

### Competencias requeridas por normas, guias e programas

| Eixo | Competencia | Fonte | Evidencias | Documentos |
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

| Eixo | Gaps | Competencias | Ofertas | Leitura |
| --- | --- | --- | --- | --- |
| dados_e_tecnologia | 932 | 50 | 47 | oferta_e_lacuna_mapeadas |
| direitos_humanos_e_inclusao | 795 | 34 | 19 | oferta_e_lacuna_mapeadas |
| avaliacao_e_monitoramento | 608 | 74 | 17 | oferta_e_lacuna_mapeadas |
| inovacao_e_transformacao | 449 | 20 | 15 | oferta_e_lacuna_mapeadas |
| atendimento_e_servicos_judiciarios | 390 | 28 | 17 | oferta_e_lacuna_mapeadas |
| nao_classificado | 333 | 23 | 50 | oferta_e_lacuna_mapeadas |
| gestao_e_governanca | 304 | 69 | 21 | oferta_e_lacuna_mapeadas |
| comunicacao_e_acessibilidade | 275 | 24 | 21 | oferta_e_lacuna_mapeadas |
| saude_e_bem_estar | 199 | 8 | 7 | oferta_e_lacuna_mapeadas |
| equipes_multidisciplinares | 87 | 21 | 5 | oferta_e_lacuna_mapeadas |

## 5. Resultados priorizados

| Faixa | Proposta | Evidencias | Documentos | Score final |
| --- | --- | --- | --- | --- |
| media | Capacitacao em dados, tecnologia e inteligencia institucional | 1029 | 46 | 0.6656 |
| media | Capacitacao em direitos humanos, inclusao e acessibilidade | 848 | 48 | 0.6411 |
| media | Capacitacao em comunicacao e acessibilidade | 320 | 42 | 0.591 |
| media | Trilha de avaliacao, monitoramento e planejamento estrategico | 699 | 44 | 0.5736 |
| media | Trilha de gestao, governanca e lideranca | 394 | 51 | 0.5709 |
| media | Trilha de atendimento e servicos ao cidadao | 435 | 45 | 0.5567 |
| media | Trilha de inovacao e transformacao digital | 484 | 27 | 0.5157 |
| baixa | Capacitacao em saude e bem-estar institucional | 214 | 31 | 0.4448 |
| baixa | Trilha de formacao de liderancas | 92 | 25 | 0.4443 |
| baixa | Capacitacao para estruturacao e atuacao de equipes multidisciplinares | 113 | 24 | 0.4367 |

## 6. Portfolio recomendado

| Prioridade | Proposta | Publico prioritario | Carga horaria | Modalidade |
| --- | --- | --- | --- | --- |
| media | Capacitacao em dados, tecnologia e inteligencia institucional | gestores, analistas e equipes de dados | 12h a 20h | curso curto com laboratorio aplicado |
| media | Capacitacao em direitos humanos, inclusao e acessibilidade | servidores, gestores e equipes de politicas publicas | 12h a 16h | curso com oficina de aplicacao |
| media | Capacitacao em comunicacao e acessibilidade | equipes de comunicacao, atendimento e gestao de conteudo | 8h a 12h | oficina pratica |
| media | Trilha de avaliacao, monitoramento e planejamento estrategico | gestores e formuladores de politicas | 16h a 24h | trilha curta com mentoria |
| media | Trilha de gestao, governanca e lideranca | gestores, chefias e equipes de governanca | 16h a 24h | trilha aplicada |
| media | Trilha de atendimento e servicos ao cidadao | equipes de atendimento, comunicacao e gestao de servicos | 12h a 18h | curso com simulacao |
| media | Trilha de inovacao e transformacao digital | coordenadores e equipes de inovacao | 16h a 20h | trilha com projeto piloto |
| baixa | Capacitacao em saude e bem-estar institucional | gestores de pessoas, magistrados e equipes de apoio institucional | 12h a 16h | curso com estudo de caso |
| baixa | Trilha de formacao de liderancas | liderancas atuais e potenciais gestores | 20h a 30h | trilha com atividades reflexivas e praticas |
| baixa | Capacitacao para estruturacao e atuacao de equipes multidisciplinares | equipes tecnicas, gestores e unidades de apoio psicossocial | 12h a 20h | curso com oficina de fluxo |

## 7. Evidencias rastreaveis

| Proposta | Documento | Pagina | Score final | Evidencia rastreavel |
| --- | --- | --- | --- | --- |
| Capacitacao em dados, tecnologia e inteligencia institucional | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 44 | 0.9728 | A dificuldade em encontrar profissionais qualificados para atender a pessoas com deficiência foi um dos principais desafios relatados nos formulários. Pouco mais da metade dos(as) respondentes destacou essa questão, sugerindo que há uma escassez de mão de obra especializada, especialmente no contexto judiciário (Figura 14). Isso é agravado pela falta de treinamento adequado para magistrados(as) e servidores(as) em temas de acessibilidade e inclusão. Embora os dados do Painel do Balanço da Sustentabilidade do CNJ indiquem um aumento considerável no investimento em capacitação de gestores(as) em |
| Capacitacao em dados, tecnologia e inteligencia institucional | Pesquisa sobre Percepção e Avaliação do Poder Judiciário Brasileiro | 64 | 0.9728 | falta de capacitação do Poder Judiciário, seguido pelo PJe (14,8%). As dificuldades relacionadas à usabilidade variaram principalmente con­ forme os públicos. O público de advogados(as) indicou essa dificuldade de maneira majoritariamente uniforme entre os sistemas, variando entre 42,4% (SAJ) e 44,3% (PJe). O Projudi foi o mais indicado no que toca à ausência de comunicação entre outros sistemas e/ou cadastros (26,7%). O PJe foi o mais indicado no que toca à dificuldade com formação e edição de textos (10,4%) e com o uso e navegação relacionada a layout, informação e afins (14,1%). O e-Proc fo |
| Capacitacao em dados, tecnologia e inteligencia institucional | Pesquisa sobre Percepção e Avaliação do Poder Judiciário Brasileiro | 63 | 0.9728 | (14,7%), no que toca à ausência de pessoal responsável para realizar apoio técnico e à falta de capacitação do Poder Judiciário. Vale também mencionar que as dificuldades menos mencionadas entre os(as) advogados(as) foram a dificuldade com formatação e edição de textos (8,2%), problemas de tráfego de rede e internet (12,9%) e falta de automação de alguns procedimentos (15,9%). Já os(as) defensores(as) tiveram menos apontamentos de problemas com certificados digitais (7,9%), dificuldade com formatação e edição de textos (9,3%) e dificuldade de uso e navegação rela­ cionada a layout, informação  |
| Capacitacao em direitos humanos, inclusao e acessibilidade | Avaliação sobre a aplicação das Medidas Protetivas de Urgência da Lei Maria da Penha | 139 | 0.9523 | cotidianas, o uso de dados e a alimentação dos sistemas utilizados pelo Datajud para a extração de metadados a serem publicados no Painel Nacional das Medidas Protetivas de Urgência, os quais podem subsidiar o aperfeiçoamento de programas e políticas com vistas à melhor implementação da LMP, notadamente no tocante à proteção das mulheres em situação de violência por meio das Medidas Protetivas de Urgência. Os grupos salientaram a importância do acesso e alimentação dos dados, destacando que ainda convivem com a resistência, por parte de muitos colegas, diante do próprio conceito de violência d |
| Capacitacao em direitos humanos, inclusao e acessibilidade | 2º Censo do Poder Judiciário 2023 | 123 | 0.9523 | 123 Figura 110: Percepção dos(as) servidores(as) sobre dificuldade nos processos de promoção e progressão na carreira 10,8% 0,6% 2,6% 0,5% 0,8% 2,1% 1,3% 0,5% 1,9% 83,4% De sua orientação sexual De sua religião De ser pessoa com deficiência De sua origem geográfica De sua raça/cor Do gênero com que se identifica De sua origem social De sua idade De outra natureza Não considero sofrer ou ter sofrido dificuldades 0% 25% 50% 75% 100% Fonte: Conselho Nacional de Justiça, 2023. Conforme Figura 111, foi perguntado aos(às) servidores(as) se já sofreram ou sofrem algum episódio de assédio relacionado  |
| Capacitacao em direitos humanos, inclusao e acessibilidade | Pesquisa sobre Tendência Organizacional e a Capacidade Institucional dos Tribunais Brasileiros para a Inovação | 23 | 0.9523 | 23 Quadro 3 – Antecedentes organizacionais N. Afirmativas Categorias 1 Há diversidade (idade, gênero, formação, trajetória profissional etc.) na composição da equipe. Diversidade na equipe 2 O nosso setor possui recursos técnicos e financeiros adequados para desenvolver e implemen­ tar ideias inovadoras para atender às demandas dos usuários (internos ou externos). Recursos técnicos e financeiros 3 No nosso setor, as inovações são desenvolvidas e implementadas em conjunto, muitas ve­ zes com colaboração de pessoas de outros setores e que possuem formação e experiência diversificada. Trabalho em |
| Trilha de avaliacao, monitoramento e planejamento estrategico | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 43 | 0.9063 | com frequência significativa (36,0%). Outros desafios mencionados incluem a falta de infraestrutura acessível e a inexistência de mecanismos efetivos de monitoramento e avaliação das ações. Esses resultados evidenciam a complexidade do cenário enfrentado e reforçam a necessidade de ações integradas para superar tais barreiras (Figura 14). Figura 14 - Percentual de respondentes sobre os desafios de implementar ações para acessibilidadeo gráfico apresenta nove barras horizontais, cada uma representando a frequência percentual dos desafios enfrentados na gestão de iniciativas de acessibilidade, c |
| Trilha de avaliacao, monitoramento e planejamento estrategico | Pesquisa sobre Tendência Organizacional e a Capacidade Institucional dos Tribunais Brasileiros para a Inovação | 195 | 0.9063 | 195 Codex, as audiências virtuais, o Balcão Virtual, a ampla adoção do teletrabalho durante a pandemia, a disseminação do uso de dashboards de apoio à gestão, entre outras iniciativas. • Mas os(as) entrevistados(as) apontaram como um dos principais desafios a exclusão digital e, portanto, a impossibilidade de parte da sociedade acessar os serviços judiciários disponibilizados eletronicamente. • A desigualdade digital foi identificada também entre os(as) advogados(as), pois nem todos têm acesso aos equipamentos mais modernos • As questões regionais também afetam a comunicação digital, principal |
| Trilha de avaliacao, monitoramento e planejamento estrategico | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 106 | 0.9063 | e o engajamento dos(as) participantes, além de incluir instrumentos de avaliação da aprendizagem para garantir a efetividade dos conteúdos ministrados. As capacitações devem ser oferecidas de forma permanente, podendo ser disponibilizadas em plataformas de Ensino a Distância (EAD) com sistemas de gerenciamento da aprendizagem, permitindo acesso a qualquer tempo e facilitando a adesão de todos os públicos envolvidos. Participação de instrutores com deficiência: incluir profissionais com deficiência nos corpos docentes dos cursos, enriquecendo a capacitação com vivências e perspectivas práticas. |
| Trilha de gestao, governanca e lideranca | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 43 | 0.8574 | com frequência significativa (36,0%). Outros desafios mencionados incluem a falta de infraestrutura acessível e a inexistência de mecanismos efetivos de monitoramento e avaliação das ações. Esses resultados evidenciam a complexidade do cenário enfrentado e reforçam a necessidade de ações integradas para superar tais barreiras (Figura 14). Figura 14 - Percentual de respondentes sobre os desafios de implementar ações para acessibilidadeo gráfico apresenta nove barras horizontais, cada uma representando a frequência percentual dos desafios enfrentados na gestão de iniciativas de acessibilidade, c |
| Trilha de gestao, governanca e lideranca | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 41 | 0.8574 | que pode explicar a diversidade na forma de planejar pode estar na insuficiente previsão orçamentária para essas ações. Toni (2019), em seu estudo sobre planejamento estratégico no setor público, destaca que a falta de orçamento adequado pode levar a uma série de problemas na administração pública, incluindo a duplicação de esforços, a falta de coordenação entre diferentes planos e projetos e, em última análise, a ineficiência administrativa. A administração pública enfrenta diversos desafios na gestão orçamentária para ações de acessibilidade, incluindo: dificuldades em alocar recursos sufici |
| Trilha de gestao, governanca e lideranca | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 71 | 0.8574 | a necessidade de incluir tecnologias assistivas e acessibilidade digital como parte das capacitações (MAG7), ampliando o conhecimento dos(as) servidores(as) sobre os direitos das pessoas com deficiência. Eu acho importante ter [capacitação em Libras] para o servidor poder atender essas pessoas (Trecho de entrevista com promotor(a) de justiça — MP6). Capacitar juízes e servidores para esses sistemas (Trecho de entrevista com magistrado(a) — MAG7). Quando perguntados sobre quais tipos de capacitação e treinamento em acessibilidade e inclusão deveriam ser priorizados pela gestão, quase 80% dos tr |
| Trilha de atendimento e servicos ao cidadao | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 44 | 0.8458 | A dificuldade em encontrar profissionais qualificados para atender a pessoas com deficiência foi um dos principais desafios relatados nos formulários. Pouco mais da metade dos(as) respondentes destacou essa questão, sugerindo que há uma escassez de mão de obra especializada, especialmente no contexto judiciário (Figura 14). Isso é agravado pela falta de treinamento adequado para magistrados(as) e servidores(as) em temas de acessibilidade e inclusão. Embora os dados do Painel do Balanço da Sustentabilidade do CNJ indiquem um aumento considerável no investimento em capacitação de gestores(as) em |
| Trilha de atendimento e servicos ao cidadao | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 71 | 0.8458 | a necessidade de incluir tecnologias assistivas e acessibilidade digital como parte das capacitações (MAG7), ampliando o conhecimento dos(as) servidores(as) sobre os direitos das pessoas com deficiência. Eu acho importante ter [capacitação em Libras] para o servidor poder atender essas pessoas (Trecho de entrevista com promotor(a) de justiça — MP6). Capacitar juízes e servidores para esses sistemas (Trecho de entrevista com magistrado(a) — MAG7). Quando perguntados sobre quais tipos de capacitação e treinamento em acessibilidade e inclusão deveriam ser priorizados pela gestão, quase 80% dos tr |
| Trilha de atendimento e servicos ao cidadao | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 91 | 0.8458 |  em tecnologia assistiva para seus(suas) servidores(as), o que limita o uso eficiente dos sistemas por parte de pessoas com deficiência (Figura 49). Participantes do estudo relataram a necessidade urgente de treinamento, especialmente para juízes(as) e servidores(as) que interagem com esses sistemas no dia a dia. A falta de formação adequada resulta em falhas de usabilidade, como mencionado por um(a) participante: O chefe já tinha pedido várias vezes pra TI, e a TI não acessibilizou o sistema” (Trecho de entrevista com servidor(a) — S1). Não existe software e nem orientação da unidade de TI co |
| Capacitacao em comunicacao e acessibilidade | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 85 | 0.8152 | alternativas de segurança que não dependam da verificação manual pelo usuário, reduzindo, assim, as barreiras de acessibilidade (Moreno et al., 2014). Adicionalmente, CAPTCHAs com textos distorcidos dificultam a interação de usuários com dificuldades de aprendizagem, gerando frustração e reduzindo a taxa de sucesso nesses testes. Isso reforça a necessidade de CAPTCHAs mais acessíveis que considerem diferentes tipos de deficiência (Gafni; Nagar, 2016). A falta de rótulos em campos de formulários representa um obstáculo crítico para usuários com deficiência visual, pois impede que softwares leit |
| Capacitacao em comunicacao e acessibilidade | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 43 | 0.8152 | com frequência significativa (36,0%). Outros desafios mencionados incluem a falta de infraestrutura acessível e a inexistência de mecanismos efetivos de monitoramento e avaliação das ações. Esses resultados evidenciam a complexidade do cenário enfrentado e reforçam a necessidade de ações integradas para superar tais barreiras (Figura 14). Figura 14 - Percentual de respondentes sobre os desafios de implementar ações para acessibilidadeo gráfico apresenta nove barras horizontais, cada uma representando a frequência percentual dos desafios enfrentados na gestão de iniciativas de acessibilidade, c |
| Capacitacao em comunicacao e acessibilidade | Diagnóstico sobre acessibilidade e inclusão da pessoa com deficiência nos órgãos do Poder Judiciário | 44 | 0.8152 | A dificuldade em encontrar profissionais qualificados para atender a pessoas com deficiência foi um dos principais desafios relatados nos formulários. Pouco mais da metade dos(as) respondentes destacou essa questão, sugerindo que há uma escassez de mão de obra especializada, especialmente no contexto judiciário (Figura 14). Isso é agravado pela falta de treinamento adequado para magistrados(as) e servidores(as) em temas de acessibilidade e inclusão. Embora os dados do Painel do Balanço da Sustentabilidade do CNJ indiquem um aumento considerável no investimento em capacitação de gestores(as) em |

## 8. Limitacoes e riscos

- 1550 trechos apresentam score textual baixo (< 3); devem ser lidos como hipoteses tecnicas.
- 7 evidencias repetem o mesmo documento e trecho; a sintese consolida a mensagem para reduzir duplicidade.
- 1792 evidencias foram classificadas como potenciais; elas apoiam recomendacoes, mas nao constituem conclusoes institucionais isoladas.

As evidencias automatizadas devem ser lidas como subsidio tecnico. A decisao final sobre oferta educacional, sequenciamento, carga horaria e publico prioritario deve considerar validacao institucional, disponibilidade de instrutores, calendario e capacidade de execucao.

## 9. Conclusao

O pacote produzido oferece uma base objetiva, rastreavel e replicavel para transformar producoes do CNJ em uma agenda inicial de capacitacao. A principal contribuicao e reduzir a dependencia de revisao manual massiva, mantendo transparencia metodologica, evidencia citavel e limites explicitos para uso institucional.
