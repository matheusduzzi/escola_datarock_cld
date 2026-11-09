# Minha planilha calculadora

Salve uma cópia e preencha. Não escreva número de pedido, nome da loja, CNPJ nem dado de comprador.

## Parte 1: a minha planilha

Marketplace, tipo de conta e produto: 
Nome do arquivo .xlsx: 
Como foi feita (pedido ao Claude, com a data, ou montada à mão e "não testado na plataforma"): 

O pedido que eu mandei (cole aqui):

```text

```

### A estrutura

| Pergunta | Minha resposta |
|---|---|
| Nome da aba de regras e o que tem nela | |
| Célula do preço e célula da renda | |
| Fórmula da célula que acha a faixa | |
| Fórmula de cada linha de taxa | |
| Algum número de regra escrito dentro de uma fórmula? Onde? | |

### Os testes

| Teste | Preço | Renda esperada | Renda na planilha | Bateu? |
|---|---|---|---|---|
| Pedido-gabarito | | | | |
| Logo antes de um limite de faixa | | | | |
| No limite de faixa | | | | |

O comando que eu rodei e a saída do `conferir_planilha.py` depois de abrir e salvar a planilha:

```text

```

O que o Claude disse que tinha testado, e o que eu achei diferente:

## Parte 2: mexer na aba Taxas

Use o `planilha_calculadora.xlsx` do kit. Depois de cada mudança, salve e rode o `conferir_planilha.py`.

| Mudança | Preço | Renda que apareceu | O que o conferidor disse |
|---|---|---|---|
| 1. Recarga de 0% | R$ 10,90 | | |
| 2. Recarga de volta a 2% e taxa fixa da primeira faixa em R$ 4,00 | R$ 10,90 | | |
| 3a. Taxa fixa de volta a R$ 4,50 e faixa de teste na linha 8, sem mexer nas fórmulas | R$ 350,00 | | |
| 3b. Depois de ajustar as fórmulas | R$ 350,00 | | |

Na mudança 1, de onde eu já conhecia esse número:

Na mudança 2, por que o teste do gabarito falhar é bom sinal:

Na mudança 3, quais células eu ajustei e o que mudou em cada uma:
