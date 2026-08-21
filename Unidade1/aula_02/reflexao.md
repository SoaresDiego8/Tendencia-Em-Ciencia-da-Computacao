# Reflexão

## Cognitivo

**O que mudou na minha compreensão sobre o uso de IA depois de aprender a estruturar um prompt iterativo?**

Antes eu usava LLM como quem pergunta a um colega: mando a dúvida, leio a
resposta, decido se aproveito. O que mudou foi o critério de avaliação.

Parei de perguntar "essa resposta está boa?" e passei a perguntar
"quantos campos ela cobriu e quantos ela inventou?". Escrevi um script curto que
responde isso sem depender do meu olho. A primeira resposta tinha 60% de
cobertura.

A segunda coisa: técnica de prompt não é preferência estética. Testando uma por
vez, deu para ver que cada uma resolve uma falha diferente. A restrição contra
inferência zerou campo inventado e quase não mexeu na cobertura. O formato JSON
aumentou cobertura sem eu ter pedido cobertura. O exemplo resolveu os casos que
os outros dois não tocaram. Se eu tivesse mudado tudo de uma vez, teria um prompt
melhor e nenhuma ideia do motivo.

## Ético

**Qual é a principal responsabilidade de um profissional de tecnologia que utiliza IA generativa para tomar decisões ou produzir conhecimento?**

Manter um critério de verificação que não dependa do modelo.

"Revisar a saída" é fácil de dizer e quase sempre vazio, porque revisar sem
critério é reler até parecer razoável, e texto de LLM sempre parece razoável.
Verificar de verdade é ter algo externo para comparar: o payload, o teste, o dado
bruto. No que fiz aqui, o script não confia nem na contagem que o próprio modelo
declarou. Ele reabre o JSON e conta de novo.

Em pipeline de dados isso pesa mais do que em texto. Um parágrafo errado alguém
lê e desconfia. Um campo mapeado errado vira coluna, vira medida, vira número no
dashboard, e a partir daí ninguém mais questiona: número em dashboard tem uma
autoridade que texto não tem. O erro atravessa a camada onde seria detectável e
chega já com cara de fato.

E a parte que não é técnica: quem assina o pipeline sou eu. "A IA errou" não
existe como justificativa para o cliente. O que existe é ter aceitado a saída sem
conferir.

A regra que eu levo: para toda tarefa em que eu use IA, preciso conseguir
responder como eu saberia que a resposta está errada. Se não tenho resposta para
isso, o problema não é a IA. É que eu ainda não entendi a tarefa bem o bastante
para usar IA nela.
