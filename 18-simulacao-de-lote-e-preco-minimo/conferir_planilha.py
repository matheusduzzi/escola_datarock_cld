"""Confere uma planilha calculadora antes de usar.

Lê as fórmulas gravadas no .xlsx, segue tudo de que a célula da renda depende e recalcula
com o preço que você pedir. Mostra:
  - se as regras moram numa aba própria e se a renda é fórmula, não número digitado;
  - se a busca por faixa usa MATCH (CORRESP) e se cada linha de taxa passa por ROUND (ARRED);
  - a renda recalculada em cada teste, ao centavo;
  - o valor que a própria planilha gravou na última vez em que foi calculada.

Uso:
    python3 conferir_planilha.py planilha_calculadora.xlsx
    python3 conferir_planilha.py minha.xlsx --preco Calculadora!B6 --renda Calculadora!B17 \\
        --regras Taxas --teste 10.90=4.00 --teste 79.99=57.89

Sai com código 0 quando nada deu ERRO e 1 quando algum teste falhou. Só usa a biblioteca padrão.
"""
import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP, ROUND_DOWN

# ======================= leitura do .xlsx =======================


def _sem_ns(tag):
    return tag.rsplit("}", 1)[-1]


def _filhos(no, nome):
    return [f for f in no if _sem_ns(f.tag) == nome]


def _filho(no, nome):
    achados = _filhos(no, nome)
    return achados[0] if achados else None


def col_num(letras):
    n = 0
    for ch in letras.upper():
        n = n * 26 + ord(ch) - 64
    return n


def col_letras(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


REF = re.compile(r"^\$?([A-Za-z]{1,3})\$?(\d+)$")


def separa(endereco):
    m = REF.match(endereco)
    if not m:
        raise ValueError("endereço inválido: " + endereco)
    return col_num(m.group(1)), int(m.group(2))


class Planilha:
    def __init__(self, caminho):
        self.formulas, self.valores, self.gravados, self.nomes_def = {}, {}, {}, {}
        with zipfile.ZipFile(caminho) as z:
            arquivos = set(z.namelist())
            wb = ET.fromstring(z.read("xl/workbook.xml"))
            rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            alvo = {r.get("Id"): r.get("Target") for r in rels}
            textos = []
            if "xl/sharedStrings.xml" in arquivos:
                for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
                    textos.append("".join(t.text or "" for t in si.iter() if _sem_ns(t.tag) == "t"))
            self.abas = []
            for folha in _filho(wb, "sheets"):
                nome = folha.get("name")
                rid = next(v for k, v in folha.attrib.items() if k.endswith("}id"))
                caminho_aba = alvo[rid].lstrip("/")
                if not caminho_aba.startswith("xl/"):
                    caminho_aba = "xl/" + caminho_aba
                self.abas.append(nome)
                self._ler_aba(nome, ET.fromstring(z.read(caminho_aba)), textos)
            nomes = _filho(wb, "definedNames")
            for d in (nomes if nomes is not None else []):
                if d.get("localSheetId") is None:
                    self.nomes_def[d.get("name").upper()] = d.text or ""

    def _ler_aba(self, nome, raiz, textos):
        compartilhadas = {}
        dados = _filho(raiz, "sheetData")
        for linha in (dados if dados is not None else []):
            for c in _filhos(linha, "c"):
                end = c.get("r").upper()
                chave = (nome, end)
                tipo = c.get("t", "n")
                f, v = _filho(c, "f"), _filho(c, "v")
                if f is not None:
                    texto = f.text or ""
                    if f.get("t") == "shared":
                        si = f.get("si")
                        if texto:
                            compartilhadas[si] = (end, texto)
                        else:
                            origem, base = compartilhadas[si]
                            texto = desloca(base, origem, end)
                    self.formulas[chave] = texto
                valor = None
                if tipo == "inlineStr":
                    is_ = _filho(c, "is")
                    valor = "".join(t.text or "" for t in is_.iter() if _sem_ns(t.tag) == "t") if is_ is not None else ""
                elif v is not None and v.text is not None:
                    if tipo == "s":
                        valor = textos[int(v.text)]
                    elif tipo == "b":
                        valor = v.text == "1"
                    elif tipo in ("str", "e"):
                        valor = v.text
                    else:
                        valor = float(v.text)
                if f is not None:
                    self.gravados[chave] = valor
                elif valor is not None:
                    self.valores[chave] = valor

    def aba_real(self, nome):
        for a in self.abas:
            if a.lower() == nome.lower():
                return a
        raise KeyError("a planilha não tem a aba «%s» (abas: %s)" % (nome, ", ".join(self.abas)))


# ======================= fórmulas =======================

TOKEN = re.compile(r"""
    (?P<espaco>\s+)
  | (?P<texto>"(?:[^"]|"")*")
  | (?P<erro>\#(?:N/A|DIV/0!|VALUE!|REF!|NAME\?|NUM!|NULL!))
  | (?P<ref>(?:(?:'(?:[^']|'')+'|[A-Za-z_À-ſ][\w.À-ſ]*)!)?\$?[A-Za-z]{1,3}\$?\d+(?::\$?[A-Za-z]{1,3}\$?\d+)?)(?![\w(])
  | (?P<numero>\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)
  | (?P<funcao>[A-Za-z_][\w.]*)\s*\(
  | (?P<nome>[A-Za-z_\\][\w.]*)
  | (?P<op><>|<=|>=|[-+*/^&=<>%])
  | (?P<abre>\()
  | (?P<fecha>\))
  | (?P<virgula>[,;])
""", re.X)


def tokens(formula):
    pos, saida = 0, []
    while pos < len(formula):
        m = TOKEN.match(formula, pos)
        if not m:
            raise ValueError("não entendi a fórmula a partir de: " + formula[pos:])
        tipo = m.lastgroup
        if tipo != "espaco":
            valor = m.group("funcao") if tipo == "funcao" else m.group(tipo)
            saida.append((tipo, valor, m.start(), m.end()))
        pos = m.end()
    return saida


def desloca(formula, origem, destino):
    """Fórmula compartilhada: desloca as referências relativas da célula de origem para a de destino."""
    (c0, l0), (c1, l1) = separa(origem), separa(destino)
    dc, dl = c1 - c0, l1 - l0
    partes, pos = [], 0
    for tipo, valor, ini, fim in tokens(formula):
        if tipo != "ref":
            continue
        partes.append(formula[pos:ini])
        aba, _, intervalo = valor.rpartition("!")
        novos = []
        for ponto in intervalo.split(":"):
            m = re.match(r"(\$?)([A-Za-z]{1,3})(\$?)(\d+)$", ponto)
            col = m.group(2) if m.group(1) else col_letras(col_num(m.group(2)) + dc)
            lin = m.group(4) if m.group(3) else str(int(m.group(4)) + dl)
            novos.append(m.group(1) + col + m.group(3) + lin)
        partes.append((aba + "!" if aba else "") + ":".join(novos))
        pos = fim
    partes.append(formula[pos:])
    return "".join(partes)


class ErroPlanilha(Exception):
    """Valor de erro de planilha (#N/A, #DIV/0!...)."""


class NaoSuportado(Exception):
    pass


class Intervalo:
    def __init__(self, aba, c1, l1, c2, l2):
        self.aba, self.c1, self.l1, self.c2, self.l2 = aba, min(c1, c2), min(l1, l2), max(c1, c2), max(l1, l2)

    def celulas(self):
        return [[(self.aba, col_letras(c) + str(l)) for c in range(self.c1, self.c2 + 1)]
                for l in range(self.l1, self.l2 + 1)]


def _num(v):
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if v is None or v == "":
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        raise ErroPlanilha("#VALUE!")


def arred(x, casas, modo=ROUND_HALF_UP):
    # A planilha guarda 15 algarismos significativos; arredonda a metade para longe do zero.
    d = Decimal(format(_num(x), ".15g"))
    return float(d.quantize(Decimal(1).scaleb(-int(_num(casas))), rounding=modo))


class Calculo:
    def __init__(self, planilha, entradas=None):
        self.p, self.entradas, self.memo, self.pilha = planilha, dict(entradas or {}), {}, set()
        self.usadas = set()  # células com fórmula que entraram no cálculo
        self.lidas = set()  # todas as células lidas

    def valor(self, chave):
        self.lidas.add(chave)
        if chave in self.entradas:
            return self.entradas[chave]
        if chave in self.memo:
            return self.memo[chave]
        if chave not in self.p.formulas:
            return self.p.valores.get(chave)
        if chave in self.pilha:
            raise ErroPlanilha("referência circular em %s!%s" % chave)
        self.pilha.add(chave)
        self.usadas.add(chave)
        try:
            r = Expressao(self, chave[0], self.p.formulas[chave]).resolver()
            if isinstance(r, Intervalo):
                r = self.valor(r.celulas()[0][0])
        except ErroPlanilha as e:
            r = e
        self.pilha.discard(chave)
        self.memo[chave] = r
        return r


class Expressao:
    def __init__(self, calc, aba, formula):
        self.calc, self.aba, self.t, self.i = calc, aba, tokens(formula.lstrip("=")), 0

    def resolver(self):
        v = self.comparacao()
        if self.i != len(self.t):
            raise ValueError("sobrou texto na fórmula: " + str(self.t[self.i:]))
        if isinstance(v, ErroPlanilha):
            raise v
        return v

    def _ve(self, tipo, valor=None):
        if self.i < len(self.t) and self.t[self.i][0] == tipo and (valor is None or self.t[self.i][1] in valor):
            self.i += 1
            return self.t[self.i - 1][1]
        return None

    def _escalar(self, v):
        if isinstance(v, Intervalo):
            cel = v.celulas()
            if len(cel) == 1 and len(cel[0]) == 1:
                v = self.calc.valor(cel[0][0])
            else:
                raise ErroPlanilha("#VALUE!")
        if isinstance(v, ErroPlanilha):
            raise v
        return v

    def comparacao(self):
        a = self.concat()
        while True:
            op = self._ve("op", ("=", "<>", "<", ">", "<=", ">="))
            if not op:
                return a
            b = self.concat()
            x, y = self._escalar(a), self._escalar(b)
            if isinstance(x, str) or isinstance(y, str):
                x, y = str(x if x is not None else "").lower(), str(y if y is not None else "").lower()
            else:
                x, y = _num(x), _num(y)
            a = {"=": x == y, "<>": x != y, "<": x < y, ">": x > y, "<=": x <= y, ">=": x >= y}[op]

    def concat(self):
        a = self.soma()
        while self._ve("op", ("&",)):
            b = self.soma()
            a = str(self._escalar(a) or "") + str(self._escalar(b) or "")
        return a

    def soma(self):
        a = self.produto()
        while True:
            op = self._ve("op", ("+", "-"))
            if not op:
                return a
            b = self.produto()
            a = _num(self._escalar(a)) + (_num(self._escalar(b)) if op == "+" else -_num(self._escalar(b)))

    def produto(self):
        a = self.potencia()
        while True:
            op = self._ve("op", ("*", "/"))
            if not op:
                return a
            b = self.potencia()
            x, y = _num(self._escalar(a)), _num(self._escalar(b))
            if op == "/" and y == 0:
                raise ErroPlanilha("#DIV/0!")
            a = x * y if op == "*" else x / y

    def potencia(self):
        a = self.unario()
        while self._ve("op", ("^",)):
            b = self.unario()
            a = _num(self._escalar(a)) ** _num(self._escalar(b))
        return a

    def unario(self):
        if self._ve("op", ("-",)):
            return -_num(self._escalar(self.unario()))
        if self._ve("op", ("+",)):
            return self.unario()
        v = self.primario()
        while self._ve("op", ("%",)):
            v = _num(self._escalar(v)) / 100
        return v

    def primario(self):
        if self.i >= len(self.t):
            raise ValueError("fórmula terminou antes da hora")
        tipo, valor = self.t[self.i][0], self.t[self.i][1]
        self.i += 1
        if tipo == "numero":
            return float(valor)
        if tipo == "texto":
            return valor[1:-1].replace('""', '"')
        if tipo == "erro":
            return ErroPlanilha(valor)
        if tipo == "abre":
            v = self.comparacao()
            if not self._ve("fecha"):
                raise ValueError("faltou fechar parêntese")
            return v
        if tipo == "ref":
            return self.referencia(valor)
        if tipo == "nome":
            if valor.upper() in ("TRUE", "FALSE"):
                return valor.upper() == "TRUE"
            definicao = self.calc.p.nomes_def.get(valor.upper())
            if definicao is None:
                raise ErroPlanilha("#NAME?")
            return Expressao(self.calc, self.aba, definicao).comparacao()
        if tipo == "funcao":
            return self.funcao(valor)
        raise ValueError("não esperava %s na fórmula" % valor)

    def referencia(self, texto):
        aba, _, intervalo = texto.rpartition("!")
        aba = aba.strip("'").replace("''", "'") if aba else self.aba
        aba = self.calc.p.aba_real(aba)
        pontos = [separa(x) for x in intervalo.split(":")]
        (c1, l1), (c2, l2) = pontos[0], pontos[-1]
        return Intervalo(aba, c1, l1, c2, l2)

    def _argumentos(self):
        args = []
        if self._ve("fecha"):
            return args
        while True:
            if self.i < len(self.t) and self.t[self.i][0] in ("virgula", "fecha"):
                args.append(None)  # argumento vazio
            else:
                args.append(self.comparacao())
            if self._ve("fecha"):
                return args
            if not self._ve("virgula"):
                raise ValueError("esperava vírgula ou parêntese")

    def _lista(self, args):
        saida = []
        for a in args:
            if isinstance(a, Intervalo):
                for linha in a.celulas():
                    for ch in linha:
                        v = self.calc.valor(ch)
                        if isinstance(v, ErroPlanilha):
                            raise v
                        if isinstance(v, (int, float)) and not isinstance(v, bool):
                            saida.append(float(v))
            else:
                saida.append(_num(self._escalar(a)))
        return saida

    def _vetor(self, intervalo):
        return [self.calc.valor(ch) for linha in intervalo.celulas() for ch in linha]

    def funcao(self, nome):
        nome = nome.upper()
        for prefixo in ("_XLFN._XLWS.", "_XLFN.", "_XLWS."):
            if nome.startswith(prefixo):
                nome = nome[len(prefixo):]
        if nome in ("IF", "IFERROR"):
            return self._se(nome)
        args = self._argumentos()
        e = self._escalar
        if nome == "SUM":
            return sum(self._lista(args))
        if nome in ("MIN", "MAX"):
            valores = self._lista(args)
            return (min if nome == "MIN" else max)(valores) if valores else 0.0
        if nome == "ROUND":
            return arred(e(args[0]), e(args[1]))
        if nome in ("ROUNDUP", "ROUNDDOWN"):
            return arred(e(args[0]), e(args[1]), ROUND_UP if nome == "ROUNDUP" else ROUND_DOWN)
        if nome == "INT":
            import math
            return float(math.floor(_num(e(args[0]))))
        if nome == "ABS":
            return abs(_num(e(args[0])))
        if nome in ("AND", "OR"):
            vals = [bool(x) for x in self._lista(args)]
            return all(vals) if nome == "AND" else any(vals)
        if nome == "NOT":
            return not bool(_num(e(args[0])))
        if nome == "MATCH":
            return self._match(e(args[0]), args[1], 1 if len(args) < 3 or args[2] is None else int(_num(e(args[2]))))
        if nome == "INDEX":
            return self._index(args)
        if nome == "VLOOKUP":
            return self._vlookup(args)
        if nome == "XLOOKUP":
            return self._xlookup(args)
        raise NaoSuportado(nome)

    def _se(self, nome):
        # IF e IFERROR só calculam o ramo usado, como a planilha.
        inicio = self.i
        args_txt, nivel, atual = [], 0, inicio
        while True:
            tipo = self.t[self.i][0]
            if tipo in ("abre", "funcao"):
                nivel += 1
            elif tipo == "fecha":
                if nivel == 0:
                    args_txt.append((atual, self.i))
                    self.i += 1
                    break
                nivel -= 1
            elif tipo == "virgula" and nivel == 0:
                args_txt.append((atual, self.i))
                atual = self.i + 1
            self.i += 1
        fim = self.i

        def calcula(k):
            if k >= len(args_txt) or args_txt[k][0] == args_txt[k][1]:
                return False if nome == "IF" and k == 2 else 0.0
            sub = Expressao.__new__(Expressao)
            sub.calc, sub.aba, sub.t, sub.i = self.calc, self.aba, self.t[args_txt[k][0]:args_txt[k][1]], 0
            return sub.resolver()

        try:
            if nome == "IF":
                cond = calcula(0)
                cond = self._escalar(cond)
                ramo = 1 if (bool(_num(cond)) if not isinstance(cond, str) else bool(cond)) else 2
                return calcula(ramo)
            try:
                v = calcula(0)
                self._escalar(v) if isinstance(v, Intervalo) else None
                return v
            except ErroPlanilha:
                return calcula(1)
        finally:
            self.i = fim

    def _match(self, procurado, intervalo, tipo):
        if not isinstance(intervalo, Intervalo):
            raise ErroPlanilha("#N/A")
        vals = self._vetor(intervalo)
        if tipo == 0:
            for k, v in enumerate(vals):
                if v is not None and (str(v).lower() == str(procurado).lower() if isinstance(procurado, str)
                                      else not isinstance(v, str) and _num(v) == _num(procurado)):
                    return float(k + 1)
            raise ErroPlanilha("#N/A")
        x, achado = _num(procurado), None
        for k, v in enumerate(vals):
            if v is None or v == "" or isinstance(v, str):
                continue
            if (tipo == 1 and _num(v) <= x) or (tipo == -1 and _num(v) >= x):
                achado = k + 1
            else:
                break
        if achado is None:
            raise ErroPlanilha("#N/A")
        return float(achado)

    def _index(self, args):
        intervalo = args[0]
        linha = int(_num(self._escalar(args[1]))) if len(args) > 1 and args[1] is not None else 1
        coluna = int(_num(self._escalar(args[2]))) if len(args) > 2 and args[2] is not None else 1
        cel = intervalo.celulas()
        if len(cel) == 1 and len(args) == 2:  # intervalo de uma linha: o número é a coluna
            linha, coluna = 1, linha
        if not (1 <= linha <= len(cel) and 1 <= coluna <= len(cel[0])):
            raise ErroPlanilha("#REF!")
        return self.calc.valor(cel[linha - 1][coluna - 1])

    def _vlookup(self, args):
        procurado, intervalo = self._escalar(args[0]), args[1]
        coluna = int(_num(self._escalar(args[2])))
        aproximado = True if len(args) < 4 or args[3] is None else bool(_num(self._escalar(args[3])))
        primeira = Intervalo(intervalo.aba, intervalo.c1, intervalo.l1, intervalo.c1, intervalo.l2)
        pos = int(self._match(procurado, primeira, 1 if aproximado else 0))
        return self.calc.valor(intervalo.celulas()[pos - 1][coluna - 1])

    def _xlookup(self, args):
        procurado, onde, retorno = self._escalar(args[0]), args[1], args[2]
        modo = 0 if len(args) < 5 or args[4] is None else int(_num(self._escalar(args[4])))
        if modo not in (0, -1):
            raise NaoSuportado("XLOOKUP com modo de correspondência %d" % modo)
        try:
            pos = int(self._match(procurado, onde, 0 if modo == 0 else 1))
        except ErroPlanilha:
            if len(args) > 3 and args[3] is not None:
                return self._escalar(args[3])
            raise
        return self._vetor(retorno)[pos - 1]


# ======================= conferência =======================


def chave(planilha, texto, aba_padrao=None):
    aba, _, end = texto.rpartition("!")
    aba = aba.strip("'") if aba else aba_padrao
    return planilha.aba_real(aba), end.replace("$", "").upper()


def nome_celula(ch):
    return "%s!%s" % ch


def centavos(x):
    return ("%.2f" % x).replace(".", ",")


def conferir(caminho, preco, renda, regras, testes):
    erros, avisos = [], []

    def ok(msg):
        print("ok    " + msg)

    def erro(msg):
        erros.append(msg)
        print("ERRO  " + msg)

    def aviso(msg):
        avisos.append(msg)
        print("AVISO " + msg)

    p = Planilha(caminho)
    print("Planilha: %s" % caminho)
    print("Abas: %s" % ", ".join(p.abas))
    try:
        aba_regras = p.aba_real(regras)
        ok("as regras moram numa aba própria: «%s»" % aba_regras)
    except KeyError as e:
        aba_regras = None
        erro(str(e) + ": as regras precisam de uma aba só delas")
    ch_preco, ch_renda = chave(p, preco), chave(p, renda)
    if ch_preco in p.formulas:
        erro("%s (preço) é fórmula; o preço é entrada, digitado" % nome_celula(ch_preco))
    elif not isinstance(p.valores.get(ch_preco), float):
        erro("%s (preço) está vazio ou não é número" % nome_celula(ch_preco))
    else:
        ok("%s (preço) é entrada: %s" % (nome_celula(ch_preco), centavos(p.valores[ch_preco])))
    if ch_renda not in p.formulas:
        erro("%s (renda) não tem fórmula: é um número digitado e não muda quando o preço muda"
             % nome_celula(ch_renda))
        return erros
    ok("%s (renda) é fórmula: =%s" % (nome_celula(ch_renda), p.formulas[ch_renda]))

    # Tudo de que a renda depende, no preço que está na planilha.
    base = Calculo(p)
    try:
        valor_atual = base.valor(ch_renda)
    except NaoSuportado as e:
        erro("função %s não é lida por esse conferidor; confira no Excel trocando o preço à mão" % e)
        return erros
    cadeia = sorted(base.usadas, key=lambda c: (c[0], separa(c[1])[1], separa(c[1])[0]))
    if ch_preco not in base.lidas:
        erro("a renda não depende de %s: mudar o preço não muda o resultado" % nome_celula(ch_preco))
    print("Fórmulas de que a renda depende:")
    for c in cadeia:
        print("      %-18s =%s" % (nome_celula(c), p.formulas[c]))
    # A busca por faixa é olhada célula por célula: uma célula com MATCH não salva outra com PROCV ou IF.
    com_match = [nome_celula(c) for c in cadeia if re.search(r"\bMATCH\s*\(", p.formulas[c].upper())]
    com_procv = [nome_celula(c) for c in cadeia if re.search(r"\b(VLOOKUP|XLOOKUP)\s*\(", p.formulas[c].upper())]
    com_if = [nome_celula(c) for c in cadeia
              if re.search(r"\bIF\s*\([^,]*[<>]=?\s*\d{2,}", p.formulas[c].upper())]
    if com_procv:
        erro("a faixa sai de PROCV/PROCX, não de MATCH (CORRESP), em %s; peça a troca por INDEX e MATCH"
             % ", ".join(com_procv))
    if com_if:
        erro("a faixa é escolhida com IF e limite escrito na fórmula, sem MATCH (CORRESP), em %s" % ", ".join(com_if))
    if not com_match:
        erro("a busca por faixa não usa MATCH (CORRESP)")
    elif not com_procv and not com_if:
        ok("busca por faixa com MATCH (CORRESP) em %s" % ", ".join(com_match))
    if aba_regras:
        fora = [c for c in cadeia if c[0] != aba_regras]
        constantes = []
        for c in fora:
            for t in tokens(p.formulas[c]):
                if t[0] == "numero" and float(t[1]) not in (0.0, 1.0, 2.0):
                    constantes.append("%s em %s" % (t[1], nome_celula(c)))
        if constantes:
            erro("regra escrita dentro da fórmula, fora da aba «%s»: %s" % (aba_regras, "; ".join(constantes)))
        elif not any(aba_regras.upper() in p.formulas[c].upper() for c in fora):
            erro("as fórmulas da renda não leem a aba «%s»" % aba_regras)
        else:
            ok("as fórmulas leem as regras da aba «%s», sem número de regra escrito nelas" % aba_regras)
    sem_round = [nome_celula(c) for c in cadeia
                 if re.search(r"[*/]", p.formulas[c]) and not re.search(r"\bROUND(UP|DOWN)?\s*\(", p.formulas[c].upper())]
    if sem_round:
        erro("linha de taxa com multiplicação ou divisão sem ROUND (ARRED): %s; o extrato arredonda cada linha"
             % ", ".join(sem_round))
    else:
        ok("cada linha com multiplicação ou divisão passa por ROUND (ARRED) em 2 casas")

    for preco_teste, esperado in testes:
        calc = Calculo(p, {ch_preco: preco_teste})
        r = calc.valor(ch_renda)
        if isinstance(r, ErroPlanilha):
            erro("preço %s: a renda dá erro %s" % (centavos(preco_teste), r))
            continue
        if round(r, 2) == round(esperado, 2):
            ok("preço %s: renda recalculada %s, igual ao esperado ao centavo" % (centavos(preco_teste), centavos(r)))
        else:
            erro("preço %s: renda recalculada %s, esperado %s (diferença de %s)" % (
                centavos(preco_teste), centavos(r), centavos(esperado), centavos(r - esperado)))

    gravado = p.gravados.get(ch_renda)
    if isinstance(valor_atual, ErroPlanilha):
        erro("no preço da planilha, a renda dá erro %s" % valor_atual)
    elif gravado is None:
        aviso("o arquivo ainda não foi calculado: %s não tem valor gravado. Abra no Excel, LibreOffice ou "
              "Google Planilhas, salve como .xlsx e rode de novo" % nome_celula(ch_renda))
    elif not isinstance(gravado, float) or round(gravado, 2) != round(valor_atual, 2):
        erro("valor gravado pela planilha em %s é %s, e o recálculo dá %s no mesmo preço" % (
            nome_celula(ch_renda), gravado if not isinstance(gravado, float) else centavos(gravado),
            centavos(valor_atual)))
    else:
        ok("valor gravado pela planilha em %s: %s, igual ao recálculo no preço %s" % (
            nome_celula(ch_renda), centavos(gravado), centavos(p.valores[ch_preco])))
    return erros


def main(argv=None):
    ap = argparse.ArgumentParser(description="Confere uma planilha calculadora antes de usar.")
    ap.add_argument("arquivo")
    ap.add_argument("--preco", default="Calculadora!B6", help="célula do preço do kit (padrão Calculadora!B6)")
    ap.add_argument("--renda", default="Calculadora!B17", help="célula da renda do pedido (padrão Calculadora!B17)")
    ap.add_argument("--regras", default="Taxas", help="nome da aba de regras (padrão Taxas)")
    ap.add_argument("--teste", action="append", default=[],
                    help="preço=renda esperada, com ponto ou vírgula (padrão 10.90=4.00, o pedido-gabarito)")
    a = ap.parse_args(argv)
    testes = []
    for t in a.teste or ["10.90=4.00"]:
        preco, _, esperado = t.replace(",", ".").partition("=")
        testes.append((float(preco), float(esperado)))
    try:
        erros = conferir(a.arquivo, a.preco, a.renda, a.regras, testes)
    except (KeyError, ValueError, zipfile.BadZipFile) as e:
        print("ERRO  não consegui ler a planilha: %s" % e)
        return 1
    print("resultado: " + ("tudo ok" if not erros else "%d erro(s)" % len(erros)))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
