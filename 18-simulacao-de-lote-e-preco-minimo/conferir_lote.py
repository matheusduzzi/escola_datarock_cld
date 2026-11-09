"""Confere a aba Simulação de lote de uma planilha antes de usar o número.

Lê as fórmulas do .xlsx (com o mesmo leitor do conferir_planilha.py), recalcula a aba com as
entradas que você pedir e testa o comportamento de cada custo:
  - mexer no frete muda o investimento no mesmo valor (o frete entrou uma vez, no lote);
  - mexer na embalagem muda o investimento uma vez por kit, não por pote;
  - mexer no custo do pote muda só os potes que entraram nos kits (a sobra fica fora);
  - os kits montados são um número inteiro;
  - o preço mínimo lê a aba de regras e, arredondado para cima no centavo, não dá prejuízo;
  - cada linha da tabela de preços dá a mesma renda que a Calculadora no mesmo preço.

Uso:
    python3 conferir_lote.py planilha_simulacao.xlsx
    python3 conferir_lote.py planilha_simulacao.xlsx --preco 29.90
    python3 conferir_lote.py minha.xlsx --potes 600 --custo-pote 1.20 --itens 4 --embalagem 3.50 \\
        --frete 40 --preco 24.90 --esperado kits=150

As opções mudam as entradas só na conta do conferidor; o arquivo não é alterado. As células são
as do case (Simulação de lote!B5 a B26, A30 a E35); para outra planilha, use --celula nome=Aba!B5.

Sai com código 0 quando nada deu ERRO e 1 quando algum teste falhou. Só usa a biblioteca padrão.
"""
import argparse
import math
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conferir_planilha import Calculo, ErroPlanilha, NaoSuportado, Planilha, tokens  # noqa: E402

LOTE = "Simulação de lote"
CELULAS = {  # nome: (aba, célula), como no case
    "potes": (LOTE, "B5"), "custo_pote": (LOTE, "B6"), "itens_lote": (LOTE, "B7"),
    "embalagem": (LOTE, "B8"), "frete": (LOTE, "B9"),
    "kits": (LOTE, "B12"), "sobra": (LOTE, "B13"), "custo_potes": (LOTE, "B14"),
    "custo_embalagens": (LOTE, "B15"), "frete_lote": (LOTE, "B16"), "investimento": (LOTE, "B17"),
    "custo_kit": (LOTE, "B18"), "preco_lote": (LOTE, "B21"), "renda": (LOTE, "B22"),
    "lucro_kit": (LOTE, "B23"), "lucro_lote": (LOTE, "B24"), "retorno": (LOTE, "B25"),
    "minimo": (LOTE, "B26"),
    "itens": ("Calculadora", "B5"), "preco": ("Calculadora", "B6"), "renda_calc": ("Calculadora", "B17"),
    "inicio_faixa2": ("Taxas", "A5"),
}
TABELA = [(LOTE, r) for r in range(30, 36)]  # A: preço, B: renda, C: lucro por kit, D: lucro do lote, E: retorno
ENTRADAS = {"potes": "potes", "custo_pote": "custo_pote", "itens": "itens", "embalagem": "embalagem",
            "frete": "frete", "preco": "preco"}


def brl(x):
    s = "%.2f" % x
    inteiro, dec = s.split(".")
    neg = inteiro.startswith("-")
    inteiro = inteiro.lstrip("-")
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    return ("-" if neg else "") + ".".join(grupos) + "," + dec


def pct(x):
    return ("%.0f%%" % (x * 100)).replace(".", ",")


def inteiro(x):
    return brl(x)[:-3] if abs(x - round(x)) < 1e-9 else brl(x)


class Conta:
    """Recalcula a planilha com as entradas mudadas, sem tocar no arquivo."""

    def __init__(self, p, cel, mudancas):
        self.p, self.cel, self.mudancas = p, cel, dict(mudancas)

    def com(self, **extra):
        m = dict(self.mudancas)
        for nome, valor in extra.items():
            m[self.cel[nome]] = valor
        return Conta(self.p, self.cel, m)

    def v(self, nome_ou_chave):
        chave = self.cel[nome_ou_chave] if isinstance(nome_ou_chave, str) else nome_ou_chave
        r = Calculo(self.p, self.mudancas).valor(chave)
        if isinstance(r, ErroPlanilha):
            raise r
        return 0.0 if r is None else float(r)


def conferir(caminho, cel, mudancas, esperados):
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
    for nome in list(cel):
        aba, end = cel[nome]
        try:
            cel[nome] = (p.aba_real(aba), end)
        except KeyError as e:
            erro(str(e))
            return erros
    c = Conta(p, cel, {cel[k]: v for k, v in mudancas.items()})

    # 1. Entradas digitadas e ligação com a Calculadora
    for nome, rotulo in [("potes", "potes comprados"), ("custo_pote", "custo por pote"),
                         ("embalagem", "embalagem por kit"), ("frete", "frete do lote")]:
        if cel[nome] in p.formulas:
            erro("%s!%s (%s) é fórmula; é entrada, digitada" % (cel[nome] + (rotulo,)))
    for nome, origem in [("itens_lote", "itens"), ("preco_lote", "preco"), ("renda", "renda_calc")]:
        f = p.formulas.get(cel[nome], "")
        alvo = "%s!%s" % cel[origem]
        if f.replace("$", "").replace("'", "").upper() != alvo.upper():
            erro("%s!%s precisa ler %s (está «%s»): a aba de lote e a Calculadora deixam de falar a mesma coisa"
                 % (cel[nome] + (alvo, ("=" + f) if f else "número digitado")))
    if not erros:
        ok("entradas digitadas; itens, preço e renda vêm da Calculadora")

    try:
        base = {n: c.v(n) for n in ("potes", "custo_pote", "itens_lote", "embalagem", "frete", "kits", "sobra",
                                    "custo_potes", "custo_embalagens", "frete_lote", "investimento", "custo_kit",
                                    "preco_lote", "renda", "lucro_kit", "lucro_lote", "retorno", "minimo")}
    except ErroPlanilha as e:
        erro("a aba de lote dá erro %s com essas entradas" % e)
        return erros
    except NaoSuportado as e:
        erro("função %s não é lida por esse conferidor; confira no Excel trocando as entradas à mão" % e)
        return erros

    print("Entradas: %s potes a R$ %s, kit de %s, embalagem de R$ %s por kit, frete de R$ %s, preço de R$ %s"
          % (inteiro(base["potes"]), brl(base["custo_pote"]), inteiro(base["itens_lote"]), brl(base["embalagem"]),
             brl(base["frete"]), brl(base["preco_lote"])))

    # 2. Kits inteiros e sobra
    k, itens, potes = base["kits"], base["itens_lote"], base["potes"]
    esperado_kits = math.floor(potes / itens + 1e-9) if itens > 0 else 0
    if abs(k - round(k)) > 1e-9:
        erro("kits montados = %s: kit não sai pela metade; arredonde para baixo (INT)" % brl(k))
    elif round(k) != esperado_kits:
        erro("kits montados = %s, mas %s potes em kits de %s dão %s" % (inteiro(k), inteiro(potes), inteiro(itens),
                                                                          esperado_kits))
    else:
        ok("kits montados: %s; potes que sobram: %s" % (inteiro(k), inteiro(base["sobra"])))

    # 3. Cada custo, testado pelo comportamento
    if k > 0:
        d_frete = c.com(frete=base["frete"] + 10).v("investimento") - base["investimento"]
        d_emb = c.com(embalagem=base["embalagem"] + 1).v("investimento") - base["investimento"]
        d_pote = c.com(custo_pote=base["custo_pote"] + 1).v("investimento") - base["investimento"]
        if abs(d_frete - 10) > 0.005:
            erro("R$ 10 a mais de frete mudam o investimento em R$ %s, e não em R$ 10,00: o frete do lote "
                 "precisa entrar uma vez no investimento" % brl(d_frete))
        else:
            ok("frete entra uma vez, no lote: R$ 10 a mais de frete, R$ 10,00 a mais de investimento")
        if abs(d_emb - k) > 0.005:
            erro("R$ 1 a mais de embalagem muda o investimento em R$ %s, e não em R$ %s (um por kit)"
                 % (brl(d_emb), brl(k)))
        else:
            ok("embalagem por kit: R$ 1 a mais de embalagem, R$ %s a mais de investimento (%s kits)"
               % (brl(d_emb), inteiro(k)))
        usados = k * itens
        if abs(d_pote - usados) > 0.005:
            erro("R$ 1 a mais por pote muda o investimento em R$ %s, e não em R$ %s: entram só os %s potes "
                 "usados nos kits" % (brl(d_pote), brl(usados), inteiro(usados)))
        else:
            ok("custo do pote: entram os %s potes usados nos kits; a sobra fica fora" % inteiro(usados))
        if abs(base["custo_kit"] - base["investimento"] / k) > 0.005:
            erro("custo por kit = %s, mas investimento ÷ kits = %s" % (brl(base["custo_kit"]),
                                                                       brl(base["investimento"] / k)))
    else:
        erro("nenhum kit montado: com %s potes não sai um kit de %s" % (inteiro(potes), inteiro(itens)))

    print("Custo do lote: potes R$ %s + embalagens R$ %s + frete R$ %s = investimento R$ %s; custo por kit "
          "R$ %s (%s)" % (brl(base["custo_potes"]), brl(base["custo_embalagens"]), brl(base["frete_lote"]),
                         brl(base["investimento"]), brl(base["custo_kit"]),
                         ("%.4f" % base["custo_kit"]).replace(".", ",")))

    # 4. Preço mínimo
    f_min = p.formulas.get(cel["minimo"], "")
    soltos = [t[1] for t in tokens(f_min) if t[0] == "numero" and float(t[1]) not in (0.0, 1.0)] if f_min else []
    minimo = base["minimo"]
    if not f_min:
        erro("%s!%s (preço mínimo) não tem fórmula" % cel["minimo"])
    elif soltos:
        erro("preço mínimo com regra escrita na fórmula (%s): ele precisa ler a aba de regras" % ", ".join(soltos))
    elif "TAXAS!" not in f_min.upper():
        erro("preço mínimo não lê a aba de regras")
    elif minimo >= c.v("inicio_faixa2"):
        aviso("preço mínimo de R$ %s passa do começo da faixa 2 (R$ %s): a fórmula vale só na primeira faixa; "
              "teste preços na tabela" % (brl(minimo), brl(c.v("inicio_faixa2"))))
    else:
        # A fórmula não arredonda as taxas linha a linha. O menor preço em centavos sem prejuízo sai da
        # própria planilha: testo os centavos em volta do valor da fórmula.
        centavos = None
        for n in range(int(math.floor(minimo * 100)) - 10, int(math.floor(minimo * 100)) + 11):
            if c.com(preco=n / 100).v("lucro_lote") >= -0.005:
                centavos = n / 100
                break
        if centavos is None:
            erro("preço mínimo de R$ %s não acerta: nenhum preço até R$ %s, 10 centavos acima, fecha o lote sem "
                 "prejuízo; a fórmula esqueceu um custo ou uma taxa" % (brl(minimo), brl(math.floor(minimo * 100) / 100 + 0.10)))
        elif centavos < minimo - 0.05:
            erro("preço mínimo de R$ %s está alto demais: o lote já fecha sem prejuízo em R$ %s" % (brl(minimo),
                                                                                                      brl(centavos)))
        else:
            abaixo = round(centavos - 0.01, 2)
            ok("preço mínimo: a fórmula dá %s; o menor preço em centavos sem prejuízo é R$ %s (lote com R$ %s); "
               "R$ %s dá prejuízo de R$ %s" % (("%.4f" % minimo).replace(".", ","), brl(centavos),
                                              brl(c.com(preco=centavos).v("lucro_lote")), brl(abaixo),
                                              brl(-c.com(preco=abaixo).v("lucro_lote"))))
            base["minimo_centavos"] = centavos

    # 5. Resultado no preço da Calculadora
    print("No preço da Calculadora (R$ %s): renda R$ %s, lucro por kit R$ %s, lucro do lote R$ %s, retorno %s"
          % (brl(base["preco_lote"]), brl(base["renda"]), brl(base["lucro_kit"]), brl(base["lucro_lote"]),
             pct(base["retorno"])))
    if base["lucro_lote"] < -0.005:
        aviso("prejuízo de R$ %s no lote: esse bloco usa o preço da aba Calculadora (R$ %s). Troque o preço lá, "
              "ou rode com --preco, para ver outro valor" % (brl(-base["lucro_lote"]), brl(base["preco_lote"])))

    # 6. Tabela de preços contra a Calculadora
    print("Tabela de preços (antes de imposto e anúncios):")
    print("      %-12s %-10s %-10s %-14s %s" % ("preço", "renda", "lucro/kit", "lucro do lote", "retorno"))
    divergentes = []
    for aba, r in TABELA:
        try:
            pr = c.v((aba, "A%d" % r))
            linha = [c.v((aba, col + str(r))) for col in "BCDE"]
        except ErroPlanilha as e:
            erro("linha %d da tabela dá erro %s" % (r, e))
            continue
        renda_calc = c.com(preco=pr).v("renda_calc")
        if abs(linha[0] - renda_calc) > 0.005:
            divergentes.append("R$ %s (tabela %s, Calculadora %s)" % (brl(pr), brl(linha[0]), brl(renda_calc)))
        if abs(linha[1] - (linha[0] - base["custo_kit"])) > 0.005 or abs(linha[2] - linha[1] * k) > 0.01:
            divergentes.append("R$ %s: lucro da linha não é renda − custo por kit, vezes os kits" % brl(pr))
        print("      %-12s %-10s %-10s %-14s %s" % ("R$ " + brl(pr), brl(linha[0]), brl(linha[1]), brl(linha[2]),
                                                    pct(linha[3])))
    if divergentes:
        erro("a tabela e a Calculadora dão números diferentes: " + "; ".join(divergentes))
    else:
        ok("cada linha da tabela dá a mesma renda que a Calculadora no mesmo preço")

    # 7. Esperados do aluno
    for nome, valor in esperados:
        if nome not in base:
            erro("não conheço «%s»; use: %s" % (nome, ", ".join(sorted(base))))
            continue
        obtido = base[nome]
        if abs(round(obtido, 2) - round(valor, 2)) < 0.005:
            ok("%s = %s, igual ao esperado" % (nome, brl(obtido)))
        else:
            erro("%s = %s, esperado %s" % (nome, brl(obtido), brl(valor)))

    # 8. Valor gravado pelo programa de planilha
    if not mudancas:
        gravado = p.gravados.get(cel["lucro_lote"])
        if gravado is None:
            aviso("o arquivo ainda não foi calculado: %s!%s não tem valor gravado. Abra no Excel, LibreOffice ou "
                  "Google Planilhas, salve como .xlsx e rode de novo" % cel["lucro_lote"])
        elif not isinstance(gravado, float) or abs(gravado - base["lucro_lote"]) > 0.005:
            erro("valor gravado pela planilha em %s!%s é %s, e o recálculo dá %s" % (
                cel["lucro_lote"] + (gravado, brl(base["lucro_lote"]))))
        else:
            ok("valor gravado pela planilha em %s!%s: %s, igual ao recálculo" % (cel["lucro_lote"] + (brl(gravado),)))
    return erros


def numero(texto):
    return float(texto.replace(",", "."))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Confere a aba Simulação de lote antes de usar o número.")
    ap.add_argument("arquivo")
    ap.add_argument("--potes", type=numero, help="potes comprados (Simulação de lote!B5)")
    ap.add_argument("--custo-pote", type=numero, dest="custo_pote", help="custo por pote (B6)")
    ap.add_argument("--itens", type=numero, help="itens por kit (Calculadora!B5)")
    ap.add_argument("--embalagem", type=numero, help="embalagem por kit (B8)")
    ap.add_argument("--frete", type=numero, help="frete do lote (B9)")
    ap.add_argument("--preco", type=numero, help="preço do kit (Calculadora!B6)")
    ap.add_argument("--esperado", action="append", default=[],
                    help="nome=valor, por exemplo kits=333, investimento=2684.03, minimo=16.10, "
                         "minimo_centavos=16.11")
    ap.add_argument("--celula", action="append", default=[], help="nome=Aba!B5, para planilha com outro layout")
    a = ap.parse_args(argv)
    cel = dict(CELULAS)
    for item in a.celula:
        nome, _, ref = item.partition("=")
        aba, _, end = ref.rpartition("!")
        cel[nome] = (aba.strip("'"), end.replace("$", "").upper())
    mudancas = {nome: getattr(a, campo) for campo, nome in ENTRADAS.items() if getattr(a, campo) is not None}
    esperados = []
    for item in a.esperado:
        nome, _, valor = item.partition("=")
        esperados.append((nome.strip(), numero(valor)))
    try:
        erros = conferir(a.arquivo, cel, mudancas, esperados)
    except (KeyError, ValueError, zipfile.BadZipFile) as e:
        print("ERRO  não consegui ler a planilha: %s" % e)
        return 1
    print("resultado: " + ("tudo ok" if not erros else "%d erro(s)" % len(erros)))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
