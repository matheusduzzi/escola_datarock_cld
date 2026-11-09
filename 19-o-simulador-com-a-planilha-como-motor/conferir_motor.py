"""Confere se o motor do simulador e a planilha dão o mesmo número, antes de publicar.

O motor é o engine.js (ou a página do simulador com o motor dentro). O conferidor:
  1. roda o motor no Node.js, sem a HyperFormula, só para anotar o que ele grava em cada célula;
  2. compara célula por célula com a planilha: fórmula com fórmula, regra com regra;
  3. calcula os casos de casos.json (gabarito, lote a R$ 29,90, tabela de preços, degrau) com as
     fórmulas da planilha e com as fórmulas do motor, e compara os dois com o esperado;
  4. compara cada ponto da aba Curva, a do gráfico, com a Calculadora no mesmo preço.

Uso:
    python3 conferir_motor.py
    python3 conferir_motor.py --motor simulador.html --planilha minha_planilha.xlsx
    python3 conferir_motor.py --motor engine.js --casos meus_casos.json

A conta usa o avaliador de fórmulas do conferir_planilha.py, não a HyperFormula. Para rodar o
motor com a HyperFormula de verdade, use o testar_motor.js.

Sai com código 0 quando nada deu ERRO, 1 quando algum teste falhou e 2 quando não deu para ler o
motor (falta o Node.js, ou o arquivo não tem a função buildEngine). Só usa a biblioteca padrão.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conferir_planilha import Calculo, ErroPlanilha, Planilha  # noqa: E402

CAL, LOTE, TAXAS, CURVA = "Calculadora", "Simulação de lote", "Taxas", "Curva"
# Células que a pessoa mexe. Se o motor abre com outro valor nelas, é AVISO, não ERRO.
ENTRADAS = {(CAL, "B5"), (CAL, "B6"), (LOTE, "B5"), (LOTE, "B6"), (LOTE, "B8"), (LOTE, "B9")}
ENTRADAS |= {(LOTE, "A%d" % r) for r in range(30, 36)}

# Roda o buildEngine com uma HyperFormula de mentira, que só anota o que o motor grava.
LER_MOTOR = r"""
const fs = require('fs'), vm = require('vm');
const arquivo = process.argv[1];
let codigo = fs.readFileSync(arquivo, 'utf8');
if (/\.html?$/i.test(arquivo)) {
  const blocos = [...codigo.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
  const achado = blocos.filter(b => /function\s+buildEngine\s*\(/.test(b));
  if (!achado.length) { console.error('a página não tem um <script> com a função buildEngine'); process.exit(2); }
  codigo = achado[0];
}
const ctx = { module: { exports: null }, console: console, Math: Math };
vm.createContext(ctx);
vm.runInContext(codigo + '\n;this.__motor = typeof buildEngine === "function" ? buildEngine : module.exports;', ctx);
if (typeof ctx.__motor !== 'function') { console.error('o arquivo não tem a função buildEngine'); process.exit(2); }
const abas = [], celulas = {};
function letras(c) { let s = ''; c += 1; while (c) { const r = (c - 1) % 26; s = String.fromCharCode(65 + r) + s; c = Math.floor((c - 1) / 26); } return s; }
const falsa = {
  buildEmpty: function () {
    return {
      addSheet: function (n) { abas.push(n); celulas[n] = {}; return n; },
      getSheetId: function (n) { const i = abas.indexOf(n); if (i < 0) throw new Error('aba sem nome: ' + n); return i; },
      setCellContents: function (a, v) {
        v.forEach(function (linha, i) { linha.forEach(function (x, j) { celulas[abas[a.sheet]][letras(a.col + j) + (a.row + i + 1)] = x; }); });
      },
      getCellValue: function (a) { return celulas[abas[a.sheet]][letras(a.col) + (a.row + 1)]; },
      batch: function (f) { f(); }
    };
  }
};
const E = ctx.__motor(falsa);
console.log(JSON.stringify({ abas: abas, celulas: celulas, curvaN: E && E.curvaN }));
"""


class Motor:
    """As fórmulas do motor no mesmo formato da Planilha do conferir_planilha.py."""

    def __init__(self, gravado):
        self.abas = gravado["abas"]
        self.curva_n = gravado.get("curvaN")
        self.formulas, self.valores, self.gravados, self.nomes_def = {}, {}, {}, {}
        for aba, cels in gravado["celulas"].items():
            for end, v in cels.items():
                if isinstance(v, str) and v.startswith("="):
                    self.formulas[(aba, end)] = v[1:]
                else:
                    self.valores[(aba, end)] = v

    def aba_real(self, nome):
        for a in self.abas:
            if a.lower() == nome.lower():
                return a
        raise KeyError("o motor não tem a aba «%s» (abas: %s)" % (nome, ", ".join(self.abas)))


def ler_motor(caminho):
    if not shutil.which("node"):
        print("ERRO não achei o Node.js. Instale o Node.js (nodejs.org) e rode de novo.")
        sys.exit(2)
    r = subprocess.run(["node", "-e", LER_MOTOR, str(caminho)], capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO não deu para ler o motor %s: %s" % (caminho, (r.stderr.strip().splitlines() or ["?"])[-1]))
        sys.exit(2)
    return Motor(json.loads(r.stdout))


def normaliza(formula):
    """Tira o = do começo e os espaços fora de texto, e põe em maiúsculas fora de texto."""
    partes = re.split(r'("(?:[^"]|"")*")', formula.lstrip("="))
    return "".join(p if p.startswith('"') else re.sub(r"\s+", "", p).upper() for p in partes)


def brl(x):
    neg, x = x < 0, abs(x)
    centavos = abs(x * 100 - round(x * 100)) < 1e-6
    s = ("%.2f" if centavos else "%.4f") % x
    inteiro, dec = s.split(".")
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    return ("-" if neg else "") + ".".join(grupos) + "," + dec


def separa(ref):
    aba, end = ref.rsplit("!", 1)
    return aba.strip("'"), end.replace("$", "").upper()


def valor(fonte, entradas, chave):
    v = Calculo(fonte, entradas).valor(chave)
    if isinstance(v, ErroPlanilha):
        return str(v)
    return v


def main():
    ap = argparse.ArgumentParser(description="Confere se o motor do simulador e a planilha dão o mesmo número.")
    ap.add_argument("--motor", default="engine.js", help="engine.js ou a página .html do simulador")
    ap.add_argument("--planilha", default="planilha_simulacao.xlsx")
    ap.add_argument("--casos", default="casos.json")
    a = ap.parse_args()

    motor = ler_motor(Path(a.motor))
    pla = Planilha(a.planilha)
    casos = json.loads(Path(a.casos).read_text(encoding="utf-8"))["casos"]
    erros, avisos = [], []

    def linha(tipo, texto):
        print("%-5s %s" % (tipo, texto))
        (erros if tipo == "ERRO" else avisos if tipo == "AVISO" else []).append(texto)

    print("Motor: %s · planilha: %s" % (a.motor, a.planilha))

    # 1. Mesmas células, mesmas fórmulas
    iguais = 0
    for aba in pla.abas:
        if aba not in motor.abas:
            linha("ERRO", "a planilha tem a aba «%s» e o motor não" % aba)
            continue
        for chave, f in sorted(pla.formulas.items()):
            if chave[0] != aba:
                continue
            fm = motor.formulas.get(chave)
            if fm is None:
                linha("ERRO", "%s!%s: a planilha tem =%s e o motor não tem fórmula nessa célula" % (chave + (f,)))
            elif normaliza(fm) != normaliza(f):
                linha("ERRO", "%s!%s: fórmula diferente\n        planilha: =%s\n        motor:    =%s" % (chave + (f, fm)))
            else:
                iguais += 1
        for chave, v in sorted(pla.valores.items()):
            if chave[0] != aba or not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            vm = motor.valores.get(chave, motor.formulas.get(chave))
            if vm is None:
                linha("ERRO", "%s!%s: a planilha tem %s e o motor deixou a célula vazia" % (chave + (brl(v),)))
            elif isinstance(vm, str) or abs(vm - v) > 1e-9:
                tipo = "AVISO" if chave in ENTRADAS else "ERRO"
                quem = "entrada" if chave in ENTRADAS else "regra"
                linha(tipo, "%s!%s: %s diferente, a planilha tem %s e o motor abre com %s" % (chave + (quem, brl(v), vm if isinstance(vm, str) else brl(vm))))
            else:
                iguais += 1
    extras = sorted({k[0] for k in list(motor.formulas) + list(motor.valores)} - set(pla.abas))
    print("ok    %d células com a mesma fórmula ou o mesmo número na planilha e no motor" % iguais if not erros else
          "      %d células iguais na planilha e no motor" % iguais)
    for aba in extras:
        n = sum(1 for k in motor.formulas if k[0] == aba)
        print("info  aba «%s» só no motor: %d fórmulas (é a aba do gráfico)" % (aba, n) if aba == CURVA else
              "info  aba «%s» só no motor: %d fórmulas" % (aba, n))

    # 2. Os casos, com as mesmas entradas nos dois
    base = {k: v for k, v in pla.valores.items() if k in ENTRADAS}
    for caso in casos:
        ent = dict(base)
        ent.update({separa(r): v for r, v in caso["entradas"].items()})
        for ref, esperado in caso["esperado"].items():
            chave = separa(ref)
            vp, vmo = valor(pla, ent, chave), valor(motor, ent, chave)
            if isinstance(vp, str) or isinstance(vmo, str):
                linha("ERRO", "%s · %s: planilha %s | motor %s" % (caso["nome"], ref, vp, vmo))
                continue
            ok_p, ok_m = abs(vp - esperado) < 0.005, abs(vmo - esperado) < 0.005
            fmt = (lambda x: "%d" % x if x == int(x) else brl(x)) if isinstance(esperado, int) else brl
            texto = "%s · %s: planilha %s | motor %s | esperado %s" % (caso["nome"], ref, fmt(vp), fmt(vmo), fmt(esperado))
            if abs(vp - vmo) >= 0.005:
                linha("ERRO", texto + " (planilha e motor diferentes)")
            elif not (ok_p and ok_m):
                linha("ERRO", texto + " (os dois iguais, longe do esperado)")
            else:
                linha("ok", texto)

    # 3. A curva do gráfico contra a Calculadora
    if CURVA in motor.abas:
        n, diverge = 0, []
        precos = sorted({r for (aba, end) in motor.valores if aba == CURVA and end.startswith("A")
                         for r in [int(end[1:])]})
        kits = valor(pla, base, (LOTE, "B12"))
        custo = valor(pla, base, (LOTE, "B18"))
        for r in precos:
            p = motor.valores[(CURVA, "A%d" % r)]
            ent = dict(base)
            ent[(CAL, "B6")] = p
            renda_p = valor(pla, ent, (CAL, "B17"))
            renda_m = valor(motor, base, (CURVA, "B%d" % r))
            lucro_m = valor(motor, base, (CURVA, "C%d" % r))
            n += 1
            if isinstance(renda_m, str) or isinstance(lucro_m, str) or abs(renda_p - renda_m) >= 0.005 \
                    or abs((renda_p - custo) * kits - lucro_m) >= 0.005:
                diverge.append(p)
        primeiro, ultimo = motor.valores[(CURVA, "A%d" % precos[0])], motor.valores[(CURVA, "A%d" % precos[-1])]
        if diverge:
            linha("ERRO", "curva do gráfico: %d de %d preços diferentes da planilha, o primeiro em R$ %s" % (len(diverge), n, brl(diverge[0])))
        else:
            linha("ok", "curva do gráfico: %d preços de R$ %s a R$ %s, renda e lucro do lote iguais aos da planilha" % (n, brl(primeiro), brl(ultimo)))

    if erros:
        print("resultado: %d ERRO. Não publique: corrija o motor ou a planilha e rode de novo." % len(erros))
        sys.exit(1)
    print("resultado: tudo ok" + (" (%d AVISO)" % len(avisos) if avisos else ""))


if __name__ == "__main__":
    main()
