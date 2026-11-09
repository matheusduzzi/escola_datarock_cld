# Agenda e auditoria com dados reais

Arquivos da prática dessa aula. Você liga as 12 gravações de outubro da Renata aos eventos da agenda, corrige os nomes falados pelo nome do convite, reunião por reunião, e audita o resultado antes de gravar. A Loja Aurora é inventada para o curso: ninguém foi gravado, e os e-mails terminam em `.example`, que não existe.

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `gravacoes.json` | As 12 gravações: título, início, duração e os nomes de pessoas que a extração deixou, do jeito que foram escritos. Não mude esse arquivo |
| `agenda-outubro.json` | A agenda de outubro da Renata, no formato compacto do case. Não mude esse arquivo |
| `resumos/` | Os resumos das 12 reuniões, para você ler quando a auditoria pedir uma decisão |
| `banco/nao-unir.json` | O par de "não unir" da aula anterior, guardado no banco. A auditoria lê e nunca grava por cima |
| `regra-antiga.json` | A regra que a página usava antes da auditoria. É o "antes" da tabela. Não mude esse arquivo |
| `minha-regra.json` | A sua regra. Começa igual à antiga |
| `auditar.py` | Liga, corrige, mostra os achados, a lista para confirmação e a tabela antes e depois. Com `--gravar`, grava em `gravado/` se nada estragar o grafo |
| `ligador.py` | As funções que o `auditar.py` usa: ligação pelo horário e pelas pessoas, correção de nomes e os achados |
| `codigo-do-case.md` | Os trechos do código do case, em JavaScript, para ler ao lado do `ligador.py` |
| `respostas-da-renata.md` | O que a Renata respondeu sobre a lista para confirmação. Abra só depois de montar a sua lista |
| `minhas-anotacoes.md` | Onde você anota as tabelas e as decisões |
| `exemplos/por-reuniao.json` | A regra da prática guiada |

Os scripts usam só o Python que vem instalado, sem pacote extra.

## A regra

`minha-regra.json` tem quatro chaves:

- `casamento`: `"horario"` liga a gravação ao evento só pelo horário, como a regra antiga. `"horario_e_pessoas"` usa também quem foi citado e está no convite.
- `correcao`: `"global"` corrige um nome falado no grafo inteiro, pela primeira reunião em que ele bateu com um convidado. `"por_reuniao"` corrige cada nome só com o convite da própria reunião.
- `emails_confirmados`: e-mails de convite que a Renata disse de quem são, no formato `{"e-mail": "Nome"}`.
- `nomes_confirmados`: nomes que a Renata decidiu, um por reunião, no formato `["reuniao-NN", "nome falado", "nome do convidado"]`. Para deixar um nome sem correção, use `null` no lugar do convidado.

O nome falado precisa estar na lista de pessoas da reunião em `gravacoes.json`. Acento e maiúscula não importam.

## Como rodar sem terminal

Você não precisa instalar nada. Abra uma conversa do Claude com a execução de código ligada. Ela fica em Configurações, Capacidades; a ajuda em inglês chama de "Code execution and file creation".

1. Compacte essa pasta num arquivo .zip e anexe na conversa. Peça para descompactar e rodar os comandos dentro da pasta.
2. Para cada comando, peça: "Rode exatamente este comando e me mostre a saída inteira, sem corrigir nada:" e cole o comando.
3. Quando mudar a regra, mude você mesmo o `minha-regra.json` e anexe de novo, ou peça para trocar o arquivo pelo texto que você colar.

Se a conversa oferecer decidir quem é quem por você, recuse. Quem decide é a Renata, e você monta a pergunta.

## Como rodar no terminal

Se você tem Python 3, abra o terminal dentro dessa pasta e rode os mesmos comandos.

## Os comandos

Auditar a sua regra, sem gravar nada:

```
python3 auditar.py
```

Ver só uma reunião nas listas:

```
python3 auditar.py --reuniao reuniao-08
```

Auditar outra regra, por exemplo a antiga ou a da prática guiada:

```
python3 auditar.py --regra regra-antiga.json
python3 auditar.py --regra exemplos/por-reuniao.json
```

Gravar, se a auditoria passar:

```
python3 auditar.py --gravar
```

Se a regra tiver um erro, o script diz qual é, sai com erro e não audita nada. Se a auditoria achar uma correção para quem não estava no convite, escolhida entre dois convidados ou contra um "não unir", o `--gravar` diz quais são, sai com erro e não grava nada.

O que o kit não tem: gravação longa que cobre duas reuniões, evento sem convidados e ligação manual de gravação a evento. O case tinha os três, e o `codigo-do-case.md` mostra as regras.

## Para pedir ajuda

Deixe um comentário na aula com o seu objetivo, o comando, a saída e o que você já tentou, sem dados pessoais.
