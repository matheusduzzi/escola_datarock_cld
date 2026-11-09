# Pedido do simulador

Mande numa conversa com a sua planilha anexada. Troque os números pelos da sua planilha e do seu extrato. Antes, veja se a execução de código e criação de arquivos está ligada na sua conta (Settings > Capabilities).

```text
Crie uma página interativa que use as mesmas fórmulas da planilha anexa como motor
de cálculo, com a HyperFormula 2.7.1. Não reescreva as contas em JavaScript: grave
as fórmulas da planilha nas mesmas abas e nas mesmas células.

Quero mexer no preço com um controle deslizante, ver o extrato do pedido, o custo e
o lucro do lote, e um gráfico de lucro do lote por preço marcando o degrau de R$ 80.
Mostre uma frase com o resultado e, se der prejuízo, o preço mínimo.
Se a biblioteca não carregar, a página mostra um aviso e nenhum número.

Antes de fazer a tela, teste o motor em Node.js contra a planilha:
- o pedido de R$ 10,90 precisa dar R$ 4,00 de renda (é o meu extrato real);
- o lote a R$ 29,90 precisa dar R$ 3.583,03 de lucro;
- R$ 79,99 precisa render mais que R$ 80,00.
Me mande o engine.js separado, num arquivo, e a saída inteira do teste.
Rode node --check no JavaScript da página antes de publicar.

No fim, liste as limitações: o que acontece quando eu mudar a planilha, o que a
página não salva, em que preço ela abre e o que você não conseguiu testar.
```

Se a sua conta não roda código, peça só o `engine.js` e a página em arquivos, e rode os testes do kit na sua máquina.
