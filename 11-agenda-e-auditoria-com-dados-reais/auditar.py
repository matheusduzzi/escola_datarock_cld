"""Audita a ligação das gravações com a agenda e a correção dos nomes, e compara com a regra antiga.

Uso:
  python3 auditar.py [--regra minha-regra.json] [--reuniao reuniao-08] [--gravar]

Sem --gravar, só lê e mostra. Com --gravar, grava em gravado/ se a auditoria não achar
correção para quem não estava no convite nem correção contra um "não unir".
"""
import argparse
import json
import sys

import ligador as L

ap = argparse.ArgumentParser(description="Audita as ligações e as correções de nome antes de gravar.")
ap.add_argument("--regra", default="minha-regra.json")
ap.add_argument("--reuniao", help="mostra só essa gravação nas listas")
ap.add_argument("--gravar", action="store_true", help="grava em gravado/ se a auditoria passar")
args = ap.parse_args()

grav, eventos, separar = L.ler_dados()
try:
    regra = L.ler_regra(args.regra, grav, eventos)
    antiga = L.ler_regra(L.PASTA / "regra-antiga.json", grav, eventos)
except L.RegraErrada as e:
    print("regra recusada: " + str(e))
    print("nada foi auditado nem gravado.")
    sys.exit(1)
if args.reuniao and args.reuniao not in {g["id"] for g in grav}:
    print(f'regra recusada: "{args.reuniao}" não é uma das gravações')
    print("nada foi auditado nem gravado.")
    sys.exit(1)

res = L.auditar(grav, eventos, separar, regra)
velho = L.auditar(grav, eventos, separar, antiga)
CAS = {"horario": "só horário", "horario_e_pessoas": "horário e pessoas"}
COR = {"global": "global", "por_reuniao": "por reunião"}
mostrar = (lambda gid: gid == args.reuniao) if args.reuniao else (lambda gid: True)
por_id = {g["id"]: g for g in grav}


def hm(t):
    return t.strftime("%H:%M")


print(f"regra: {args.regra} | casamento: {CAS[regra['casamento']]} | correção: {COR[regra['correcao']]}")
print("\nligações")
for g in grav:
    if not mostrar(g["id"]):
        continue
    ev, info = res["lig"][g["id"]]
    quando = g["s"].strftime("%d/%m %H:%M")
    if not ev:
        print(f"  {g['id']}  {quando}  sem evento")
        continue
    extra = []
    if info["atraso_min"]:
        extra.append(f"começou {info['atraso_min']} min depois do fim")
    if len(info["mesmo_horario"]) > 1:
        extra.append(f"{len(info['mesmo_horario'])} eventos no mesmo horário")
    if info.get("hits"):
        extra.append(f"{info['hits']} citado(s) no convite")
    print(f"  {g['id']}  {quando}  -> {ev['t']} ({hm(ev['ts'])}-{hm(ev['te'])})" + (f"; {', '.join(extra)}" if extra else ""))

print("\nnomes corrigidos")
ORIG = {"regra": "", "confirmado": " (confirmado)", "global": " (mapa global)"}
for c in res["correcoes"]:
    if not mostrar(c["g"]) or not c["mudou"]:
        continue
    alerta = []
    if not c["no_convite"]:
        alerta.append("NÃO ESTÁ NO CONVITE" if c["tem_evento"] else "A GRAVAÇÃO NÃO TEM EVENTO")
    if c["entre_dois"]:
        alerta.append("O CONVITE TEM DOIS QUE BATEM")
    if c["contra_nao_unir"]:
        alerta.append('JUNTA UM PAR DE "NÃO UNIR"')
    print(f"  {c['g']}  {c['falado']} -> {c['alvo']}{ORIG[c['origem']]}" + (f"  <- {'; '.join(alerta)}" if alerta else ""))
for s in res["sem_correcao"]:
    if mostrar(s["g"]):
        print(f"  {s['g']}  {s['falado']}: fica sem correção (confirmado)")

print("\nachados da auditoria (todas as gravações)")
sem = [g["id"] for g in grav if not res["lig"][g["id"]][0]]
print(f"  gravações sem evento: {len(sem)}" + (f" ({', '.join(sem)})" if sem else ""))
print(f"  gravações ligadas sem ninguém citado no convite: {len(res['talvez'])}"
      + (f" ({', '.join(res['talvez'])})" if res["talvez"] else ""))
duplos = [gid for gid, (ev, info) in res["lig"].items() if ev and len(info["mesmo_horario"]) > 1]
print(f"  gravações com dois eventos no mesmo horário: {len(duplos)}" + (f" ({', '.join(duplos)})" if duplos else ""))
sem_nome = [p for p in res["palpites"]]
print(f"  e-mails sem nome nos convites: {len(sem_nome)}"
      + (" (" + ", ".join(f"{p['email']} em {p['presencas']} eventos" for p in sem_nome) + ")" if sem_nome else ""))
print(f"  nome falado que vira pessoas diferentes em reuniões diferentes: {len(res['varias'])}")
for falado, alvos in res["varias"].items():
    print(f"    {falado}: " + "; ".join(f"{alvo} em {', '.join(gs)}" for alvo, gs in alvos.items()))
b = L.bloqueios(res)
print(f"  correções para quem não estava no convite: {sum(1 for x in b if 'convite dessa' in x or 'não tem evento' in x)}")
print(f"  correções escolhidas entre dois convidados: {sum(1 for x in b if 'entre dois' in x)}")
print(f"  correções contra um \"não unir\": {sum(1 for x in b if 'não unir' in x)}")

pend = [p for p in res["pendentes"] if mostrar(p["g"])]
emails_pend = [p for p in res["palpites"] if p["nome"]]
print(f"\npara confirmação humana: {len(pend) + (0 if args.reuniao else len(emails_pend))}")
for p in pend:
    dica = f"; parecidos: {', '.join(p['parecidos'])}" if p["parecidos"] else ""
    print(f"  {p['g']}  {p['falado']}: {p['motivo']}{dica}")
if not args.reuniao:
    for p in emails_pend:
        print(f"  {p['email']}: palpite {p['nome']} (citada sem dono em {len(p['em'])} de {p['de']} reuniões ligadas"
              f" com esse e-mail: {', '.join(p['em'])}; sem 1:1 no título)")

a, d = L.resumo(velho), L.resumo(res)
mudaram = sum(1 for gid in res["lig"] if (res["lig"][gid][0] or {}).get("id") != (velho["lig"][gid][0] or {}).get("id"))
print("\nantes e depois (antes = regra-antiga.json)")
linhas = [("gravações ligadas a um evento", a["ligadas"], d["ligadas"]),
          ("ligações diferentes da regra antiga", "-", mudaram),
          ("citações de nome corrigidas", a["corrigidas"], d["corrigidas"]),
          ("correções para quem não estava no convite", a["fora"], d["fora"]),
          ("correções contra um \"não unir\"", a["contra"], d["contra"]),
          ("correções escolhidas entre dois convidados", a["entre_dois"], d["entre_dois"]),
          ("para confirmação humana", a["pendentes"], d["pendentes"])]
print(f"{'indicador':<44}{'antes':>6}{'depois':>8}")
for nome, x, y in linhas:
    print(f"{nome:<44}{x:>6}{y:>8}")

if args.gravar:
    if b:
        print("\ngravação recusada: a auditoria achou correções que estragam o grafo")
        for x in b:
            print("  " + x)
        print("nada foi gravado.")
        sys.exit(1)
    destino = L.PASTA / "gravado"
    destino.mkdir(exist_ok=True)
    ligacoes = {gid: (ev["id"] if ev else "") for gid, (ev, _) in res["lig"].items()}
    mapa = {}
    for c in res["correcoes"]:
        if c["mudou"]:
            mapa.setdefault(c["g"], {})[c["falado"]] = c["alvo"]
    abertos = {p["g"] for p in res["pendentes"]}
    feitas = sorted(gid for gid, (ev, _) in res["lig"].items() if ev and gid not in abertos)
    (destino / "ligacoes.json").write_text(json.dumps(ligacoes, ensure_ascii=False, indent=2) + "\n")
    (destino / "correcoes.json").write_text(json.dumps({"map": mapa, "done": feitas}, ensure_ascii=False, indent=2) + "\n")
    (destino / "emails.json").write_text(json.dumps(regra["emails"], ensure_ascii=False, indent=2) + "\n")
    lista = [{"reuniao": p["g"], "falado": p["falado"], "motivo": p["motivo"], "parecidos": p["parecidos"]} for p in res["pendentes"]]
    lista += [{"email": p["email"], "palpite": p["nome"], "em": p["em"]} for p in emails_pend]
    (destino / "pendentes.json").write_text(json.dumps(lista, ensure_ascii=False, indent=2) + "\n")
    print(f"\ngravado em gravado/: {len(ligacoes)} ligações, {sum(len(v) for v in mapa.values())} correções em "
          f"{len(mapa)} reuniões, {len(regra['emails'])} e-mail(s) confirmado(s), {len(lista)} pendente(s)."
          " banco/nao-unir.json não foi tocado.")
