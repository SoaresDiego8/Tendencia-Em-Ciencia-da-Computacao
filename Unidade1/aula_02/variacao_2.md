# Variacao 2: Formato de Saida

**Hipótese:** um schema de saída rígido, com um objeto por campo mapeado, força
o modelo a percorrer a estrutura em vez de resumir em prosa, aumentando a
cobertura.
**O que mudou em relação ao inicial:** formato Markdown substituído por JSON
estrito com schema declarado.
**O que permaneceu igual:** persona genérica, tarefa e contexto do prompt
inicial. Sem restrição anti-inferência, sem exemplo.

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

Formato de saída: responda exclusivamente com um objeto JSON válido, sem
texto antes ou depois, sem cercas de código, obedecendo ao schema:

{
  "tabelas": [
    {
      "nome": "<nome da tabela de destino>",
      "granularidade": "<uma linha por ...>",
      "colunas": [
        {
          "caminho_origem": "<caminho JSONPath simplificado no payload, ou DERIVADO>",
          "coluna_destino": "<nome no destino>",
          "tipo": "<tipo SQL>",
          "nulo_permitido": true,
          "transformacao": "<regra ou 'copia direta'>"
        }
      ]
    }
  ],
  "pontos_de_atencao": ["<string>"]
}

Gere um objeto em "colunas" para cada campo mapeado.

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

```json
{
  "tabelas": [
    {
      "nome": "dim_processo",
      "granularidade": "uma linha por processo",
      "colunas": [
        {"caminho_origem": "_id", "coluna_destino": "id_documento_origem", "tipo": "VARCHAR(80)", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.numeroProcesso", "coluna_destino": "numero_processo", "tipo": "VARCHAR(20)", "nulo_permitido": false, "transformacao": "remover mascara se presente"},
        {"caminho_origem": "_source.tribunal", "coluna_destino": "sigla_tribunal", "tipo": "VARCHAR(10)", "nulo_permitido": false, "transformacao": "uppercase"},
        {"caminho_origem": "_source.grau", "coluna_destino": "grau", "tipo": "VARCHAR(3)", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.nivelSigilo", "coluna_destino": "nivel_sigilo", "tipo": "SMALLINT", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.dataAjuizamento", "coluna_destino": "data_ajuizamento", "tipo": "TIMESTAMPTZ", "nulo_permitido": false, "transformacao": "parse ISO-8601 UTC"},
        {"caminho_origem": "_source.dataHoraUltimaAtualizacao", "coluna_destino": "data_ultima_atualizacao", "tipo": "TIMESTAMPTZ", "nulo_permitido": false, "transformacao": "parse ISO-8601 UTC; usado como watermark"},
        {"caminho_origem": "_source.dataArquivamento", "coluna_destino": "data_arquivamento", "tipo": "TIMESTAMPTZ", "nulo_permitido": true, "transformacao": "parse ISO-8601 UTC quando nao nulo"},
        {"caminho_origem": "_source.classe.codigo", "coluna_destino": "cod_classe", "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.classe.nome", "coluna_destino": "nome_classe", "tipo": "VARCHAR(255)", "nulo_permitido": false, "transformacao": "trim"},
        {"caminho_origem": "_source.sistema.codigo", "coluna_destino": "cod_sistema", "tipo": "SMALLINT", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.sistema.nome", "coluna_destino": "nome_sistema", "tipo": "VARCHAR(50)", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.formato.codigo", "coluna_destino": "cod_formato", "tipo": "SMALLINT", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.formato.nome", "coluna_destino": "nome_formato", "tipo": "VARCHAR(20)", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.orgaoJulgador.codigo", "coluna_destino": "cod_orgao_julgador", "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.orgaoJulgador.nome", "coluna_destino": "nome_orgao_julgador", "tipo": "VARCHAR(255)", "nulo_permitido": false, "transformacao": "trim"},
        {"caminho_origem": "_source.orgaoJulgador.codigoMunicipioIBGE", "coluna_destino": "cod_municipio_ibge", "tipo": "INTEGER", "nulo_permitido": true, "transformacao": "chave para dimensao geografica"},
        {"caminho_origem": "_source.@timestamp", "coluna_destino": "data_indexacao_origem", "tipo": "TIMESTAMPTZ", "nulo_permitido": false, "transformacao": "parse ISO-8601 UTC"},
        {"caminho_origem": "DERIVADO", "coluna_destino": "sk_processo", "tipo": "BIGINT", "nulo_permitido": false, "transformacao": "sequencia gerada na carga"},
        {"caminho_origem": "DERIVADO", "coluna_destino": "data_ingestao", "tipo": "TIMESTAMPTZ", "nulo_permitido": false, "transformacao": "now() na execucao"}
      ]
    },
    {
      "nome": "processo_assunto",
      "granularidade": "uma linha por assunto do processo",
      "colunas": [
        {"caminho_origem": "DERIVADO", "coluna_destino": "numero_processo", "tipo": "VARCHAR(20)", "nulo_permitido": false, "transformacao": "propagado do pai"},
        {"caminho_origem": "_source.assuntos[].codigo", "coluna_destino": "cod_assunto", "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.assuntos[].nome", "coluna_destino": "nome_assunto", "tipo": "VARCHAR(255)", "nulo_permitido": false, "transformacao": "trim"}
      ]
    },
    {
      "nome": "processo_movimento",
      "granularidade": "uma linha por movimento do processo",
      "colunas": [
        {"caminho_origem": "DERIVADO", "coluna_destino": "numero_processo", "tipo": "VARCHAR(20)", "nulo_permitido": false, "transformacao": "propagado do pai"},
        {"caminho_origem": "_source.movimentos[].codigo", "coluna_destino": "cod_movimento", "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "codigo TPU"},
        {"caminho_origem": "_source.movimentos[].nome", "coluna_destino": "nome_movimento", "tipo": "VARCHAR(255)", "nulo_permitido": false, "transformacao": "trim"},
        {"caminho_origem": "_source.movimentos[].dataHora", "coluna_destino": "data_hora_movimento", "tipo": "TIMESTAMPTZ", "nulo_permitido": false, "transformacao": "parse ISO-8601 UTC"}
      ]
    },
    {
      "nome": "movimento_complemento",
      "granularidade": "uma linha por complemento tabelado de movimento",
      "colunas": [
        {"caminho_origem": "DERIVADO", "coluna_destino": "numero_processo", "tipo": "VARCHAR(20)", "nulo_permitido": false, "transformacao": "propagado do avo"},
        {"caminho_origem": "_source.movimentos[].complementosTabelados[].codigo", "coluna_destino": "cod_complemento", "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.movimentos[].complementosTabelados[].nome", "coluna_destino": "nome_complemento", "tipo": "VARCHAR(255)", "nulo_permitido": false, "transformacao": "copia direta"},
        {"caminho_origem": "_source.movimentos[].complementosTabelados[].valor", "coluna_destino": "valor_complemento", "tipo": "INTEGER", "nulo_permitido": true, "transformacao": "copia direta"},
        {"caminho_origem": "_source.movimentos[].complementosTabelados[].descricao", "coluna_destino": "descricao_complemento", "tipo": "VARCHAR(255)", "nulo_permitido": true, "transformacao": "copia direta"}
      ]
    }
  ],
  "pontos_de_atencao": [
    "Arrays aninhados nao possuem identificador estavel; a carga dos filhos deve ser delete/insert por processo.",
    "O vinculo entre movimento e complemento depende da posicao no array, o que exige gerar um indice na carga.",
    "Todas as datas chegam em UTC e devem ser convertidas em um unico ponto do pipeline.",
    "Um unico documento de exemplo nao permite inferir cardinalidade nem opcionalidade real dos campos."
  ]
}
```

## Leitura do resultado

Cobertura de 81,8%, sem nenhum campo inexistente.

O prompt nao pede exaustividade em momento nenhum. A cobertura subiu porque um
schema que exige um objeto por campo empurra o modelo a percorrer a estrutura em
vez de resumir. Prosa permite resumir; JSON com schema declarado, nao.

Todo o ganho em relacao a Variacao 1 foi dentro de `complementosTabelados`: uma
linha por campo obriga a abrir o array. Sobraram seis campos, todos do tipo
dificil: chave presente em so um item do array, objeto aninhado em dois niveis e
campo nulo.

Ganho colateral que a metrica de cobertura nao mostra: a saida e JSON valido,
consumivel direto por script. As respostas em Markdown precisam de alguem para
transcrever, e a transcricao e o passo onde o erro humano entra.
