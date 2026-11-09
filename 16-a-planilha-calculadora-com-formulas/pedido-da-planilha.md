# O pedido da planilha

Copie, troque o que está entre colchetes e mande ao Claude numa conversa com a criação de arquivos ligada. Se você usa o kit de potes do case, cole a tabela de `regra-conciliada.md` no lugar da regra.

```text
Gere uma planilha Excel (.xlsx) com fórmulas, não valores fixos.

Entradas: quantidade de itens no kit e preço do kit.
Resultado: renda do pedido, o que sobra depois das taxas.

Regras: [cole a tabela de faixas com "preço a partir de", percentual e
taxa fixa, e as regras extras, como a metade do preço abaixo de R$ 8
e a recarga de 2%].

Como montar:
- todas as regras numa aba chamada Taxas, uma por célula, para eu editar;
- na aba Calculadora, a faixa achada com INDEX e MATCH tipo 1 sobre a
  coluna "preço a partir de", em ordem crescente, sem IF aninhado;
- cada linha de taxa arredondada em 2 casas com ROUND, antes de somar;
- as taxas como valores negativos e a renda como preço + taxas.

Antes de me mandar:
- recalcule o arquivo e leia os valores calculados, não as fórmulas;
- teste com o pedido de [R$ 10,90], que precisa dar [R$ 4,00] de renda;
- teste [R$ 79,99] e [R$ 80,00], dos dois lados de um limite de faixa;
- me mostre cada linha de taxa desses três preços e a fórmula de cada célula.
```

Quando o arquivo chegar, não use antes de passar pelo `conferir_planilha.py`.
