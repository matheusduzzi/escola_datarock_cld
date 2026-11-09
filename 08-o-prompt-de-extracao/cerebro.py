"""Funções que montar.py, validar.py e contar.py usam juntas. Só biblioteca padrão do Python."""
import json
import re
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
LOTES = {1: ["reuniao-01", "reuniao-02", "reuniao-03"],
         2: ["reuniao-04", "reuniao-05", "reuniao-06"],
         3: ["reuniao-07", "reuniao-08", "reuniao-09"],
         4: ["reuniao-10", "reuniao-11", "reuniao-12"]}
TODAS = [r for ids in LOTES.values() for r in ids]
CAMPOS_LISTA = {"pessoas": 12, "projetos": 8, "empresas": 6, "decisoes": 5}
TEMAS = (2, 5)
MAX_ACOES = 8
CHAVES = {"id", "resumo", "pessoas", "projetos", "temas", "empresas", "decisoes", "acoes"}
CHAVES_ACAO = {"responsavel", "tarefa", "prazo"}
# Mesma normalização do case: sem acento, minúsculas, só letras e números.
CORP = set("s sa ltda me eireli inc llc corp co grupo group holding".split())


def norm(texto):
    s = unicodedata.normalize("NFD", str(texto or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def norm_empresa(texto):
    """Empresa ignora sufixo societário: 'Fio Nobre Têxtil S.A.' = 'Fio Nobre Têxtil'."""
    return " ".join(t for t in norm(texto).split() if t not in CORP and len(t) > 1)


def ler_resumo(rid):
    texto = (PASTA / "resumos" / (rid + ".md")).read_text(encoding="utf-8")
    cabecalho, corpo = texto.split("\n\n", 1)
    campos = dict(linha.split(": ", 1) for linha in cabecalho.splitlines())
    return campos, corpo.strip()


def ler_resposta(arquivo):
    """Lê a resposta do Claude como JSON estrito. Retorna (dados, erros)."""
    bruto = Path(arquivo).read_text(encoding="utf-8").strip()
    if bruto.startswith("```"):
        return None, ["a resposta veio dentro de cercas de código (```): salve só o JSON"]
    if not bruto.startswith("{"):
        return None, ["há texto antes do JSON: a resposta precisa começar com {"]
    try:
        return json.loads(bruto), []
    except json.JSONDecodeError as e:
        return None, [f"JSON inválido na linha {e.lineno}, coluna {e.colno}: {e.msg}"]


def _lista_de_textos(valor):
    return isinstance(valor, list) and all(isinstance(x, str) and x.strip() for x in valor)


def validar_lote(arquivo, ids):
    """Confere formato, ids e limites de um lote. Retorna (reunioes por id, erros)."""
    dados, erros = ler_resposta(arquivo)
    if erros:
        return {}, erros
    if not isinstance(dados, dict) or set(dados) != {"reunioes"}:
        return {}, ['o JSON precisa ser um objeto com uma única chave, "reunioes"']
    lista = dados["reunioes"]
    if not isinstance(lista, list):
        return {}, ['"reunioes" precisa ser uma lista']
    achadas = {}
    for i, r in enumerate(lista, 1):
        if not isinstance(r, dict):
            erros.append(f"item {i}: não é um objeto")
            continue
        rid = r.get("id")
        nome = rid if isinstance(rid, str) and rid else f"item {i}"
        if "id" not in r or not rid:
            erros.append(f"item {i}: sem id")
        elif rid not in ids:
            erros.append(f"{nome}: id fora desse lote (esperado um de {', '.join(ids)})")
        elif rid in achadas:
            erros.append(f"{nome}: id repetido")
        faltam = CHAVES - set(r) - {"id"}
        sobram = set(r) - CHAVES
        if faltam:
            erros.append(f"{nome}: faltam as chaves {', '.join(sorted(faltam))}")
        if sobram:
            erros.append(f"{nome}: chaves que o formato não tem: {', '.join(sorted(sobram))}")
        if "resumo" in r and not (isinstance(r["resumo"], str) and r["resumo"].strip()):
            erros.append(f"{nome}: resumo vazio ou não é texto")
        for campo, limite in list(CAMPOS_LISTA.items()) + [("temas", TEMAS[1])]:
            if campo not in r:
                continue
            valor = r[campo]
            if not _lista_de_textos(valor):
                erros.append(f"{nome}: {campo} precisa ser uma lista de textos não vazios")
                continue
            if len(valor) > limite:
                erros.append(f"{nome}: {campo} tem {len(valor)} itens (máximo {limite})")
            normas = [norm(x) for x in valor]
            if len(set(normas)) < len(normas):
                erros.append(f"{nome}: {campo} repete o mesmo nome")
        if "temas" in r and _lista_de_textos(r["temas"]) and len(r["temas"]) < TEMAS[0]:
            erros.append(f"{nome}: temas tem {len(r['temas'])} item (mínimo {TEMAS[0]})")
        if "acoes" in r:
            acoes = r["acoes"]
            if not isinstance(acoes, list):
                erros.append(f"{nome}: acoes precisa ser uma lista")
            else:
                if len(acoes) > MAX_ACOES:
                    erros.append(f"{nome}: acoes tem {len(acoes)} itens (máximo {MAX_ACOES})")
                for j, a in enumerate(acoes, 1):
                    if not isinstance(a, dict) or set(a) != CHAVES_ACAO:
                        erros.append(f"{nome}: ação {j} precisa ter exatamente responsavel, tarefa e prazo")
                    elif not all(isinstance(a[k], str) for k in CHAVES_ACAO) or not a["tarefa"].strip():
                        erros.append(f"{nome}: ação {j} com valor que não é texto ou tarefa vazia")
        if isinstance(rid, str) and rid in ids and rid not in achadas:
            achadas[rid] = r
    for rid in ids:
        if rid not in achadas:
            erros.append(f"faltou a {rid}")
    return achadas, erros


def validar_pasta(pasta, lotes=None):
    """Valida lote-N.json de uma pasta. Retorna (reunioes por id, erros por arquivo)."""
    pasta = Path(pasta)
    reunioes, relatorio = {}, {}
    for n in lotes or sorted(LOTES):
        arquivo = pasta / f"lote-{n}.json"
        if not arquivo.is_file():
            relatorio[arquivo.name] = ["arquivo não encontrado"]
            continue
        achadas, erros = validar_lote(arquivo, LOTES[n])
        relatorio[arquivo.name] = erros
        if not erros:
            reunioes.update(achadas)
    return reunioes, relatorio
