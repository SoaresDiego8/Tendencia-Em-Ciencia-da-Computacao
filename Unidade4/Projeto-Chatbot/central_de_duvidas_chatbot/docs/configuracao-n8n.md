# Configuração dos workflows no n8n

Este documento descreve os componentes necessários para reproduzir ou revisar os dois workflows. Os arquivos de exportação estão em [`../n8n/`](../n8n/) e podem ser importados com **Import from File**. Eles **não contêm credenciais**: depois de importar, é preciso selecionar as credenciais, a planilha e a aba em cada nó indicado. Esta documentação não substitui a inspeção dos nós no ambiente n8n.

## Visão geral

| Workflow | Arquivo | Endpoint | Nós |
|---|---|---|---|
| **Central de Dúvidas - Abertura e Triagem com IA** | `abrir-duvida-n8n.json` | `POST /webhook/abrir-duvida` | 14 + 4 notas |
| **Central de Dúvidas - Chatbot de Acompanhamento** | `chatbot-duvidas-n8n.json` | `POST /webhook/chat-duvida` | 20 + 4 notas |

Os dois workflows usam o fuso `America/Sao_Paulo` e compartilham a mesma planilha.

## Credenciais necessárias

| Credencial | Onde é usada |
|---|---|
| Google Gemini (PaLM) API | Modelo Gemini (Triagem), Modelo Gemini (Chat) |
| Google Sheets OAuth2 | Registrar Dúvida na Planilha, Buscar Dúvida na Planilha, Registrar Informação na Dúvida |
| Gmail OAuth2 | Enviar Resposta ao Aluno, Alertar Equipe |

A chave do Gemini é gerada no Google AI Studio (a mesma usada na Unidade 3 pode ser reaproveitada).

> **Atenção ao importar:** ao selecionar a planilha e a aba nos nós do Google Sheets, o n8n recarrega as colunas e **apaga o mapeamento** que veio no arquivo. Depois de escolher a aba, preencha de novo cada campo com a expressão `{{ $json.<nome_da_coluna> }}` (por exemplo, `{{ $json.protocolo }}`), conforme as listas das seções 6 (envio) e 4 (chat). Deixe vazias as colunas que o nó não deve alterar.
>
> **Testes com `curl` no Windows:** envie o corpo a partir de um arquivo UTF-8 (`--data-binary @arquivo.json`). Passado direto na linha de comando, o texto pode perder a acentuação e o curso "Ciência da Computação" é recusado como inválido.

## Planilha

Crie uma planilha com estas colunas na linha 1, exatamente com estes nomes:

`protocolo, data_abertura, nome, email, curso, duvida, categoria, urgencia, resumo, resposta_ia, classificado_por_ia, status, responsavel, ultima_atualizacao, informacoes_aluno, data_ultima_interacao`

As 12 primeiras são preenchidas no envio. `responsavel` e `ultima_atualizacao` são preenchidas pela equipe. `informacoes_aluno` e `data_ultima_interacao` são preenchidas pela assistente. Restrinja o compartilhamento da planilha e evite dados reais em demonstrações.

---

## Workflow 1: envio e triagem

### 1. Entrada

- Nó **Receber Dúvida da Página** (Webhook): método `POST`, caminho `abrir-duvida`, resposta pelo nó *Respond to Webhook*, `Allowed Origins = *`.
- Recebe JSON com `nome`, `email`, `curso` e `duvida`.
- Como a página é servida em uma origem diferente do n8n, verifique CORS e preflight conforme a hospedagem escolhida. Para uso real, troque `*` pelo domínio da página.
- A URL de teste (`/webhook-test/...`) só funciona enquanto o n8n está ouvindo um evento de teste. A página deve usar a **Production URL** (`/webhook/...`), com o workflow ativo. O endpoint não deve ser tratado como secreto ou mecanismo de autenticação.

### 2. Validação e normalização

Nó **Validar e Normalizar** (Code). Valida os dados no servidor, mesmo que a página também valide no navegador:

| Campo | Regra |
|---|---|
| `nome` | Obrigatório; pelo menos 3 caracteres após trim; espaços repetidos removidos. |
| `email` | Obrigatório; validar formato e converter para minúsculas. |
| `curso` | Obrigatório; um dos cursos da lista. |
| `duvida` | Obrigatória; 10 a 1.000 caracteres após trim. |

O nó **Dados Válidos?** (IF) envia os dados inválidos para **Responder Erro de Validação**, que devolve HTTP 422 com `sucesso: false`, `mensagem` e `erros` por campo.

O mesmo nó cria `duvida_ia`, uma cópia da dúvida em que `{` e `}` viram parênteses. As chaves são usadas como variáveis de template pelo LangChain e poderiam quebrar o prompt.

### 3. Protocolo

Gerado no mesmo nó, no formato `DV-AAAAMMDD-XXXX`, com a data de envio e quatro caracteres aleatórios. Caracteres ambíguos (O/0 e I/1) são evitados. Para uso real, avaliar colisões e garantir unicidade no armazenamento.

### 4. Triagem com IA

- Nó **Classificar e Responder com IA** (Basic LLM Chain), com o prompt de sistema descrito em [`prompt-n8n.md`](prompt-n8n.md).
- Sub-nó **Modelo Gemini (Triagem)**: `models/gemini-3.1-flash-lite`, temperatura 0,2. Se o modelo não estiver disponível na lista, escolha o Flash-Lite ou o Flash mais recente.
- Sub-nó **Formato da Triagem** (Structured Output Parser) com JSON Schema:
  - `categoria`: Acadêmico, Técnico, Financeiro, Outro ou Revisão manual.
  - `urgencia`: Baixa, Média ou Alta.
  - `resumo`: uma frase curta.
  - `resposta`: resposta ao aluno baseada somente na FAQ.
- Configuração do nó: **On Error → Continue (using error output)**. Assim, uma falha da IA segue para o fallback em vez de interromper o fluxo.

### 5. Fallback

O nó **Consolidar Triagem** (Code) recebe tanto a saída de sucesso quanto a de erro da IA. Se a IA falhou ou devolveu valores fora das listas permitidas, aplica:

- `categoria = "Revisão manual"`
- `urgencia = "Média"`
- `resumo`: primeiros 100 caracteres da dúvida
- `resposta_ia = "Recebemos sua dúvida. A equipe da disciplina vai analisá-la e responder em breve."`
- `classificado_por_ia = false`

Também define o `status` inicial (`Respondida` ou `Em revisão`) e o campo `precisa_equipe` (urgência Alta ou status Em revisão).

### 6. Google Sheets

Nó **Registrar Dúvida na Planilha** (Append Row), com as 12 colunas do envio. Configuração: **On Error → Continue (using error output)**. Se a gravação falhar, **Responder Falha no Registro** devolve HTTP 500: a página não mostra sucesso se o registro não ocorreu.

### 7. E-mail e ramificação

- **Enviar Resposta ao Aluno** (Gmail, texto simples): protocolo, categoria, urgência, status, a dúvida e a resposta, com o aviso de que a resposta foi gerada com apoio de IA.
- **Precisa da Equipe?** (IF): se `precisa_equipe` for verdadeiro, **Alertar Equipe** envia um e-mail com assunto `[ATENÇÃO] Dúvida <protocolo> - <urgência> / <categoria>`.
- **Troque `equipe.duvidas@exemplo.com`** pelo e-mail real da equipe no nó **Alertar Equipe**.
- Os dois nós de Gmail estão com **On Error → Continue**: uma falha de e-mail não desfaz o registro, mas também não é informada ao aluno. Teste esse cenário antes de demonstrar.

### 8. Resposta para o frontend

**Responder Sucesso** devolve:

```json
{
  "sucesso": true,
  "protocolo": "DV-20261126-K7QZ",
  "data_abertura": "26/11/2026 10:30",
  "categoria": "Acadêmico",
  "urgencia": "Média",
  "resumo": "Aluno pergunta a data da apresentação do projeto final.",
  "resposta": "A apresentação do projeto final (exposição dos grupos) é em 26/11, no mesmo dia da Avaliação A1.",
  "status": "Respondida",
  "classificado_por_ia": true
}
```

Quando `classificado_por_ia` é `false`, a página informa que a resposta automática não estava disponível.

---

## Workflow 2: chatbot de acompanhamento

### 1. Entrada e validação

- Nó **Receber Mensagem do Chat** (Webhook): `POST`, caminho `chat-duvida`, resposta pelo nó *Respond to Webhook*, `Allowed Origins = *`.
- Nó **Validar Entrada do Chat** (Code):

| Campo | Regra |
|---|---|
| `protocolo` | Formato `DV-AAAAMMDD-XXXX` (convertido para maiúsculas). |
| `email` | Formato válido (convertido para minúsculas). |
| `mensagem` | 1 a 1.000 caracteres. |
| `sessionId` | 8 a 64 caracteres (letras, números e hífen). |

- Entrada inválida → **Responder Entrada Inválida** (HTTP 422).

### 2. Busca e verificação

- **Buscar Dúvida na Planilha** (Get Rows) filtra por `protocolo`. Configurado com **Always Output Data** (para continuar mesmo sem resultado) e **On Error → Continue (using error output)** (falha → **Responder Planilha Indisponível**, HTTP 503).
- **Verificar Identidade** (Code) só libera a conversa se existir uma linha com o protocolo **e** o mesmo e-mail. Monta o contexto enviado à IA apenas com os dados dessa dúvida.
- **Protocolo e E-mail Conferem?** (IF) → se não, **Responder Não Encontrado** (HTTP 404, sem revelar se o protocolo existe).

### 3. Atendimento com Gemini

- **Assistente Gemini** (AI Agent), com o prompt de sistema da persona Duda (veja [`prompt-n8n.md`](prompt-n8n.md)). O agente não tem ferramentas: ele não lê nem grava a planilha.
- Sub-nó **Modelo Gemini (Chat)**: `models/gemini-3.1-flash-lite`, temperatura 0,3.
- Sub-nó **Memória da Sessão** (Window Buffer Memory): chave `protocolo-sessionId`, últimas 10 mensagens.
- Sub-nó **Formato da Resposta** (Structured Output Parser): `resposta` (texto), `informacao_nova` (booleano) e `resumo_informacao` (texto).
- **On Error → Continue (using error output)**: falha → **Responder Assistente Indisponível** (HTTP 503), sem alterar a dúvida.

### 4. Registro e resposta

- **Preparar Resposta** (Code) normaliza a saída e monta a nova linha de `informacoes_aluno` no formato `[dd/MM/aaaa HH:mm] resumo`, acrescentada ao conteúdo anterior.
- **Informação Nova?** (IF):
  - Sim → **Registrar Informação na Dúvida** (Update Row, coluna de busca `protocolo`) → **Responder com Registro** (`registrado: true`). Se a gravação falhar, **Responder sem Registro** devolve a resposta com um aviso e `registrado: false`.
  - Não → **Responder ao Chat** (`registrado: false`).

Formato da resposta:

```json
{ "sucesso": true, "resposta": "Sua dúvida está em revisão com a Profa. Ana...", "status": "Em revisão", "registrado": false }
```

## Credenciais e segurança

- Configure as credenciais do Google, do Gmail e do Gemini no gerenciador de credenciais do n8n.
- Não coloque chaves, tokens, senhas ou credenciais no HTML, no repositório ou nos prompts.
- Restrinja a exposição dos webhooks com controles apropriados: CORS limitado ao domínio da página, limitação de requisições, proteção contra spam e monitoramento.
- Antes de publicar uma nova exportação dos workflows, revise o JSON e remova IDs internos de planilhas, e-mails reais e dados específicos do ambiente.

## Checklist antes de demonstrar

- [ ] Planilha criada com as 16 colunas.
- [ ] Credenciais funcionais configuradas no n8n (Gemini, Sheets, Gmail).
- [ ] E-mail da equipe trocado no nó Alertar Equipe.
- [ ] Os dois workflows ativos (publicados).
- [ ] Validação executada também no servidor.
- [ ] Resposta HTTP 422 testada nos dois workflows.
- [ ] Saída válida da IA conferida.
- [ ] Fallback da IA testado.
- [ ] Gravação no Sheets conferida.
- [ ] E-mail de resposta e alerta conferidos.
- [ ] Verificação de protocolo + e-mail testada (HTTP 404).
- [ ] Registro de informação nova conferido na planilha.
- [ ] Falhas das integrações testadas.
- [ ] Página configurada com as URLs corretas dos webhooks.
- [ ] Apenas dados fictícios utilizados na demonstração.
