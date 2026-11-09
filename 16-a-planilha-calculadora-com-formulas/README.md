# A planilha calculadora com fórmulas

Arquivos da prática e do exercício dessa aula.

- `planilha_calculadora.xlsx`: a calculadora do case, com as abas Calculadora e Taxas. Abre no Excel, no LibreOffice e no Google Planilhas. Ela sai do gerador sem nenhum valor calculado: a planilha calcula ao abrir.
- `gerar_planilha.py`: o gerador desse arquivo, com as mesmas fórmulas da planilha que o Claude fez no case. Rode `python3 gerar_planilha.py` para gerar de novo.
- `conferir_planilha.py`: lê as fórmulas de um `.xlsx`, recalcula a renda nos preços que você pedir e diz se as regras estão numa aba própria, se a faixa sai de MATCH e se cada linha passa por ROUND.
- `regra-conciliada.md`: a regra de taxas que o pedido-gabarito confirmou, do jeito que vai para a aba Taxas.
- `extrato-pedido-gabarito.md`: o extrato do pedido-gabarito (kit de 3 potes a R$ 10,90, renda de R$ 4,00), redesenhado em tabela. É o mesmo das aulas anteriores do módulo.
- `pedido-da-planilha.md`: o pedido para mandar ao Claude, com os testes que ele precisa fazer antes de entregar.
- `minha-planilha.md`: o modelo do exercício.

## O que você precisa

Python 3.9 ou mais novo, para os dois scripts. Eles só usam a biblioteca padrão: não precisa instalar nada. Para abrir a planilha, Excel, LibreOffice ou Google Planilhas.

Rode os comandos dentro dessa pasta:

```bash
python3 gerar_planilha.py
python3 conferir_planilha.py planilha_calculadora.xlsx
python3 conferir_planilha.py planilha_calculadora.xlsx --teste 10.90=4.00 --teste 79.99=57.89 --teste 80=51.20
```

Para a sua planilha, diga onde ficam o preço, a renda e as regras:

```bash
python3 conferir_planilha.py minha.xlsx --preco Calculadora!B6 --renda Calculadora!B17 --regras Taxas --teste 10.90=4.00
```

O conferidor lê as funções mais comuns de planilha (SUM, ROUND, IF, INDEX, MATCH, VLOOKUP, XLOOKUP, MIN, MAX, INT, ABS, IFERROR). Se a sua planilha usa outra, ele avisa qual. Aí você confere no Excel, trocando o preço à mão.

Salve uma cópia de `minha-planilha.md` e responda nela.

O case é real e foi anonimizado: não tem loja, conta, CNPJ nem número de pedido. As taxas são as da Shopee Brasil em outubro de 2026. Elas mudam: pesquise a regra do seu marketplace no dia em que fizer a planilha. A renda do pedido é antes do custo do produto, da embalagem, do imposto e dos anúncios.

Para pedir ajuda, deixe um comentário na aula com o seu objetivo, o comando que rodou, o que apareceu e o que já tentou, sem dados pessoais.
