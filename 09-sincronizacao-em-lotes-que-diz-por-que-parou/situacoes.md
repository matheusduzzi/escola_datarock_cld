# Dez situações da sincronização da Loja Aurora

Cada situação é algo que pode acontecer no meio de uma sincronização da página da Renata. Para cada uma, você escreve uma linha na `minha-tabela-de-erros.md`: etapa, código, para ou pula, e a mensagem que a Renata lê na tela.

As etapas são três: `gravador` (listar as gravações e ler as notas), `claude` (a chamada que extrai as entidades) e `banco` (gravar a reunião ou o motivo).

1. O Claude recusa a chamada com o código `rate_limited`. O texto original do erro é "sampling too often".
2. O Claude recusa a chamada com o código `rate_limited`. O texto original não fala de frequência: o limite de uso da conta da Renata acabou.
3. A resposta de um lote vem fora do JSON. A página pede de novo reunião por reunião, e uma delas volta fora do JSON outra vez.
4. O pedido de um lote passa do tamanho que o Claude aceita. O código é `prompt_too_large`.
5. O banco recusa gravar porque o limite de documentos da página acabou. O código é `quota_exceeded`.
6. O banco responde `resource_exhausted`: gravações seguidas demais em pouco tempo.
7. A Renata recusou o pedido de permissão para a página ler as notas do gravador.
8. A nota de uma reunião chega sem resumo. O gravador não gerou o resumo dessa gravação.
9. A listagem do gravador vem em páginas. A primeira página chegou, e a segunda falhou.
10. Chega um erro com um código que a sua tabela não tem.
