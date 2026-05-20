# ✅ Proximos Passos e Fluxo de Trabalho

Este arquivo e o painel de bordo do workspace ENAJU. Abra-o sempre que entrar no projeto para lembrar o que esta pendente, por onde recomecar e qual fluxo seguir.

## 🚀 Comece por Aqui

```text
1. Atualizar o repositorio central
2. Atualizar os repositorios vinculados
3. Verificar pendencias no Git
4. Escolher uma frente de trabalho
5. Registrar o que foi feito
6. Fazer commit e push
```

Comandos:

```powershell
git pull
git submodule update --init --recursive
git status
```

Se for trabalhar dentro de um projeto vinculado, entre na pasta dele e rode:

```powershell
git pull
git status
```

## 📌 Pendencias Principais

| | Prioridade | Pendencia | Onde mexer | Resultado esperado | Status |
| --- | --- | --- | --- | --- | --- |
| 🟢 | Alta | Revisar a central ENAJU no GitHub e confirmar se a navegacao esta clara | `00_CENTRAL_ENAJU/` | Central facil de explicar para outras pessoas | Feito - manter revisao continua |
| 🟢 | Alta | Criar fichas curtas dos projetos ativos | `Projetos/` ou pasta de cada projeto | Cada frente com objetivo, responsavel, status e proximo marco | Feito - primeira versao |
| 🟡 | Alta | Decidir quais projetos ficam como submodulos e quais ficam apenas como links | `.gitmodules` e `05_REPOS_EXISTENTES.md` | Carteira sem duplicidade ou confusao | Parcial - `balanco-socio-10` classificado como relacionado |
| 🟢 | Media | Atualizar o inventario depois de cada mudanca relevante | `04_INVENTARIO_ATUAL.md` | Mapa sempre confiavel do workspace | Atualizado |
| 🟡 | Media | Organizar novos documentos em `Inputs`, `Fontes` e `Outputs` | Pastas estruturais | Separar insumos, fontes editaveis e entregaveis finais | Continuo |
| 🟢 | Media | Criar backlog de oportunidades derivado dos 13 projetos do Art. 19 | `Backlog/` | Lista priorizada de proximas iniciativas | Feito - primeira versao |

## 🧭 Frentes de Trabalho

### 🏠 1. Central ENAJU

Objetivo: manter o repositorio `ENAJU` como porta de entrada institucional.

Proximas acoes:

| | Acao | Arquivo/pasta |
| --- | --- | --- |
| 🗣️ | Revisar linguagem dos guias para publico nao tecnico | `00_CENTRAL_ENAJU/*.md` |
| 🔗 | Conferir se todos os links funcionam no GitHub | `README.md` e `00_CENTRAL_ENAJU/README.md` |
| 🧩 | Atualizar a lista de repositorios vinculados | `00_CENTRAL_ENAJU/05_REPOS_EXISTENTES.md` |
| ✅ | Manter este painel atualizado | `00_CENTRAL_ENAJU/06_PROXIMOS_PASSOS.md` |

### 🏛️ 2. Estrategia e Governanca ENAJU

Objetivo: transformar planos e competencias em carteira operacional.

Proximas acoes:

| | Acao | Arquivo/pasta |
| --- | --- | --- |
| 📚 | Revisar os planos ja movidos para `Inputs/Planos` | `Inputs/Planos/` |
| ✅ | Converter os 13 projetos estrategicos em backlog priorizado | `Backlog/2026-05-carteira-art19-enaju.md` |
| ✅ | Criar fichas para os projetos mais importantes | `Projetos/` |
| 🎯 | Definir status, responsavel e proximo marco de cada projeto | `Projetos/*/ficha-projeto.md` |

### 🔗 3. Projetos Vinculados

Objetivo: manter cada repositorio proprio organizado e conectado a central.

| | Projeto | Proxima verificacao | Comando util |
| --- | --- | --- | --- |
| 🔮 | `design-futuros` | Ver roadmap, produtos e entregaveis de foresight | `git -C design-futuros status` |
| 📊 | `enaju-gcpj` | Ver pipeline, artigo e outputs bibliometricos | `git -C enaju-gcpj status` |
| 💻 | `futuros-da-justica` | Ver app, dados YAML e testes | `git -C futuros-da-justica status` |
| 📡 | `radar-competencias-enaju` | Ver dashboard, pipeline e relatorios | `git -C radar-competencias-enaju status` |
| 📘 | `balanco-socio-10` | Projeto relacionado ao CNJ; validar se deve permanecer no workspace ENAJU | `git -C balanco-socio-10 status` |

Quando atualizar um submodulo:

```powershell
git -C nome-do-projeto pull
git status
git add nome-do-projeto
git commit -m "chore: atualiza ponteiro de nome-do-projeto"
git push
```

### 📣 4. Publicacoes e Entregaveis

Objetivo: separar rascunhos, fontes e versoes finais.

Proximas acoes:

| | Acao | Onde |
| --- | --- | --- |
| 📝 | Conferir o estado do Artigo ENAJUS 2026 | `Inputs/Artigo ENAJUS 2026`, `Fontes/Artigo ENAJUS 2026`, `Outputs/Artigo ENAJUS 2026` |
| 🏷️ | Registrar qual arquivo e a versao mais atual | README ou nota dentro da pasta do artigo |
| 🗂️ | Separar documentos de referencia de produtos finais | `Inputs/`, `Fontes/`, `Outputs/` |

## 🔁 Rotina de Entrada

Sempre que abrir o workspace:

1. Abra `00_CENTRAL_ENAJU/06_PROXIMOS_PASSOS.md`.
2. Rode `git status`.
3. Se houver mudancas, entenda se sao suas, de outro agente ou de arquivos gerados.
4. Atualize submodulos se necessario.
5. Escolha uma unica frente para trabalhar.
6. Antes de fechar, atualize este arquivo se alguma pendencia mudou.

## 📤 Rotina de Saida

Antes de encerrar:

```powershell
git status
git add caminho/do/arquivo
git commit -m "mensagem objetiva"
git push
```

Checklist:

| | Pergunta | Sim/Nao |
| --- | --- | --- |
| 🧾 | O que fiz esta registrado em algum README, ficha ou nota? |  |
| 📦 | O entregavel final esta em `Outputs/` ou na pasta correta? |  |
| 🗺️ | O inventario precisa ser atualizado? |  |
| 🔗 | Algum submodulo foi atualizado e precisa ter o ponteiro commitado? |  |
| 🔒 | Nao ha credenciais, chaves ou dados sensiveis no commit? |  |

## ⚖️ Decisoes a Tomar

| | Decisao | Por que importa | Status |
| --- | --- | --- | --- |
| 👤 | Quem sera o dono institucional de cada frente | Evita projetos sem responsavel claro | Pendente |
| 🧩 | Se `balanco-socio-10` deve continuar como submodulo da central ENAJU | Evita mistura entre projetos ENAJU e projetos CNJ relacionados | Pendente |
| 🗓️ | Qual cadencia de revisao da carteira | Mantem o portfolio vivo | Pendente |
| 📦 | Onde publicar entregaveis finais oficiais | Facilita acesso e evita versoes concorrentes | Pendente |

## 📝 Notas Rapidas

- Use `Backlog/` para ideias ainda abertas.
- Use `Projetos/` para iniciativas novas em estruturacao.
- Use `Inputs/` para insumos e referencias.
- Use `Fontes/` para arquivos editaveis.
- Use `Outputs/` para entregaveis finais.
- Use os repositorios vinculados para codigo, pipelines e produtos com vida propria.
