# Sincronização em lotes que diz por que parou

Arquivos da prática dessa aula. Você desenha a sincronização do seu cérebro, escreve a tabela de erros e lê o que a página da Loja Aurora gravou em três paradas para dizer por que cada uma parou. A Loja Aurora é inventada para o curso: ninguém foi gravado.

Não tem script para rodar. Os arquivos `.json` e `.txt` abrem em qualquer editor de texto, e também dá para anexar numa conversa do Claude e pedir para mostrar o conteúdo sem mudar nada.

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `lista-do-gravador.json` | As 12 gravações de outubro que o gravador da Renata lista, da mais recente para a mais antiga, e a data de início do horizonte (`desde`) |
| `paradas/exemplo/` | A parada da prática guiada |
| `paradas/parada-1/` a `paradas/parada-3/` | As três paradas do exercício |
| `situacoes.md` | Dez situações para a sua tabela de erros |
| `minha-sincronizacao.md` | Onde você desenha a sincronização |
| `minha-tabela-de-erros.md` | Onde você escreve a tabela de erros |
| `meu-diagnostico.md` | Onde você escreve o diagnóstico das três paradas |
| `codigo-do-case.md` | Os trechos do código do case sobre listagem, lotes e erros, copiados do documento do case, para ler |

## O que tem em cada parada

| Arquivo | O que é |
|---|---|
| `tela.txt` | O que a Renata viu na tela quando a página parou, e o texto do botão |
| `banco.json` | As reuniões que estão no banco da página depois da parada: `status` (`ok` ou `erro`), a hora em que foi gravada (`processedAt`) e, quando deu erro, a etapa e o código |
| `config-sync.json` | O motivo que a página gravou: resultado, etapa, código, mensagem, texto original do erro (`detalhe`), lidas, total, pendentes e a hora |

A parada 3 é da primeira versão da página, que não gravava o motivo. Por isso ela não tem `config-sync.json`.

As horas estão no horário da Renata. Eu escrevi esses registros no formato do case. O texto original de cada erro é um exemplo meu, menos o "sampling too often", que é o do case.

## Para pedir ajuda

Deixe um comentário na aula com o seu objetivo, o arquivo que você leu, o que você concluiu e o que já tentou, sem dados pessoais.
