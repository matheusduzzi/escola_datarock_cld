# Lista de auditorias da skill do case

A skill do case mede esta lista no vídeo final. Os nomes dos itens são do case. A régua é a que o case escreveu; onde ele só anotou um número, a linha diz isso. A coluna "Onde dá para medir" é para o seu roteiro, que ainda não virou vídeo.

| Item | O que se mede | Régua no case | Onde dá para medir |
|---|---|---|---|
| Quadro 0 | O primeiro quadro tem a promessa legível e algo já em movimento | Sem número: está ou não está | No roteiro (cena 1) e nos styleframes |
| Leitura sem som | Cada mensagem tem uma imagem que funciona sem a trilha | Sem número | No roteiro e no animatic |
| Fio condutor | O elemento visual está em todas as cenas | Sem número | No roteiro |
| Atos e marcos | Re-ganchos a cada uns 7,5 s, duas interrupções perto de 1/3 e de 2/3, clímax por volta de 75% | As batidas da grade de 64 | No roteiro |
| Loop | Diferença média entre o último e o primeiro quadro, de 0 a 255 | Sem limite escrito. Reel 1: 1,08. Reel 2: 0,44 | No roteiro, só o plano. O número sai do vídeo |
| Texto e safe zone | Tamanho do texto e se ele fica dentro da área livre | Rótulos com 34 px ou mais (Reel 1) e 40 px ou mais (Reel 2); x de 60 a 1020 e y de 250 a 1500 num quadro de 1080×1920 | Nos styleframes do tamanho real e no vídeo |
| Leitura em letras por segundo | Letras do texto, contando os espaços, por segundo | Até 15 | No beat sheet |
| Contraste | Razão entre a cor do texto e a do fundo | No Reel 2, de 9,6:1 a 12,8:1. No design system do curso, 4,5:1 ou mais para texto normal | Nos styleframes, com o `contraste.py` |
| Paleta por ato e cor da marca | A cor da marca no vídeo, medida como diferença de cor (ΔE2000) | No Reel 2, de 0,8 a 1,2. Abaixo de uns 2 quase não se vê | No vídeo |
| Brancos, flashes e fotossensibilidade | Trocas de tela muito claras e rápidas | No Reel 2, no máximo 2 trocas de tela por segundo | No animatic e no vídeo |
| Easings e duração de cena | O tipo de aceleração de cada movimento e as batidas de cada cena | De 3 a 15 batidas por cena | No beat sheet; os easings, no animatic |
| Transições | Cortes e passagens entre as cenas | Sem número | No animatic |
| Contato com o chão e gravidade | Uma gravidade para a peça toda; pés no chão | 9,81 m/s² numa escala fixa | Só no vídeo, quando tem personagem |
| Congelamentos (`motion_audit`) | Quadros em que a imagem para | Sem número no case | No vídeo |
| Travadas de imagem e som (`stall_audit`) | Preto com silêncio, que parece buffering | Nenhum preto, nenhum silêncio | No roteiro (a ação e o som de cada interrupção) e no vídeo |
| Poses paradas (`freeze_audit`) | Velocidade visível dentro da caixa do foco, por fluxo óptico | Reprova abaixo de 120 px/s por mais de 0,1 s | No roteiro, só o plano (o que se mexe no foco de cada cena). O número sai do vídeo |
| LUFS integrado e por ato | Volume percebido do vídeo inteiro e de cada ato | −14 LUFS no vídeo inteiro; o clímax como a parte mais alta | No animatic, que tem a trilha, e no vídeo depois do AAC |
| True peak depois do AAC | O pico entre as amostras, no arquivo final | Até −1,1 dBTP | Só no arquivo final codificado |
| Mono | O quanto o som perde quando os dois canais viram um | No Reel 2, perdeu 0,08 dB | No vídeo |
| Ataques no grid | Os golpes mais fortes da trilha caem nas batidas | No Reel 1, 20 de 20 | No animatic e no vídeo |
| Grave audível em celular | O bumbo e o baixo têm harmônicos que o alto-falante pequeno toca | Sem número | No vídeo, e uma pessoa ouve no celular |

## O que o case deixou para uma pessoa

- Reel 1: o timbre das guitarras e a posição da interface do Instagram.
- Reel 2: ouvir no alto-falante do celular e testar numa conta privada antes de publicar.
- Antes de publicar: assistir com som no celular, subir em rascunho ou numa conta privada para ver a interface por cima, revisar legenda, hashtags e respostas prontas.
