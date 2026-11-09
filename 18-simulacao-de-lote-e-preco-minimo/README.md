# Simulação de lote e preço mínimo

Arquivos da prática e do exercício dessa aula.

- `planilha_simulacao.xlsx`: a planilha do case com as abas Calculadora, Simulação de lote e Taxas. Abre no Excel, no LibreOffice e no Google Planilhas. Ela sai do gerador sem nenhum valor calculado: a planilha calcula ao abrir.
- `gerar_planilha.py`: o gerador desse arquivo, com as mesmas fórmulas da planilha que o Claude fez no case. Rode `python3 gerar_planilha.py` para gerar de novo.
- `conferir_lote.py`: lê a aba Simulação de lote, recalcula com as entradas que você pedir e testa cada custo mexendo numa entrada de cada vez. Diz o menor preço em centavos sem prejuízo e compara a tabela de preços com a Calculadora.
- `conferir_planilha.py`: o conferidor da Calculadora, da aula «A planilha calculadora com fórmulas». O `conferir_lote.py` usa o leitor de fórmulas dele: deixe os dois na mesma pasta.
- `extrato-pedido-gabarito.md`: o extrato do pedido-gabarito (kit de 3 potes a R$ 10,90, renda de R$ 4,00), redesenhado em tabela. É o mesmo das aulas anteriores do módulo.
- `pedido-da-simulacao.md`: o pedido para mandar ao Claude, com as premissas e os testes.
- `minha-simulacao.md`: o modelo do exercício.

## O que você precisa

Python 3.9 ou mais novo, para os scripts. Eles só usam a biblioteca padrão: não precisa instalar nada. Para abrir a planilha, Excel, LibreOffice ou Google Planilhas.

Rode os comandos dentro dessa pasta:

```bash
python3 gerar_planilha.py
python3 conferir_lote.py planilha_simulacao.xlsx
python3 conferir_lote.py planilha_simulacao.xlsx --preco 29.90
python3 conferir_lote.py planilha_simulacao.xlsx --frete 0 --preco 29.90
python3 conferir_planilha.py planilha_simulacao.xlsx
```

As opções `--potes`, `--custo-pote`, `--itens`, `--embalagem`, `--frete` e `--preco` mudam as entradas só na conta do conferidor. O arquivo fica como está. Para testar um número que você já sabe, use `--esperado`, por exemplo `--esperado kits=333 --esperado investimento=2684.03 --esperado minimo_centavos=16.11`.

Se a sua aba de lote tem outras células, diga onde fica cada uma, por exemplo `--celula investimento="Simulação de lote!B17"`. Os nomes estão no começo do `conferir_lote.py`.

Depois de abrir a planilha num programa de planilha e salvar como `.xlsx`, rode o conferidor de novo, sem opções. A última linha antes do resultado passa a comparar o lucro do lote que a planilha gravou com o recálculo.

Salve uma cópia de `minha-simulacao.md` e responda nela.

O case é real e foi anonimizado: não tem loja, conta, CNPJ nem número de pedido. As taxas são as da Shopee Brasil em outubro de 2026. Elas mudam: pesquise a regra do seu marketplace no dia em que fizer a simulação. Os números são exemplo, não promessa de lucro, e todo lucro é antes de imposto e anúncios.

Para pedir ajuda, deixe um comentário na aula com o seu objetivo, o comando que rodou, o que apareceu e o que já tentou, sem dados pessoais.
