# Como Acessar a Central ENAJU

Este guia mostra tres formas de acesso: pelo navegador, pelo computador com Git e pelo VS Code.

## 1. Acesso pelo navegador

1. Abra o GitHub em `https://github.com`.
2. Entre na conta autorizada a acessar o repositorio.
3. Acesse o repositorio:
   `https://github.com/cairesmachado-svg/ENAJU`
4. Clique na pasta `00_CENTRAL_ENAJU`.
5. Abra o arquivo `README.md` para ver a pagina inicial da central.

## 2. Baixar uma copia sem usar Git

1. Abra o repositorio no GitHub.
2. Clique em `Code`.
3. Clique em `Download ZIP`.
4. Extraia o arquivo no computador.
5. Abra a pasta extraida e comece pelo arquivo `00_CENTRAL_ENAJU/README.md`.

Use esta opcao para leitura, consulta ou compartilhamento rapido. Para editar com historico e sincronizacao, prefira Git.

## 3. Clonar com Git

No PowerShell, escolha uma pasta de trabalho e rode:

```powershell
git clone --recurse-submodules https://github.com/cairesmachado-svg/ENAJU.git
cd ENAJU
```

Para atualizar a copia local depois:

```powershell
git pull
git submodule update --init --recursive
```

Para verificar o que mudou antes de enviar ao GitHub:

```powershell
git status
```

## 4. Abrir no VS Code como workspace

1. Abra o VS Code.
2. Clique em `File` > `Open Workspace from File`.
3. Selecione `ENAJU.code-workspace`.
4. Use o painel lateral para navegar pelos grupos:
   - Central e Governanca
   - Projetos de Pesquisa
   - Produtos Digitais
   - Inputs e Outputs

Se preferir abrir pelo terminal:

```powershell
code ENAJU.code-workspace
```

## 5. Enviar alteracoes ao GitHub

Depois de editar arquivos:

```powershell
git status
git add .
git commit -m "organiza central de projetos ENAJU"
git push
```

Boas praticas:

| Situacao | Recomendacao |
| --- | --- |
| Edicao pequena em documento | Commit direto com mensagem objetiva. |
| Projeto novo | Criar pasta, adicionar ficha de projeto e registrar no inventario. |
| Arquivo sensivel ou credencial | Nao enviar ao GitHub. Usar `.env` local quando necessario. |
| Entregavel final | Colocar em `Outputs/` ou em `outputs/` dentro do projeto. |

## 6. Atualizar projetos vinculados

Alguns projetos sao repositorios proprios dentro da central. Para baixar ou atualizar esses projetos:

```powershell
git submodule update --init --recursive
```

Para trazer a versao mais recente dos repositorios vinculados:

```powershell
git submodule update --init --recursive --remote
```

## 7. Caminho recomendado para novas pessoas

1. Abrir `00_CENTRAL_ENAJU/README.md`.
2. Ler `04_INVENTARIO_ATUAL.md`.
3. Identificar o projeto de interesse.
4. Abrir o README da pasta do projeto.
5. Registrar duvidas ou demandas no `Backlog/`.
