# Pedidos para começar completo e cortar

Copie, troque o que está entre colchetes e mande ao Claude numa conversa com a criação de arquivos ligada.

## Os pedidos do case

Os pedidos 5 a 9 da conversa do vendedor, com as palavras dele:

| Pedido | O que o vendedor escreveu |
|---|---|
| 5 | "Gere uma planilha onde eu coloco a quantidade de itens que vai no kit, o valor que estou cobrando pelo kit e ela calcula, com base nas taxas, o valor total que vai sobrar." |
| 6 | "O vendedor é CNPJ" |
| 7 | "Remove [o campo de CPF], tira o custo por item e imposto também" |
| 8 | "Taxa de recarga automática: mantenha o valor calculado e não deixe como campo" |
| 9 | "Coloque como resultado só a renda do pedido" |

## Pedido da versão 1, completa

```text
Gere uma planilha Excel (.xlsx) com fórmulas, não valores fixos, para
calcular a renda de um pedido no [marketplace], vendendo [produto].

Regras: [cole a regra conciliada com o seu extrato].

Nessa primeira versão, ponha todos os campos que podem importar para
essa conta, mesmo os que eu talvez não use: entradas, regras e resultados.
Eu vou cortar depois. Ao lado de cada campo, escreva para que ele serve.

Como montar:
- as regras numa aba chamada Taxas, uma por célula;
- a faixa achada com INDEX e MATCH tipo 1;
- cada linha de taxa arredondada em 2 casas com ROUND;
- rótulos na coluna A: "Valor cobrado pelo kit" no preço e
  "Renda do pedido" na renda.

Antes de me mandar, recalcule o arquivo e teste o pedido de [R$ 10,90],
que precisa dar [R$ 4,00] de renda. Salve como versao_1.xlsx.
```

## Pedido de cada corte

```text
Na planilha que você me mandou, tire o campo [nome do campo].
Motivo: [por que eu não uso].
Destino: [some / vira regra na aba Taxas / vai para outra aba].
Não mexa em mais nada. A renda do pedido precisa continuar igual
em todos os preços, e o pedido de [R$ 10,90] precisa dar [R$ 4,00].
Mande o arquivo com outro nome: versao_[N].xlsx.
Antes de mandar, diga o que mudou entre a versão anterior e a nova,
célula por célula.
```

Quando o arquivo chegar, rode o `comparar_versoes.py` com a versão anterior e a nova antes do próximo corte.
