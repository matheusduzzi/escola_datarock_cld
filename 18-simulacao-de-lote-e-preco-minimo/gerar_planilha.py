"""Gera planilha_simulacao.xlsx: a calculadora de kit do case com a aba Simulação de lote.

Abas: Calculadora | Simulação de lote | Taxas. As fórmulas são as mesmas da planilha que o
Claude gerou no case. O arquivo sai sem nenhum valor calculado: o Excel, o LibreOffice ou o
Google Planilhas calculam ao abrir.

Uso:
    python3 gerar_planilha.py                  # grava planilha_simulacao.xlsx
    python3 gerar_planilha.py outro_nome.xlsx

Só usa a biblioteca padrão do Python: não precisa instalar nada.
"""
import sys
import zipfile
from xml.sax.saxutils import escape

# ---------- Estilos: (formato, fonte, preenchimento, borda, quebra de linha) ----------
BRL = '"R$" #,##0.00;[Red]-"R$" #,##0.00;"R$" 0.00'
PCT = '0.0%'
FONTES = [  # (tamanho, negrito, itálico, cor)
    (11, False, False, None),       # 0 texto
    (11, True, False, "0000FF"),    # 1 entrada: letra azul em negrito
    (11, True, False, None),        # 2 negrito
    (11, True, False, "FFFFFF"),    # 3 cabeçalho
    (15, True, False, None),        # 4 título
    (10, False, True, "595959"),    # 5 nota
    (11, False, False, "0000FF"),   # 6 regra editável: letra azul
    (13, True, False, None),        # 7 título da aba Taxas
    (11, False, False, "008000"),   # 8 valor puxado de outra aba: letra verde
]
FUNDOS = [None, None, "FFF2CC", "C55A11", "F2F2F2", "E2F0D9"]  # 2 amarelo, 3 laranja, 4 cinza, 5 verde
ESTILOS = {
    "texto": (None, 0, 0, 0, False),
    "titulo": (None, 4, 0, 0, False),
    "titulo_taxas": (None, 7, 0, 0, False),
    "nota": (None, 5, 0, 0, False),
    "rotulo_quebra": (None, 0, 0, 0, True),
    "negrito": (None, 2, 0, 0, False),
    "cabecalho": (None, 3, 3, 1, True),
    "entrada_n": ("0", 1, 2, 1, False),
    "entrada_brl": (BRL, 1, 2, 1, False),
    "entrada_milhar": ("#,##0", 1, 2, 1, False),
    "elo_n": ("0", 8, 0, 1, False),
    "elo_brl": (BRL, 8, 0, 1, False),
    "calc_milhar": ("#,##0", 0, 0, 1, False),
    "cabecalho_tabela": (None, 2, 4, 1, False),
    "preco_tabela": (BRL, 6, 0, 1, False),
    "regra_brl": (BRL, 6, 0, 1, False),
    "regra_pct": (PCT, 6, 0, 1, False),
    "calc_pct": (PCT, 0, 0, 1, False),
    "calc_brl": (BRL, 0, 0, 1, False),
    "total_rotulo": (None, 2, 4, 0, False),
    "total_brl": (BRL, 2, 4, 1, False),
    "resultado_rotulo": (None, 2, 5, 0, False),
    "resultado_brl": (BRL, 2, 5, 1, False),
}


def planilha():
    """Devolve as abas na ordem: {nome: {"celulas": {endereço: (valor, estilo)}, "larguras": {...}}}."""
    tx = {}
    tx["A1"] = ("Tabela de comissão por faixa de preço do item", "titulo_taxas")
    for col, titulo in zip("ABC", ["Preço a partir de (R$)", "Comissão (%)", "Taxa fixa por item (R$)"]):
        tx[col + "3"] = (titulo, "cabecalho")
    faixas = [(0, 0.20, 4.50), (80, 0.14, 16), (100, 0.14, 20), (200, 0.14, 26)]
    for linha, (a, b, c) in enumerate(faixas, start=4):
        tx["A%d" % linha] = (a, "regra_brl")
        tx["B%d" % linha] = (b, "regra_pct")
        tx["C%d" % linha] = (c, "regra_brl")
    tx["A9"] = ("Parâmetros gerais", "negrito")
    tx["A10"] = ("Preço abaixo do qual a taxa fixa vira metade do preço (R$)", "rotulo_quebra")
    tx["B10"] = (8, "regra_brl")
    tx["A11"] = ("Recarga Automática (pedido): % do valor do pedido, como no extrato", "rotulo_quebra")
    tx["B11"] = (0.02, "regra_pct")
    notas = [
        "Regras da Shopee Brasil para vendedor CNPJ em outubro de 2026, conciliadas com um extrato real.",
        "Taxa fixa até R$ 79,99: R$ 4,50 a partir de 01/10/2026 (era R$ 4,00).",
        "As células em azul são as regras: se a regra mudar, edite aqui e a Calculadora acompanha.",
    ]
    for linha, nota in enumerate(notas, start=13):
        tx["A%d" % linha] = (nota, "nota")

    ca = {}
    ca["A1"] = ("Calculadora de kit", "titulo")
    ca["A2"] = ("Preencha só as células amarelas (letra azul). O resto é calculado pelas fórmulas.", "nota")
    ca["A4"] = ("ENTRADAS", "cabecalho")
    ca["B4"] = ("", "cabecalho")
    ca["A5"] = ("Quantidade de itens no kit", "texto")
    ca["B5"] = (3, "entrada_n")
    ca["A6"] = ("Valor cobrado pelo kit (R$)", "texto")
    ca["B6"] = (10.90, "entrada_brl")
    ca["A8"] = ("TAXAS POR PEDIDO", "cabecalho")
    ca["B8"] = ("", "cabecalho")
    linhas = [
        (9, "Faixa de preço aplicada (comissão %)",
         "=INDEX(Taxas!$B$4:$B$7,MATCH($B$6,Taxas!$A$4:$A$7,1))", "calc_pct"),
        (10, "Comissão (já inclui a taxa de transação)", "=-ROUND($B$6*B9,2)", "calc_brl"),
        (11, "Taxa por item vendido (o kit conta como 1 item)",
         "=-ROUND(IF($B$6<Taxas!$B$10,$B$6/2,INDEX(Taxas!$C$4:$C$7,MATCH($B$6,Taxas!$A$4:$A$7,1))),2)", "calc_brl"),
        (12, "Recarga Automática (pedido)", "=-ROUND($B$6*Taxas!$B$11,2)", "calc_brl"),
        (13, "Total de taxas", "=SUM(B10:B12)", "total_brl"),
        (14, "Taxas como % do preço", "=IF($B$6=0,0,-B13/$B$6)", "calc_pct"),
    ]
    for linha, rotulo, formula, estilo in linhas:
        ca["A%d" % linha] = (rotulo, "total_rotulo" if linha == 13 else "texto")
        ca["B%d" % linha] = (formula, estilo)
    ca["A16"] = ("RESULTADO", "cabecalho")
    ca["B16"] = ("", "cabecalho")
    ca["A17"] = ("RENDA DO PEDIDO (o que sobra do kit)", "resultado_rotulo")
    ca["B17"] = ("=$B$6+B13", "resultado_brl")
    ca["A19"] = ("Observações", "negrito")
    obs = [
        "A taxa fixa é cobrada por item vendido: o kit anunciado como 1 anúncio paga uma vez só.",
        "Abaixo de R$ 8, a taxa fixa por item é metade do preço.",
        "Frete subsidiado pela Shopee não muda a renda (valor pago = desconto).",
        "Teste: 3 itens a R$ 10,90, com recarga de 2%, dá renda de R$ 4,00, igual ao extrato real.",
        "A renda é antes do custo do produto, da embalagem, do imposto e dos anúncios.",
    ]
    for linha, texto in enumerate(obs, start=20):
        ca["A%d" % linha] = (texto, "nota")
    return {
        "Calculadora": {"celulas": ca, "larguras": {1: 52, 2: 18}},
        "Simulação de lote": {"celulas": lote(), "larguras": {1: 52, 2: 20, 3: 20, 4: 20, 5: 20}},
        "Taxas": {"celulas": tx, "larguras": {1: 52, 2: 16, 3: 24}},
    }


def lote():
    """Aba Simulação de lote, célula a célula como no case."""
    sm = {}
    sm["A1"] = ("Simulação de lote: compra de potes, kits e lucro", "titulo")
    sm["A2"] = ("Preencha só as células amarelas. Itens por kit e preço vêm da aba Calculadora.", "nota")
    sm["A4"] = ("ENTRADAS", "cabecalho")
    sm["B4"] = ("", "cabecalho")
    for linha, rotulo, valor, estilo in [(5, "Quantidade de potes comprados", 1000, "entrada_milhar"),
                                         (6, "Custo por pote (R$)", 0.97, "entrada_brl"),
                                         (8, "Embalagem por kit (R$)", 5.00, "entrada_brl"),
                                         (9, "Frete do lote (R$)", 50.00, "entrada_brl")]:
        sm["A%d" % linha] = (rotulo, "texto")
        sm["B%d" % linha] = (valor, estilo)
    sm["A7"] = ("Itens por kit (vem da aba Calculadora)", "texto")
    sm["B7"] = ("=Calculadora!B5", "elo_n")
    sm["A11"] = ("CUSTO DO LOTE", "cabecalho")
    sm["B11"] = ("", "cabecalho")
    for linha, rotulo, formula, estilo in [
        (12, "Kits montados", "=IF($B$7=0,0,INT($B$5/$B$7))", "calc_milhar"),
        (13, "Potes que sobram", "=$B$5-$B$12*$B$7", "calc_milhar"),
        (14, "Custo dos potes usados nos kits", "=$B$12*$B$7*$B$6", "calc_brl"),
        (15, "Custo das embalagens", "=$B$12*$B$8", "calc_brl"),
        (16, "Frete do lote", "=$B$9", "calc_brl"),
        (17, "Investimento total", "=SUM(B14:B16)", "total_brl"),
        (18, "Custo por kit", "=IF($B$12=0,0,B17/$B$12)", "calc_brl"),
    ]:
        sm["A%d" % linha] = (rotulo, "total_rotulo" if linha == 17 else "texto")
        sm["B%d" % linha] = (formula, estilo)
    sm["A20"] = ("RESULTADO NO PREÇO DA ABA CALCULADORA", "cabecalho")
    sm["B20"] = ("", "cabecalho")
    for linha, rotulo, formula, estilo in [
        (21, "Preço do kit", "=Calculadora!B6", "elo_brl"),
        (22, "Renda do pedido", "=Calculadora!B17", "elo_brl"),
        (23, "Lucro por kit", "=B22-B18", "calc_brl"),
        (24, "LUCRO FINAL DO LOTE", "=B23*B12", "resultado_brl"),
        (25, "Retorno sobre o investimento", "=IF($B$17=0,0,B24/$B$17)", "calc_pct"),
        (26, "Preço mínimo para não ter prejuízo (faixa até R$ 79,99)",
         "=(Taxas!C4+B18)/(1-Taxas!B4-Taxas!B11)", "calc_brl"),
    ]:
        sm["A%d" % linha] = (rotulo, "resultado_rotulo" if linha == 24 else "texto")
        sm["B%d" % linha] = (formula, estilo)
    sm["A28"] = ("SIMULAÇÃO POR PREÇO DO KIT (edite os preços em azul)", "cabecalho")
    for col in "BCDE":
        sm[col + "28"] = ("", "cabecalho")
    for col, titulo in zip("ABCDE", ["Preço do kit", "Renda do pedido", "Lucro por kit", "Lucro final do lote",
                                     "Retorno"]):
        sm[col + "29"] = (titulo, "cabecalho_tabela")
    for linha, preco in enumerate([19.90, 24.90, 29.90, 34.90, 39.90, 49.90], start=30):
        a = "A%d" % linha
        sm[a] = (preco, "preco_tabela")
        # renda do pedido para o preço da linha: a lógica da Calculadora numa fórmula só
        sm["B%d" % linha] = ("=%s-ROUND(%s*INDEX(Taxas!$B$4:$B$7,MATCH(%s,Taxas!$A$4:$A$7,1)),2)"
                             "-ROUND(IF(%s<Taxas!$B$10,%s/2,INDEX(Taxas!$C$4:$C$7,MATCH(%s,Taxas!$A$4:$A$7,1))),2)"
                             "-ROUND(%s*Taxas!$B$11,2)" % ((a,) * 7), "calc_brl")
        sm["C%d" % linha] = ("=B%d-$B$18" % linha, "calc_brl")
        sm["D%d" % linha] = ("=C%d*$B$12" % linha, "calc_brl")
        sm["E%d" % linha] = ("=IF($B$17=0,0,D%d/$B$17)" % linha, "calc_pct")
    sm["A37"] = ("Resultado antes de imposto e anúncios. Embalagem considerada por kit; frete é o do lote de potes.",
                 "nota")
    return sm


# ---------- Gravação do .xlsx (Office Open XML) ----------
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _coluna(endereco):
    letras = "".join(ch for ch in endereco if ch.isalpha())
    numero = 0
    for ch in letras:
        numero = numero * 26 + ord(ch) - 64
    return numero, int(endereco[len(letras):])


def _estilos():
    formatos = sorted({e[0] for e in ESTILOS.values() if e[0] and e[0] != "0"})
    id_formato = {f: 164 + i for i, f in enumerate(formatos)}
    id_formato["0"] = 1
    xs = ['<numFmts count="%d">' % len(formatos)]
    xs += ['<numFmt numFmtId="%d" formatCode="%s"/>' % (id_formato[f], escape(f, {'"': "&quot;"})) for f in formatos]
    xs.append('</numFmts><fonts count="%d">' % len(FONTES))
    for tam, neg, ita, cor in FONTES:
        xs.append("<font>%s%s<sz val=\"%d\"/>%s<name val=\"Arial\"/></font>" % (
            "<b/>" if neg else "", "<i/>" if ita else "", tam, '<color rgb="FF%s"/>' % cor if cor else ""))
    xs.append('</fonts><fills count="%d">' % len(FUNDOS))
    xs.append('<fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>')
    for cor in FUNDOS[2:]:
        xs.append('<fill><patternFill patternType="solid"><fgColor rgb="FF%s"/><bgColor indexed="64"/></patternFill></fill>' % cor)
    lado = '<%s style="thin"><color rgb="FFBFBFBF"/></%s>'
    xs.append('</fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border>'
              + "".join(lado % (l, l) for l in ("left", "right", "top", "bottom")) + "<diagonal/></border></borders>")
    xs.append('<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>')
    nomes = list(ESTILOS)
    xs.append('<cellXfs count="%d">' % len(nomes))
    for nome in nomes:
        fmt, fonte, fundo, borda, quebra = ESTILOS[nome]
        xs.append('<xf numFmtId="%d" fontId="%d" fillId="%d" borderId="%d" xfId="0" applyNumberFormat="1" '
                  'applyFont="1" applyFill="1" applyBorder="1"%s>%s</xf>' % (
                      id_formato.get(fmt, 0), fonte, fundo, borda, ' applyAlignment="1"' if quebra else "",
                      '<alignment wrapText="1" vertical="top"/>' if quebra else ""))
    xs.append('</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<styleSheet xmlns="%s">' % NS
            + "".join(xs) + "</styleSheet>"), {n: i for i, n in enumerate(nomes)}


def _aba(aba, indice_estilo):
    por_linha = {}
    for endereco, (valor, estilo) in aba["celulas"].items():
        col, lin = _coluna(endereco)
        por_linha.setdefault(lin, []).append((col, endereco, valor, estilo))
    linhas = []
    for lin in sorted(por_linha):
        celulas = []
        for col, endereco, valor, estilo in sorted(por_linha[lin]):
            s = indice_estilo[estilo]
            if isinstance(valor, str) and valor.startswith("="):
                celulas.append('<c r="%s" s="%d"><f>%s</f></c>' % (endereco, s, escape(valor[1:])))
            elif isinstance(valor, str):
                celulas.append('<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                               % (endereco, s, escape(valor)))
            else:
                celulas.append('<c r="%s" s="%d"><v>%s</v></c>' % (endereco, s, repr(valor)))
        linhas.append('<row r="%d">%s</row>' % (lin, "".join(celulas)))
    colunas = "".join('<col min="%d" max="%d" width="%s" customWidth="1"/>' % (c, c, w)
                      for c, w in sorted(aba["larguras"].items()))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="%s" xmlns:r="%s">'
            '<sheetViews><sheetView workbookViewId="0" showGridLines="0"/></sheetViews>'
            '<cols>%s</cols><sheetData>%s</sheetData></worksheet>' % (NS, NS_R, colunas, "".join(linhas)))


def salvar(abas, caminho):
    estilos, indice_estilo = _estilos()
    nomes = list(abas)
    tipos = ['<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/'
             'vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1) for i in range(len(nomes))]
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + "".join(tipos) + "</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
            'officeDocument" Target="xl/workbook.xml"/></Relationships>')
    folhas = "".join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escape(n), i + 1, i + 1)
                     for i, n in enumerate(nomes))
    # fullCalcOnLoad: quem abrir o arquivo calcula todas as fórmulas na hora.
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="%s" xmlns:r="%s">'
                '<bookViews><workbookView activeTab="0"/></bookViews><sheets>%s</sheets>'
                '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>' % (NS, NS_R, folhas))
    wb_rels = "".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                      'relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1)
                      for i in range(len(nomes)))
    wb_rels += ('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/styles" Target="styles.xml"/>' % (len(nomes) + 1))
    wb_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships '
               'xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + wb_rels + "</Relationships>")
    partes = [("[Content_Types].xml", content_types), ("_rels/.rels", rels), ("xl/workbook.xml", workbook),
              ("xl/_rels/workbook.xml.rels", wb_rels), ("xl/styles.xml", estilos)]
    partes += [("xl/worksheets/sheet%d.xml" % (i + 1), _aba(abas[nome], indice_estilo)) for i, nome in enumerate(nomes)]
    with zipfile.ZipFile(caminho, "w") as z:
        for nome, conteudo in partes:
            # Data fixa: o mesmo conteúdo gera sempre o mesmo arquivo.
            info = zipfile.ZipInfo(nome, date_time=(2026, 11, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, conteudo.encode("utf-8"))


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "planilha_simulacao.xlsx"
    salvar(planilha(), destino)
    print("ok: " + destino + " (abas Calculadora, Simulação de lote e Taxas; abra no Excel, LibreOffice ou "
          "Google Planilhas)")
