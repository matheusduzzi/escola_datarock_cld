# Estudo de marca forense

Arquivos do exercício dessa aula. O estúdio, as professoras, os números e as legendas são inventados para o curso.

- `site/`: o site do Studio Aurora Pilates. Abra `site/index.html` no navegador para ver como ele fica. As cores e as fontes estão em `site/css/aurora.css`, o estilo do estúdio, e em `site/css/tema-base.css`, o tema do construtor de páginas.
- `instagram.md`: o perfil, as quatro últimas legendas e as avaliações no Google.
- `02-estudo-de-marca.md`: o modelo do estudo, com as nove seções.
- `contar_css.py`: conta as cores e lista as fontes e os pesos dos arquivos CSS.
- `guiada/cafe.css`: o CSS do Café da Praça, da prática guiada.

Salve uma cópia de `02-estudo-de-marca.md` com o mesmo nome e responda nela.

## O contador

Precisa só do Python 3, sem instalar nada. Dentro da pasta dessa aula:

```
python3 contar_css.py site/css/aurora.css site/css/tema-base.css
```

Ele junta maiúscula e minúscula e a forma curta (`#fff` é `#FFFFFF`) e não conta cor escrita só em comentário. Ele conta cada declaração do CSS, não quantas vezes a cor aparece na tela. Sem Python, use a busca do editor em cada arquivo e procure também a forma minúscula e a curta.

Para pedir ajuda, deixe um comentário na aula com o seu objetivo, o comando ou o prompt, o que apareceu e o que já tentou, sem dados pessoais.
