# Inventario Atual do Workspace

Leitura realizada a partir da estrutura e dos documentos principais do repositorio local `ENAJU`.

## Sintese

O workspace ja e um repositorio Git e esta conectado ao GitHub em:

```text
https://github.com/cairesmachado-svg/ENAJU
```

Ele contem uma carteira inicial de projetos da ENAJU com foco em:

| Eixo | Conteudo atual |
| --- | --- |
| Estrategia institucional | Plano de acao, portfolio de projetos estrategicos e competencias da Coordenacao de Desenvolvimento Educacional, Pesquisa e Inovacao |
| Pesquisa aplicada | Bibliometria, foresight, educacao corporativa publica e judiciaria |
| Inteligencia educacional | Radar nacional de competencias, classificacao tematica, relatorios e dashboard |
| Produtos digitais | Simulador Futuros da Justica |
| Publicacoes | Artigo ENAJUS 2026, artigo GCPJ, relatorios e manuscritos |
| Evidencias e bases | Inputs, outputs, datasets, figuras, relatorios e bases bibliograficas |

## Projetos e Frentes

| Projeto/pasta | Natureza | Status observado | Onde comecar |
| --- | --- | --- | --- |
| `plano_de_acao_enaju.md` | Diretriz estrategica | Documento estruturado | Abrir arquivo na raiz |
| `projetos_estrategicos_coordenacao.md` | Carteira Art. 19 | Documento estruturado com 13 projetos | Abrir arquivo na raiz |
| `design-futuros` | Programa de foresight e futurismo publico | Repositorio vinculado como submodulo | `design-futuros/README.md` |
| `radar-competencias-enaju` | Inteligencia de competencias | Repositorio vinculado como submodulo | `radar-competencias-enaju/README.md` |
| `futuros-da-justica` | Produto digital | Repositorio vinculado como submodulo | `futuros-da-justica/README.md` |
| `enaju-gcpj` | Pesquisa bibliometrica | Repositorio vinculado como submodulo | `enaju-gcpj/README.md` |
| `Artigo ENAJUS 2026` | Publicacao | Inputs, fontes e outputs distribuidos em pastas | `Inputs/Artigo ENAJUS 2026/` e `Fontes/Artigo ENAJUS 2026/` |
| `balanco-socio-10` | Revisao de relatorio | Subprojeto dentro de `futuros-da-justica` | `futuros-da-justica/balanco-socio-10/README.md` |

## Pastas Estruturais

| Pasta | Papel recomendado | Observacao |
| --- | --- | --- |
| `00_CENTRAL_ENAJU` | Porta de entrada do workspace | Criada para orientar acesso, organizacao e rotina |
| `Backlog` | Ideias e demandas futuras | Atualmente sem arquivos listados |
| `Projetos` | Novos projetos em estruturacao | Atualmente sem arquivos listados |
| `Inputs` | Insumos, textos-base, dados e referencias | Ja contem materiais do Artigo ENAJUS e documentos de competencias |
| `Fontes` | Fontes editaveis de produtos | Ja contem artigo Quarto e figuras |
| `Outputs` | Entregaveis finais | Ja contem versoes e figuras do Artigo ENAJUS |

## Leitura dos Documentos Principais

| Documento | Conteudo identificado |
| --- | --- |
| `plano_de_acao_enaju.md` | Estruturacao da coordenacao, regras CNJ, frentes macro e proximas fases |
| `projetos_estrategicos_coordenacao.md` | 13 projetos derivados das competencias do Art. 19 |
| `design-futuros/README.md` | Programa guarda-chuva de produtos de foresight publico e futuros da justica |
| `design-futuros/produtos/README.md` | Sete produtos: observatorio, laboratorio, radar, metodologias, publicacoes, parcerias e casos |
| `radar-competencias-enaju/README.md` | MVP para mapear competencias estrategicas com pipeline e dashboard |
| `futuros-da-justica/README.md` | Simulador de cenarios futuros, competencias, trilhas e acoes |
| `enaju-gcpj/README.md` | Pipeline bibliometrico global sobre educacao corporativa publica e judiciaria |
| `enaju-gcpj/PESQUISA.md` | Passo a passo de execucao do pipeline R/Quarto |

## Recomendacao de Carteira ENAJU

```mermaid
flowchart TB
    A[Carteira ENAJU] --> B[1. Estrategia e Governanca]
    A --> C[2. Pesquisa e Evidencias]
    A --> D[3. Produtos Digitais]
    A --> E[4. Publicacoes e Difusao]
    A --> F[5. Rede e Parcerias]

    B --> B1[Plano de acao]
    B --> B2[Portfolio Art. 19]
    C --> C1[enaju-gcpj]
    C --> C2[radar-competencias-enaju]
    C --> C3[design-futuros]
    D --> D1[futuros-da-justica]
    E --> E1[Artigo ENAJUS 2026]
    E --> E2[Relatorios e policy papers]
    F --> F1[Parcerias institucionais]
    F --> F2[Laboratorios e oficinas]
```

## Proximas Melhorias Recomendadas

| Prioridade | Acao |
| --- | --- |
| Alta | Criar fichas resumidas para cada projeto ativo em `Projetos/` ou nas pastas existentes. |
| Alta | Definir status, responsavel e proximo marco de cada frente. |
| Media | Mover novas iniciativas para `Projetos/` antes de virarem pastas de primeiro nivel. |
| Media | Padronizar `Inputs`, `Fontes` e `Outputs` nos projetos maiores. |
| Media | Criar um backlog de oportunidades a partir dos 13 projetos estrategicos do Art. 19. |
