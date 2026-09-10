# Atividade - Refinamento de Prompts

## Identificação
- Nome: Diego Henrique Silva Soares
- Data: 03/09/2026
- Disciplina: Tendências em Ciência da Computação
- Ferramenta de IA utilizada: Claude (Anthropic), modelo Claude Opus 5, via claude.ai

---

## Problema escolhido

### Contexto
Todo dia, o sistema de uma loja gera um arquivo com as vendas do dia. Um programa precisa pegar esse arquivo e levar as vendas para o banco de dados que alimenta o painel de faturamento. Esse tipo de programa se chama **ETL**: ele **extrai** os dados de um lugar, **transforma** (limpa e organiza) e **carrega** em outro.

Parece simples, mas o arquivo vem com as "sujeiras" de sempre:
- acentos gravados num padrão antigo;
- colunas separadas por ponto e vírgula;
- valores com vírgula nos centavos (`1.234,56`);
- uma linha de total no fim;
- venda que aparece duas vezes porque foi editada;
- status escrito de jeitos diferentes (` cancelada `);
- de vez em quando, um campo vazio.

Estes são os dois arquivos usados na atividade:

`vendas_2026-09-02.csv`
```text
id_venda;data;cliente;produto;quantidade;valor_unitario;status;atualizado_em
1001;02/09/2026;João Araújo;Caderno universitário;2;18,90;FATURADA;02/09/2026 09:12
1002;02/09/2026;Márcia Lima;Notebook;1;3.299,00;FATURADA;02/09/2026 15:47
1003;02/09/2026;Pedro Sá;Cadeira de escritório;4;1.234,56;FATURADA;02/09/2026 10:40
1002;02/09/2026;Márcia Lima;Notebook;1;3.499,00;FATURADA;02/09/2026 10:05
1004;02/09/2026;Ana Côrtes;Mouse sem fio;3;79,90; cancelada ;02/09/2026 11:20
1005;02/09/2026;Luís Peña;Teclado mecânico;;149,90;FATURADA;02/09/2026 13:02
1006;02/09/2026;Cláudia Reis;Monitor 24 pol;2;899,99;FATURADA;02/09/2026 16:30
Total de registros: 7
```

`vendas_2026-09-03.csv`
```text
id_venda;data;cliente;produto;quantidade;valor_unitario;status;atualizado_em
1007;03/09/2026;Rui Antunes;Caderno universitário;5;18,90;FATURADA;03/09/2026 08:55
1008;03/09/2026;Sônia Prado;Mouse sem fio;1;79,90;FATURADA;03/09/2026 09:30
1003;02/09/2026;Pedro Sá;Cadeira de escritório;4;1.234,56;CANCELADA;03/09/2026 11:00
Total de registros: 3
```

### Problema
Quero descobrir o quanto o jeito de pedir muda o programa que a IA entrega. Em ETL existe uma armadilha: o programa pode dizer "deu certo" e mesmo assim deixar os números errados no painel. Por isso, "rodou" não serve como prova.

### Objetivo
Conseguir um programa que leve as vendas para o banco sem errar os números e que possa ser rodado de novo sem estragar nada.

Para comparar as respostas sem depender de impressão, escrevi **antes** de começar dez perguntas de sim ou não. Depois rodei cada programa sempre na mesma sequência: carga do dia 02/09, a mesma carga de novo (como se o programa tivesse falhado e alguém rodasse outra vez) e a carga do dia 03/09.

| # | Pergunta |
|---|---|
| C1 | O programa consegue abrir o arquivo com acentos? |
| C2 | Ignora a linha de total do fim? |
| C3 | Centavos e totais ficam certos (`1.234,56` vira 1234,56)? |
| C4 | `02/09/2026` vira 2 de setembro, e não 9 de fevereiro? |
| C5 | Venda repetida: fica só a versão mais recente? |
| C6 | Venda cancelada fica de fora? |
| C7 | Linha com defeito vai para uma lista separada, em vez de sumir ou entrar errada? |
| C8 | Rodar de novo o mesmo arquivo não duplica as vendas? |
| C9 | A carga de um dia novo mantém os dias anteriores? |
| C10 | Venda cancelada no dia seguinte (a 1003, em 03/09) sai do painel? |

---

## Prompt 1

### Prompt
```text
Crie um script ETL em Python que carregue um CSV de vendas em um banco de dados.
```

### Resultado
A IA entregou um programa organizado em três partes (extrair, transformar, carregar):

```python
import logging
import sqlite3

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extrair(caminho_csv: str) -> pd.DataFrame:
    """Lê o arquivo CSV de vendas."""
    logging.info("Extraindo dados de %s", caminho_csv)
    return pd.read_csv(caminho_csv)


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e padroniza os dados."""
    logging.info("Transformando %d linhas", len(df))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.drop_duplicates()
    df = df.dropna()

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    if {"quantidade", "preco"}.issubset(df.columns):
        df["total"] = df["quantidade"] * df["preco"]

    return df


def carregar(
    df: pd.DataFrame, caminho_banco: str, tabela: str = "vendas"
) -> None:
    """Grava os dados no banco SQLite."""
    logging.info("Carregando %d linhas na tabela %s", len(df), tabela)
    with sqlite3.connect(caminho_banco) as conn:
        df.to_sql(tabela, conn, if_exists="replace", index=False)


def executar_etl(caminho_csv: str, caminho_banco: str) -> None:
    df = extrair(caminho_csv)
    df = transformar(df)
    carregar(df, caminho_banco)
    logging.info("ETL concluído com sucesso")


if __name__ == "__main__":
    executar_etl("vendas.csv", "vendas.db")
```

Depois do código, explicou cada parte e sugeriu adaptar os nomes das colunas.

### Análise
- **O que funcionou:** o programa é bem organizado. Como ponto de partida, é razoável.
- **O que aconteceu com o arquivo real:** travou logo no começo, no primeiro acento. A IA supôs que o arquivo usava o padrão de acentos mais comum, e não usava. Resultado: 0 de 10.
- **O que mais me preocupou:** corrigi os acentos do arquivo para ver até onde o programa ia. Ele terminou com a mensagem "ETL concluído com sucesso" e gravou tudo embaralhado, numa coluna só. Como não sabia que as colunas eram separadas por ponto e vírgula, cortou cada linha na vírgula dos centavos. O travamento era o melhor cenário; o pior é o erro que não avisa.
- **Outros problemas, lendo o código:**
  - lê `02/09/2026` como 9 de fevereiro (formato americano);
  - cada carga apaga os dias anteriores;
  - linhas com campo vazio somem sem deixar registro;
  - procura uma coluna chamada `preco`, que não existe, então o total nunca é calculado.
- **O que faltou no meu pedido:** tudo o que a IA não tinha como adivinhar. Como o arquivo é, quais são as regras da loja e como o programa vai ser usado.

---

## Prompt 2

### Alterações realizadas
- **Papel:** engenheiro de dados.
- **Contexto:** de onde vem o arquivo, para onde vai, as primeiras linhas dele e o seu formato (acentos, ponto e vírgula, centavos, datas).
- **Objetivo:** um programa para esse arquivo específico, com as regras da loja (cancelada não entra, venda repetida vale a mais recente, como calcular o total).
- **Público:** estudante de Ciência da Computação que usa pandas no básico.
- **Formato:** separar em extrair, transformar e carregar.
- **Restrições:** usar só as bibliotecas pandas e sqlite3.
- **Critérios:** código legível, com comentários.

### Prompt
```text
Atue como engenheiro de dados com experiência em Python e pandas.

Contexto: uma loja exporta do ERP, todo dia, um arquivo
vendas_AAAA-MM-DD.csv. Preciso carregar esses arquivos num banco SQLite
(vendas.db) que alimenta um dashboard de faturamento.

O arquivo vem assim (primeiras linhas):

id_venda;data;cliente;produto;quantidade;valor_unitario;status;atualizado_em
1001;02/09/2026;João Araújo;Caderno universitário;2;18,90;FATURADA;02/09/2026 09:12
1003;02/09/2026;Pedro Sá;Cadeira de escritório;4;1.234,56;FATURADA;02/09/2026 10:40

- codificação latin-1, separador ";";
- valores com vírgula decimal e ponto de milhar;
- datas no formato dia/mês/ano.

Regras de negócio:
- vendas com status CANCELADA não entram na tabela;
- se o mesmo id_venda aparecer mais de uma vez, vale a linha com
  atualizado_em mais recente;
- valor_total = quantidade × valor_unitario.

Tabela de destino "vendas": id_venda, data_venda, cliente, produto,
quantidade, valor_unitario, valor_total.

Escreva o script ETL. Sou estudante de Ciência da Computação e já uso
pandas no básico.

Formato: funções separadas para extrair, transformar e carregar, e uma
função executar(caminho_csv, caminho_banco).
Restrições: apenas pandas e sqlite3.
Critérios: código legível, com comentários curtos onde a regra de
negócio aparece.
```

### Resultado
```python
import sqlite3

import pandas as pd

COLUNAS_DESTINO = ["id_venda", "data_venda", "cliente", "produto",
                   "quantidade", "valor_unitario", "valor_total"]


def extrair(caminho_csv):
    # latin-1 e ";" vêm do ERP; decimal e thousands convertem "1.234,56"
    return pd.read_csv(
        caminho_csv,
        sep=";",
        encoding="latin-1",
        decimal=",",
        thousands=".",
        dtype={"id_venda": str},
    )


def transformar(df):
    df = df.copy()

    # Regra: canceladas ficam de fora (normaliza caixa e espaços)
    df["status"] = df["status"].str.strip().str.upper()
    df = df[df["status"] != "CANCELADA"]

    # Datas em dia/mês/ano
    df["data_venda"] = pd.to_datetime(df["data"], format="%d/%m/%Y").dt.date
    df["atualizado_em"] = pd.to_datetime(
        df["atualizado_em"], format="%d/%m/%Y %H:%M"
    )

    # Regra: se o id se repete, vale a versão mais recente
    df = df.sort_values("atualizado_em").drop_duplicates(
        "id_venda", keep="last"
    )

    # Regra: valor_total = quantidade x valor_unitario
    df["valor_total"] = (df["quantidade"] * df["valor_unitario"]).round(2)

    return df[COLUNAS_DESTINO]


def carregar(df, caminho_banco):
    with sqlite3.connect(caminho_banco) as conn:
        df.to_sql("vendas", conn, if_exists="append", index=False)


def executar(caminho_csv, caminho_banco):
    df = extrair(caminho_csv)
    df = transformar(df)
    carregar(df, caminho_banco)
    return len(df)
```

A IA explicou as três partes e deixou um aviso no fim: se o mesmo arquivo for rodado duas vezes, as vendas se repetem.

---

## Comparação

| Critério | Prompt 1 | Prompt 2 |
|---|---:|---:|
| Clareza | 4 | 5 |
| Precisão | 1 | 3 |
| Relevância | 2 | 4 |
| Organização | 4 | 4 |
| Adequação ao público | 3 | 5 |
| Atendimento ao objetivo | 1 | 3 |
| Utilidade prática | 1 | 3 |
| **Total** | **16** | **27** |

Nas dez perguntas, o programa 1 fez 0 e o programa 2 fez 6. Só de descrever o arquivo, os acentos, os centavos e as datas passaram a funcionar.

As quatro falhas do programa 2 têm algo em comum: **nenhuma mostrou erro na tela**.
- **C2:** a linha de total virou uma venda, com o nome "Total de registros: 7";
- **C7:** a venda com quantidade vazia entrou sem valor, e o painel somaria menos sem avisar;
- **C8:** depois de rodar de novo e carregar o dia seguinte, havia 15 linhas para 9 vendas;
- **C10:** a venda 1003, cancelada no dia 03/09, continuou no painel.

---

## Prompt 3

### O que ainda precisava melhorar?
1. **As linhas de exemplo só mostravam vendas "bonitas".** A linha de total e o campo vazio não apareciam nelas, e a IA não tratou nenhum dos dois.
2. **Eu não disse como o programa é usado.** Ele roda todo dia, às vezes precisa rodar de novo, e o arquivo de hoje pode trazer mudanças em vendas de ontem. Nada disso está no arquivo, então a IA não tinha como saber.
3. **A IA viu o problema de rodar de novo, mas não resolveu.** Só avisou no fim.
4. **"Código legível" não dá para conferir.** E não evitou nenhuma das falhas.

**O que foi retirado:** as linhas de exemplo, trocadas por uma descrição do arquivo que inclui a linha de total e os campos vazios; e o critério "código legível", trocado por critérios que dá para testar.

### Hipótese
Acredito que a resposta ficará melhor porque, contando à IA como o arquivo realmente chega e como o programa realmente é usado, ela vai tratar os casos que o programa 2 deixou passar sem avisar. Pedir que ela liste as dúvidas antes do código também deve mostrar decisões que antes ficavam escondidas.

### Prompt
```text
PAPEL
Atue como engenheiro de dados com experiência em pipelines de carga
incremental em Python.

CONTEXTO
Uma loja exporta do ERP, todo dia, um arquivo vendas_AAAA-MM-DD.csv com
as vendas criadas ou alteradas naquele dia. O script roda agendado e,
se falhar, é executado de novo com o mesmo arquivo. O banco SQLite
(vendas.db) alimenta um dashboard de faturamento.

ARQUIVO DE ORIGEM
- codificação latin-1, separador ";";
- valores com vírgula decimal e ponto de milhar ("1.234,56");
- datas dd/mm/aaaa e atualizado_em dd/mm/aaaa hh:mm;
- a última linha é um rodapé do ERP: "Total de registros: N";
- às vezes vem linha com campo obrigatório vazio.

Colunas: id_venda;data;cliente;produto;quantidade;valor_unitario;status;atualizado_em

REGRAS
R1: status CANCELADA (qualquer caixa, com ou sem espaços) não fica na
    tabela vendas, inclusive se a venda já tiver sido carregada antes;
R2: id_venda repetido: vale o atualizado_em mais recente;
R3: valor_total = quantidade × valor_unitario, com 2 casas;
R4: linha inválida não entra em vendas e vai para a tabela rejeitados,
    com o motivo;
R5: rodar o mesmo arquivo de novo não pode duplicar nem perder dados.

DESTINO
vendas(id_venda PK, data_venda, cliente, produto, quantidade,
       valor_unitario, valor_total, atualizado_em)
rejeitados(arquivo, linha, motivo)

PÚBLICO
Estudante de Ciência da Computação que usa pandas no básico.

TAREFA
1. Antes do código, liste as ambiguidades e a decisão em cada uma.
2. Escreva o script, com a função executar(caminho_csv, caminho_banco).
3. Explique em até cinco linhas como o script garante a R5.

RESTRIÇÕES
- apenas pandas e sqlite3;
- não usar if_exists="replace";
- a carga de um arquivo é tudo ou nada (uma transação).

CRITÉRIOS DE QUALIDADE
- toda linha do arquivo termina em vendas, em rejeitados ou numa
  contagem de descartes (canceladas, duplicatas, rodapé);
- executar duas vezes o mesmo arquivo deixa o banco igual.
```

### Resultado

**Ambiguidades apontadas pela IA**

| # | Ponto não definido | Decisão adotada |
|---|---|---|
| A1 | O arquivo do dia pode trazer venda de dia anterior (alteração) | Tratar como atualização pelo `id_venda` (upsert) |
| A2 | Quantidade zero ou negativa | Rejeitar, mesmo não sendo campo vazio |
| A3 | Reprocessar o arquivo gera os mesmos rejeitados de novo | Apagar os rejeitados daquele arquivo antes de gravar |
| A4 | Cancelada que nunca foi carregada | Só entra na contagem de canceladas |
| A5 | Arquivo antigo reprocessado depois de um mais novo | Só sobrescrever se `atualizado_em` for igual ou mais recente |

**Script**
```python
"""
Carga incremental das vendas diárias do ERP para o SQLite.

Uso: executar("vendas_2026-09-02.csv", "vendas.db")
"""
import sqlite3
from pathlib import Path

import pandas as pd

COLUNAS = ["id_venda", "data", "cliente", "produto", "quantidade",
           "valor_unitario", "status", "atualizado_em"]

DDL = """
CREATE TABLE IF NOT EXISTS vendas (
    id_venda       TEXT PRIMARY KEY,
    data_venda     TEXT NOT NULL,
    cliente        TEXT NOT NULL,
    produto        TEXT NOT NULL,
    quantidade     INTEGER NOT NULL,
    valor_unitario REAL NOT NULL,
    valor_total    REAL NOT NULL,
    atualizado_em  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rejeitados (
    arquivo TEXT NOT NULL,
    linha   INTEGER NOT NULL,
    motivo  TEXT NOT NULL
);
"""

# Só sobrescreve se a versão que chega for igual ou mais nova (A5)
UPSERT = """
INSERT INTO vendas VALUES (:id_venda, :data_venda, :cliente, :produto,
    :quantidade, :valor_unitario, :valor_total, :atualizado_em)
ON CONFLICT(id_venda) DO UPDATE SET
    data_venda     = excluded.data_venda,
    cliente        = excluded.cliente,
    produto        = excluded.produto,
    quantidade     = excluded.quantidade,
    valor_unitario = excluded.valor_unitario,
    valor_total    = excluded.valor_total,
    atualizado_em  = excluded.atualizado_em
WHERE excluded.atualizado_em >= vendas.atualizado_em
"""

APAGAR_CANCELADA = (
    "DELETE FROM vendas WHERE id_venda = ? AND atualizado_em <= ?"
)


def numero_br(texto):
    """'1.234,56' -> 1234.56"""
    return float(texto.replace(".", "").replace(",", "."))


def extrair(caminho_csv):
    # tudo como texto: a conversão acontece na transformação, linha a linha
    df = pd.read_csv(caminho_csv, sep=";", encoding="latin-1",
                     dtype=str, keep_default_na=False)
    df["linha"] = df.index + 2  # linha no arquivo (cabeçalho é a 1)
    return df


def transformar(df, arquivo):
    resumo = {"lidas": len(df), "rodape": 0, "rejeitadas": 0,
              "canceladas": 0, "duplicatas": 0, "carregadas": 0}
    rejeitados, validas = [], []

    for reg in df.to_dict("records"):
        if reg["id_venda"].strip().lower().startswith("total de registros"):
            resumo["rodape"] += 1
            continue

        vazios = [c for c in COLUNAS if not str(reg.get(c) or "").strip()]
        if vazios:
            rejeitados.append(
                (arquivo, reg["linha"], "campo vazio: " + ", ".join(vazios))
            )
            continue

        try:
            quantidade = int(reg["quantidade"])
            valor_unitario = numero_br(reg["valor_unitario"])
            data_venda = pd.to_datetime(reg["data"], format="%d/%m/%Y")
            atualizado_em = pd.to_datetime(
                reg["atualizado_em"], format="%d/%m/%Y %H:%M"
            )
        except ValueError:
            rejeitados.append((arquivo, reg["linha"], "formato inválido"))
            continue

        if not reg["id_venda"].strip().isdigit() or quantidade <= 0:
            rejeitados.append(
                (arquivo, reg["linha"], "id_venda ou quantidade inválidos")
            )
            continue

        validas.append({
            "id_venda": reg["id_venda"].strip(),
            "data_venda": data_venda.strftime("%Y-%m-%d"),
            "cliente": reg["cliente"].strip(),
            "produto": reg["produto"].strip(),
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "valor_total": round(quantidade * valor_unitario, 2),
            "atualizado_em": atualizado_em.strftime("%Y-%m-%d %H:%M:%S"),
            "cancelada": reg["status"].strip().upper() == "CANCELADA",
        })

    resumo["rejeitadas"] = len(rejeitados)

    # R2: por id_venda, vale o atualizado_em mais recente
    validas.sort(key=lambda v: v["atualizado_em"])
    ultima = {v["id_venda"]: v for v in validas}
    resumo["duplicatas"] = len(validas) - len(ultima)

    vendas, cancelar = [], []
    for v in ultima.values():
        if v.pop("cancelada"):
            cancelar.append((v["id_venda"], v["atualizado_em"]))
        else:
            vendas.append(v)
    resumo["canceladas"] = len(cancelar)
    resumo["carregadas"] = len(vendas)
    return vendas, cancelar, rejeitados, resumo


def carregar(vendas, cancelar, rejeitados, arquivo, caminho_banco):
    conn = sqlite3.connect(caminho_banco)
    try:
        conn.executescript(DDL)
        with conn:  # uma transação: commit no fim ou rollback se algo falhar
            conn.execute(
                "DELETE FROM rejeitados WHERE arquivo = ?", (arquivo,)
            )
            conn.executemany(
                "INSERT INTO rejeitados VALUES (?, ?, ?)", rejeitados
            )
            conn.executemany(UPSERT, vendas)
            # R1: canceladas saem, inclusive as de dias anteriores
            conn.executemany(APAGAR_CANCELADA, cancelar)
    finally:
        conn.close()


def executar(caminho_csv, caminho_banco):
    arquivo = Path(caminho_csv).name
    df = extrair(caminho_csv)
    vendas, cancelar, rejeitados, resumo = transformar(df, arquivo)
    carregar(vendas, cancelar, rejeitados, arquivo, caminho_banco)
    return resumo
```

**Como o script garante a R5, segundo a IA:** `id_venda` é chave primária e a gravação é um upsert, então a mesma venda nunca vira duas linhas. Os rejeitados do arquivo são apagados e regravados. Tudo roda numa transação: se algo falhar no meio, nada fica gravado pela metade. Rodar o mesmo arquivo de novo leva ao mesmo estado.

A função `executar` devolve um resumo com as contagens (lidas, rodapé, rejeitadas, canceladas, duplicatas, carregadas), que permite conferir o critério de "toda linha tem destino".

---

## Comparação final

| Critério | Prompt 1 | Prompt 2 | Prompt 3 |
|---|---:|---:|---:|
| Clareza | 4 | 5 | 4 |
| Precisão | 1 | 3 | 4 |
| Relevância | 2 | 4 | 5 |
| Organização | 4 | 4 | 5 |
| Adequação ao público | 3 | 5 | 3 |
| Atendimento ao objetivo | 1 | 3 | 5 |
| Utilidade | 1 | 3 | 5 |
| **Total (máx. 35)** | **16** | **27** | **31** |

**Por que o Prompt 3 não levou 5 em precisão:** acertou as dez perguntas, mas falhou num teste a mais que eu fiz para conferir uma promessa da própria resposta (ver Validação).

**Por que clareza e adequação ao público caíram:** o programa 3 tem quase três vezes o tamanho do programa 2. Está correto e bem organizado, mas é difícil para quem "usa pandas no básico", que foi o público que eu mesmo declarei.

**Qual modificação teve maior impacto no resultado?** Do Prompt 1 para o 2, descrever como o arquivo é. Do Prompt 2 para o 3, descrever como o programa é usado: "roda todo dia, roda de novo se falhar, o arquivo pode trazer mudanças de ontem". Essa informação não está em lugar nenhum do arquivo, e foi ela que resolveu as duplicações e a venda cancelada que continuava no painel.

Uma limitação do meu teste: mudei várias coisas de uma vez em cada rodada, então não dá para dizer qual delas, sozinha, fez a diferença.

---

## Validação

Não aceitei nenhum programa só porque parecia certo. Os três rodaram com os dois arquivos, na mesma sequência, e um script de conferência (`avaliar.py`) respondeu as dez perguntas automaticamente.

| Pergunta | Prompt 1 | Prompt 2 | Prompt 3 |
|---|:---:|:---:|:---:|
| C1 Abre o arquivo com acentos | não | sim | sim |
| C2 Ignora a linha de total | não | não | sim |
| C3 Centavos e totais certos | não | sim | sim |
| C4 Data no formato brasileiro | não | sim | sim |
| C5 Venda repetida: fica a mais recente | não | sim | sim |
| C6 Cancelada fica de fora | não | sim | sim |
| C7 Linha com defeito vai para lista separada | não | não | sim |
| C8 Rodar de novo não duplica | não | não | sim |
| C9 Dia novo mantém os anteriores | não | sim | sim |
| C10 Cancelada no dia seguinte sai | não | não | sim |
| **Total** | **0/10** | **6/10** | **10/10** |

**Teste a mais: a promessa da resposta 3.** A IA garantiu que, se um arquivo antigo fosse rodado de novo depois de um mais novo, nada seria desfeito. Testei: carreguei o dia 02/09, depois o 03/09 (que cancela a venda 1003) e rodei o 02/09 outra vez. **A venda cancelada voltou para o painel.** O motivo, em palavras simples: quando a venda é cancelada, o programa apaga a venda inteira, e junto some a informação de que ela foi cancelada. Quando o arquivo antigo é rodado de novo, o programa não tem mais como saber disso e trata a venda como nova. Uma saída seria marcar a venda como cancelada em vez de apagar; seria a hipótese de um quarto prompt, que não cheguei a testar.

**Conferência das contas.** O programa 3 informa quantas linhas foram para cada lugar, e as contas fecham. No arquivo de 02/09: 8 linhas = 1 linha de total + 1 com defeito + 1 repetida + 1 cancelada + 4 vendas carregadas.

**Conferência dos valores.** Refiz as contas à mão: 4 × 1.234,56 = 4.938,24 e 2 × 899,99 = 1.799,98. A venda 1002 aparece duas vezes e deve ficar com 3.299,00 (a das 15:47). No arquivo, a versão mais nova vem antes da antiga, de propósito, para testar se o programa olha o horário e não a ordem das linhas.

**Checklist da aula**
- [x] A informação pode ser confirmada? Sim, rodando os programas com os arquivos.
- [x] Os conceitos existem? Sim, os recursos usados funcionaram nas versões testadas.
- [x] A resposta atende ao problema? Programa 1 não; programa 2 em parte; programa 3 sim, com a falha do teste a mais.
- [x] Existem afirmações sem sustentação? Sim: a promessa da resposta 3 que o teste derrubou.
- [x] A IA apresentou referências? Não havia referências nas respostas.
- [x] Consigo explicar a resposta com minhas palavras? Sim, inclusive o motivo da falha do teste a mais.

**Limites da validação:** os arquivos de teste são pequenos e foram montados por mim, então só cobrem os problemas que eu conheço. Não testei arquivos grandes.

Os arquivos da validação (os dois arquivos de vendas, os três programas e o `avaliar.py`) estão na pasta `aula-03/validacao/` do repositório. Para reproduzir: `pip install pandas` e `python avaliar.py`.

---

## Reflexão

### 1. Qual foi a principal diferença entre os prompts?
O Prompt 1 pedia "um ETL qualquer". O 2 descrevia o arquivo. O 3 descrevia o arquivo como ele realmente chega, contava como o programa é usado no dia a dia e dizia como eu ia conferir o resultado.

### 2. Quais elementos tiveram maior impacto?
O contexto, em duas partes: como o dado é (do 1 para o 2) e como o programa é usado (do 2 para o 3). O papel ("atue como engenheiro de dados") e o público quase não mudaram o resultado.

### 3. Um prompt maior é necessariamente melhor?
Não. O Prompt 3 é o maior e deu o melhor programa, mas a melhora veio de poucas frases, como "se falhar, é executado de novo com o mesmo arquivo". Por outro lado, a resposta também cresceu e ficou difícil para o público que declarei. E o pedido de "código legível", que só aumentava o prompt, não mudou nada.

### 4. O que ocorre quando o objetivo não é claro?
A IA preenche o que falta com o caso mais comum. No Prompt 1, ela supôs o padrão de acentos mais comum, vírgula como separador, data no formato americano e uma carga que apaga tudo antes. Cada suposição faz sentido sozinha; juntas, deram um programa que trava ou, pior, grava tudo errado e diz que deu certo.

### 5. Quais informações são indispensáveis?
Como o dado chega (inclusive os defeitos), as regras do negócio, como o programa vai ser usado e um jeito de conferir se a resposta está certa.

### 6. Como essa habilidade pode ser utilizada profissionalmente?
Em qualquer trabalho com dados. As coisas que mais dão problema (rodar de novo, carregar só o que mudou, guardar as linhas com defeito) quase nunca aparecem no pedido inicial. Aprender a escrever isso num prompt é o mesmo que aprender a escrever um bom pedido para outra pessoa.

### 7. Quais riscos existem ao confiar automaticamente na IA?
Com dados, o maior risco é o erro que não avisa. Os programas 1 (com os acentos corrigidos) e 2 terminaram sem erro e deixaram o painel errado: vendas duplicadas, venda cancelada contando como faturamento e uma "venda" chamada "Total de registros: 7". Alguém tomaria decisão em cima desses números.

### 8. Houve alguma situação em que o Prompt 3 ficou pior que o Prompt 2?
Sim. O programa ficou quase três vezes maior e mais difícil de entender para um iniciante. E a resposta fez uma promessa que não se confirmou no teste. Quanto mais coisas a resposta garante, mais coisas é preciso conferir.

### 9. Existe um ponto em que adicionar mais instruções começa a prejudicar a resposta?
Existe. Cada regra nova aumenta o programa e a chance de duas regras se atrapalharem. Foi o que aconteceu aqui: "cancelada sai do painel" e "arquivo antigo não desfaz nada" funcionam separadas, mas juntas geraram o erro do teste a mais. O sinal de alerta é a resposta crescer mais rápido que o problema.

### 10. O que você faria para verificar se a resposta está tecnicamente correta?
Rodar com o dado real, e não com um exemplo limpo. Escrever as perguntas de conferência antes de ver a resposta. Testar o que acontece quando o programa roda de novo. E testar cada promessa que a própria resposta faz.

---

## Take Away

> Um bom prompt não é simplesmente um prompt longo. Ele precisa contar a situação real (como o dado chega e como a resposta vai ser usada) e dizer como o resultado vai ser conferido.

---

## Cinco recomendações

1. **Mostre o dado como ele chega, com os defeitos.** Exemplo bonito gera resposta que só funciona com dado bonito.
2. **Conte como a resposta vai ser usada.** Todo dia? Pode rodar de novo? A IA não tem como adivinhar.
3. **Diga como você vai conferir.** "Rodar duas vezes deixa tudo igual" ajuda; "faça um bom código" não.
4. **Peça que a IA liste as dúvidas antes de responder.** Assim quem decide é você.
5. **Confira com o dado real e teste as promessas da resposta.** "Concluído com sucesso" na tela não prova nada.

---

## Desafio final

Um colega diz: "Meu prompt não funcionou. A IA respondeu errado." Antes de mexer no prompt, eu perguntaria:

1. O que exatamente você esperava, e isso estava escrito no prompt?
2. A IA viu o material real (o arquivo, a planilha, o erro) ou só uma descrição?
3. A resposta está errada ou só diferente do que você imaginava?
4. Como você descobriu que está errada: testou, comparou com uma fonte ou só leu?
5. Se rodar o mesmo prompt de novo, o erro se repete?

**O problema está no prompt, na resposta, nas informações ou na avaliação?** Nesta atividade apareceram os quatro. O Prompt 1 não tinha informação suficiente. As linhas de exemplo do Prompt 2 só mostravam o caso fácil. A resposta 3 prometeu algo que não cumpria. E, se eu tivesse confiado na mensagem "ETL concluído com sucesso" do programa 1, teria aprovado um painel com dados embaralhados.
