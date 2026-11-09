# Começar completo e cortar

Arquivos da prática e do exercício dessa aula.

- `versao_1.xlsx` a `versao_4.xlsx`: as quatro versões da planilha calculadora do case, da primeira, com seis entradas, à final, com duas. A versão 4 é a planilha da aula «A planilha calculadora com fórmulas». O case guarda os campos de cada versão, não os arquivos: as versões 1 a 3 foram remontadas a partir da final, com os campos que o case lista. Elas saem do gerador sem nenhum valor calculado: a planilha calcula ao abrir.
- `gerar_versoes.py`: o gerador das quatro versões. Rode `python3 gerar_versoes.py` para gerar de novo.
- `gerar_planilha.py`: o gerador da planilha final, o mesmo da aula anterior. O `gerar_versoes.py` usa esse arquivo.
- `comparar_versoes.py`: compara as versões em ordem. Mostra o que saiu e o que entrou em cada passo, testa o pedido-gabarito em cada versão, testa se a renda ficou igual em 13 preços, dos dois lados de cada limite de faixa, e aponta regra que nenhuma fórmula lê.
- `conferir_planilha.py`: o conferidor da aula anterior, para testar a versão final depois de abrir e salvar.
- `versao_3_recebida.xlsx`: o arquivo da Parte 2 do exercício.
- `extrato-pedido-gabarito.md`: o extrato do pedido-gabarito (kit de 3 potes a R$ 10,90, renda de R$ 4,00), redesenhado em tabela. É o mesmo das aulas anteriores do módulo.
- `pedidos-de-corte.md`: os pedidos do case e os modelos para a primeira versão e para cada corte.
- `minhas-versoes.md`: o modelo do exercício.

## O que você precisa

Python 3.9 ou mais novo, para os scripts. Eles só usam a biblioteca padrão: não precisa instalar nada. Para abrir as planilhas, Excel, LibreOffice ou Google Planilhas.

Rode os comandos dentro dessa pasta:

```bash
python3 gerar_versoes.py
python3 comparar_versoes.py versao_1.xlsx versao_2.xlsx versao_3.xlsx versao_4.xlsx
python3 conferir_planilha.py versao_4.xlsx
```

O comparador acha o preço e a renda pelo rótulo da coluna A: a entrada com "valor cobrado" ou "preço" e a conta com "renda do pedido". Se os rótulos das suas versões forem outros, diga quais:

```bash
python3 comparar_versoes.py v1.xlsx v2.xlsx v3.xlsx v4.xlsx --teste 10.90=4.00 --rotulo-preco "preço de venda" --rotulo-renda "renda líquida" --regras Taxas
```

Os 13 preços que ele usa para ver se a renda ficou igual estão em volta dos limites de faixa do case (R$ 8, 80, 100 e 200). Se a sua regra tem outros limites, passe um preço de cada lado de cada um, separados por vírgula e com ponto:

```bash
python3 comparar_versoes.py v1.xlsx v2.xlsx v3.xlsx v4.xlsx --teste 10.90=4.00 --precos 9.99,10,49.99,50,99.99,100
```

Os dois scripts leem as funções mais comuns de planilha (SUM, ROUND, IF, INDEX, MATCH, VLOOKUP, XLOOKUP, MIN, MAX, INT, ABS, IFERROR). Se a sua planilha usa outra, eles avisam qual. Aí você compara no Excel, trocando o preço à mão.

Salve uma cópia de `minhas-versoes.md` e responda nela.

O case é real e foi anonimizado: não tem loja, conta, CNPJ nem número de pedido. As taxas são as da Shopee Brasil em outubro de 2026. Elas mudam: pesquise a regra do seu marketplace no dia em que fizer a planilha. A renda do pedido é antes do custo do produto, da embalagem, do imposto e dos anúncios.

Para pedir ajuda, deixe um comentário na aula com o seu objetivo, o comando que rodou, o que apareceu e o que já tentou, sem dados pessoais.
