"""Valida as respostas do Claude: JSON estrito, um objeto por reunião, ids do lote e limites de cada campo.

Uso: python3 validar.py PASTA [--lote N]
A PASTA tem lote-1.json a lote-4.json. Sem --lote, os quatro são obrigatórios.
Sai com código 0 se tudo passou e 1 se houve erro."""
import argparse
import sys

from cerebro import LOTES, validar_pasta

p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
p.add_argument("pasta")
p.add_argument("--lote", type=int, choices=sorted(LOTES))
a = p.parse_args()
lotes = [a.lote] if a.lote else None
reunioes, relatorio = validar_pasta(a.pasta, lotes)
total = sum(len(LOTES[n]) for n in (lotes or LOTES))
for arquivo, erros in relatorio.items():
    print(f"{arquivo}: " + ("ok" if not erros else f"{len(erros)} erro(s)"))
    for e in erros:
        print(f"  - {e}")
print(f"reuniões aceitas: {len(reunioes)} de {total} (lote com erro não entra)")
sys.exit(0 if all(not e for e in relatorio.values()) else 1)
