# Painel de Cursos — ENAJU (build publicada)

Esta pasta é a **build publicada** do painel de acompanhamento da carteira de
ações educacionais da ENAJU. O site é servido pelo GitHub Pages em:

**https://cnj-proj-icm.github.io/enaju-estrategia/**

## Não edite os arquivos desta pasta

O conteúdo é gerado a partir do repositório de trabalho da ENAJU
(`01-gestao/Agenda-cursos`). Qualquer alteração feita aqui é sobrescrita na
próxima publicação. Para atualizar o painel, rode no repositório de origem:

```powershell
pwsh 01-gestao/Agenda-cursos/scripts/publicar_painel.ps1
```

O script reimporta as bases (Planner/Outlook), copia os arquivos de runtime para
cá, aplica os ajustes da build pública e envia o commit. O workflow
[`painel-cursos-pages.yml`](../.github/workflows/painel-cursos-pages.yml) publica
automaticamente a cada push em `main`.

## Ajustes aplicados nesta build

- `noindex, nofollow` no `index.html` e `robots.txt` bloqueando rastreadores,
  para que o painel não apareça em buscadores;
- os PDFs dos processos SEI **não** são publicados, e o botão "Abrir processo
  PDF" fica oculto via `styles.css`.

## Aviso

O site é público na internet. O login `admin` da página é apenas uma barreira
visual — os arquivos em `data/` são acessíveis diretamente pela URL. Não inclua
aqui dados pessoais sensíveis ou informações sigilosas.
