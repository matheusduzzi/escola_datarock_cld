# Design system a partir do estudo

Arquivos do exercício dessa aula. O estúdio, as professoras, os números e as legendas são inventados para o curso.

- `site/`: o mesmo site do Studio Aurora Pilates da aula «Estudo de marca forense». Abra `site/index.html` no navegador. As cores e as fontes estão em `site/css/aurora.css` e em `site/css/tema-base.css`, o tema do construtor de páginas.
- `instagram.md`: o perfil e as quatro últimas legendas, para a prancha de voz.
- `03-design-system.md`: o modelo do design system, com as seis pranchas e a tabela de contraste.
- `contraste.py`: mede o contraste entre a cor do texto e a do fundo.
- `pares-aurora.txt`: o arquivo onde você escreve os pares do estúdio, um por linha.
- `guiada/pares-cafe.txt`: os pares do Café da Praça, da prática guiada.

Você também vai usar o seu `02-estudo-de-marca.md`, da aula anterior.

## O medidor de contraste

Precisa só do Python 3, sem instalar nada. Dentro da pasta dessa aula:

```
python3 contraste.py "#FFFFFF" "#E07A5F"
python3 contraste.py --arquivo guiada/pares-cafe.txt
python3 contraste.py --arquivo pares-aurora.txt
```

Cada par é a cor do texto e depois a do fundo. A razão sai com duas casas, cortada: 4,499 aparece como 4,49 e não passa. Texto normal precisa de 4,5:1, texto grande precisa de 3:1. Se uma cor estiver escrita errado, nada é medido e o programa diz em que linha está o erro.

Sem Python, use um verificador de contraste na web e anote a razão que ele mostrar, sem arredondar para cima.

Para pedir ajuda, deixe um comentário na aula com o seu objetivo, o comando ou o prompt, o que apareceu e o que já tentou, sem dados pessoais.
