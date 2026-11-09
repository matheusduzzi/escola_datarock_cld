"""Conta as cores em hex e lista fontes e pesos de arquivos CSS.

Uso: python3 contar_css.py site/css/aurora.css site/css/tema-base.css

Junta maiúscula e minúscula (#e27c61 = #E27C61) e a forma curta (#fff = #FFFFFF).
Comentário não conta: uma cor escrita só num comentário não é usada pelo site.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def normalizar(h):
    h = h.upper()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def regras(texto):
    """Pares (seletor, [(propriedade, valor)]) do CSS, sem comentários."""
    texto = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)
    for bloco in re.finditer(r"([^{}]+)\{([^}]*)\}", texto):
        seletor = " ".join(bloco.group(1).split())
        decls = [d.split(":", 1) for d in bloco.group(2).split(";") if ":" in d]
        yield seletor, [(p.strip(), v.strip()) for p, v in decls]


def main(nomes):
    cores, onde = Counter(), defaultdict(list)
    fontes, pesos = [], []
    for nome in nomes:
        caminho = Path(nome)
        if not caminho.is_file():
            print(f"arquivo não encontrado: {nome}")
            return 1
        for seletor, decls in regras(caminho.read_text(encoding="utf-8")):
            for prop, valor in decls:
                for m in HEX.finditer(valor):
                    cor = normalizar(m.group(1))
                    cores[cor] += 1
                    onde[cor].append(f"{caminho.name}  {seletor}  ({prop})")
                if prop == "font-family":
                    fontes.append(f"{valor.split(',')[0].strip(chr(39) + chr(34))}  em  {seletor}")
                if prop == "font-weight":
                    pesos.append(f"{valor}  em  {seletor}")
    print("CORES")
    for cor, n in cores.most_common():
        print(f"{cor}  {n}x")
        for o in onde[cor]:
            print(f"    {o}")
    print(f"{len(cores)} cores, {sum(cores.values())} usos")
    print("FONTES (font-family)")
    for f in fontes:
        print(f"    {f}")
    print("PESOS (font-weight)")
    for p in pesos:
        print(f"    {p}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
