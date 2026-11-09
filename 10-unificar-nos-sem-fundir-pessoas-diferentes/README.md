# Unificar nós sem fundir pessoas diferentes

Arquivos da prática dessa aula. Você monta o resolvedor de nomes da Loja Aurora em camadas, mede contra o gabarito da Renata e marca os pares que nunca podem ficar juntos. A Loja Aurora é inventada para o curso: ninguém foi gravado.

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `nomes-do-grafo.json` | Os nomes que a extração deixou nas 12 reuniões de outubro, do jeito que foram escritos. Não mude esse arquivo |
| `gabarito.json` | O gabarito da Renata: quais nomes são a mesma pessoa, projeto, empresa ou tema |
| `minha-config.json` | A sua configuração: siglas extras, uniões manuais e pares de "não unir" |
| `resolver.py` | Mostra os nós, as uniões que o "não unir" recusou e as sugestões de pares parecidos |
| `medir.py` | Mede o resultado contra o gabarito, camada por camada |
| `resolvedor.py` | As funções que os dois scripts usam: normalização, chave fonética, siglas, uniões e Jaro-Winkler |
| `codigo-do-case.md` | Os trechos do código do case, em JavaScript, para ler ao lado do `resolvedor.py` |
| `minhas-medidas.md` | Onde você anota as medidas e as decisões |
| `exemplos/` | Duas configurações da prática guiada |

Os scripts usam só o Python que vem instalado, sem pacote extra.

## A configuração

`minha-config.json` tem quatro chaves:

- `auto`: `true` liga a chave fonética e as siglas. A normalização vale sempre.
- `siglas`: pares `["expressão", "sigla"]` além das que o case já traz e das que o resolvedor aprende sozinho.
- `pares`: uniões manuais, cada uma com dois nomes.
- `nao_unir`: pares que nunca ficam no mesmo nó, nem por regra automática nem por união manual.

Cada nome vai no formato `"tipo:Nome"`, com o tipo `pessoa`, `projeto`, `empresa` ou `tema`. Exemplo de par: `["pessoa:Juju", "pessoa:Juliana Prado"]`. O nome precisa existir em `nomes-do-grafo.json`. Acento e maiúscula não importam.

## Como rodar sem terminal

Você não precisa instalar nada. Abra uma conversa do Claude com a execução de código ligada. Ela fica em Configurações, Capacidades; a ajuda em inglês chama de "Code execution and file creation".

1. Compacte essa pasta num arquivo .zip e anexe na conversa. Peça para descompactar e rodar os comandos dentro da pasta.
2. Para cada comando, peça: "Rode exatamente este comando e me mostre a saída inteira, sem corrigir nada:" e cole o comando.
3. Quando mudar a configuração, mude você mesmo o `minha-config.json` e anexe de novo, ou peça para trocar o arquivo pelo texto que você colar.

Se a conversa oferecer montar a configuração por você, recuse. Quem decide se dois nomes são a mesma pessoa é você.

## Como rodar no terminal

Se você tem Python 3, abra o terminal dentro dessa pasta e rode os mesmos comandos.

## Os comandos

Medir a sua configuração contra o gabarito:

```
python3 medir.py
```

Ver os nós de pessoas e as sugestões:

```
python3 resolver.py --tipo pessoa
```

Parar numa camada, por exemplo antes das siglas:

```
python3 resolver.py --ate fonetica
```

As camadas são `normalizacao`, `fonetica`, `siglas`, `manual` e `nao_unir`.

Os exemplos da prática guiada:

```
python3 medir.py --config exemplos/sem-fonetica.json
python3 medir.py --config exemplos/so-nao-unir.json
```

Se a configuração tiver um erro, o script diz qual é, sai com erro e não mede nada.

## Para pedir ajuda

Deixe um comentário na aula com o seu objetivo, o comando, a saída e o que você já tentou, sem dados pessoais.
