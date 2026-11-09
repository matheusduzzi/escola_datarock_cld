"""Conta duplicatas nas respostas do Claude, comparando uma pasta com outra.

Uso: python3 contar.py PASTA [PASTA ...] [--lote N]
Cada nome vira um nó pela grafia sem acento e em minúsculas, como no grafo do case. A chave
chave-de-grafias.json diz qual pessoa, projeto ou empresa cada grafia é, reunião por reunião.
Duplicata é um nó a mais para a mesma coisa. Só conta pastas que passam no validar.py."""
import argparse
import json
import re
import sys
from pathlib import Path

from cerebro import LOTES, PASTA, norm, norm_empresa, validar_pasta

TIPOS = ["pessoas", "projetos", "empresas", "temas"]
GENERICO = re.compile(r"^(falante|speaker|locutor|participante|orador|pessoa) \d+$")
REGRAS = {"!dono": "dona das gravações como pessoa", "!generico": "rótulo genérico como pessoa",
          "!projeto CLARA": "assistente CLARA como pessoa", "!loja": "Loja Aurora como empresa"}
CHAVE = json.loads((PASTA / "chave-de-grafias.json").read_text(encoding="utf-8"))


def resolver(tipo, chave_nome, rid):
    if tipo == "pessoas" and GENERICO.match(chave_nome):
        return ["!generico"]
    regra = CHAVE[tipo]
    valor = regra["por_reuniao"].get(chave_nome, {}).get(rid)
    if valor is None:
        valor = regra["global"].get(chave_nome)
    if valor is None:
        return None
    return valor if isinstance(valor, list) else [valor]


def medir(reunioes):
    m = {"regras": {k: set() for k in REGRAS}, "fora": [], "tipos": {}}
    for tipo in TIPOS:
        nos = {}
        for rid in sorted(reunioes):
            for nome in reunioes[rid][tipo]:
                k = norm_empresa(nome) if tipo == "empresas" else norm(nome)
                no = nos.setdefault(k, {"grafias": set(), "reunioes": set(), "entidades": set(), "fora": False})
                no["grafias"].add(nome)
                no["reunioes"].add(rid)
                ents = resolver(tipo, k, rid)
                if ents is None:
                    no["fora"] = True
                    continue
                for e in ents:
                    if e.startswith("!"):
                        m["regras"][e].add(rid)
                    else:
                        no["entidades"].add(e)
        por_entidade = {}
        for k, no in nos.items():
            for e in no["entidades"]:
                por_entidade.setdefault(e, []).append(k)
            if no["fora"] and tipo != "temas":
                m["fora"].append((tipo, " / ".join(sorted(no["grafias"])), ", ".join(sorted(no["reunioes"]))))
        m["tipos"][tipo] = {
            "nos": len(nos),
            "duplicatas": sum(len(ks) - 1 for ks in por_entidade.values()),
            "grupos": {e: sorted(" / ".join(sorted(nos[k]["grafias"])) for k in ks)
                       for e, ks in sorted(por_entidade.items()) if len(ks) > 1},
            "fusoes": {" / ".join(sorted(no["grafias"])): sorted(no["entidades"])
                       for no in nos.values() if len(no["entidades"]) > 1},
        }
    return m


p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
p.add_argument("pastas", nargs="+")
p.add_argument("--lote", type=int, choices=sorted(LOTES))
a = p.parse_args()
lotes = [a.lote] if a.lote else None
total = sum(len(LOTES[n]) for n in (lotes or LOTES))
medidas = {}
for pasta in a.pastas:
    reunioes, relatorio = validar_pasta(pasta, lotes)
    ruins = {k: v for k, v in relatorio.items() if v}
    if ruins:
        print(f"{pasta}: não passou no validar.py, nada foi contado.")
        for k, v in ruins.items():
            print(f"  {k}: {v[0]}")
        sys.exit(1)
    medidas[Path(pasta).name or pasta] = (len(reunioes), medir(reunioes))

nomes = list(medidas)
largura = max(12, *(len(n) for n in nomes))
linhas = [("reuniões contadas", [f"{n}/{total}" for n, _ in medidas.values()])]
for tipo in TIPOS:
    linhas.append((f"{tipo}: nós", [m["tipos"][tipo]["nos"] for _, m in medidas.values()]))
    linhas.append((f"{tipo}: duplicatas", [m["tipos"][tipo]["duplicatas"] for _, m in medidas.values()]))
linhas.append(("total de duplicatas", [sum(m["tipos"][t]["duplicatas"] for t in TIPOS) for _, m in medidas.values()]))
linhas.append(("nós que juntam duas pessoas", [len(m["tipos"]["pessoas"]["fusoes"]) for _, m in medidas.values()]))
for k, rotulo in REGRAS.items():
    linhas.append((f"{rotulo} (reuniões)", [len(m["regras"][k]) for _, m in medidas.values()]))
linhas.append(("nós fora da chave", [len(m["fora"]) for _, m in medidas.values()]))
print(" " * 40 + "".join(n.rjust(largura + 2) for n in nomes))
for rotulo, valores in linhas:
    print(rotulo.ljust(40) + "".join(str(v).rjust(largura + 2) for v in valores))

for nome, (_, m) in medidas.items():
    print(f"\n{nome}")
    for tipo in TIPOS:
        for e, grafias in m["tipos"][tipo]["grupos"].items():
            print(f"  duplicata em {tipo}: {e} aparece como " + "; ".join(grafias))
    for grafia, ents in m["tipos"]["pessoas"]["fusoes"].items():
        print(f"  nó que junta pessoas diferentes: {grafia} = " + " e ".join(ents))
    for k, rotulo in REGRAS.items():
        if m["regras"][k]:
            print(f"  {rotulo}: " + ", ".join(sorted(m["regras"][k])))
    for tipo, grafia, rids in m["fora"]:
        print(f"  fora da chave, {tipo}: {grafia} ({rids}). Decida você se é duplicata.")
