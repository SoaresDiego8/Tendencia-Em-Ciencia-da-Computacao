# Variacao 1: Persona + Restricao

**Hipótese:** uma persona mais específica, somada a uma restrição explícita
contra inferência, reduz a invenção de campos que não existem no payload.
**O que mudou em relação ao inicial:** persona detalhada e bloco de restrições.
**O que permaneceu igual:** tarefa, contexto e formato de saída (tabela Markdown).

**Modelo:** Claude Opus 5 (Anthropic) | **Data:** 20/08/2026
**Entrada:** o payload de `prompts.md`, secao 4.

## Prompt

```text
Você é um engenheiro de dados sênior responsável por pipelines de ingestão de
APIs públicas. Sua reputação depende de nunca entregar um mapeamento que
referencie campos inexistentes, porque isso quebra a carga em produção.

Analise o JSON abaixo, retornado pela API pública do Datajud (CNJ), e proponha
o mapeamento dele para um schema normalizado que será carregado em um data
warehouse. Descreva os campos de origem, os campos de destino e as regras de
transformação necessárias.

Contexto: a ingestão é incremental e alimenta um dashboard de acompanhamento
processual. O destino é um banco relacional.

Restrições:
- Mapeie exclusivamente campos que existem literalmente no JSON fornecido.
- Não presuma a existência de campos que costumam aparecer nesse tipo de API.
- Se um campo que você considera necessário não estiver presente, liste-o em
  uma seção separada chamada "Campos ausentes no payload", nunca na tabela de
  mapeamento.
- Colunas derivadas (chaves surrogate, auditoria) devem ser marcadas com
  origem "DERIVADO".

Formato: apresente o resultado em uma tabela Markdown seguida de um breve
comentário sobre os pontos de atenção da transformação.

<json>
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
}</json>
```

## Resultado obtido

Output colado sem edicao.

## Mapeamento

### `dim_processo`

| Campo de origem | Campo de destino | Tipo | Regra |
|---|---|---|---|
| `_source.numeroProcesso` | `numero_processo` | VARCHAR(20) | Chave natural, sem máscara. |
| `_source.tribunal` | `sigla_tribunal` | VARCHAR(10) | — |
| `_source.grau` | `grau` | VARCHAR(3) | — |
| `_source.nivelSigilo` | `nivel_sigilo` | SMALLINT | Não expor no dashboard quando > 0. |
| `_source.dataAjuizamento` | `data_ajuizamento` | TIMESTAMPTZ | UTC de origem. |
| `_source.dataHoraUltimaAtualizacao` | `data_ultima_atualizacao` | TIMESTAMPTZ | Watermark. |
| `_source.dataArquivamento` | `data_arquivamento` | TIMESTAMPTZ NULL | Nulo no exemplo. |
| `_source.classe.codigo` | `cod_classe` | INTEGER | — |
| `_source.classe.nome` | `nome_classe` | VARCHAR(255) | — |
| `_source.sistema.codigo` | `cod_sistema` | SMALLINT | — |
| `_source.sistema.nome` | `nome_sistema` | VARCHAR(50) | — |
| `_source.formato.codigo` | `cod_formato` | SMALLINT | — |
| `_source.formato.nome` | `nome_formato` | VARCHAR(20) | — |
| `_source.orgaoJulgador.codigo` | `cod_orgao_julgador` | INTEGER | — |
| `_source.orgaoJulgador.nome` | `nome_orgao_julgador` | VARCHAR(255) | — |
| `_source.orgaoJulgador.codigoMunicipioIBGE` | `cod_municipio_ibge` | INTEGER | — |
| `_source.@timestamp` | `data_indexacao_origem` | TIMESTAMPTZ | Timestamp do índice de origem. |
| `_id` | `id_documento_origem` | VARCHAR(80) | Identificador do documento no índice. |
| DERIVADO | `sk_processo` | BIGINT | Chave surrogate. |
| DERIVADO | `data_ingestao` | TIMESTAMPTZ | Momento da execução do pipeline. |

### `processo_assunto`

| Campo de origem | Campo de destino | Tipo | Regra |
|---|---|---|---|
| `_source.assuntos[].codigo` | `cod_assunto` | INTEGER | — |
| `_source.assuntos[].nome` | `nome_assunto` | VARCHAR(255) | — |
| DERIVADO | `numero_processo` | VARCHAR(20) | Propagado do pai. |

### `processo_movimento`

| Campo de origem | Campo de destino | Tipo | Regra |
|---|---|---|---|
| `_source.movimentos[].codigo` | `cod_movimento` | INTEGER | Código TPU. |
| `_source.movimentos[].nome` | `nome_movimento` | VARCHAR(255) | — |
| `_source.movimentos[].dataHora` | `data_hora_movimento` | TIMESTAMPTZ | — |
| `_source.movimentos[].complementosTabelados[].descricao` | `descricao_complemento` | VARCHAR(255) | Concatenar múltiplos. |
| DERIVADO | `numero_processo` | VARCHAR(20) | Propagado do pai. |

## Campos ausentes no payload

- Valor da causa: não existe neste retorno; se o dashboard precisar, será
  necessário outra fonte.
- Partes do processo: ausente por decisão da API pública.
- Situação/fase processual: não vem pronta; teria de ser derivada do último
  movimento.

## Pontos de atenção

1. `dataArquivamento` veio nulo no exemplo. Um único registro não permite
   concluir se o campo é sempre nulo ou opcional.
2. `complementosTabelados` só aparece em dois dos três movimentos, então a
   modelagem precisa tolerar ausência.
3. A carga incremental por `dataHoraUltimaAtualizacao` exige upsert no pai e
   substituição completa dos filhos, já que arrays não trazem identificador
   estável.

## Leitura do resultado

Cobertura subiu de 60,6% para 72,7% e os campos inexistentes cairam de 2 para 0.

O ganho de cobertura foi quase todo em campos de primeiro nivel: `sistema.codigo`,
`formato.codigo`, `@timestamp` e `_id`. A restricao fez o modelo olhar o payload
com mais cuidado, mas nao ensinou a descer nos aninhamentos: os nove campos que
faltaram sao os de dentro de arrays e os nulos.

O ponto mais util foi outro. `valorCausa` e `situacao` reapareceram, agora na
secao "Campos ausentes no payload", com a observacao de que precisariam de outra
fonte. A informacao sempre foi util. O problema era ela estar dentro da tabela de
mapeamento, onde viraria codigo de parse quebrado.
