# Ficha de Projeto — CADERNOS_ENAJU

## Identificação

| Campo | Preencher |
| --- | --- |
| Nome do projeto | CADERNOS_ENAJU |
| KR (EAB) | B3 · KR 3.1 (CADERNOS_ENAJU) |
| Inciso Art.19 | IV (Observatório ENAJU) |
| Unidade responsável | CODE — Coordenação de Desenvolvimento, Pesquisa e Inovação |
| Eixo | Pesquisa aplicada / Educação judicial / Inovação / Políticas judiciárias |
| Responsável | A definir |
| Coordenação científica | A definir |
| Coordenação editorial | A definir |
| Apoio técnico (VS Code/GitHub/dados) | A definir |
| Status | Estruturação inicial (Fase 1 — Implantação) |
| Data de início | 2026-06-06 |
| Próximo marco | Aprovar o charter e fichar o artigo de validação do REI-40 |

## Problema

Há baixa estruturação de mecanismos contínuos para converter pesquisa aplicada
em produtos pedagógicos e institucionais voltados à educação judicial e à
formulação de políticas judiciárias baseadas em evidências. Ambientes de
inovação e formação operam com diagnósticos fragmentados sobre como
magistrados, gestores e equipes processam informação, aderem a mudanças e
participam da implementação de políticas.

## Objetivo

Instituir o CADERNOS_ENAJU como projeto da CODE para produzir conhecimento
aplicado, fomentar pesquisas em rede e apoiar a elaboração de trilhas formativas
baseadas em evidências, tendo como piloto uma agenda sobre estilos de
pensamento, inovação e políticas judiciárias a partir do REI-40.

## Público-alvo

- CODE e equipes técnicas da ENAJU
- Escolas judiciais e unidades de formação parceiras
- Laboratórios de inovação do sistema de justiça
- Pesquisadores, magistrados, servidores e gestores em educação judicial,
  inovação e políticas judiciárias

## Entregáveis

| Entregável | Formato | Pasta de destino | Status |
| --- | --- | --- | --- |
| Charter e governança | Markdown | `docs/projeto/` | Em rascunho |
| Caderno ENAJU n. 1 | Markdown (e DOCX/PDF na publicação) | `docs/cadernos/` | Estrutura criada |
| Protocolo de pesquisa-piloto (REI-40) | Markdown + YAML | `docs/protocolos/` e `config` | Em rascunho |
| Modelo de TCLE | Markdown | `docs/protocolos/` | Em rascunho |
| Template de trilha baseada em evidências | Markdown | `docs/trilhas/` | Em rascunho |
| Nota técnica da CODE para a ENAJU | Markdown | `docs/notas-tecnicas/` | Pendente |
| Workspace VS Code com agentes | JSON + Markdown | `.vscode/` e `prompts/` | Estrutura criada |
| Repositório versionado com CI | YAML | `.github/` | Estrutura criada |

## Insumos

| Insumo | Local | Observação |
| --- | --- | --- |
| Documento-mãe do projeto | `cadernos_enaju_projeto.md` | Planejamento integral aprovado como base |
| Artigo de validação do REI-40 | `references/` | Referência metodológica inicial; fichar |
| Convenções dos projetos-irmãos | `Projetos/lacunas-capacitacao-cnj/` | Padrão de estrutura e documentação |

## Plano de trabalho

| Etapa | Descrição | Responsável | Prazo | Status |
| --- | --- | --- | --- | --- |
| 1 | Aprovar charter e governança mínima | A definir | Fase 1 (30 dias) | Pendente |
| 2 | Fichar o REI-40 e montar a base bibliográfica | A definir | Fase 2 (30 dias) | Pendente |
| 3 | Fechar protocolo-piloto e TCLE | A definir | Fase 2–3 | Pendente |
| 4 | Redigir o Caderno ENAJU n. 1 | A definir | Fase 3 (45 dias) | Pendente |
| 5 | Derivar template de trilha para um caso | A definir | Fase 4 (30 dias) | Pendente |
| 6 | Nota técnica e roadmap do próximo ciclo | A definir | Fase 5 (15 dias) | Pendente |

## Decisões

| Data | Decisão | Motivo |
| --- | --- | --- |
| 2026-06-06 | Estruturar o projeto em `Projetos/cadernos-enaju/` | Manter a iniciativa no monorepo ENAJU, junto aos projetos-irmãos |
| 2026-06-06 | Seguir a estrutura do documento-mãe com stack Python em `src/` | Alinhar com a convenção de `lacunas-capacitacao-cnj` |
| 2026-06-06 | Uso do REI-40 voluntário e não obrigatório | O projeto estrutura ambiente de pesquisa, não institucionaliza a escala |
| 2026-06-06 | Licenciamento dual (CC BY 4.0 conteúdo / MIT código) como proposta | Conteúdo e código têm naturezas distintas; confirmar na CODE |

## Riscos e pendências

| Item | Impacto | Encaminhamento |
| --- | --- | --- |
| Responsáveis ainda não designados | Pode atrasar o ciclo | Designar antes do fim da Fase 1 |
| Tratamento de dados de pessoas (LGPD) | Risco jurídico e ético | TCLE, anonimização e revisão de conformidade obrigatórios |
| Confundir uso do REI-40 com institucionalização | Risco de leitura equivocada | Reforçar caráter voluntário no caderno e no protocolo |
| Licenciamento não confirmado | Bloqueia publicação externa | CODE deve validar a proposta em `LICENSE` |
| Dependência de agentes sem revisão | Risco de erro propagado | Toda saída de agente passa por revisão humana |
