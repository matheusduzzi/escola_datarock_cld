"""Mede o resolvedor contra o gabarito, camada por camada.

Uso: python3 medir.py [--config minha-config.json]
"""
import argparse
import sys

import resolvedor as r

ap = argparse.ArgumentParser(description="Compara os nós do resolvedor com o gabarito.")
ap.add_argument("--config", default="minha-config.json")
args = ap.parse_args()

nomes = r.ler_nomes()
try:
    cfg = r.ler_config(args.config, nomes)
    gab = r.ler_gabarito(r.PASTA / "gabarito.json", nomes)
except r.ConfigErrada as e:
    print("configuração recusada: " + str(e))
    print("nada foi medido.")
    sys.exit(1)

print(f"{'camada':<18}{'nós':>5}{'certas':>8}{'erradas':>9}{'faltou unir':>13}")
for camada in ["nenhuma"] + r.CAMADAS:
    nos, recusadas = r.resolver(nomes, cfg, camada)
    m = r.medir(nos, gab)
    print(f"{r.NOME_CAMADA[camada]:<18}{m['nos']:>5}{len(m['certas']):>8}{len(m['erradas']):>9}{len(m['faltou']):>13}")
print(f"{'gabarito':<18}{m['nos_gabarito']:>5}{len(m['certas']) + len(m['faltou']):>8}{0:>9}{0:>13}")

print(f"\nuniões erradas no fim: {len(m['erradas'])}")
for t, a, b in m["erradas"]:
    print(f"  {t}: {a} + {b}")
print(f"faltou unir no fim: {len(m['faltou'])}")
for t, a, b in m["faltou"]:
    print(f"  {t}: {a} + {b}")

no_de = {(t, x): i for t, lista in nos.items() for i, no in enumerate(lista) for x in no["membros"]}
print(f"pares de não unir: {len(cfg['nao_unir'])}")
for t, a, b in cfg["nao_unir"]:
    ok = no_de[(t, a)] != no_de[(t, b)]
    print(f"  {t}: {a} x {b}: {'respeitado, nós separados' if ok else 'NO MESMO NÓ'}")
print(f"uniões recusadas pelo não unir: {len(recusadas)}")
for x in recusadas:
    print(f"  {x['tipo']}: {x['a']} + {x['b']} ({x['origem']})")
