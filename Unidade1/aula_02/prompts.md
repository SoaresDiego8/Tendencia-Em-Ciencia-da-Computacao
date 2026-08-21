# Prompts

Este arquivo reune o molde reutilizavel (prompt mestre), a primeira instancia
concreta dele (prompt inicial), o payload usado como entrada e a resposta obtida
do LLM na primeira tentativa.

Cada prompt foi executado em uma conversa nova. Rodar as variacoes em sequencia
no mesmo chat faria o modelo carregar o contexto da resposta anterior, e a
variacao deixaria de isolar o eixo que se quer medir.

**Modelo usado:** Claude Opus 5 (Anthropic) | **Data:** 21/08/2026

---

## 1. Prompt Mestre (molde)

Anatomia profissional com os campos a preencher. Todas as versoes testadas neste
trabalho sao instancias deste molde, variando um bloco por vez.

```text
[PAPEL] Voce e {persona}.

[INSTRUCAO] {tarefa central em uma frase}.

[CONTEXTO] {para quem, para que, qual o destino, qual a frequencia}.

[RESTRICOES]
- {limite 1}
- {limite 2}

[CRITERIOS DE QUALIDADE]
1. {metrica pela qual a resposta sera medida}
2. {metrica 2}

[FORMATO] {estrutura exata da saida}.

[EXEMPLOS] (opcional) {par entrada/saida}.

[ENTRADA]
<json>
{payload}
</json>
```

---

## 2. Tecnicas utilizadas

| Tecnica | Onde aparece |
|---|---|
| Role Prompting | Todas as versoes; refinada na Variacao 1 com persona especifica e consequencia declarada |
| Instrucao (Task) | Todas |
| Contexto | Todas: carga incremental, destino relacional, consumo em dashboard |
| Formato de Saida | Markdown no inicial, na Variacao 1 e na Variacao 3; JSON estrito na Variacao 2 e no refinado |
| Restricoes | Variacao 1 e refinado: proibicao de inferir campos, secao obrigatoria para ausentes |
| Few-Shot | Variacao 3 e refinado: par entrada/saida com campo nulo e array aninhado |
| Criterios de Qualidade | Apenas no refinado: cobertura exaustiva, fidelidade, rastreabilidade e autoverificacao com contagem |

---

## 3. Prompt Inicial

Preenche Papel, Instrucao, Contexto e Formato. Sem restricoes, sem criterios de
qualidade e sem exemplos: e a primeira tentativa, e serve de linha de base.

```text
Você é um engenheiro de dados.

Analise o JSON abaixo, retornado pela API pública do Datajud (CNJ), e proponha
o mapeamento dele para um schema normalizado que será carregado em um data
warehouse. Descreva os campos de origem, os campos de destino e as regras de
transformação necessárias.

Contexto: a ingestão é incremental e alimenta um dashboard de acompanhamento
processual. O destino é um banco relacional.

Formato: apresente o resultado em uma tabela Markdown seguida de um breve
comentário sobre os pontos de atenção da transformação.

<json>
{cole aqui o conteúdo de dados/payload-exemplo.json}
</json>
```

---

## 4. Payload de entrada

Substitui o marcador `{cole aqui...}` em todos os prompts deste trabalho.

Arquivo sintetico: reproduz a estrutura da API publica do Datajud (CNJ),
incluindo aninhamentos, campos nulos e chaves opcionais, sem usar dado de
processo real. A escolha permite conhecer com precisao a resposta correta, que e
o que torna a metrica de cobertura possivel.

```json
{
  "_index": "api_publica_tjdft",
  "_id": "TJDFT_G1_13597_07001234520248070001",
  "_score": 1.0,
  "_source": {
    "numeroProcesso": "07001234520248070001",
    "tribunal": "TJDFT",
    "grau": "G1",
    "nivelSigilo": 0,
    "dataAjuizamento": "2024-03-11T14:22:05.000Z",
    "dataHoraUltimaAtualizacao": "2026-08-14T03:11:47.921Z",
    "classe": {
      "codigo": 436,
      "nome": "Procedimento Comum Cível"
    },
    "sistema": {
      "codigo": 1,
      "nome": "PJe"
    },
    "formato": {
      "codigo": 1,
      "nome": "Eletrônico"
    },
    "orgaoJulgador": {
      "codigo": 13597,
      "nome": "3ª Vara Cível de Brasília",
      "codigoMunicipioIBGE": 5300108,
      "codigoOrgaoJustica": null
    },
    "assuntos": [
      {
        "codigo": 10431,
        "nome": "Inadimplemento"
      },
      {
        "codigo": 7681,
        "nome": "Cláusula Penal",
        "principal": false
      }
    ],
    "movimentos": [
      {
        "codigo": 26,
        "nome": "Distribuição",
        "dataHora": "2024-03-11T14:22:05.000Z",
        "orgaoJulgador": {
          "codigoOrgao": 13597,
          "nomeOrgao": "3ª Vara Cível de Brasília"
        },
        "complementosTabelados": [
          {
            "codigo": 3,
            "valor": 1,
            "nome": "tipo_de_distribuicao_redistribuicao",
            "descricao": "sorteio"
          }
        ]
      },
      {
        "codigo": 51,
        "nome": "Conclusão",
        "dataHora": "2024-04-02T09:07:41.000Z"
      },
      {
        "codigo": 193,
        "nome": "Julgamento",
        "dataHora": "2025-11-18T16:45:00.000Z",
        "complementosTabelados": [
          {
            "codigo": 7,
            "valor": 2,
            "nome": "tipo_de_decisao",
            "descricao": "com resolução do mérito"
          }
        ]
      }
    ],
    "dataArquivamento": null,
    "@timestamp": "2026-08-14T03:12:02.118Z"
  }
}
```

---

## 5. Resposta obtida (prompt inicial)

Output colado sem edicao, exatamente como retornado pelo modelo.

## Mapeamento proposto

Sugiro modelar em três tabelas relacionais: uma dimensão de processo e duas
tabelas filhas para os arrays.

### `dim_processo`

| Campo de origem | Campo de destino | Tipo | Regra de transformação |
|---|---|---|---|
| `numeroProcesso` | `numero_processo` | VARCHAR(20) | Chave natural. Remover máscara se vier formatada. |
| `tribunal` | `sigla_tribunal` | VARCHAR(10) | Uppercase. |
| `grau` | `grau` | VARCHAR(3) | Domínio: G1, G2, JE. |
| `nivelSigilo` | `nivel_sigilo` | SMALLINT | Filtrar registros com sigilo > 0 antes de expor no dashboard. |
| `dataAjuizamento` | `data_ajuizamento` | TIMESTAMP | Converter de UTC para America/Sao_Paulo. |
| `dataHoraUltimaAtualizacao` | `data_ultima_atualizacao` | TIMESTAMP | Watermark da carga incremental. |
| `classe.codigo` | `cod_classe` | INTEGER | — |
| `classe.nome` | `nome_classe` | VARCHAR(255) | Trim. |
| `sistema.nome` | `sistema_origem` | VARCHAR(50) | — |
| `formato.nome` | `formato_processo` | VARCHAR(20) | — |
| `orgaoJulgador.codigo` | `cod_orgao_julgador` | INTEGER | — |
| `orgaoJulgador.nome` | `nome_orgao_julgador` | VARCHAR(255) | — |
| `orgaoJulgador.codigoMunicipioIBGE` | `cod_municipio_ibge` | INTEGER | Chave para dimensão geográfica. |
| `dataArquivamento` | `data_arquivamento` | TIMESTAMP NULL | Nulo indica processo em curso. |
| `valorCausa` | `valor_causa` | NUMERIC(15,2) | Converter para centavos ou manter duas casas. |
| `situacao` | `situacao_processo` | VARCHAR(50) | Normalizar para domínio controlado. |
| — | `sk_processo` | BIGINT | Chave surrogate gerada na carga. |
| — | `data_ingestao` | TIMESTAMP | Timestamp de execução do pipeline. |

### `fato_movimento`

| Campo de origem | Campo de destino | Tipo | Regra de transformação |
|---|---|---|---|
| `movimentos[].codigo` | `cod_movimento` | INTEGER | Código da TPU/CNJ. |
| `movimentos[].nome` | `nome_movimento` | VARCHAR(255) | — |
| `movimentos[].dataHora` | `data_hora_movimento` | TIMESTAMP | Converter fuso. |
| `movimentos[].complementosTabelados[].descricao` | `descricao_complemento` | VARCHAR(255) | Concatenar quando houver mais de um. |
| — | `numero_processo` | VARCHAR(20) | Propagar do pai para manter o vínculo. |

### `ponte_processo_assunto`

| Campo de origem | Campo de destino | Tipo | Regra de transformação |
|---|---|---|---|
| `assuntos[].codigo` | `cod_assunto` | INTEGER | — |
| `assuntos[].nome` | `nome_assunto` | VARCHAR(255) | — |
| — | `numero_processo` | VARCHAR(20) | Propagar do pai. |

## Pontos de atenção

1. **Achatamento de arrays.** `movimentos` e `assuntos` são coleções aninhadas e
   não cabem na tabela de processo sem perda. Explodir em tabelas filhas é o
   caminho mais seguro.
2. **Fuso horário.** Todas as datas chegam em UTC com sufixo `Z`. Padronize a
   conversão em um único ponto do pipeline.
3. **Carga incremental.** Use `dataHoraUltimaAtualizacao` como watermark, mas
   trate reprocessamento: o mesmo processo volta com movimentos novos, então a
   estratégia deve ser upsert por `numeroProcesso` e delete/insert dos filhos.
4. **Campos opcionais.** Alguns registros podem não trazer `dataArquivamento`
   ou `valorCausa`. Defina os campos como nullable no destino.
5. **Partes do processo.** Se o payload completo trouxer o array de partes,
   será necessária mais uma tabela filha com CPF/CNPJ mascarado por LGPD.

---

## Leitura rapida do resultado inicial

Cobertura de 60,6% dos 33 caminhos-folha do payload, com dois campos citados que
nao existem no JSON: `valorCausa` e `situacao`. Nenhum dos dois e aleatorio, os
dois aparecem em outras APIs processuais. O modelo completou o que era provavel
para o dominio, e o resultado passa despercebido justamente por ser plausivel.

A medicao esta em `comparacao.md`.
