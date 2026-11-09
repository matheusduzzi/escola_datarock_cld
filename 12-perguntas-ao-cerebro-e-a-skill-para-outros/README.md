# Perguntas ao cérebro e a skill para outros projetos

Arquivos da prática dessa aula. Você faz perguntas ao cérebro da Renata, compara a busca que conta palavras com a busca que olha pessoa, projeto, empresa, recência e agenda, responde citando as reuniões e escreve a skill que ensina outro projeto a consultar o cérebro. A Loja Aurora é inventada para o curso: ninguém foi gravado, e os e-mails terminam em `.example`, que não existe.

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `cerebro/meetings/` | As 12 reuniões de outubro, uma por arquivo, no formato do banco do case. Os nomes estão do jeito que a transcrição escreveu |
| `cerebro/cal/` | A agenda de outubro e a de novembro, no formato compacto do case |
| `cerebro/config/` | As correções que as aulas anteriores gravaram: nomes por reunião, e-mail confirmado, uniões e "não unir", ligação de cada gravação a um evento |
| `perguntar.py` | Escolhe as reuniões que vão para o Claude responder uma pergunta, pelo modo antigo ou pelo modo do case. Não chama modelo nenhum |
| `codigo-do-case.md` | O código da busca e a skill do case, para ler ao lado do `perguntar.py` |
| `minhas-respostas.md` | Onde você anota as buscas e escreve as respostas |
| `cerebro-aurora/SKILL.md` | O modelo da sua skill, para preencher |
| `conferir_skill.py` | Olha se a sua skill está no formato que o Claude aceita no upload |

Os scripts usam só o Python que vem instalado, sem pacote extra. Não mude os arquivos de `cerebro/`: o `perguntar.py` lê daí.

## Os comandos

Perguntar com a busca do case (o padrão):

```
python3 perguntar.py "O que ficou pendente com a Rápido Sul?"
```

Perguntar com a busca antiga, que conta palavras:

```
python3 perguntar.py "O que ficou pendente com a Rápido Sul?" --modo palavras
```

Ver o texto inteiro que iria para o Claude, com as reuniões escolhidas e as instruções:

```
python3 perguntar.py "O que ficou pendente com a Rápido Sul?" --prompt
```

O script considera que hoje é segunda, 2 de novembro de 2026, às 8:00. Para mudar, use `--hoje 2026-11-04T10:00`.

A saída mostra quem a pergunta cita, as palavras com peso, o evento da agenda quando a pergunta é sobre a próxima reunião, o ranking com os pontos de cada reunião e a lista do que vai para o contexto. A busca do case leva até 4 reuniões; com agenda, até 3 gravações ligadas ao evento e mais 2 da busca. A busca antiga leva as 4 com mais palavras; no empate, a mais antiga primeiro, na ordem do banco.

Conferir o formato da skill:

```
python3 conferir_skill.py
```

Com o modelo do jeito que vem, ele aponta o que falta e sai com erro. Quando a skill estiver preenchida, ele diz "formato ok". Formato certo não quer dizer regra certa: quem testa as regras são as perguntas.

## Como rodar sem terminal

Abra uma conversa do Claude com a execução de código ligada. Ela fica em Configurações, Capacidades; a ajuda em inglês chama de "Code execution and file creation".

1. Compacte essa pasta num arquivo .zip e anexe na conversa. Peça para descompactar e rodar os comandos dentro da pasta.
2. Para cada comando, peça: "Rode exatamente este comando e me mostre a saída inteira, sem corrigir nada:" e cole o comando.
3. Para responder a pergunta, copie o texto que o `--prompt` mostra (da linha "texto para o Claude" até o fim) e cole numa conversa nova, sem o zip.

## Para usar a skill

No app do Claude, a skill sobe como um .zip da pasta `cerebro-aurora`, em Personalizar, Skills; a execução de código precisa estar ligada. No Claude Code, a pasta vai para `~/.claude/skills/` (vale em todos os projetos da máquina) ou para `.claude/skills/` do projeto. Plano e menus mudam: veja na ajuda do Claude na data em que for usar.

## Para pedir ajuda

Deixe um comentário na aula com o seu objetivo, o comando, a saída e o que você já tentou, sem dados pessoais.
