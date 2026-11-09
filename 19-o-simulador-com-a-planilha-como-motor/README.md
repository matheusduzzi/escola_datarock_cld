# O simulador com a planilha como motor

Arquivos da prática e do exercício dessa aula.

- `engine.js`: o motor do simulador do case. Uma função, `buildEngine`, que cria na HyperFormula as abas Calculadora, Simulação de lote, Taxas e Curva e grava nelas as mesmas fórmulas da planilha.
- `test.js`: o teste do case. Imprime os valores do motor para você comparar com a planilha.
- `casos.json`: os casos que o motor precisa acertar, com o valor esperado de cada um: o pedido-gabarito de R$ 10,90, o lote a R$ 29,90, a tabela de seis preços e o degrau de R$ 80.
- `testar_motor.js`: roda o motor com a HyperFormula de verdade e compara cada caso de `casos.json` ao centavo. Também compara a curva do gráfico com a Calculadora.
- `conferir_motor.py`: compara o motor com a planilha, célula por célula, e calcula os casos com as fórmulas dos dois. Aceita o `engine.js` ou a página `.html` do simulador.
- `motor_reescrito.js`: o motor do case com uma linha reescrita à mão, para a pergunta 3 da prática.
- `planilha_simulacao.xlsx` e `gerar_planilha.py`: a planilha da aula «Simulação de lote e preço mínimo» e o gerador dela.
- `conferir_planilha.py`: o leitor de fórmulas da aula «A planilha calculadora com fórmulas». O `conferir_motor.py` faz a conta com ele: deixe os dois na mesma pasta.
- `extrato-pedido-gabarito.md`: o extrato do pedido-gabarito (kit de 3 potes a R$ 10,90, renda de R$ 4,00), redesenhado em tabela. É o mesmo das aulas anteriores do módulo.
- `pedido-do-simulador.md`: o pedido para mandar ao Claude, com o teste e as limitações.
- `meu-simulador.md`: o modelo do exercício.

## O que você precisa

Python 3.9 ou mais novo, para os scripts `.py`. Eles só usam a biblioteca padrão. Node.js 18 ou mais novo, para os arquivos `.js`: o `conferir_motor.py` também usa o Node.js para ler o motor.

Rode os comandos dentro dessa pasta:

```bash
python3 conferir_motor.py
python3 conferir_motor.py --motor motor_reescrito.js
python3 conferir_motor.py --motor simulador.html --planilha minha_planilha.xlsx --casos meus_casos.json
```

O `conferir_motor.py` não usa a HyperFormula. Para rodar o motor com ela, instale a biblioteca nessa pasta, uma vez, e rode o teste:

```bash
npm init -y
npm install hyperformula@2.7.1
node testar_motor.js
node test.js
node testar_motor.js meu_engine.js meus_casos.json
```

Os dois scripts saem com código 0 quando tudo bate e 1 quando algum teste falhou. Não publique com código 1.

A HyperFormula usa a licença GPL v3. O `engine.js` liga a biblioteca com a chave `gpl-v3`. Para um produto fechado que você vende, leia os termos da licença antes.

Salve uma cópia de `meu-simulador.md` e responda nela.

O case é real e foi anonimizado: não tem loja, conta, CNPJ nem número de pedido. As taxas são as da Shopee Brasil em outubro de 2026. Elas mudam: pesquise a regra do seu marketplace no dia em que fizer o simulador. Os números são exemplo, não promessa de lucro, e todo lucro é antes de imposto e anúncios.

Para pedir ajuda, deixe um comentário na aula. Conte o seu objetivo, o comando que rodou, o que apareceu e o que já tentou, sem dados pessoais.
