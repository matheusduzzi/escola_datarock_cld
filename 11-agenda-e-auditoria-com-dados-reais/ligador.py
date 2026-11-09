"""Liga cada gravação a um evento da agenda, corrige os nomes falados pelo convite e audita o resultado.

Só biblioteca padrão. norm, fon e jaro_winkler são as mesmas da aula anterior (resolvedor.py),
que seguem o código do case. As regras de ligação e de correção seguem as seções 11.2 e 11.3
do case (codigo-do-case.md). auditar.py usa esse arquivo.
"""
import json
import re
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

PASTA = Path(__file__).resolve().parent
MIN = timedelta(minutes=1)
STOP = set("de da do das dos e a o as os em no na nos nas para por com the of and".split())
# Apelidos que o case cita com o nome de destino (NICK). Só o primeiro nome é trocado.
APELIDOS = {"leo": ["leonardo", "leandro"], "juju": ["juliana", "juliano", "julia"]}
# E-mail de função: com dígito ou com uma dessas palavras, o nome não sai do e-mail (seção 11.1).
GENERICOS = {"ds", "produto", "comercial", "financeiro", "sala", "agenda", "atendimento"}
CHAVES_REGRA = {"casamento", "correcao", "emails_confirmados", "nomes_confirmados"}


class RegraErrada(Exception):
    pass


def norm(texto):
    s = unicodedata.normalize("NFD", str(texto or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def fon(tok, plural):
    """Chave fonética para português, igual à função phon do case."""
    if re.fullmatch(r"\d+", tok):
        return tok
    s = tok
    if plural and len(s) > 3:
        if re.search(r"oes$|aes$", s):
            s = s[:-3] + "ao"
        elif re.search(r"ns$", s):
            s = s[:-2] + "m"
        elif re.search(r"[^s]s$", s):
            s = s[:-1]
    for padrao, troca in [(r"ph", "f"), (r"th", "t"), (r"[sc]h", "x"), (r"lh", "li"), (r"nh", "ni"),
                          (r"y", "i"), (r"w", "v"), (r"k", "c"), (r"qu(?=[ei])", "c"), (r"q", "c"),
                          (r"gu(?=[ei])", "g"), (r"c(?=[ei])", "s"), (r"z", "s"), (r"^h", ""), (r"h", ""),
                          (r"(.)\1+", r"\1")]:
        s = re.sub(padrao, troca, s)
    if len(s) > 2:
        s = re.sub(r"e$", "i", s)
        s = re.sub(r"u$", "o", s)
    return s


def jaro_winkler(a, b):
    if a == b:
        return 1.0
    la, lb = len(a), len(b)
    if not la or not lb:
        return 0.0
    janela = max(la, lb) // 2 - 1
    ma, mb = [False] * la, [False] * lb
    iguais = 0
    for i, c in enumerate(a):
        for j in range(max(0, i - janela), min(lb, i + janela + 1)):
            if not mb[j] and b[j] == c:
                ma[i] = mb[j] = True
                iguais += 1
                break
    if not iguais:
        return 0.0
    trocas, k = 0, 0
    for i in range(la):
        if ma[i]:
            while not mb[k]:
                k += 1
            if a[i] != b[k]:
                trocas += 1
            k += 1
    jaro = (iguais / la + iguais / lb + (iguais - trocas / 2) / iguais) / 3
    prefixo = 0
    for x, y in zip(a[:4], b[:4]):
        if x != y:
            break
        prefixo += 1
    return jaro + prefixo * 0.1 * (1 - jaro)


def chave(nome):
    """A chave fonética do nome de pessoa, sem espaços: a mesma que junta nós no grafo."""
    return "".join(fon(t, False) for t in norm(nome).split())


def toks(nome):
    return [fon(t, False) for t in norm(nome).split()]


def casa(falado, convidado):
    """Regra automática do case (fuzzyInviteHits), para um par: nome falado x nome do convite.

    Um nome só: igual ao primeiro ou ao último nome do convidado, ou Jaro-Winkler >= 0,9 com 4+ letras.
    Vários nomes: cada um >= 0,92 com o nome na mesma posição (primeiro com primeiro, último com último).
    Apelido conhecido no primeiro nome é trocado antes. Devolve "regra", "apelido" ou "".
    """
    c = toks(convidado)
    if not c:
        return ""
    base = toks(falado)
    if not base:
        return ""
    variantes = [(base, "regra")]
    primeiro = norm(falado).split()[0]
    variantes += [([fon(x, False)] + base[1:], "apelido") for x in APELIDOS.get(primeiro, [])]
    for v, origem in variantes:
        if len(v) == 1:
            t = v[0]
            for ct in {c[0], c[-1]}:
                if t == ct or (len(t) >= 4 and len(ct) >= 4 and jaro_winkler(t, ct) >= 0.9):
                    return origem
        elif len(v) <= len(c):
            pares = list(zip(v, c)) if len(v) == len(c) else [(v[0], c[0]), (v[-1], c[-1])]
            if all(a == b or jaro_winkler(a, b) >= 0.92 for a, b in pares):
                return origem
    return ""


def ler_json(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def hora(texto):
    return datetime.fromisoformat(texto)


def ler_dados(pasta=PASTA):
    grav = ler_json(pasta / "gravacoes.json")["gravacoes"]
    for g in grav:
        g["s"] = hora(g["inicio"])
        g["e"] = g["s"] + g["duracao_min"] * MIN
    eventos = ler_json(pasta / "agenda-outubro.json")["events"]
    for x in eventos:
        x["ts"], x["te"] = hora(x["s"]), hora(x["e"])
    separar = []
    for a, b in ler_json(pasta / "banco/nao-unir.json")["nao_unir"]:
        separar.append((a.split(":", 1)[1], b.split(":", 1)[1]))
    return grav, eventos, separar


def nome_do_email(email):
    """Nome tirado do e-mail (marcos.valente@ vira Marcos Valente), exceto e-mail de função."""
    local = email.split("@")[0]
    partes = re.split(r"[._-]+", local)
    if re.search(r"\d", local) or GENERICOS & set(partes) or len(partes) < 2:
        return ""
    return " ".join(p.capitalize() for p in partes)


def nome_convidado(a, emails):
    """E-mail confirmado vence o nome do convite; sem nome, tenta o e-mail."""
    return emails.get(a["e"]) or a.get("n") or nome_do_email(a["e"])


def ler_regra(caminho, grav, eventos):
    try:
        regra = ler_json(caminho)
    except FileNotFoundError:
        raise RegraErrada(f"não achei o arquivo {caminho}")
    except json.JSONDecodeError as e:
        raise RegraErrada(f"{caminho} não é JSON válido (linha {e.lineno}, coluna {e.colno}: {e.msg})")
    if not isinstance(regra, dict):
        raise RegraErrada("a regra precisa ser um objeto JSON")
    chaves = {k for k in regra if not k.startswith("_")}
    if chaves != CHAVES_REGRA:
        faltam, sobram = CHAVES_REGRA - chaves, chaves - CHAVES_REGRA
        raise RegraErrada("a regra precisa ter casamento, correcao, emails_confirmados e nomes_confirmados"
                          + (f"; faltam: {', '.join(sorted(faltam))}" if faltam else "")
                          + (f"; chaves que não existem: {', '.join(sorted(sobram))}" if sobram else ""))
    if regra["casamento"] not in ("horario", "horario_e_pessoas"):
        raise RegraErrada('casamento precisa ser "horario" ou "horario_e_pessoas"')
    if regra["correcao"] not in ("global", "por_reuniao"):
        raise RegraErrada('correcao precisa ser "global" ou "por_reuniao"')
    emails_agenda = {a["e"] for x in eventos for a in x["a"]}
    if not isinstance(regra["emails_confirmados"], dict):
        raise RegraErrada('emails_confirmados precisa ser um objeto {"e-mail": "Nome"}')
    emails = {}
    for email, nome in regra["emails_confirmados"].items():
        if email not in emails_agenda:
            raise RegraErrada(f'emails_confirmados: "{email}" não aparece em nenhum convite da agenda')
        if not isinstance(nome, str) or not norm(nome):
            raise RegraErrada(f'emails_confirmados: o nome de "{email}" está vazio')
        emails[email] = nome.strip()
    if not isinstance(regra["nomes_confirmados"], list):
        raise RegraErrada("nomes_confirmados precisa ser uma lista")
    por_id = {g["id"]: g for g in grav}
    confirmados = {}
    for i, item in enumerate(regra["nomes_confirmados"], 1):
        onde = f"nomes_confirmados, item {i}"
        if not (isinstance(item, list) and len(item) == 3):
            raise RegraErrada(f'{onde}: precisa ser ["reuniao-NN", "nome falado", "nome do convidado" ou null]')
        gid, falado, alvo = item
        if gid not in por_id:
            raise RegraErrada(f'{onde}: "{gid}" não é uma das gravações')
        iguais = [p for p in por_id[gid]["pessoas"] if isinstance(falado, str) and norm(p) == norm(falado)]
        if not iguais:
            raise RegraErrada(f'{onde}: "{falado}" não é um nome falado em {gid}')
        if alvo is not None and not (isinstance(alvo, str) and norm(alvo)):
            raise RegraErrada(f"{onde}: o nome do convidado precisa ser um texto ou null")
        if (gid, iguais[0]) in confirmados:
            raise RegraErrada(f'{onde}: "{iguais[0]}" em {gid} já foi confirmado em outro item')
        confirmados[(gid, iguais[0])] = alvo.strip() if alvo else None
    return {"casamento": regra["casamento"], "correcao": regra["correcao"], "emails": emails, "confirmados": confirmados}


def convidados(x, emails):
    """Nomes dos convidados de um evento, sem os que ficaram sem nome."""
    return [n for n in (nome_convidado(a, emails) for a in x["a"]) if n]


def batem(falado, nomes):
    return [n for n in nomes if casa(falado, n)]


def semelhanca_titulo(a, b):
    pa = {t for t in norm(a).split() if t not in STOP}
    pb = {t for t in norm(b).split() if t not in STOP}
    return len(pa & pb) / len(pa | pb) if pa | pb else 0.0


def ligar(g, eventos, regra):
    """O evento da gravação (seção 11.2 do case) ou None, com o motivo."""
    rs, re_ = g["s"], g["e"]
    cands = []
    for x in eventos:
        if not (x["ts"] <= re_ + 30 * MIN and x["te"] >= rs - 60 * MIN):
            continue
        ov = max(timedelta(0), min(re_, x["te"]) - max(rs, x["ts"]))
        cov_rec, cov_ev = ov / (re_ - rs), ov / (x["te"] - x["ts"])
        depois_fim = rs - x["te"]
        antes_inicio = x["ts"] - re_
        if regra["casamento"] == "horario":
            # Versão antiga do case: sobreposição de 30% da gravação ou até 15 min de atraso.
            hits = 0
            ok = cov_rec >= 0.3 or timedelta(0) <= depois_fim <= 15 * MIN
        else:
            nomes = convidados(x, regra["emails"])
            hits = sum(1 for p in g["pessoas"] if batem(p, nomes))
            ok = cov_rec >= 0.3 or cov_ev >= 0.5
            if not ok and hits:
                ok = (ov >= 5 * MIN or timedelta(0) <= depois_fim <= 60 * MIN
                      or timedelta(0) <= antes_inicio <= 30 * MIN)
            if not ok and not hits and timedelta(0) <= depois_fim <= 15 * MIN:
                ok = True
        if ok:
            tempo = ov / max(re_ - rs, x["te"] - x["ts"])
            cands.append({"ev": x, "tempo": tempo, "hits": hits, "ts": semelhanca_titulo(g["titulo"], x["t"]),
                          "atraso_min": int(depois_fim / MIN) if depois_fim > timedelta(0) else 0})
    if not cands:
        return None, {"candidatos": 0}
    alguem = any(c["hits"] for c in cands)
    for c in cands:
        if regra["casamento"] == "horario":
            c["nota"] = c["tempo"]
        else:
            citados = len(g["pessoas"]) or 1
            c["nota"] = (c["tempo"] * (0.6 if alguem and not c["hits"] else 1)
                         + 0.8 * c["hits"] / citados + (0.1 if c["hits"] else 0) + 0.5 * c["ts"])
    melhor = max(cands, key=lambda c: c["nota"])  # empate: o primeiro da agenda
    mesmo_horario = [c["ev"]["id"] for c in cands if c["ev"]["ts"] == melhor["ev"]["ts"] and c["ev"]["te"] == melhor["ev"]["te"]]
    return melhor["ev"], {"candidatos": len(cands), "hits": melhor["hits"], "atraso_min": melhor["atraso_min"],
                          "mesmo_horario": mesmo_horario, "nota": round(melhor["nota"], 2)}


def parecidos(falado, nomes):
    """Convidados com o mesmo primeiro ou último nome do falado: ajuda para quem confirma."""
    f = toks(falado)
    return [n for n in nomes if toks(n) and (toks(n)[0] == f[0] or toks(n)[-1] == f[-1])]


def separados(a, b, separar):
    return any({norm(a), norm(b)} == {norm(x), norm(y)} for x, y in separar)


def auditar(grav, eventos, separar, regra):
    """Roda a ligação e a correção em todas as gravações, sem gravar nada, e junta os achados."""
    lig = {}
    for g in grav:
        ev, info = ligar(g, eventos, regra)
        lig[g["id"]] = (ev, info)
    # Correção de cada nome falado, reunião por reunião.
    local = {}
    for g in sorted(grav, key=lambda g: g["s"]):
        ev = lig[g["id"]][0]
        nomes = convidados(ev, regra["emails"]) if ev else []
        for p in g["pessoas"]:
            if (g["id"], p) in regra["confirmados"]:
                local[(g["id"], p)] = ("confirmado", [regra["confirmados"][(g["id"], p)]], nomes)
            else:
                local[(g["id"], p)] = ("regra", batem(p, nomes), nomes)
    correcoes, pendentes, sem_correcao = [], [], []
    mapa_global = {}
    if regra["correcao"] == "global":
        # Versão testada só com dados simulados: a primeira correção de um nome vale no grafo inteiro.
        for g in sorted(grav, key=lambda g: g["s"]):
            for p in g["pessoas"]:
                origem, alvos, _ = local[(g["id"], p)]
                if len(alvos) == 1 and alvos[0] and chave(p) not in mapa_global:
                    mapa_global[chave(p)] = (alvos[0], g["id"])
    for g in sorted(grav, key=lambda g: g["s"]):
        ev = lig[g["id"]][0]
        for p in g["pessoas"]:
            origem, alvos, nomes = local[(g["id"], p)]
            alvo, de_onde = None, origem
            if origem == "confirmado":
                alvo = alvos[0]
                if alvo is None:
                    sem_correcao.append({"g": g["id"], "falado": p})
                    continue
            elif regra["correcao"] == "global" and chave(p) in mapa_global:
                alvo, primeira = mapa_global[chave(p)]
                de_onde = "global" if primeira != g["id"] else "regra"
            elif len(alvos) == 1:
                alvo = alvos[0]
            if alvo is None:
                if not ev:
                    continue
                motivo = (f"bate com {len(alvos)} convidados" if len(alvos) > 1
                          else "nenhum convidado bate pela regra")
                pendentes.append({"g": g["id"], "falado": p, "motivo": motivo,
                                  "parecidos": alvos if len(alvos) > 1 else parecidos(p, nomes)})
                continue
            correcoes.append({"g": g["id"], "falado": p, "alvo": alvo, "origem": de_onde,
                              "entre_dois": origem == "regra" and len(alvos) > 1,
                              "no_convite": alvo in nomes, "tem_evento": bool(ev), "contra_nao_unir": separados(p, alvo, separar),
                              "mudou": norm(p) != norm(alvo)})
    # Um mesmo nome falado que vira pessoas diferentes em reuniões diferentes.
    por_chave = {}
    for c in correcoes:
        por_chave.setdefault(c["falado"], {}).setdefault(c["alvo"], []).append(c["g"])
    for p in pendentes:
        if len(p["parecidos"]) > 1 and p["motivo"].startswith("bate"):
            por_chave.setdefault(p["falado"], {}).setdefault("?", []).append(p["g"])
    varias = {k: v for k, v in por_chave.items() if len(v) > 1}
    # E-mails sem nome: palpite pelos nomes falados que nenhum convidado com nome explica.
    palpites = []
    for email in sorted({a["e"] for x in eventos for a in x["a"]}):
        exemplo = next(a for x in eventos for a in x["a"] if a["e"] == email)
        if nome_convidado(exemplo, regra["emails"]):
            continue
        presencas = sum(1 for x in eventos if any(a["e"] == email for a in x["a"]))
        ligadas = [g for g in grav if lig[g["id"]][0] and any(a["e"] == email for a in lig[g["id"]][0]["a"])]
        sobras = {}
        for g in ligadas:
            nomes = convidados(lig[g["id"]][0], regra["emails"])
            for p in g["pessoas"]:
                if (g["id"], p) in regra["confirmados"] or batem(p, nomes) or parecidos(p, nomes):
                    continue
                sobras.setdefault(toks(p)[0], []).append((g["id"], p))
        if sobras:
            melhor = max(sobras.values(), key=len)
            nome = max((p for _, p in melhor), key=len)
            palpites.append({"email": email, "presencas": presencas, "nome": nome,
                             "em": sorted({gid for gid, _ in melhor}), "de": len(ligadas)})
        else:
            palpites.append({"email": email, "presencas": presencas, "nome": "", "em": [], "de": len(ligadas)})
    # Gravações ligadas a um evento em que ninguém citado está no convite: talvez o evento errado.
    talvez = []
    for g in grav:
        ev = lig[g["id"]][0]
        if ev and g["pessoas"] and not any(batem(p, convidados(ev, regra["emails"])) for p in g["pessoas"]):
            talvez.append(g["id"])
    return {"lig": lig, "correcoes": correcoes, "pendentes": pendentes, "sem_correcao": sem_correcao,
            "varias": varias, "palpites": palpites, "talvez": talvez}


def resumo(res):
    """Os números da tabela antes e depois."""
    c = res["correcoes"]
    return {
        "ligadas": sum(1 for ev, _ in res["lig"].values() if ev),
        "corrigidas": sum(1 for x in c if x["mudou"]),
        "fora": sum(1 for x in c if x["mudou"] and not x["no_convite"]),
        "contra": sum(1 for x in c if x["contra_nao_unir"]),
        "entre_dois": sum(1 for x in c if x["entre_dois"]),
        "pendentes": len(res["pendentes"]) + sum(1 for p in res["palpites"] if p["nome"]),
    }


def bloqueios(res):
    """O que impede gravar: correção para quem não estava no convite, escolhida entre dois convidados
    sem confirmação ou contra um "não unir". O que é duvidoso fica de fora e vai para a lista."""
    saida = []
    for x in res["correcoes"]:
        if x["entre_dois"]:
            saida.append(f'{x["g"]}: {x["falado"]} -> {x["alvo"]}, escolhido entre dois convidados que batem')
        if x["mudou"] and not x["no_convite"]:
            onde = "que não está no convite dessa reunião" if x["tem_evento"] else "e essa gravação não tem evento"
            saida.append(f'{x["g"]}: {x["falado"]} -> {x["alvo"]}, {onde}')
        if x["contra_nao_unir"]:
            saida.append(f'{x["g"]}: {x["falado"]} -> {x["alvo"]} junta um par de "não unir"')
    return saida
