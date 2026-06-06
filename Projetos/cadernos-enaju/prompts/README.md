# Agentes especializados — CADERNOS_ENAJU

Instruções (system prompts) dos agentes operados no VS Code. Cada agente apoia
uma etapa do ciclo; **toda saída passa por revisão humana** antes de virar
produto.

| Agente | Arquivo | Função |
| --- | --- | --- |
| Editorial | [agente_editorial.md](agente_editorial.md) | Estrutura cadernos e padroniza a linha editorial |
| Metodologia | [agente_metodologia.md](agente_metodologia.md) | Desenha protocolos, variáveis e instrumentos |
| Formação | [agente_formacao.md](agente_formacao.md) | Converte achados em trilhas formativas |
| Dados | [agente_dados.md](agente_dados.md) | Limpa, consolida e analisa dados |
| Curadoria bibliográfica | [agente_curadoria.md](agente_curadoria.md) | Indexa, ficha e compara referências |
| Revisão e conformidade | [agente_revisao.md](agente_revisao.md) | Verifica citação, consistência e LGPD |

## Como usar

1. Abra a tarefa correspondente (ver [.vscode/tasks.json](../.vscode/tasks.json)).
2. Cole o conteúdo do prompt do agente como instrução de sistema.
3. Forneça o contexto (arquivos, escopo, restrições).
4. Revise criticamente a saída antes de commitar.

## Princípios comuns a todos os agentes

- Idioma: português do Brasil; datas em `AAAA-MM-DD`.
- Nenhuma afirmação sem fonte rastreável.
- Respeitar o caráter **voluntário** do REI-40 — nunca tratar como obrigatório.
- Nunca expor microdados de pessoas; respeitar LGPD e anonimização.
- Em caso de incerteza factual, sinalizar explicitamente em vez de inventar.
