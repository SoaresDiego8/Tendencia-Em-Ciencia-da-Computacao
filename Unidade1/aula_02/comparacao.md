# Comparacao: Prompt Inicial x Prompt Refinado

Prompt inicial em `prompts.md`, prompt refinado em `refinado.md`. Mesma entrada,
mesmo modelo (Claude Opus 5), mesma data.

---

## Numeros

O payload de entrada tem **33 caminhos-folha**. Duas metricas objetivas:

- **Cobertura**: quantos desses caminhos a resposta tratou;
- **Campos inexistentes**: quantos caminhos a resposta citou que nao existem no JSON.

| | Inicial | Refinado |
|---|---|---|
| Cobertura | 60,6% (20 de 33) | 100% (33 de 33) |
| Campos faltantes | 13 | 0 |
| Campos inexistentes | 2 | 0 |
| Saida consumivel por script | nao (Markdown) | sim (JSON valido) |
| Omissoes declaradas | nao | sim (`campos_ignorados`) |
| Contagem propria para conferencia | nao | sim (`autoverificacao`) |

## As tres diferencas que importam

### 1. Campos inventados

O inicial mapeou `valorCausa` e `situacao`. Nenhum dos dois existe no payload.
Tambem nao sao aleatorios: os dois aparecem em outras APIs processuais e em
telas de sistemas judiciais. O modelo preencheu o que era provavel para o
dominio, e por isso o erro passa: parece certo.

No refinado esses campos nao aparecem em lugar nenhum, porque a restricao proibe
mapear o que nao esta literalmente no JSON.

Consequencia pratica: mapeamento com campo inexistente vira codigo de parse que
quebra na primeira execucao.

### 2. Campos omitidos

O inicial deixou 13 campos de fora sem avisar. Entre eles, todos os
`complementosTabelados` exceto `descricao`, os dois campos do `orgaoJulgador`
dentro de movimento, e `assuntos[].principal`.

O refinado cobriu os 33 e listou `_score` em `campos_ignorados` com justificativa
(metadado de relevancia da consulta, sem valor analitico).

Esse e o modo de falha mais perigoso dos dois. Campo inventado quebra o pipeline
e aparece no log. Campo omitido nao quebra nada: a carga roda, o dashboard
carrega, e a coluna simplesmente nunca existiu. Ninguem percebe ate alguem
perguntar por um dado que nunca foi ingerido.

### 3. Interpretacao semantica

Dois casos que so o refinado registrou:

- `complementosTabelados[].valor` e o codigo do complemento tabelado, nao um
  valor monetario. O inicial tratou como campo qualquer. Mapeado para uma coluna
  chamada `valor`, alguem somaria aquilo no dashboard achando que e dinheiro.
- O objeto `orgaoJulgador` aparece duas vezes com nomes de chave diferentes:
  `codigo`/`nome` no processo e `codigoOrgao`/`nomeOrgao` no movimento. Tratar
  como a mesma estrutura quebraria o parse.

## O que causou a diferenca

Cada variacao isolou um eixo, e cada uma resolveu um problema distinto:

| Tecnica adicionada | Efeito medido |
|---|---|
| Persona + restricao anti-inferencia | zerou campos inexistentes (2 para 0) |
| Formato JSON estrito | +21 pontos de cobertura, sem pedir cobertura |
| Exemplo resolvido (few-shot) | cobriu os casos dificeis: campo nulo, chave presente em so um item do array, objeto aninhado em dois niveis |
| Criterios de qualidade | tornou a omissao visivel, com contagem declarada |

O refinado e a soma dos quatro.

## Validacao

Item do checklist: *como a resposta foi conferida por humanos?*

**Camada automatica.** Um script le o payload, percorre a arvore JSON e extrai
todos os caminhos terminais, normalizando indices de array para `[]`
(`movimentos[0].codigo` e `movimentos[1].codigo` contam como um caminho so).
Depois compara com os caminhos citados em cada resposta:

```python
def caminhos_folha(no, prefixo=""):
    folhas = set()
    if isinstance(no, dict):
        for chave, valor in no.items():
            atual = f"{prefixo}.{chave}" if prefixo else chave
            folhas |= caminhos_folha(valor, atual)
    elif isinstance(no, list):
        for item in no:
            folhas |= caminhos_folha(item, f"{prefixo}[]")
    else:
        folhas.add(prefixo)
    return folhas

esperados = caminhos_folha(json.load(open("payload.json")))
faltantes = esperados - tratados_na_resposta
inexistentes = tratados_na_resposta - esperados
```

O script nao confia na contagem que o modelo declarou em `autoverificacao`.
Reabre o JSON e conta de novo. Bateu, mas poderia nao ter batido.

**Camada humana.** O script confere existencia, nao sentido. Os dois erros
semanticos da secao 3 acima passariam por qualquer metrica automatica e
produziriam numero errado no dashboard. Foram encontrados na leitura.

**Limitacao.** A lista de campos citados na resposta inicial foi extraida
manualmente, porque a saida veio em tabela Markdown. Isso e um argumento a favor
de exigir saida estruturada: no refinado, que devolve JSON, a extracao e
automatica.

**O que nao foi validado.** Nada aqui prova que o schema proposto funciona. Prova
que ele descreve campos que existem e nao deixa campo de fora. A validacao real
seria executar a carga contra uma amostra maior da API e verificar constraints,
cardinalidade e opcionalidade. Um documento unico nao permite concluir que um
campo e sempre preenchido.
