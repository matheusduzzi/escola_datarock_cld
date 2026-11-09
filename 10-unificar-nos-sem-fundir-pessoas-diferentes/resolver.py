"""Mostra os nós que o resolvedor monta, as uniões que o "não unir" recusou e as sugestões de pares parecidos.

Uso: python3 resolver.py [--config minha-config.json] [--tipo pessoa] [--ate siglas] [--sem-sugestoes]
"""
import argparse
import sys

import resolvedor as r

ap = argparse.ArgumentParser(description="Monta os nós do grafo com a sua configuração.")
ap.add_argument("--config", default="minha-config.json")
ap.add_argument("--tipo", choices=list(r.TIPOS), help="mostra só um tipo")
ap.add_argument("--ate", choices=r.CAMADAS, default="nao_unir", help="para na camada indicada")
ap.add_argument("--sem-sugestoes", action="store_true")
args = ap.parse_args()

nomes = r.ler_nomes()
try:
    cfg = r.ler_config(args.config, nomes)
except r.ConfigErrada as e:
    print("configuração recusada: " + str(e))
    print("nada foi montado.")
    sys.exit(1)

nos, recusadas = r.resolver(nomes, cfg, args.ate)
tipos = [args.tipo] if args.tipo else list(r.TIPOS)
print(f"camada: {r.NOME_CAMADA[args.ate]} | auto: {'ligado' if cfg['auto'] else 'desligado'}")
for tipo in tipos:
    lista = sorted(nos[tipo], key=lambda n: (-len(n["membros"]), n["rotulo"]))
    print(f"\n{r.TIPOS[tipo]}: {len(lista)} nós a partir de {len(nomes[tipo])} nomes")
    for no in lista:
        outros = [m for m in no["membros"] if m != no["rotulo"]]
        print(f"  {no['rotulo']}" + (f"  <- {', '.join(outros)}" if outros else ""))

rec = [x for x in recusadas if x["tipo"] in tipos]
print(f"\nuniões recusadas pelo não unir: {len(rec)}")
for x in rec:
    print(f"  {x['tipo']}: {x['a']} + {x['b']} ({x['origem']}) recusada, porque {x['par'][0]} e {x['par'][1]} não são iguais")

if not args.sem_sugestoes:
    sug = [s for s in r.sugestoes(nomes, cfg, nos) if s["tipo"] in tipos]
    print(f"\nsugestões para você decidir (unir ou não unir): {len(sug)}")
    for s in sug:
        nota = f"{s['nota']:.2f}".replace(".", ",")
        print(f"  {s['tipo']}: {s['a']} x {s['b']}  nota {nota}  (nós: {s['no_a']} | {s['no_b']})")
