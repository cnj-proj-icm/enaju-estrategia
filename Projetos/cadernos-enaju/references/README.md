# references — base bibliográfica

| Local | Conteúdo | Versionado? |
| --- | --- | --- |
| [bibliografia.bib](bibliografia.bib) | Entradas BibTeX de todas as fontes | Sim |
| [fichamentos/](fichamentos/) | Fichamentos padronizados, um por fonte | Sim |
| `artigos/` | PDFs/cópias dos textos (direitos autorais) | **Não** (ignorado) |

## Fluxo

1. Adicione a fonte em `bibliografia.bib` com a chave de citação.
2. Crie um fichamento em `fichamentos/<chave>.md` a partir do
   [template](fichamentos/_template-fichamento.md).
3. Cite a fonte nos cadernos usando a mesma chave.

## Regras

- Nenhuma entrada inventada: preencher com metadados reais e verificáveis.
- Distinguir achado do estudo de interpretação do projeto.
- Cópias de artigos ficam em `artigos/` e **não** entram no controle de versão.
