---
protocolo: "REI-40 — piloto"
versao: "0.1"
status: "rascunho"
data: "2026-06-06"
responsavel_metodologico: "A definir"
---

# Protocolo de pesquisa-piloto — REI-40

> Protocolo replicável para aplicação **voluntária** do REI-40 em labs, escolas
> judiciais e equipes de formação. Não institucionaliza a escala; orienta seu
> uso científico no contexto do CADERNOS_ENAJU.

## 1. Pergunta e objetivos

- **Pergunta-piloto:** como os estilos de pensamento (racional/experiencial) se
  relacionam com adesão à inovação e participação em políticas judiciárias?
- **Objetivo:** gerar evidências preliminares que informem trilhas formativas.

## 2. Desenho

- **Tipo:** estudo transversal, exploratório, de baixo risco.
- **Participação:** voluntária, com consentimento livre e esclarecido (TCLE).
- **Anonimização:** desde a coleta; sem microdados identificáveis no repositório.

## 3. População e amostra

| Item | Definição |
| --- | --- |
| Público | Magistrados, servidores e gestores participantes voluntários |
| Critérios de inclusão | Vínculo com a instituição parceira; aceite do TCLE |
| Critérios de exclusão | Não aceite do TCLE; questionário incompleto |
| Estratégia amostral | Amostra de conveniência no piloto; calibrar depois |
| Tamanho mínimo | A definir com a coordenação científica |

## 4. Instrumentos e variáveis

| Bloco | Conteúdo | Observação |
| --- | --- | --- |
| Consentimento | TCLE | Ver [tcle-modelo.md](tcle-modelo.md) |
| REI-40 | 40 itens, 4 fatores | Uso voluntário; versão validada em português |
| Variáveis contextuais | Função, tempo de carreira, unidade, exposição a inovação | Mínimas e não identificáveis |

Os itens e a chave de codificação ficam em
[questionarios/](questionarios/) (a preencher) e o dicionário de variáveis em
[data/dictionaries/](../../data/dictionaries/).

## 5. Coleta

- Plataforma a definir (preferir ferramenta com conformidade LGPD).
- Janela de coleta definida por piloto.
- Registro de proveniência: data, instituição, instrumento e versão.

## 6. Análise

- Estatística descritiva por fator do REI-40.
- Associações exploratórias com variáveis contextuais.
- Sem inferência causal no piloto; resultados são preliminares.
- Scripts em [src/analysis/](../../src/analysis/); saídas em
  [data/outputs/](../../data/outputs/).

## 7. Devolutiva

- Relatório agregado e anonimizado às instituições participantes.
- Achados alimentam o Caderno ENAJU n. 1 e as trilhas.

## 8. Ética e conformidade (LGPD)

- TCLE obrigatório antes de qualquer item.
- Base legal, finalidade e prazo de guarda definidos no TCLE.
- Anonimização e minimização de dados.
- Avaliar necessidade de submissão a comitê de ética, conforme a instituição.

## 9. Checklist de aprovação

- [ ] Pergunta e objetivos validados pela coordenação científica
- [ ] Tamanho amostral mínimo definido
- [ ] Instrumento e chave de codificação anexados
- [ ] TCLE revisado juridicamente
- [ ] Plano de análise definido
- [ ] Plano de devolutiva acordado com a instituição
