# Os 14 pedidos do case

O projeto inteiro aconteceu numa única conversa. Cada linha traz o pedido do vendedor, resumido como no documento do projeto, e o que voltou do Claude. Use com o modelo `linha-do-tempo.md`.

| # | Pedido do vendedor | O que voltou |
|---|---|---|
| 1 | "Detalhe o que é taxa de comissão líquida, taxa de transação, taxa por item vendido e taxa de recarga automática (pedido) na Shopee" | Explicação das quatro linhas do extrato, com a tabela de faixas de comissão de outubro de 2026 (20% e R$ 4,50 fixos até R$ 79,99). O Claude pesquisou na web antes de responder. |
| 2 | "Um kit de 3 itens por R$ 10,90, quanto fica o líquido?" | Conta na conversa: R$ 4,22 de líquido (20% de comissão e R$ 4,50 fixos). |
| 3 | "E um kit de 6 itens por R$ 39,90?" | Conta na conversa: R$ 27,42 de líquido. As taxas levam 61% do preço no kit de 3 e 31% no kit de 6. |
| 4 | Mandou o print do extrato real do pedido de 3 potes: "corrija" | Conciliação linha a linha com o extrato. A renda real é R$ 4,00: faltava a recarga de 2% (R$ 0,22). A definição de "comissão líquida" foi corrigida. O kit de 6 refeito dá R$ 26,62. |
| 5 | "Gere uma planilha onde coloco a quantidade de itens e o valor do kit e ela calcula o que sobra" | Arquivo Excel com as abas Calculadora e Taxas. Campos de entrada: itens no kit, preço, % da recarga, vendedor CPF com mais de 450 pedidos (Sim ou Não), custo por item e imposto. Testado com o extrato: R$ 4,00. |
| 6 | "O vendedor é CNPJ" | Explicação: o adicional de R$ 3,00 por item, que vale para CPF com mais de 450 pedidos em 90 dias, não se aplica. |
| 7 | "Remove [o campo de CPF], tira o custo por item e imposto também" | Planilha nova. Campos de entrada: itens no kit, preço e % da recarga. |
| 8 | "Taxa de recarga automática: mantenha o valor calculado e não deixe como campo" | Planilha nova. Os 2% vão para a aba Taxas e a recarga vira linha calculada. Campos de entrada: itens no kit e preço. |
| 9 | "Coloque como resultado só a renda do pedido" | Planilha nova, com um resultado só: a renda do pedido. |
| 10 | "Como fica a taxa se passar de 79 reais?" | Tabela das faixas. A R$ 79,99, a renda é R$ 57,89. A R$ 80,00, cai para R$ 51,20, porque a taxa fixa sobe de R$ 4,50 para R$ 16,00. Conselho: evitar preços de R$ 80,00 até perto de R$ 88,00, onde a renda volta a passar a de R$ 79,99. |
| 11 | "Simule: 1.000 potes a R$ 0,97, kits de 3, embalagem de R$ 5. Quanto posso cobrar e qual o lucro?" | Tabela de seis preços, preço mínimo e faixa recomendada. A R$ 29,90, o lucro do lote fica em cerca de R$ 3.633, antes de imposto e de anúncios. |
| 12 | "Esqueci, coloque o frete de R$ 50 para entregar os 1.000 potes" | Tudo refeito com o frete: investimento de R$ 2.684,03, custo por kit de R$ 8,06 e preço mínimo de R$ 16,10. A R$ 29,90, o lucro do lote fica em R$ 3.583,03, antes de imposto e de anúncios. |
| 13 | "Consigo colocar isso na planilha também?" | Aba nova na mesma planilha: Simulação de lote. |
| 14 | "Crie um artefato de simulação. Leve a planilha para ser o mecanismo por trás" | Página interativa publicada como artefato, que roda as fórmulas da planilha (HyperFormula) e desenha o gráfico (Chart.js). O motor foi testado contra a planilha antes da tela. |
