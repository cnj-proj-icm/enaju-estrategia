# Governança mínima — CADERNOS_ENAJU

> Define papéis, responsabilidades e o fluxo de decisão do projeto.

## Papéis e responsabilidades

| Papel | Responsabilidade | Titular |
| --- | --- | --- |
| CODE | Coordenação geral, curadoria institucional, pactuação e supervisão | A definir |
| Coordenação científica | Desenho metodológico, critérios de qualidade, agenda de pesquisa | A definir |
| Coordenação editorial | Linha editorial, padronização dos cadernos e revisão | A definir |
| Apoio técnico | Operação de VS Code, GitHub, automações e organização de dados | A definir |
| Parceiros | Participação em pilotos, validação de insumos, eventual replicação | A definir |

## Fluxo de decisão

1. Propostas entram como [Issue](../../.github/ISSUE_TEMPLATE/) (caderno,
   protocolo ou trilha).
2. A coordenação correspondente avalia escopo, mérito e prioridade.
3. Itens aprovados viram branch `feature/*` e seguem o pipeline editorial.
4. A integração em `main` exige Pull Request revisado e validação institucional.
5. Decisões estruturantes são registradas em
   [ficha-projeto.md](../../ficha-projeto.md) (seção Decisões).

## Pipeline editorial

```
backlog → em curadoria → em redação → em revisão → em validação institucional → publicado
```

| Estágio | Responsável principal | Critério de saída |
| --- | --- | --- |
| backlog | CODE | Issue priorizada |
| em curadoria | Coord. científica | Base teórica/bibliográfica suficiente |
| em redação | Coord. editorial | Minuta completa |
| em revisão | Agente de revisão + humano | Conformidade e consistência |
| em validação institucional | CODE | Aprovação formal |
| publicado | CODE | Artefato exportado e divulgado |

## Qualidade e conformidade

- Toda saída de agente passa por **revisão humana** antes de virar produto.
- Dados de pessoas seguem **LGPD**, TCLE e anonimização (ver protocolos).
- Citações e proveniência são obrigatórias; nada de evidência sem fonte.
- A validação documental automatizada (`validar_estrutura.py`) precisa passar
  antes da integração.

## Cadência

| Ritual | Frequência | Objetivo |
| --- | --- | --- |
| Revisão de backlog | Quinzenal | Priorizar e destravar itens |
| Revisão editorial | Por entregável | Garantir padrão e coerência |
| Checkpoint institucional | Por fase | Validar marcos com a CODE |
