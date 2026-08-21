# Variacao 3: Few-Shot

**Hipótese:** um exemplo resolvido de outro payload ancora o padrão de saída,
principalmente no tratamento de campos nulos e de arrays aninhados em dois
níveis.
**O que mudou em relação ao inicial:** inclusão de um par entrada/saída como
exemplo.
**O que permaneceu igual:** persona genérica, tarefa, contexto e formato
Markdown. Sem restrição anti-inferência, sem schema rígido.

**Modelo:** Claude Opus 5 (Anthropic) | **Data:** 20/08/2026
**Entrada:** o payload de `prompts.md`, secao 4.

## Prompt

```text
Você é um engenheiro de dados.

Analise o JSON abaixo, retornado pela API pública do Datajud (CNJ), e proponha
o mapeamento dele para um schema normalizado que será carregado em um data
warehouse.

Contexto: a ingestão é incremental e alimenta um dashboard de acompanhamento
processual. O destino é um banco relacional.

Siga exatamente o padrão do exemplo abaixo.

### Exemplo de entrada

{
  "_id": "ABC_1",
  "_source": {
    "codigoUnidade": 55,
    "responsavel": null,
    "etiquetas": [
      {"id": 9, "texto": "urgente", "meta": {"origem": "manual"}}
    ]
  }
}

### Exemplo de saída

**Tabela `dim_unidade`** — uma linha por unidade

| Caminho de origem | Coluna de destino | Tipo | Nulo? | Transformação |
|---|---|---|---|---|
| `_id` | `id_documento_origem` | VARCHAR(80) | não | cópia direta |
| `_source.codigoUnidade` | `cod_unidade` | INTEGER | não | cópia direta |
| `_source.responsavel` | `responsavel` | VARCHAR(255) | sim | nulo no exemplo; manter nullable |

**Tabela `unidade_etiqueta`** — uma linha por etiqueta

| Caminho de origem | Coluna de destino | Tipo | Nulo? | Transformação |
|---|---|---|---|---|
| `_source.etiquetas[].id` | `id_etiqueta` | INTEGER | não | cópia direta |
| `_source.etiquetas[].texto` | `texto_etiqueta` | VARCHAR(255) | não | trim |
| `_source.etiquetas[].meta.origem` | `origem_etiqueta` | VARCHAR(50) | sim | achatar objeto aninhado |

### Entrada real

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

**Tabela `dim_processo`**, uma linha por processo

| Caminho de origem | Coluna de destino | Tipo | Nulo? | Transformação |
|---|---|---|---|---|
| `_id` | `id_documento_origem` | VARCHAR(80) | não | cópia direta |
| `_index` | `indice_origem` | VARCHAR(60) | não | identifica o tribunal no índice |
| `_source.numeroProcesso` | `numero_processo` | VARCHAR(20) | não | remover máscara |
| `_source.tribunal` | `sigla_tribunal` | VARCHAR(10) | não | uppercase |
| `_source.grau` | `grau` | VARCHAR(3) | não | cópia direta |
| `_source.nivelSigilo` | `nivel_sigilo` | SMALLINT | não | cópia direta |
| `_source.dataAjuizamento` | `data_ajuizamento` | TIMESTAMPTZ | não | parse ISO-8601 |
| `_source.dataHoraUltimaAtualizacao` | `data_ultima_atualizacao` | TIMESTAMPTZ | não | watermark da carga |
| `_source.dataArquivamento` | `data_arquivamento` | TIMESTAMPTZ | sim | nulo no exemplo; manter nullable |
| `_source.classe.codigo` | `cod_classe` | INTEGER | não | achatar objeto aninhado |
| `_source.classe.nome` | `nome_classe` | VARCHAR(255) | não | achatar objeto aninhado |
| `_source.sistema.codigo` | `cod_sistema` | SMALLINT | não | achatar objeto aninhado |
| `_source.sistema.nome` | `nome_sistema` | VARCHAR(50) | não | achatar objeto aninhado |
| `_source.formato.codigo` | `cod_formato` | SMALLINT | não | achatar objeto aninhado |
| `_source.formato.nome` | `nome_formato` | VARCHAR(20) | não | achatar objeto aninhado |
| `_source.orgaoJulgador.codigo` | `cod_orgao_julgador` | INTEGER | não | achatar objeto aninhado |
| `_source.orgaoJulgador.nome` | `nome_orgao_julgador` | VARCHAR(255) | não | trim |
| `_source.orgaoJulgador.codigoMunicipioIBGE` | `cod_municipio_ibge` | INTEGER | sim | achatar objeto aninhado |
| `_source.orgaoJulgador.codigoOrgaoJustica` | `cod_orgao_justica` | INTEGER | sim | nulo no exemplo; manter nullable |
| `_source.@timestamp` | `data_indexacao_origem` | TIMESTAMPTZ | não | parse ISO-8601 |

**Tabela `processo_assunto`**, uma linha por assunto

| Caminho de origem | Coluna de destino | Tipo | Nulo? | Transformação |
|---|---|---|---|---|
| `_source.assuntos[].codigo` | `cod_assunto` | INTEGER | não | cópia direta |
| `_source.assuntos[].nome` | `nome_assunto` | VARCHAR(255) | não | trim |
| `_source.assuntos[].principal` | `flag_principal` | BOOLEAN | sim | ausente no primeiro item do array; assumir NULL |

**Tabela `processo_movimento`**, uma linha por movimento

| Caminho de origem | Coluna de destino | Tipo | Nulo? | Transformação |
|---|---|---|---|---|
| `_source.movimentos[].codigo` | `cod_movimento` | INTEGER | não | cópia direta |
| `_source.movimentos[].nome` | `nome_movimento` | VARCHAR(255) | não | trim |
| `_source.movimentos[].dataHora` | `data_hora_movimento` | TIMESTAMPTZ | não | parse ISO-8601 |
| `_source.movimentos[].orgaoJulgador.codigoOrgao` | `cod_orgao_movimento` | INTEGER | sim | achatar objeto aninhado; presente só em alguns movimentos |
| `_source.movimentos[].orgaoJulgador.nomeOrgao` | `nome_orgao_movimento` | VARCHAR(255) | sim | achatar objeto aninhado |

**Tabela `movimento_complemento`**, uma linha por complemento tabelado

| Caminho de origem | Coluna de destino | Tipo | Nulo? | Transformação |
|---|---|---|---|---|
| `_source.movimentos[].complementosTabelados[].codigo` | `cod_complemento` | INTEGER | não | cópia direta |
| `_source.movimentos[].complementosTabelados[].nome` | `nome_complemento` | VARCHAR(255) | não | cópia direta |
| `_source.movimentos[].complementosTabelados[].valor` | `valor_complemento` | INTEGER | sim | cópia direta |
| `_source.movimentos[].complementosTabelados[].descricao` | `descricao_complemento` | VARCHAR(255) | sim | cópia direta |

Observação: `_score` não foi mapeado por ser metadado de relevância da consulta,
sem valor analítico.

## Leitura do resultado

Cobertura de 100%, sem nenhum campo inexistente.

Os campos que sobravam nas variacoes 1 e 2 tinham um padrao claro: aninhados em
dois niveis (`movimentos[].orgaoJulgador.codigoOrgao`), presentes em apenas parte
dos itens do array (`assuntos[].principal`) e nulos
(`orgaoJulgador.codigoOrgaoJustica`). O exemplo do prompt mostrava exatamente
esses tres casos resolvidos, e os tres foram cobertos.

Foi a tecnica de maior retorno isolado deste teste: 18,2 pontos de cobertura com
um unico bloco de exemplo.

O que ela nao resolveu: a saida continua em Markdown, entao nao serve para
automacao. E o campo `_score`, que o modelo decidiu nao mapear, foi declarado em
uma frase solta no fim do texto. A decisao esta certa, mas so foi encontrada
porque estava sendo procurada.
