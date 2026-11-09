"""Monta o pedido de um lote: o seu prompt com o glossário, os nomes que já existem e as 3 reuniões.

Uso: python3 montar.py --prompt meu-prompt.md (--glossario meu-glossario.md | --sem-glossario) --lote N --saidas PASTA
Grava PASTA/lote-N-pedido.txt. Para o lote 2 em diante, lê os lotes anteriores da mesma PASTA,
que precisam passar no validar.py, e põe no pedido os nomes que eles já usaram."""
import argparse
import re
import sys
from pathlib import Path

from cerebro import LOTES, ler_resumo, norm, validar_pasta

MARCAS = ["{glossario}", "{nomes_existentes}", "{n}", "{reunioes}"]
p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
p.add_argument("--prompt", required=True)
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--glossario")
g.add_argument("--sem-glossario", action="store_true")
p.add_argument("--lote", type=int, required=True, choices=sorted(LOTES))
p.add_argument("--saidas", required=True)
a = p.parse_args()

prompt = Path(a.prompt).read_text(encoding="utf-8")
faltam = [m for m in MARCAS if prompt.count(m) != 1]
if faltam:
    sys.exit("O prompt precisa ter cada marca exatamente uma vez. Faltam ou se repetem: " + ", ".join(faltam))
glossario = "Nenhum." if a.sem_glossario else Path(a.glossario).read_text(encoding="utf-8").strip()
if not glossario:
    sys.exit("O glossário está vazio. Para rodar sem glossário, use --sem-glossario.")

saidas = Path(a.saidas)
anteriores = list(range(1, a.lote))
reunioes, relatorio = validar_pasta(saidas, anteriores) if anteriores else ({}, {})
ruins = {k: v for k, v in relatorio.items() if v}
if ruins:
    msg = "; ".join(f"{k}: {v[0]}" for k, v in ruins.items())
    sys.exit(f"Os lotes anteriores precisam passar no validar.py antes do lote {a.lote}. {msg}")

existentes = {}
for rid in sorted(reunioes):
    for campo in ("pessoas", "projetos", "temas", "empresas"):
        vistos = existentes.setdefault(campo, {})
        for nome in reunioes[rid][campo]:
            vistos.setdefault(norm(nome), nome)
rotulos = {"pessoas": "Pessoas", "projetos": "Projetos", "temas": "Temas", "empresas": "Empresas"}
nomes = "\n".join(f"{rotulos[c]}: " + (", ".join(existentes.get(c, {}).values()) or "nenhum ainda")
                  for c in rotulos)

blocos = []
for rid in LOTES[a.lote]:
    campos, corpo = ler_resumo(rid)
    dia, mes, ano = campos["gravacao"].split()[0].split("/")
    blocos.append(f'=== REUNIÃO id={rid}\nTítulo: "{campos["titulo"]}" em {dia}/{mes}/{ano[2:]}\n"""\n{corpo}\n"""')

# Troca as quatro marcas de uma vez: uma marca escrita dentro do glossário não é trocada de novo.
valores = {"{glossario}": glossario, "{nomes_existentes}": nomes,
           "{n}": str(len(LOTES[a.lote])), "{reunioes}": "\n\n".join(blocos)}
pedido = re.sub("|".join(re.escape(m) for m in MARCAS), lambda m: valores[m.group(0)], prompt)
saidas.mkdir(parents=True, exist_ok=True)
destino = saidas / f"lote-{a.lote}-pedido.txt"
destino.write_text(pedido, encoding="utf-8")
print(f"Pedido do lote {a.lote} gravado em {destino} ({len(pedido)} caracteres).")
print(f"Cole numa conversa nova do Claude e salve a resposta em {saidas / f'lote-{a.lote}.json'}.")
