# Rotina de Trabalho

Esta rotina ajuda a manter o workspace organizado quando varios projetos coexistem no mesmo repositorio.

## Ciclo Simples

```text
1. Registrar demanda
2. Criar ficha de projeto
3. Separar insumos
4. Produzir fonte editavel
5. Revisar
6. Publicar entregavel
7. Atualizar inventario
```

## Antes de Criar um Projeto

Verifique se a demanda ja pertence a uma pasta existente:

| Se for sobre... | Verificar primeiro |
| --- | --- |
| Competencias, LNC, inteligencia educacional | `radar-competencias-enaju` |
| Foresight, futuros, sinais, oficinas | `design-futuros` |
| Simulador ou produto web | `futuros-da-justica` |
| Bibliometria GCPJ, artigo RAP/FGV | `enaju-gcpj` |
| Artigo ENAJUS 2026 | `Inputs/Artigo ENAJUS 2026`, `Fontes/Artigo ENAJUS 2026`, `Outputs/Artigo ENAJUS 2026` |
| Ideia ainda aberta | `Backlog/` |

## Como Criar um Novo Projeto

1. Crie uma pasta em `Projetos/nome-curto-do-projeto/`.
2. Copie `00_CENTRAL_ENAJU/templates/FICHA_PROJETO.md`.
3. Renomeie a copia para `ficha-projeto.md`.
4. Preencha objetivo, responsavel, status, entregaveis e proximos passos.
5. Crie subpastas conforme a necessidade:

```text
Inputs/
Fontes/
Outputs/
docs/
scripts/
dados/
```

6. Atualize `04_INVENTARIO_ATUAL.md` quando o projeto entrar na carteira ativa.

## Revisao e Entregaveis

| Momento | Conferir |
| --- | --- |
| Antes da revisao | O arquivo-fonte esta em `Fontes/` ou na pasta do projeto? |
| Antes de publicar | O entregavel final esta em `Outputs/` ou `outputs/`? |
| Depois de publicar | O README/ficha informa onde esta a versao final? |
| Depois de concluir | O status foi atualizado? |

## Uso de Git

Fluxo basico:

```powershell
git pull
git status
git add .
git commit -m "descreva a mudanca"
git push
```

Mensagens recomendadas:

| Tipo | Exemplo |
| --- | --- |
| Documento | `atualiza guia de acesso da central ENAJU` |
| Projeto novo | `cria ficha do projeto observatorio ENAJU` |
| Relatorio | `adiciona versao revisada do relatorio ENAJUS` |
| Codigo | `ajusta pipeline do radar de competencias` |

## Checklist de Qualidade

- O nome da pasta e claro.
- O projeto tem README ou ficha.
- Inputs e Outputs nao estao misturados.
- O arquivo final e facil de encontrar.
- Nao ha senhas, chaves ou dados sensiveis indevidos.
- O inventario foi atualizado quando necessario.

