"""O resolvedor de nomes em camadas, do jeito do case, em Python. Só biblioteca padrão.

As funções norm, fon e as siglas seguem os trechos do case (codigo-do-case.md).
resolver.py e medir.py usam esse arquivo.
"""
import json
import re
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
TIPOS = {"pessoa": "pessoas", "projeto": "projetos", "empresa": "empresas", "tema": "temas"}
CAMADAS = ["normalizacao", "fonetica", "siglas", "manual", "nao_unir"]
NOME_CAMADA = {"nenhuma": "sem resolvedor", "normalizacao": "normalização", "fonetica": "+ chave fonética",
               "siglas": "+ siglas", "manual": "+ união manual", "nao_unir": "+ não unir"}
STOP = set("de da do das dos e a o as os em no na nos nas para por com the of and".split())
CORP = set("s sa ltda me eireli inc llc corp co grupo group holding".split())
# Dicionário base do case (a parte que o case mostra).
SIGLAS_BASE = [
    ["inteligencia artificial", "ia"], ["artificial intelligence", "ia"], ["ai", "ia"],
    ["genai", "ia generativa"], ["machine learning", "ml"], ["aprendizado de maquina", "ml"],
    ["large language model", "llm"], ["modelos de linguagem", "llm"],
    ["recursos humanos", "rh"], ["business intelligence", "bi"],
    ["prova de conceito", "poc"], ["produto minimo viavel", "mvp"],
    ["lei geral de protecao de dados", "lgpd"], ["key performance indicators", "kpi"],
    ["processamento de linguagem natural", "nlp"], ["pln", "nlp"],
]
LIMIAR = 0.88
CHAVES_CONFIG = {"auto", "siglas", "pares", "nao_unir"}


class ConfigErrada(Exception):
    pass


def norm(texto):
    s = unicodedata.normalize("NFD", str(texto or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def palavras(texto, tipo):
    """Normaliza, tira as palavras pequenas do meio do nome e, em empresa, o sufixo societário.

    O case lista STOP e CORP junto da normalização sem mostrar onde usa. Aqui a palavra pequena
    só sai entre duas outras ("painel do estoque"), para "Fornecedor A" não virar "Fornecedor".
    """
    s = norm(texto)
    if tipo == "empresa":
        s = re.sub(r"(?<!\S)s a(?!\S)", "sa", s)
        s = " ".join(t for t in s.split() if t not in CORP)
    ps = s.split()
    return [t for i, t in enumerate(ps) if not (t in STOP and 0 < i < len(ps) - 1)]


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


def trocar_siglas(texto, siglas):
    """Troca cada expressão pela sigla, palavra inteira, da mais longa para a mais curta."""
    for expr, sig in sorted(siglas, key=lambda p: -len(p[0])):
        texto = re.sub(r"(?<!\S)" + re.escape(expr) + r"(?!\S)", sig, texto)
    return texto


def siglas_aprendidas(nomes_por_tipo):
    """Rótulo todo em maiúsculas + expressão de 2 a 6 palavras do mesmo tipo com essas iniciais."""
    achadas = {}
    for tipo, nomes in nomes_por_tipo.items():
        lista = []
        for rotulo in nomes:
            if not re.fullmatch(r"[A-Z]{2,6}", rotulo.strip()):
                continue
            sig = rotulo.strip().lower()
            for outro in nomes:
                ps = palavras(outro, tipo)
                if 2 <= len(ps) <= 6 and "".join(p[0] for p in ps) == sig:
                    lista.append([" ".join(ps), sig])
        achadas[tipo] = lista
    return achadas


def chave(texto, tipo, camada_ate, siglas):
    """A chave de um nome até a camada pedida. Comparada sem espaços, como no case."""
    ps = palavras(texto, tipo)
    if CAMADAS.index(camada_ate) >= CAMADAS.index("siglas"):
        ps = trocar_siglas(" ".join(ps), siglas).split()
    if CAMADAS.index(camada_ate) >= CAMADAS.index("fonetica"):
        ps = [fon(p, tipo != "pessoa") for p in ps]
    return " ".join(ps)


def ler_json(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def ler_nomes(caminho=PASTA / "nomes-do-grafo.json"):
    """Devolve {tipo: {nome: [reuniões]}} na ordem em que os nomes aparecem."""
    dados = ler_json(caminho)
    nomes = {t: {} for t in TIPOS}
    for rid, ent in dados.items():
        if rid.startswith("_"):
            continue
        for tipo, campo in TIPOS.items():
            for nome in ent.get(campo, []):
                nomes[tipo].setdefault(nome, []).append(rid)
    return nomes


def _achar(ref, nomes, onde):
    if not isinstance(ref, str) or ":" not in ref:
        raise ConfigErrada(f'{onde}: "{ref}" precisa estar no formato "tipo:Nome"')
    tipo, nome = ref.split(":", 1)
    tipo = tipo.strip()
    if tipo not in TIPOS:
        raise ConfigErrada(f'{onde}: tipo "{tipo}" não existe (use pessoa, projeto, empresa ou tema)')
    iguais = [n for n in nomes[tipo] if norm(n) == norm(nome)]
    if not iguais:
        raise ConfigErrada(f'{onde}: "{nome}" não está entre os nomes de {TIPOS[tipo]} do grafo')
    return tipo, iguais[0]


def ler_config(caminho, nomes):
    try:
        cfg = ler_json(caminho)
    except FileNotFoundError:
        raise ConfigErrada(f"não achei o arquivo {caminho}")
    except json.JSONDecodeError as e:
        raise ConfigErrada(f"{caminho} não é JSON válido (linha {e.lineno}, coluna {e.colno}: {e.msg})")
    if not isinstance(cfg, dict):
        raise ConfigErrada("a configuração precisa ser um objeto JSON")
    chaves = {k for k in cfg if not k.startswith("_")}
    if chaves != CHAVES_CONFIG:
        faltam, sobram = CHAVES_CONFIG - chaves, chaves - CHAVES_CONFIG
        raise ConfigErrada("a configuração precisa ter auto, siglas, pares e nao_unir"
                           + (f"; faltam: {', '.join(sorted(faltam))}" if faltam else "")
                           + (f"; chaves que não existem: {', '.join(sorted(sobram))}" if sobram else ""))
    if not isinstance(cfg["auto"], bool):
        raise ConfigErrada("auto precisa ser true ou false")
    siglas = []
    for i, s in enumerate(cfg["siglas"] if isinstance(cfg["siglas"], list) else [None], 1):
        if not (isinstance(s, list) and len(s) == 2 and all(isinstance(x, str) and norm(x) for x in s)):
            raise ConfigErrada(f"siglas, item {i}: precisa ser [expressão, sigla], dois textos não vazios")
        siglas.append([norm(s[0]), norm(s[1])])
    saida = {"auto": cfg["auto"], "siglas": siglas}
    for campo in ("pares", "nao_unir"):
        lista = cfg[campo] if isinstance(cfg[campo], list) else [None]
        pares = []
        for i, par in enumerate(lista, 1):
            onde = f"{campo}, item {i}"
            if not (isinstance(par, list) and len(par) == 2):
                raise ConfigErrada(f"{onde}: precisa ser uma lista com dois nomes")
            (ta, a), (tb, b) = _achar(par[0], nomes, onde), _achar(par[1], nomes, onde)
            if ta != tb:
                raise ConfigErrada(f"{onde}: {ta} e {tb} são tipos diferentes e nunca viram o mesmo nó")
            if a == b:
                raise ConfigErrada(f'{onde}: o par repete o mesmo nome, "{a}"')
            pares.append((ta, a, b))
        saida[campo] = pares
    return saida


class Grupos:
    """Union-find que recusa juntar dois grupos quando um par marcado como "não unir" ficaria junto."""

    def __init__(self, itens, separar):
        self.pai = {x: x for x in itens}
        self.separar = separar
        self.recusadas = []

    def raiz(self, x):
        while self.pai[x] != x:
            self.pai[x] = self.pai[self.pai[x]]
            x = self.pai[x]
        return x

    def membros(self, r):
        return {x for x in self.pai if self.raiz(x) == r}

    def unir(self, a, b, origem):
        ra, rb = self.raiz(a), self.raiz(b)
        if ra == rb:
            return True
        ga, gb = self.membros(ra), self.membros(rb)
        for x, y in self.separar:
            if (x in ga and y in gb) or (x in gb and y in ga):
                recusa = {"a": a, "b": b, "origem": origem, "par": (x, y)}
                if recusa not in self.recusadas:
                    self.recusadas.append(recusa)
                return False
        self.pai[rb] = ra
        return True


def resolver(nomes, cfg, ate="nao_unir"):
    """Agrupa os nomes de cada tipo até a camada pedida. Devolve {tipo: lista de nós} e as uniões recusadas."""
    nivel = CAMADAS.index(ate) if ate in CAMADAS else -1
    todas = {t: list(n) for t, n in nomes.items()}
    aprendidas = siglas_aprendidas(todas)
    nos, recusadas = {}, []
    for tipo, lista in todas.items():
        separar = [(a, b) for t, a, b in cfg["nao_unir"] if t == tipo] if nivel >= CAMADAS.index("nao_unir") else []
        g = Grupos(lista, separar)
        if nivel >= CAMADAS.index("manual"):
            for t, a, b in cfg["pares"]:
                if t == tipo:
                    g.unir(a, b, "manual")
        if nivel >= 0:
            # A normalização é a chave de todo nome. auto=false desliga só a fonética e as siglas.
            # Cada camada automática só junta: os nomes com a mesma chave em qualquer camada até a pedida
            # ficam no mesmo nó. Quem separa é o "não unir".
            ultima = min(nivel, CAMADAS.index("siglas")) if cfg["auto"] else 0
            siglas = SIGLAS_BASE + aprendidas[tipo] + cfg["siglas"]
            for camada in CAMADAS[:ultima + 1]:
                por_chave = {}
                for nome in lista:
                    por_chave.setdefault(chave(nome, tipo, camada, siglas).replace(" ", ""), []).append(nome)
                for ids in por_chave.values():
                    for outro in ids[1:]:
                        g.unir(ids[0], outro, "automática")
        grupos = {}
        for nome in lista:
            grupos.setdefault(g.raiz(nome), []).append(nome)
        nos[tipo] = [{"rotulo": representante(m, nomes[tipo]), "membros": m} for m in grupos.values()]
        recusadas += [dict(r, tipo=tipo) for r in g.recusadas]
    return nos, recusadas


def representante(membros, reunioes):
    """O nome mais frequente; empate, o mais longo. No case, o nome do convite da agenda vinha antes."""
    return sorted(membros, key=lambda n: (-len(reunioes[n]), -len(n), n))[0]


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


def sugestoes(nomes, cfg, nos, limite=200):
    """Pares de nós diferentes com chave parecida, para unir ou marcar "não unir"."""
    todas = {t: list(n) for t, n in nomes.items()}
    aprendidas = siglas_aprendidas(todas)
    separados = {frozenset((a, b)) for _, a, b in cfg["nao_unir"]}
    saida = []
    for tipo, lista_nos in nos.items():
        siglas = SIGLAS_BASE + aprendidas[tipo] + cfg["siglas"]
        no_de = {m: i for i, no in enumerate(lista_nos) for m in no["membros"]}
        melhores = {}
        for i, a in enumerate(todas[tipo]):
            for b in todas[tipo][i + 1:]:
                na, nb = no_de[a], no_de[b]
                if na == nb or frozenset((a, b)) in separados:
                    continue
                ka, kb = chave(a, tipo, "siglas", siglas), chave(b, tipo, "siglas", siglas)
                nota = 0.0
                if len(ka) >= 4 and len(kb) >= 4 and min(len(ka), len(kb)) / max(len(ka), len(kb)) >= 0.5:
                    nota = jaro_winkler(ka, kb)
                if tipo == "pessoa":
                    for curto, longo in ((ka, kb), (kb, ka)):
                        partes = longo.split()
                        if " " not in curto and len(curto) >= 4 and len(partes) > 1 and curto in (partes[0], partes[-1]):
                            nota = max(nota, 0.8)
                if nota >= LIMIAR or (tipo == "pessoa" and nota == 0.8):
                    par = tuple(sorted((na, nb)))
                    if nota > melhores.get(par, (0,))[0]:
                        melhores[par] = (nota, a, b)
        for (na, nb), (nota, a, b) in melhores.items():
            freq = len(nomes[tipo][a]) + len(nomes[tipo][b])
            saida.append({"tipo": tipo, "nota": nota, "a": a, "b": b, "freq": freq,
                          "no_a": lista_nos[na]["rotulo"], "no_b": lista_nos[nb]["rotulo"]})
    saida.sort(key=lambda s: (-s["nota"], -s["freq"], s["tipo"], s["a"]))
    return saida[:limite]


def ler_gabarito(caminho, nomes):
    """Devolve {tipo: {nome: nó do gabarito}} e confere se o gabarito cobre todos os nomes uma vez."""
    gab = ler_json(caminho)
    saida = {}
    for tipo, campo in TIPOS.items():
        mapa = {}
        for no, membros in gab[campo].items():
            for m in membros:
                if m in mapa:
                    raise ConfigErrada(f'gabarito: "{m}" aparece em dois nós')
                mapa[m] = no
        if set(mapa) != set(nomes[tipo]):
            raise ConfigErrada(f"gabarito de {campo} não cobre os mesmos nomes do grafo")
        saida[tipo] = mapa
    return saida


def medir(nos, gab):
    """Compara pares de nomes: unidos certos, unidos errados e os que faltou unir."""
    certas, erradas, faltou = [], [], []
    for tipo, lista in nos.items():
        no_de = {m: i for i, no in enumerate(lista) for m in no["membros"]}
        nomes = list(no_de)
        for i, a in enumerate(nomes):
            for b in nomes[i + 1:]:
                junto, igual = no_de[a] == no_de[b], gab[tipo][a] == gab[tipo][b]
                if junto and igual:
                    certas.append((tipo, a, b))
                elif junto:
                    erradas.append((tipo, a, b))
                elif igual:
                    faltou.append((tipo, a, b))
    total_nos = sum(len(l) for l in nos.values())
    total_gab = sum(len(set(m.values())) for m in gab.values())
    return {"nos": total_nos, "nos_gabarito": total_gab, "certas": certas, "erradas": erradas, "faltou": faltou}
