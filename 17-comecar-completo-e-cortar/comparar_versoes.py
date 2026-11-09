"""Compara versões de uma planilha calculadora, na ordem em que você foi cortando.

Para cada versão, mostra as entradas (o que você digita) e testa o pedido-gabarito.
Entre uma versão e a seguinte, mostra:
  - as entradas, as contas e as regras que saíram ou entraram;
  - se a renda do pedido ficou igual em 13 preços, dos dois lados de cada limite de faixa do case
    (para outra regra, passe os seus preços com --precos);
  - regra que nenhuma fórmula lê (editar não muda nada) e entrada que nenhuma fórmula lê.

As células são achadas pelo rótulo da coluna A, porque um corte costuma mudar as linhas de
lugar. O preço é a entrada com "valor cobrado" ou "preço" no rótulo, e a renda é a conta com
"renda do pedido" no rótulo. Lê as fórmulas com o mesmo leitor do conferir_planilha.py.

Uso:
    python3 comparar_versoes.py versao_1.xlsx versao_2.xlsx versao_3.xlsx versao_4.xlsx
    python3 comparar_versoes.py v1.xlsx v2.xlsx --teste 10.90=4.00 --regras Taxas \\
        --rotulo-preco "preço de venda" --rotulo-renda "renda líquida" --precos 9.99,10,49.99,50

Sai com código 0 quando nada deu ERRO e 1 quando algum teste falhou. Só usa a biblioteca padrão.
"""
import argparse
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conferir_planilha as C  # noqa: E402

PRECOS = [7.99, 8.00, 10.90, 10.93, 29.90, 39.90, 79.99, 80.00, 99.99, 100.00, 199.99, 200.00, 350.00]


def rotulo(p, aba, endereco):
    col, lin = C.separa(endereco)
    if col == 1:
        return None
    texto = p.valores.get((aba, "A%d" % lin))
    return " ".join(texto.split()) if isinstance(texto, str) and texto.strip() else None


def lidas(p):
    """Todas as células que alguma fórmula lê, com os intervalos abertos célula a célula."""
    saida = set()
    for (aba, _end), formula in p.formulas.items():
        for tipo, valor, _i, _f in C.tokens(formula.lstrip("=")):
            if tipo != "ref":
                continue
            nome_aba, _, intervalo = valor.rpartition("!")
            nome_aba = p.aba_real(nome_aba.strip("'").replace("''", "'")) if nome_aba else aba
            pontos = [C.separa(x) for x in intervalo.split(":")]
            faixa = C.Intervalo(nome_aba, pontos[0][0], pontos[0][1], pontos[-1][0], pontos[-1][1])
            for linha in faixa.celulas():
                saida.update(linha)
    return saida


class Versao:
    def __init__(self, caminho, regras, rotulo_preco, rotulo_renda):
        self.caminho, self.p = caminho, C.Planilha(caminho)
        self.regras = self.p.aba_real(regras)
        self.lidas = lidas(self.p)
        self.entradas, self.contas, self.regras_cel = {}, {}, {}
        for (aba, end), valor in self.p.valores.items():
            if aba == self.regras:
                if isinstance(valor, float):
                    nome = rotulo(self.p, aba, end)
                    self.regras_cel[nome or "%s!%s" % (aba, end)] = (aba, end)
            elif valor != "" and not (isinstance(valor, str) and C.separa(end)[0] == 1):
                nome = rotulo(self.p, aba, end)
                if nome:
                    self.entradas[nome] = (aba, end)
        for (aba, end) in self.p.formulas:
            nome = rotulo(self.p, aba, end)
            if nome and aba != self.regras:
                self.contas[nome] = (aba, end)
        self.preco = self._acha(self.entradas, rotulo_preco, "a entrada do preço")
        self.renda = self._acha(self.contas, rotulo_renda, "a conta da renda do pedido")

    def _acha(self, onde, padrao, o_que):
        achados = [ch for nome, ch in onde.items() if re.search(padrao, nome, re.I)]
        if not achados:
            raise KeyError("%s: não achei %s pelo rótulo (procurei «%s» na coluna A)" % (self.caminho, o_que, padrao))
        return sorted(achados, key=lambda c: C.separa(c[1])[::-1])[0]

    def renda_em(self, preco):
        r = C.Calculo(self.p, {self.preco: preco}).valor(self.renda)
        return r


def mostra_valor(v, inteiro=False):
    if inteiro and isinstance(v, float) and v.is_integer():
        return "%d" % v
    if isinstance(v, float):
        return C.centavos(v) if abs(v * 100 - round(v * 100)) < 1e-9 else ("%.4f" % v).replace(".", ",")
    return str(v)


def comparar(caminhos, regras, testes, rotulo_preco, rotulo_renda, precos=None):
    erros = []
    lista = precos or PRECOS
    sufixo = "" if precos else ", dos dois lados de cada limite de faixa do case"

    def ok(msg):
        print("ok    " + msg)

    def erro(msg):
        erros.append(msg)
        print("ERRO  " + msg)

    def aviso(msg):
        print("AVISO " + msg)

    versoes = [Versao(c, regras, rotulo_preco, rotulo_renda) for c in caminhos]
    for n, v in enumerate(versoes, start=1):
        print("Versão %d: %s" % (n, v.caminho))
        print("      entradas (%d): %s" % (len(v.entradas), " | ".join(
            "%s %s = %s" % (end, nome, mostra_valor(v.p.valores[(aba, end)], inteiro=True))
            for nome, (aba, end) in sorted(v.entradas.items(), key=lambda x: C.separa(x[1][1])[::-1]))))
        print("      renda do pedido em %s!%s" % v.renda)
        for preco, esperado in testes:
            r = v.renda_em(preco)
            if isinstance(r, C.ErroPlanilha):
                erro("versão %d, preço %s: a renda dá erro %s" % (n, C.centavos(preco), r))
            elif round(r, 2) == round(esperado, 2):
                ok("versão %d, preço %s: renda %s, igual ao gabarito" % (n, C.centavos(preco), C.centavos(r)))
            else:
                erro("versão %d, preço %s: renda %s, gabarito %s" % (n, C.centavos(preco), C.centavos(r),
                                                                     C.centavos(esperado)))
        for nome, ch in sorted(v.regras_cel.items(), key=lambda x: C.separa(x[1][1])[::-1]):
            if ch not in v.lidas:
                erro("versão %d: a regra %s!%s (%s) não é lida por nenhuma fórmula; editar essa célula não muda nada"
                     % (n, ch[0], ch[1], nome))
        for nome, ch in v.entradas.items():
            if ch not in v.lidas:
                aviso("versão %d: a entrada %s!%s (%s) não entra em nenhuma conta" % (n, ch[0], ch[1], nome))

    for n in range(1, len(versoes)):
        a, b = versoes[n - 1], versoes[n]
        print("Da versão %d para a %d:" % (n, n + 1))
        for titulo, de, para in (("entrada", a.entradas, b.entradas), ("conta", a.contas, b.contas),
                                 ("regra", a.regras_cel, b.regras_cel)):
            for nome in de:
                if nome not in para:
                    print("      saiu %-8s %s!%s %s" % (titulo, de[nome][0], de[nome][1], nome))
            for nome in para:
                if nome not in de:
                    print("      entrou %-6s %s!%s %s" % (titulo, para[nome][0], para[nome][1], nome))
        for nome in a.regras_cel:
            if nome in b.regras_cel:
                va, vb = a.p.valores[a.regras_cel[nome]], b.p.valores[b.regras_cel[nome]]
                if va != vb:
                    print("      mudou regra  %s: %s para %s" % (nome, mostra_valor(va), mostra_valor(vb)))
        diferentes = []
        for preco in lista:
            ra, rb = a.renda_em(preco), b.renda_em(preco)
            iguais = (not isinstance(ra, C.ErroPlanilha) and not isinstance(rb, C.ErroPlanilha)
                      and abs(ra - rb) < 1e-9)
            if not iguais:
                diferentes.append("%s: %s para %s" % (C.centavos(preco), mostra_valor(ra), mostra_valor(rb)))
        if diferentes:
            erro("a renda mudou em %d de %d preços (%s); um corte que só tira campo não muda a renda"
                 % (len(diferentes), len(lista), "; ".join(diferentes)))
        else:
            ok("renda igual nos %d preços testados%s" % (len(lista), sufixo))
    return erros


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compara versões de uma planilha calculadora, em ordem.")
    ap.add_argument("arquivos", nargs="+", help="as versões, da primeira à última")
    ap.add_argument("--regras", default="Taxas", help="nome da aba de regras (padrão Taxas)")
    ap.add_argument("--teste", action="append", default=[],
                    help="preço=renda esperada, com ponto ou vírgula (padrão 10.90=4.00, o pedido-gabarito)")
    ap.add_argument("--rotulo-preco", default="valor cobrado|preço", help="texto do rótulo do preço")
    ap.add_argument("--rotulo-renda", default="renda do pedido", help="texto do rótulo da renda")
    ap.add_argument("--precos", help="preços da comparação entre versões, separados por vírgula, com ponto "
                    "(padrão: 13 preços em volta dos limites de faixa do case)")
    a = ap.parse_args(argv)
    if len(a.arquivos) < 2:
        print("ERRO  passe pelo menos duas versões, na ordem dos cortes")
        return 1
    testes = []
    for t in a.teste or ["10.90=4.00"]:
        preco, _, esperado = t.replace(",", ".").partition("=")
        testes.append((float(preco), float(esperado)))
    try:
        precos = [float(x) for x in a.precos.split(",")] if a.precos else None
        erros = comparar(a.arquivos, a.regras, testes, a.rotulo_preco, a.rotulo_renda, precos)
    except C.NaoSuportado as e:
        print("ERRO  função %s não é lida por esse comparador; compare no Excel trocando o preço à mão" % e)
        return 1
    except (KeyError, ValueError, zipfile.BadZipFile, FileNotFoundError) as e:
        print("ERRO  não consegui ler: %s" % (e.args[0] if e.args else e))
        return 1
    print("resultado: " + ("tudo ok" if not erros else "%d erro(s)" % len(erros)))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
