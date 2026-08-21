# Aula 02 — Engenharia de Prompt (Avaliação Prática A2)
## Tema

**Mapeamento de payload de API para schema normalizado de ingestão.**

Problema real e recorrente no meu trabalho com pipelines de dados: toda vez que
uma nova fonte entra no pipeline, alguém abre o retorno da API, entende a
estrutura aninhada e decide como aquilo vira tabela relacional. Trabalho manual,
repetitivo e fácil de errar por omissão.

A pergunta desta atividade é se uma IA generativa consegue produzir esse
mapeamento de forma confiável, e o que precisa estar no prompt para que a saída
seja **verificável** em vez de apenas plausível.

O payload é a resposta de consulta ao índice público do Datajud (CNJ), formato
Elasticsearch, com processo, órgão julgador, assuntos e movimentos. É um arquivo
sintético: reproduz a estrutura real da API, incluindo aninhamentos, campos nulos
e chaves opcionais, mas não usa dado de processo real. A escolha permite conhecer
com precisão a resposta correta, que é o que torna a métrica possível.

### Por que este tema

O critério de sucesso é verificável campo a campo, sem depender de opinião:

- **Cobertura:** quantos dos caminhos-folha do JSON a resposta tratou;
- **Fidelidade:** quantos campos a resposta citou que não existem no payload.

Temas mais genéricos produzem respostas que ninguém consegue reprovar, e aí a
análise crítica vira impressão pessoal.

---

## Resultados

| Versão | Cobertura | Campos inexistentes |
|---|---|---|
| Prompt inicial | 60,6% | 2 |
| Variação 1 — persona + restrição | 72,7% | 0 |
| Variação 2 — formato JSON estrito | 81,8% | 0 |
| Variação 3 — few-shot | 100% | 0 |
| Prompt refinado | 100% | 0 |

Medido contra os 33 caminhos-folha do payload. A leitura completa dos números,
incluindo os critérios que a métrica não captura, está em `comparacao.md`.

---

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `README.md` | Tema, contexto, resultados |
| `prompts.md` | Prompt mestre (molde), prompt inicial, payload de entrada, resposta obtida, técnicas utilizadas |
| `variacao1.md` | Persona + restrição: prompt, resultado e leitura |
| `variacao2.md` | Formato JSON estrito: prompt, resultado e leitura |
| `variacao3.md` | Few-shot: prompt, resultado e leitura |
| `comparacao.md` | Métricas, análise crítica, prompt refinado, validação humana |
| `reflexao.md` | Reflexão cognitiva e ética |

## Metodologia

Cada prompt foi executado em uma **conversa nova**. Rodar as variações em
sequência no mesmo chat faria o modelo carregar o contexto da resposta anterior, e
a variação deixaria de isolar o eixo que se quer medir.

Cada variação altera **um eixo por vez**, mantendo o resto idêntico ao prompt
inicial. Alterar dois de uma vez produz um prompt melhor e nenhuma evidência do
que causou a melhora.

**Modelo:** Claude Opus 5 (Anthropic) — execuções em 21/08/2026. Todas as saídas
em `prompts.md`, `variacao1.md`, `variacao2.md` e `variacao3.md` estão coladas sem
edição, exatamente como retornadas.
