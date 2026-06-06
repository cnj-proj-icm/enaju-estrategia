# data — insumos, processados e saídas

Camada de dados do projeto. **O conteúdo destas pastas não é versionado** (ver
[`.gitignore`](../.gitignore)), exceto os `.gitkeep` e os dicionários.

| Pasta | Conteúdo | Versionado? |
| --- | --- | --- |
| `raw/` | Dados brutos anonimizados, como recebidos | Não |
| `processed/` | Dados limpos e consolidados (CSV/Parquet) | Não |
| `dictionaries/` | Dicionários de variáveis e tabelas de domínio | Sim (sem microdados) |
| `outputs/` | Tabelas, relatórios e exportações geradas | Não |

## Regras

- **Nunca** colocar aqui microdados identificáveis de pessoas.
- A coleta exige TCLE e anonimização (ver
  [protocolo-piloto](../docs/protocolos/protocolo-rei40-piloto.md)).
- Registrar a proveniência (origem, data, instrumento) de cada conjunto.
- Saídas para publicação seguem para `outputs/` e são exportadas por
  `src/reports/`.
