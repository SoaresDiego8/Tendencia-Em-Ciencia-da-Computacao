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

## 5. Prompt Refinado:
```
Você é um engenheiro de dados sênior responsável por pipelines de ingestão de
APIs públicas. Sua reputação depende de nunca entregar um mapeamento que
referencie campos inexistentes, porque isso quebra a carga em produção.

Tarefa: mapear o JSON fornecido para um schema relacional normalizado de data
warehouse, incluindo caminhos de origem, colunas de destino, tipos, nulidade e
regras de transformação.

Contexto: a ingestão é incremental, alimenta um dashboard de acompanhamento
processual e roda diariamente. O payload é a resposta da API pública do Datajud
(CNJ). O destino é um banco relacional.

Restrições:
- Mapeie exclusivamente campos que existem literalmente no JSON fornecido.
- Não presuma campos que costumam aparecer nesse tipo de API.
- Colunas derivadas (chave surrogate, auditoria, propagação de chave do pai)
  devem usar o caminho de origem "DERIVADO".
- Campos que você optar por não carregar devem ir para "campos_ignorados" com
  justificativa, nunca ser omitidos em silêncio.

Critérios de qualidade (a resposta será medida por eles):
1. Cobertura: todo caminho-folha do JSON deve aparecer exatamente uma vez, seja
   em "colunas", seja em "campos_ignorados". Caminhos dentro de arrays são
   representados com "[]" e contam uma única vez.
2. Fidelidade: zero caminhos de origem que não existam no JSON.
3. Rastreabilidade: cada tabela declara sua granularidade e sua ligação com a
   tabela pai.
4. Ao final, preencha "autoverificacao" com a contagem de caminhos-folha que
   você identificou no JSON, quantos foram mapeados e quantos foram ignorados.
   Os dois últimos devem somar o primeiro.

Formato de saída: responda exclusivamente com um objeto JSON válido, sem texto
antes ou depois e sem cercas de código, no schema:

{
  "tabelas": [
    {
      "nome": "<string>",
      "granularidade": "<uma linha por ...>",
      "tabela_pai": "<nome ou null>",
      "colunas": [
        {
          "caminho_origem": "<caminho no payload ou DERIVADO>",
          "coluna_destino": "<string>",
          "tipo": "<tipo SQL>",
          "nulo_permitido": true,
          "transformacao": "<regra ou 'copia direta'>"
        }
      ]
    }
  ],
  "campos_ignorados": [
    {"caminho_origem": "<string>", "justificativa": "<string>"}
  ],
  "pontos_de_atencao": ["<string>"],
  "autoverificacao": {
    "caminhos_folha_identificados": 0,
    "mapeados": 0,
    "ignorados": 0
  }
}

Exemplo resolvido (padrão a seguir, com outro payload):

Entrada:
{"_id": "ABC_1", "_source": {"codigoUnidade": 55, "responsavel": null,
 "etiquetas": [{"id": 9, "texto": "urgente", "meta": {"origem": "manual"}}]}}

Saída:
{"tabelas": [
  {"nome": "dim_unidade", "granularidade": "uma linha por unidade",
   "tabela_pai": null, "colunas": [
    {"caminho_origem": "_id", "coluna_destino": "id_documento_origem",
     "tipo": "VARCHAR(80)", "nulo_permitido": false, "transformacao": "copia direta"},
    {"caminho_origem": "_source.codigoUnidade", "coluna_destino": "cod_unidade",
     "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "copia direta"},
    {"caminho_origem": "_source.responsavel", "coluna_destino": "responsavel",
     "tipo": "VARCHAR(255)", "nulo_permitido": true, "transformacao": "nulo no exemplo; manter nullable"}]},
  {"nome": "unidade_etiqueta", "granularidade": "uma linha por etiqueta",
   "tabela_pai": "dim_unidade", "colunas": [
    {"caminho_origem": "DERIVADO", "coluna_destino": "cod_unidade",
     "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "propagado do pai"},
    {"caminho_origem": "_source.etiquetas[].id", "coluna_destino": "id_etiqueta",
     "tipo": "INTEGER", "nulo_permitido": false, "transformacao": "copia direta"},
    {"caminho_origem": "_source.etiquetas[].texto", "coluna_destino": "texto_etiqueta",
     "tipo": "VARCHAR(255)", "nulo_permitido": false, "transformacao": "trim"},
    {"caminho_origem": "_source.etiquetas[].meta.origem", "coluna_destino": "origem_etiqueta",
     "tipo": "VARCHAR(50)", "nulo_permitido": true, "transformacao": "achatar objeto aninhado"}]}],
 "campos_ignorados": [],
 "pontos_de_atencao": ["Array sem identificador estavel exige delete/insert por pai."],
 "autoverificacao": {"caminhos_folha_identificados": 6, "mapeados": 6, "ignorados": 0}}

Entrada real:

<json>
{cole aqui o conteúdo de dados/payload-exemplo.json}
</json>
```
