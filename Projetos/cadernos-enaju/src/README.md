# src — automação, análise e geração de produtos

Código Python que apoia o ciclo do CADERNOS_ENAJU. Os módulos são contratos:
alguns já têm implementação inicial; outros são esqueletos a desenvolver
conforme o projeto avança.

## Pacotes

| Pacote | Responsabilidade | Estado |
| --- | --- | --- |
| `automation/` | Validação documental e tarefas de manutenção do repositório | `validar_estrutura.py` implementado |
| `analysis/` | Análise descritiva e exploratória dos dados do piloto | Esqueleto |
| `forms/` | Padronização de formulários, planilhas e dicionários | Esqueleto |
| `reports/` | Geração e exportação de cadernos e notas (DOCX/PDF/HTML) | Esqueleto |
| `utils/` | Funções de apoio (E/S, caminhos, proveniência) | Implementação inicial |

## Convenções

- Python 3.12+, formatado com `black`.
- Sem efeitos colaterais ao importar; lógica em funções/`main()`.
- Caminhos relativos à raiz do projeto via `utils.paths`.
- **Nunca** ler ou gravar microdados identificáveis (ver `.gitignore`).

## Execução

```powershell
.\.venv\Scripts\python.exe src\automation\validar_estrutura.py
.\.venv\Scripts\python.exe -m pytest
```
