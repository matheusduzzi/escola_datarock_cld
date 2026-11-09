"""Mede o contraste entre a cor do texto e a cor do fundo, pela conta do WCAG 2.2.

Uso:
    python3 contraste.py "#FFFFFF" "#E07A5F"
    python3 contraste.py "#FFFFFF" "#E07A5F" "#2F3A35" "#F7EFE6"
    python3 contraste.py --arquivo pares.txt

Cada par é a cor do texto e depois a cor do fundo, em hex (#fff ou #FFFFFF).
No arquivo, uma linha por par: texto, fundo e, se quiser, onde o par aparece.
Linha vazia e linha que começa com # seguido de espaço são ignoradas.

    #FFFFFF  #E07A5F  botão
    #2F3A35  #F7EFE6  títulos na página

A razão sai com duas casas, cortada e não arredondada: 4,499 aparece como 4,49
e não passa em 4,5. Texto normal precisa de 4,5:1. Texto grande precisa de 3:1.
Texto grande, no WCAG: 18 pontos (uns 24 px), ou 14 pontos (uns 18,5 px) em negrito.
Se um par estiver errado, nada é medido: corrija e rode de novo.
"""
import math
import re
import sys
from pathlib import Path

HEX = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")
NORMAL, GRANDE = 4.5, 3.0


def normalizar(cor):
    m = HEX.match(cor.strip())
    if not m:
        raise ValueError(f"cor inválida: {cor!r} (use #RGB ou #RRGGBB)")
    h = m.group(1).upper()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def luminancia(cor):
    """Luminância relativa do WCAG 2.2: canal até 0,04045 divide por 12,92."""
    canais = []
    for i in (1, 3, 5):
        c = int(cor[i:i + 2], 16) / 255
        canais.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = canais
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razao(texto, fundo):
    claro, escuro = sorted((luminancia(texto), luminancia(fundo)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


def mostrar(valor):
    """Duas casas, cortadas, com vírgula: o número mostrado nunca passa sem passar."""
    return f"{math.floor(valor * 100) / 100:.2f}".replace(".", ",")


def ler_arquivo(caminho):
    pares = []
    for n, linha in enumerate(Path(caminho).read_text(encoding="utf-8").splitlines(), 1):
        limpa = linha.strip()
        if not limpa or limpa.startswith("# ") or limpa == "#":
            continue
        partes = limpa.split(None, 2)
        if len(partes) < 2:
            raise ValueError(f"linha {n}: faltou a cor do fundo: {linha!r}")
        try:
            pares.append((normalizar(partes[0]), normalizar(partes[1]), partes[2] if len(partes) > 2 else ""))
        except ValueError as erro:
            raise ValueError(f"linha {n}: {erro}") from None
    if not pares:
        raise ValueError("o arquivo não tem nenhum par")
    return pares


def main(args):
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    try:
        if args[0] == "--arquivo":
            if len(args) != 2:
                print(__doc__)
                return 2
            if not Path(args[1]).is_file():
                print(f"arquivo não encontrado: {args[1]}")
                return 1
            pares = ler_arquivo(args[1])
        else:
            if len(args) % 2:
                print("cada par precisa de duas cores: a do texto e a do fundo")
                return 2
            pares = [(normalizar(args[i]), normalizar(args[i + 1]), "") for i in range(0, len(args), 2)]
    except ValueError as erro:
        print(f"nada foi medido: {erro}")
        return 1
    reprovados = 0
    for texto, fundo, onde in pares:
        r = razao(texto, fundo)
        normal = "passa" if r >= NORMAL else "não passa"
        grande = "passa" if r >= GRANDE else "não passa"
        if r < NORMAL:
            reprovados += 1
        print(f"{texto} sobre {fundo}  {mostrar(r)}:1  texto normal: {normal}  texto grande: {grande}" + (f"  ({onde})" if onde else ""))
    print(f"{len(pares)} " + ("par" if len(pares) == 1 else "pares") + f", {reprovados} abaixo de 4,5:1")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
