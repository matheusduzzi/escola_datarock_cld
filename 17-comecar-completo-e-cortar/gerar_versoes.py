"""Gera as quatro versões da planilha calculadora do case, da primeira, com campos demais, à final.

    versao_1.xlsx  entradas: itens no kit, preço, % de recarga, vendedor CPF com mais de 450
                   pedidos (Sim/Não), custo por item e imposto; vários resultados
    versao_2.xlsx  sem o campo de CPF, o custo e o imposto (pedido 7)
    versao_3.xlsx  a recarga sai das entradas e vira regra na aba Taxas (pedido 8)
    versao_4.xlsx  um resultado só: a renda do pedido (pedido 9)

O case guarda os campos de cada versão, não os arquivos. A versão 4 é a planilha final do case,
a mesma de gerar_planilha.py. As versões 1 a 3 foram remontadas a partir dela, com os campos que
o case lista para cada uma.

Uso:
    python3 gerar_versoes.py

Só usa a biblioteca padrão do Python: não precisa instalar nada.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_planilha as G  # noqa: E402

G.ESTILOS.setdefault("entrada_pct", (G.PCT, 1, 2, 1, False))
G.ESTILOS.setdefault("entrada_txt", (None, 1, 2, 1, False))


def _linha(endereco):
    return G._coluna(endereco)[1]


def versao_4():
    return G.planilha()


def versao_3():
    abas = G.planilha()
    ca = abas["Calculadora"]["celulas"]
    # As observações descem uma linha para caber o segundo resultado.
    notas = {k: v for k, v in ca.items() if _linha(k) >= 19}
    for k in notas:
        del ca[k]
    for k, v in notas.items():
        ca["A%d" % (_linha(k) + 1)] = v
    ca["A18"] = ("Renda por item do kit", "texto")
    ca["B18"] = ("=IF($B$5=0,0,ROUND(B17/$B$5,2))", "calc_brl")
    return abas


def versao_2():
    abas = versao_3()
    tx, ca = abas["Taxas"]["celulas"], abas["Calculadora"]["celulas"]
    del tx["A11"], tx["B11"]
    ca["A7"] = ("Recarga Automática (pedido): % do valor do pedido", "texto")
    ca["B7"] = (0.02, "entrada_pct")
    ca["B12"] = ("=-ROUND($B$6*$B$7,2)", "calc_brl")
    return abas


def versao_1():
    abas = versao_2()
    tx = abas["Taxas"]["celulas"]
    tx["A11"] = ("Adicional por item para vendedor CPF com mais de 450 pedidos em 90 dias (R$)", "rotulo_quebra")
    tx["B11"] = (3, "regra_brl")
    velha = abas["Calculadora"]["celulas"]
    ca = {k: velha[k] for k in ("A1", "A2", "A4", "B4", "A5", "B5", "A6", "B6", "A7", "B7")}
    ca["A8"] = ("Vendedor CPF com mais de 450 pedidos em 90 dias? (Sim/Não)", "texto")
    ca["B8"] = ("Não", "entrada_txt")
    ca["A9"] = ("Custo por item (R$)", "texto")
    ca["B9"] = (0.0, "entrada_brl")
    ca["A10"] = ("Imposto sobre a venda (%)", "texto")
    ca["B10"] = (0.0, "entrada_pct")
    ca["A12"], ca["B12"] = ("TAXAS POR PEDIDO", "cabecalho"), ("", "cabecalho")
    linhas = [
        (13, "Faixa de preço aplicada (comissão %)",
         "=INDEX(Taxas!$B$4:$B$7,MATCH($B$6,Taxas!$A$4:$A$7,1))", "calc_pct", "texto"),
        (14, "Comissão (já inclui a taxa de transação)", "=-ROUND($B$6*B13,2)", "calc_brl", "texto"),
        (15, "Taxa por item vendido (o kit conta como 1 item)",
         "=-ROUND(IF($B$6<Taxas!$B$10,$B$6/2,INDEX(Taxas!$C$4:$C$7,MATCH($B$6,Taxas!$A$4:$A$7,1))),2)",
         "calc_brl", "texto"),
        (16, "Adicional de vendedor CPF", '=-IF($B$8="Sim",Taxas!$B$11,0)', "calc_brl", "texto"),
        (17, "Recarga Automática (pedido)", "=-ROUND($B$6*$B$7,2)", "calc_brl", "texto"),
        (18, "Total de taxas", "=SUM(B14:B17)", "total_brl", "total_rotulo"),
        (19, "Taxas como % do preço", "=IF($B$6=0,0,-B18/$B$6)", "calc_pct", "texto"),
    ]
    for linha, rotulo, formula, estilo, estilo_rotulo in linhas:
        ca["A%d" % linha] = (rotulo, estilo_rotulo)
        ca["B%d" % linha] = (formula, estilo)
    ca["A21"], ca["B21"] = ("RESULTADO", "cabecalho"), ("", "cabecalho")
    resultados = [
        (22, "RENDA DO PEDIDO (o que sobra do kit)", "=$B$6+B18", "resultado_brl", "resultado_rotulo"),
        (23, "Renda por item do kit", "=IF($B$5=0,0,ROUND(B22/$B$5,2))", "calc_brl", "texto"),
        (24, "Custo do kit", "=-ROUND($B$5*$B$9,2)", "calc_brl", "texto"),
        (25, "Imposto sobre a venda", "=-ROUND($B$6*$B$10,2)", "calc_brl", "texto"),
        (26, "LUCRO DO KIT", "=B22+B24+B25", "resultado_brl", "resultado_rotulo"),
    ]
    for linha, rotulo, formula, estilo, estilo_rotulo in resultados:
        ca["A%d" % linha] = (rotulo, estilo_rotulo)
        ca["B%d" % linha] = (formula, estilo)
    ca["A28"] = ("Observações", "negrito")
    obs = [
        "A taxa fixa é cobrada por item vendido: o kit anunciado como 1 anúncio paga uma vez só.",
        "Abaixo de R$ 8, a taxa fixa por item é metade do preço.",
        "O adicional de CPF só vale para vendedor CPF com mais de 450 pedidos em 90 dias.",
        "Teste: 3 itens a R$ 10,90, com recarga de 2%, dá renda de R$ 4,00, igual ao extrato real.",
    ]
    for linha, texto in enumerate(obs, start=29):
        ca["A%d" % linha] = (texto, "nota")
    abas["Calculadora"]["celulas"] = ca
    return abas


VERSOES = [("versao_1.xlsx", versao_1), ("versao_2.xlsx", versao_2),
           ("versao_3.xlsx", versao_3), ("versao_4.xlsx", versao_4)]

if __name__ == "__main__":
    for nome, montar in VERSOES:
        G.salvar(montar(), nome)
        print("ok: " + nome)
    print("Abra no Excel, LibreOffice ou Google Planilhas. Cada versão calcula ao abrir.")
