# O prompt de extração

Arquivos da prática dessa aula. Você escreve um prompt, roda nos 12 resumos da Loja Aurora com e sem glossário e conta as duplicatas. A Loja Aurora é inventada para o curso: ninguém foi gravado.

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `resumos/reuniao-01.md` a `reuniao-12.md` | Os 12 resumos de reunião de outubro, do jeito que o gravador escreveu, com os erros de nome |
| `contexto-da-loja.md` | O que a dona das gravações sabe da loja: equipe, produtos e empresas de fora |
| `meu-prompt.md` | O modelo do seu prompt, com as quatro marcas que o `montar.py` troca |
| `meu-glossario.md` | Onde você escreve o glossário |
| `minhas-contagens.md` | Onde você anota a validação, a contagem e o que sobrou |
| `montar.py` | Junta o seu prompt, o glossário, os nomes que já existem e as 3 reuniões de um lote num pedido pronto para colar |
| `validar.py` | Diz se a resposta do Claude é JSON no formato pedido, com os ids certos e os limites de cada campo |
| `contar.py` | Conta as duplicatas de cada pasta e mostra lado a lado |
| `cerebro.py` | Funções que os três scripts usam juntos |
| `chave-de-grafias.json` | A régua do `contar.py`: qual pessoa, projeto ou empresa cada grafia é. Não copie nada dela para o glossário |
| `exemplos/` | Três respostas do lote 1 que eu escrevi à mão para mostrar o validador e o contador. Não saíram do Claude |

Os scripts usam só o Python que vem instalado, sem pacote extra.

## Os lotes

| Lote | Reuniões |
|---|---|
| 1 | `reuniao-01`, `reuniao-02`, `reuniao-03` |
| 2 | `reuniao-04`, `reuniao-05`, `reuniao-06` |
| 3 | `reuniao-07`, `reuniao-08`, `reuniao-09` |
| 4 | `reuniao-10`, `reuniao-11`, `reuniao-12` |

## Como rodar sem terminal

Você não precisa instalar nada. Abra uma conversa do Claude com a execução de código ligada. Ela fica em Configurações, Capacidades; a ajuda em inglês chama de "Code execution and file creation". Essa é a conversa de apoio: ela só roda os scripts. A extração acontece em outras conversas.

1. Compacte essa pasta num arquivo .zip e anexe na conversa de apoio. Peça para descompactar e rodar os comandos dentro da pasta, sem mudar nenhum arquivo.
2. Para cada comando, peça: "Rode exatamente este comando e me mostre a saída inteira, sem corrigir nada:" e cole o comando.
3. Para baixar o pedido montado, peça o arquivo `lote-1-pedido.txt` que o comando gravou.
4. Quando voltar com uma resposta, anexe o arquivo e diga onde salvar, por exemplo `sem-glossario/lote-1.json`. Depois peça o próximo comando.

Se a conversa de apoio oferecer corrigir o seu JSON, recuse. Quem corrige é o seu prompt: você pede o lote de novo numa conversa nova.

## Como rodar no terminal

Se você tem Python 3, abra o terminal dentro dessa pasta e rode os mesmos comandos.

## Os comandos

Montar o pedido do lote 1, sem glossário:

```
python3 montar.py --prompt meu-prompt.md --sem-glossario --lote 1 --saidas sem-glossario
```

Com glossário:

```
python3 montar.py --prompt meu-prompt.md --glossario meu-glossario.md --lote 1 --saidas com-glossario
```

Cole o `lote-1-pedido.txt` numa conversa anônima nova do Claude (ícone do fantasma), uma conversa por lote, e salve a resposta inteira, só o JSON, em `sem-glossario/lote-1.json` (ou `com-glossario/lote-1.json`). Depois:

```
python3 validar.py sem-glossario --lote 1
```

Do lote 2 em diante, o `montar.py` só monta o pedido se os lotes anteriores da mesma pasta passarem no `validar.py`. É ele que põe no pedido os nomes que os lotes anteriores já usaram.

Com os quatro lotes das duas pastas:

```
python3 validar.py sem-glossario
python3 validar.py com-glossario
python3 contar.py sem-glossario com-glossario
```

Para ver os scripts nos exemplos:

```
python3 validar.py exemplos/recusado --lote 1
python3 contar.py exemplos/sem-glossario exemplos/com-glossario --lote 1
```

O primeiro comando sai com erro de propósito: é a prática guiada da aula.

## Para pedir ajuda

Deixe um comentário na aula com o seu objetivo, o comando, a saída e o que você já tentou, sem dados pessoais.
