# 🧱 Mapa Visual de Pastas

Este guia diferencia as pastas do workspace ENAJU por icones e funcao. Os nomes reais das pastas foram preservados para nao quebrar links, submodulos, scripts ou historico Git.

## 🗺️ Legenda Geral

| Icone | Pasta | Funcao | Quando usar |
| --- | --- | --- | --- |
| 🧭 | `00_CENTRAL_ENAJU/` | Porta de entrada e orientacoes | Quando precisar se localizar, consultar tutoriais ou retomar pendencias |
| 🧠 | `Backlog/` | Ideias, demandas e oportunidades | Quando a iniciativa ainda nao virou projeto |
| 🧱 | `Projetos/` | Novas iniciativas em estruturacao | Quando a frente ja tem escopo inicial, mas ainda nao tem repositorio proprio |
| 📥 | `Inputs/` | Insumos, referencias e materiais de entrada | Quando o arquivo serve de base para analise, escrita ou producao |
| ✍️ | `Fontes/` | Arquivos editaveis de produtos | Quando o material e fonte de trabalho, como `.qmd`, figuras e rascunhos |
| 📦 | `Outputs/` | Entregaveis finais | Quando o arquivo esta pronto para revisao, envio, apresentacao ou publicacao |
| 🔮 | `design-futuros/` | Foresight e futurismo publico | Produtos, oficinas, metodologias, sinais e parcerias |
| 💻 | `futuros-da-justica/` | Produto digital | Simulador, dados YAML, app e testes |
| 📡 | `radar-competencias-enaju/` | Inteligencia educacional | Radar de competencias, dashboard, pipelines e relatorios |
| 📊 | `enaju-gcpj/` | Pesquisa bibliometrica | Scripts, dados, artigo e analises bibliometricas |
| 📘 | `balanco-socio-10/` | Relatorio institucional | Revisao, manuscrito e outputs do balanco socioambiental |

## 🧭 Leitura Rapida

```text
ENAJU/
├── 🧭 00_CENTRAL_ENAJU/          orientacao e governanca do workspace
├── 🧠 Backlog/                   ideias e oportunidades
├── 🧱 Projetos/                  projetos novos em estruturacao
├── 📥 Inputs/                    insumos e referencias
├── ✍️ Fontes/                    fontes editaveis
├── 📦 Outputs/                   entregaveis finais
├── 🔮 design-futuros/            foresight e futurismo publico
├── 💻 futuros-da-justica/        simulador e produto digital
├── 📡 radar-competencias-enaju/  radar e inteligencia educacional
├── 📊 enaju-gcpj/                bibliometria e artigo cientifico
└── 📘 balanco-socio-10/          relatorio socioambiental
```

## 🔁 Fluxo por Icones

```text
🧠 Backlog
  -> 🧱 Projetos
  -> 📥 Inputs
  -> ✍️ Fontes
  -> 📦 Outputs
```

Use esse fluxo quando uma ideia estiver amadurecendo ate virar produto final.

## 🔗 Projetos com Vida Propria

Estas pastas sao repositorios vinculados como submodulos:

| Icone | Projeto | Tipo |
| --- | --- | --- |
| 🔮 | `design-futuros/` | Pesquisa, programa e produtos |
| 💻 | `futuros-da-justica/` | Aplicacao Streamlit |
| 📡 | `radar-competencias-enaju/` | Pipeline e dashboard |
| 📊 | `enaju-gcpj/` | Pipeline R/Quarto e artigo |
| 📘 | `balanco-socio-10/` | Relatorio institucional |

Quando alterar um projeto com vida propria, faca commit dentro dele primeiro. Depois volte para a central e registre o novo ponteiro do submodulo.
