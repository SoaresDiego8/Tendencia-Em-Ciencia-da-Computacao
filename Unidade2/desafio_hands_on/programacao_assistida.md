# Programação Assistida e Automação com IA

## Identificação

- **Nome:** Diego Henrique Silva Soares
- **Data:** 10/09/2026
- **Ferramenta de IA utilizada:** Claude (Anthropic)
- **Problema escolhido:** Opção D - Gerador de Relatório de Vendas
- **Organização:** individual

---

## 1. Problema

Toda vez que fecho um período de vendas, repito manualmente os mesmos cálculos sobre uma lista de valores: somar tudo, calcular a média, achar o maior e o menor valor. É uma tarefa repetitiva, baseada em regras fixas e sujeita a erro de digitação, logo, boa candidata à automação.

A tarefa a automatizar: **receber uma lista de valores de vendas e produzir um resumo com total, média, maior valor e menor valor.**

---

## 2. Entrada

Uma lista de números (inteiros ou decimais) representando valores de vendas individuais.

Exemplo de entrada válida:

```python
[1500, 2300, 800, 4200, 1750]
```

Entradas que o programa também precisa tratar:

- lista vazia;
- item não numérico (ex.: `"2300"` como texto);
- valor negativo (venda não pode ser negativa neste contexto).

---

## 3. Processamento

1. validar a lista recebida;
2. somar todos os valores (**total**);
3. dividir o total pela quantidade de itens (**média**);
4. localizar o maior valor;
5. localizar o menor valor;
6. formatar os resultados no padrão monetário brasileiro.

---

## 4. Saída esperada

Um relatório em texto no formato:

```text
=== RELATORIO DE VENDAS ===
Vendas registradas: 5
Total .......: R$ 10.550,00
Media .......: R$ 2.110,00
Maior venda .: R$ 4.200,00
Menor venda .: R$ 800,00
```

Em caso de entrada inválida: uma mensagem explicando qual valor está errado, sem interromper o programa com erro técnico.

---

## 5. Prompt utilizado

Prompt inicial, deliberadamente pouco específico, para observar o que a IA produz sem restrições (estrutura mínima: papel + problema + tarefa):

```text
Atue como desenvolvedor Python.

PROBLEMA:
Preciso calcular indicadores de uma lista de vendas.

TAREFA:
Crie um programa que receba uma lista de valores de vendas
e apresente o total, a média, o maior valor e o menor valor.

LINGUAGEM:
Python, apenas biblioteca padrão.
```

Observação importante: esse prompt **não** informa o que fazer com lista vazia, com valores não numéricos ou com valores negativos. Também não pede type hints, docstring, tratamento de erros nem separação entre cálculo e exibição. Foi escrito assim de propósito, a lacuna do prompt é o que produz os defeitos analisados no item 7.

---

## 6. Código inicial

```python
def relatorio_vendas(vendas):
    total = sum(vendas)
    media = total / len(vendas)
    maior = max(vendas)
    menor = min(vendas)

    print("=== RELATORIO DE VENDAS ===")
    print("Total: R$", total)
    print("Media: R$", media)
    print("Maior venda: R$", maior)
    print("Menor venda: R$", menor)


vendas = [1500, 2300, 800, 4200, 1750]
relatorio_vendas(vendas)
```

---

## 7. Análise crítica

Aplicando o checklist da Etapa 3 (seção 19 do material):

| Pergunta | Resposta |
|---|---|
| Eu compreendo o código? | Sim. Usa apenas `sum`, `len`, `max`, `min` e `print`. |
| O código atende ao problema definido? | Só no caso feliz. |
| Há bibliotecas que eu não conheço? | Não. Apenas built-ins. |
| Há operações que podem apagar ou sobrescrever dados? | Não. O script apenas lê a lista e imprime. |
| O código utiliza dados sensíveis? | Não. Valores fictícios. |
| Há tratamento de erros? | **Não.** Nenhum. |
| Consigo explicar cada bloco? | Sim. |
| Existem casos que o código não considera? | **Sim, vários.** |

### Problemas identificados antes de executar

1. **Divisão por zero.** `total / len(vendas)` quebra com lista vazia. A IA assumiu que a lista sempre tem itens.
2. **Sem validação de tipo.** Um valor em texto (`"2300"`) faz `sum()` falhar com `TypeError`.
3. **Sem validação de domínio.** Venda negativa é aceita silenciosamente e contamina a média, o erro mais perigoso, porque não gera exceção nenhuma.
4. **Cálculo misturado com apresentação.** A função calcula e imprime ao mesmo tempo. Não há como reaproveitar os números em outro lugar (salvar em arquivo, somar com outro período) sem reescrever a função.
5. **Código executável no nível do módulo.** A chamada `relatorio_vendas(vendas)` está solta no fim do arquivo, sem `if __name__ == "__main__"`. Consequência real: ao importar a função para testar, o relatório de exemplo é impresso sozinho (isso apareceu de fato nos testes abaixo).
6. **Formatação pobre.** `print("Total: R$", total)` imprime `R$ 10550` e `R$ 2110.0`, sem separador de milhar, sem duas casas decimais, com inconsistência entre inteiro e float.
7. **Sem type hints e sem docstring**, contrariando boa prática de código Python.

---

## 8. Casos de teste

### Teste 1, Caso normal

**Entrada:** `[1500, 2300, 800, 4200, 1750]`
**Resultado esperado:** total 10550, média 2110, maior 4200, menor 800.

### Teste 2, Caso limite

**Entrada:** `[]`
**Comportamento esperado:** mensagem informando que não há vendas a processar.

### Teste 3, Caso de erro

**Entrada:** `[1500, "2300", 800]`
**Comportamento esperado:** mensagem apontando o valor inválido.

### Teste 4, Caso de erro silencioso (teste extra)

**Entrada:** `[1500, -200, 800]`
**Comportamento esperado:** rejeitar a venda negativa.

---

## 9. Problemas encontrados (resultados reais da execução)

| Teste | Entrada | Resultado obtido na v1 | Situação |
|---|---|---|---|
| 1 | `[1500, 2300, 800, 4200, 1750]` | `Total: R$ 10550` / `Media: R$ 2110.0` / `Maior: 4200` / `Menor: 800` | Passou (valores corretos, formatação ruim) |
| 2 | `[]` | `ZeroDivisionError: division by zero` | **Falhou** |
| 3 | `[1500, "2300", 800]` | `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | **Falhou** |
| 4 | `[1500, -200, 800]` | Executou normalmente: `Total: R$ 2100` / `Media: R$ 700.0` / `Menor: -200` | **Falhou silenciosamente** |

Traceback do Teste 2:

```text
  File "relatorio_vendas_v1.py", line 3, in relatorio_vendas
    media = total / len(vendas)
            ~~~~~~^~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

Traceback do Teste 3:

```text
  File "relatorio_vendas_v1.py", line 2, in relatorio_vendas
    total = sum(vendas)
            ^^^^^^^^^^^
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

**Descoberta não prevista:** nos testes 2, 3 e 4 o relatório de exemplo foi impresso antes do resultado do teste, porque o `import` da função executou a chamada solta no fim do arquivo. Isso confirma na prática o problema 5 da análise crítica, um defeito que eu só percebi ao rodar, não ao ler.

O teste 4 foi o mais grave: o programa não reclamou, apenas devolveu média errada. Erro que não levanta exceção é o mais difícil de detectar em produção.

---

## 10. Prompt de refatoração

```text
Atue como revisor de código Python.

O programa abaixo já funciona para o caso normal, mas falhou
nos seguintes testes:
- lista vazia: ZeroDivisionError;
- item em texto: TypeError;
- venda negativa: aceita silenciosamente e distorce a média;
- ao importar a função, o exemplo do fim do arquivo é executado.

Analise considerando:
- legibilidade;
- nomes de variáveis e funções;
- duplicações;
- modularização (separar cálculo de apresentação);
- tratamento de erros.

RESTRIÇÕES:
- não alterar o comportamento correto do caso normal;
- somente biblioteca padrão;
- incluir type hints e docstrings;
- formatar valores no padrão monetário brasileiro (R$ 1.234,56).

APRESENTE:
1. problemas encontrados;
2. sugestões de melhoria;
3. código refatorado;
4. justificativa das principais alterações.
```

---

## 11. Código refatorado

```python
"""Gera um resumo estatistico de uma lista de valores de vendas."""

from typing import Sequence


def validar_vendas(vendas: Sequence[float]) -> list[float]:
    """Valida a lista de vendas e devolve uma copia somente com numeros.

    Levanta ValueError se a lista estiver vazia, se algum item nao for
    numerico ou se algum valor for negativo.
    """
    if not vendas:
        raise ValueError("A lista de vendas esta vazia.")

    validadas: list[float] = []
    for posicao, valor in enumerate(vendas):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(
                f"Valor invalido na posicao {posicao}: {valor!r} nao e numerico."
            )
        if valor < 0:
            raise ValueError(
                f"Valor invalido na posicao {posicao}: venda negativa ({valor})."
            )
        validadas.append(float(valor))

    return validadas


def calcular_resumo(vendas: Sequence[float]) -> dict[str, float]:
    """Calcula total, media, maior e menor valor de uma lista de vendas.

    Exemplo:
        >>> calcular_resumo([100, 200, 300])["total"]
        600.0
    """
    valores = validar_vendas(vendas)
    return {
        "total": sum(valores),
        "media": sum(valores) / len(valores),
        "maior": max(valores),
        "menor": min(valores),
        "quantidade": len(valores),
    }


def formatar_moeda(valor: float) -> str:
    """Formata um numero no padrao monetario brasileiro (R$ 1.234,56)."""
    inteiro, centavos = f"{valor:.2f}".split(".")
    milhares = f"{int(inteiro):,}".replace(",", ".")
    return f"R$ {milhares},{centavos}"


def formatar_relatorio(resumo: dict[str, float]) -> str:
    """Monta o texto do relatorio a partir do resumo calculado."""
    linhas = [
        "=== RELATORIO DE VENDAS ===",
        f"Vendas registradas: {int(resumo['quantidade'])}",
        f"Total .......: {formatar_moeda(resumo['total'])}",
        f"Media .......: {formatar_moeda(resumo['media'])}",
        f"Maior venda .: {formatar_moeda(resumo['maior'])}",
        f"Menor venda .: {formatar_moeda(resumo['menor'])}",
    ]
    return "\n".join(linhas)


def main() -> None:
    """Executa o relatorio com uma lista de exemplo."""
    vendas = [1500, 2300, 800, 4200, 1750]
    try:
        print(formatar_relatorio(calcular_resumo(vendas)))
    except ValueError as erro:
        print(f"Nao foi possivel gerar o relatorio: {erro}")


if __name__ == "__main__":
    main()
```

### Principais alterações e justificativas

| Alteração | Justificativa |
|---|---|
| `validar_vendas()` isolada | Concentra todas as regras de entrada em um lugar; erros passam a ser explícitos e com mensagem útil. |
| `calcular_resumo()` retorna dicionário | Separa cálculo de apresentação; os números podem ser reaproveitados (exportar, comparar períodos) sem reescrever nada. |
| `formatar_moeda()` e `formatar_relatorio()` | Apresentação isolada do cálculo; elimina a repetição de `print` com formatação inconsistente. |
| `ValueError` em vez de deixar quebrar | Troca `ZeroDivisionError`/`TypeError` (erros técnicos) por mensagens de domínio, tratadas em `main()`. |
| Rejeição de valor negativo | Corrige o erro silencioso do Teste 4. |
| `isinstance(valor, bool)` na validação | Em Python `True` é `int` e passaria como venda de 1,00. Caso de borda que eu mesmo tive que apontar. |
| Type hints e docstrings | Documentam contrato de entrada e saída. |
| `if __name__ == "__main__"` | Impede a execução do exemplo ao importar o módulo, o defeito descoberto no item 9. |

### Resultados dos mesmos testes na versão refatorada

| Teste | Entrada | Resultado obtido na v2 |
|---|---|---|
| 1 | `[1500, 2300, 800, 4200, 1750]` | `Total: R$ 10.550,00` / `Media: R$ 2.110,00` / `Maior: R$ 4.200,00` / `Menor: R$ 800,00` |
| 2 | `[]` | `Nao foi possivel gerar o relatorio: A lista de vendas esta vazia.` |
| 3 | `[1500, "2300", 800]` | `Valor invalido na posicao 1: '2300' nao e numerico.` |
| 4 | `[1500, -200, 800]` | `Valor invalido na posicao 1: venda negativa (-200).` |
| 5 (extra) | `[999]` | Executou corretamente com 1 registro |

Comportamento correto do caso normal preservado: os valores são os mesmos, só a formatação mudou.

---

## 12. Comparação

Escala de 1 a 5.

| Critério | Inicial | Refatorado |
|---|---:|---:|
| Funcionamento | 2 | 5 |
| Clareza | 3 | 4 |
| Organização | 2 | 5 |
| Legibilidade | 3 | 4 |
| Tratamento de erros | 1 | 5 |
| Facilidade de manutenção | 2 | 5 |
| **Total** | **13** | **28** |

Observação honesta: a versão refatorada tem quatro funções em vez de uma e passou de 14 para cerca de 80 linhas. Para um script descartável rodado uma vez, a v1 resolveria. O ganho de organização só se paga porque a intenção é reutilizar e confiar no resultado. Código mais curto não é automaticamente melhor, nem mais longo.

---

## 13. Reflexão

### Onde a IA mais ajudou?

Na velocidade de produzir estrutura: a v1 saiu pronta em segundos e a refatoração aplicou de uma vez type hints, docstrings, separação de responsabilidades e formatação monetária, tarefas mecânicas que eu sei fazer, mas que consomem tempo.

### Onde a IA errou?

A v1 cobriu apenas o caso feliz. Assumiu lista não vazia, valores numéricos e valores positivos, sem avisar que estava assumindo. O pior caso foi o valor negativo: nenhuma exceção, apenas um resultado errado com aparência de certo. A IA também deixou a chamada solta no fim do arquivo, o que provocou efeito colateral no import.

### O que precisei modificar?

Quase todas as correções vieram de decisões que a IA não tinha como tomar sozinha, porque dependiam do domínio: venda negativa é erro ou é devolução? Lista vazia é exceção ou relatório com zeros? `True` deve contar como venda? Essas respostas são minhas, não da IA. Também fui eu que decidi rodar o teste do valor negativo, a IA não sugeriu esse caso.

### Consigo explicar o código?

Sim, função por função: `validar_vendas` aplica as regras de entrada e levanta `ValueError`; `calcular_resumo` devolve os indicadores em um dicionário; `formatar_moeda` converte número em texto no padrão brasileiro; `formatar_relatorio` monta as linhas; `main` orquestra e captura o erro.

---

## 14. Take Away

### 26. Perguntas de reflexão

1. **Em qual etapa a IA foi mais útil?** Na refatoração. Na geração ela produziu algo incompleto; na refatoração, com os defeitos já identificados e nomeados por mim, entregou exatamente o que faltava. A qualidade do resultado foi proporcional à qualidade do diagnóstico que eu forneci.
2. **Qual parte exigiu mais raciocínio humano?** Definir as regras de negócio (o que é entrada inválida) e escolher os casos de teste.
3. **A primeira solução funcionou?** No caso normal, sim. Falhou em três dos quatro testes.
4. **O que mudou após a refatoração?** Passou de um script que só funciona com entrada perfeita para um módulo que rejeita entrada inválida com mensagem clara e separa cálculo de apresentação.
5. **Consigo explicar sem consultar a IA?** Sim.
6. **Principal risco identificado?** Erro silencioso. Código que quebra é fácil de achar; código que devolve número errado sem reclamar passa direto, e quanto mais o texto da IA parece competente, menor a vontade de testar.

### 27. Desafio final

> "Programar com IA não significa deixar a IA programar por mim. Significa **usar a IA para escrever mais rápido o que eu sei revisar, e permanecer o único responsável por decidir o que está certo.**"

**Cinco regras para usar IA de forma responsável:**

1. Nunca executar código que eu não consiga explicar linha por linha.
2. Testar sempre o caso limite e o caso inválido, não só o caso que eu queria que funcionasse, a IA otimiza para o caso feliz.
3. Desconfiar especialmente do código que roda sem erro: verificar se o resultado está correto, não apenas se executou.
4. Não colocar em prompt chave, senha, token, dado pessoal ou código proprietário; usar sempre placeholder (`<SUA_CHAVE>`).
5. Decidir as regras de negócio antes de pedir o código; a IA preenche lacuna do prompt com suposição silenciosa, e a suposição dela não é responsabilidade dela.

---

## Checklist de entrega

- [x] Defini o problema.
- [x] Identifiquei entrada, processamento e saída.
- [x] Registrei o prompt utilizado.
- [x] Registrei a primeira versão do código.
- [x] Analisei criticamente a solução.
- [x] Executei pelo menos três testes (executei quatro).
- [x] Registrei os resultados.
- [x] Solicitei e analisei uma refatoração.
- [x] Comparei as versões.
- [x] Respondi à reflexão final.
- [x] Organizei o arquivo no GitHub.
