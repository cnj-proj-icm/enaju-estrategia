# Repositorios Existentes Vinculados

Este workspace usa o repositorio `ENAJU` como central e mantem alguns projetos como repositorios vinculados. Assim, cada projeto preserva seu historico, issues, workflows e publicacoes proprias, enquanto a ENAJU ganha uma porta de entrada unica.

## Repositorios

| Pasta no workspace | Repositorio remoto | Papel |
| --- | --- | --- |
| `design-futuros` | `https://github.com/enap-proj-ic/design-futuros` | Programa de foresight, futurismo publico, oficinas, produtos e bibliometria |
| `enaju-gcpj` | `https://github.com/cnj-proj-icm/enaju-gcpj` | Pesquisa bibliometrica sobre educacao corporativa publica e judiciaria |
| `futuros-da-justica` | `https://github.com/cnj-proj-icm/futuros-da-justica` | Simulador de cenarios, competencias, trilhas e acoes |
| `radar-competencias-enaju` | `https://github.com/cnj-proj-icm/radar-competencias-enaju` | Radar nacional de competencias e dashboard de inteligencia educacional |

## Como Clonar Tudo

Use:

```powershell
git clone --recurse-submodules https://github.com/cairesmachado-svg/ENAJU.git
cd ENAJU
```

Se voce ja clonou sem os submodulos:

```powershell
git submodule update --init --recursive
```

Para atualizar a central e os projetos vinculados:

```powershell
git pull
git submodule update --init --recursive --remote
```

## Como Trabalhar

| Tarefa | Onde fazer |
| --- | --- |
| Ajustar guias, inventario e organizacao geral | Repositorio central `ENAJU` |
| Alterar codigo ou documentos de um projeto especifico | Dentro da pasta do projeto vinculado |
| Atualizar o ponteiro do projeto na central | Commit no `ENAJU` apos atualizar o submodulo |
| Criar projeto novo ainda sem repositorio proprio | `Projetos/` |

## Atencao

Quando uma pasta e submodulo, ela tem vida propria. Alteracoes feitas dentro dela precisam ser commitadas e enviadas no repositorio daquele projeto; depois, o repositorio central `ENAJU` registra a nova versao apontada.
