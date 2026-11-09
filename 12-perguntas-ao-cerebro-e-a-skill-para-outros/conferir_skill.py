"""Olha se a pasta da skill tem o formato que o Claude aceita no upload. Não julga o conteúdo.

Uso:
  python3 conferir_skill.py [pasta-da-skill]      (padrão: cerebro-aurora)

Limites da central de ajuda do Claude (como criar skills, aberta em 07/11/2026): o arquivo começa
com o cabeçalho YAML entre linhas ---, com name (até 64 caracteres) e description (até 200
caracteres), e a pasta tem o mesmo nome da skill. O Claude Code aceita description mais longa;
o limite de 200 é o do upload no app.
"""
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent


def campos(cabecalho):
    """Lê name e description do cabeçalho, inclusive description em várias linhas recuadas."""
    saida, atual = {}, None
    for linha in cabecalho:
        m = re.match(r"^([a-z_]+):\s*(.*)$", linha)
        if m:
            atual = m.group(1)
            saida[atual] = m.group(2).strip()
        elif atual and linha.startswith((" ", "\t")):
            saida[atual] = (saida[atual] + " " + linha.strip()).strip()
    return saida


def conferir(pasta):
    problemas = []
    arquivo = pasta / "SKILL.md"
    if not arquivo.is_file():
        return [f"não achei {pasta.name}/SKILL.md"]
    linhas = arquivo.read_text(encoding="utf-8").split("\n")
    if linhas[0].strip() != "---":
        return ["a primeira linha precisa ser --- (o cabeçalho com name e description)"]
    try:
        fim = linhas.index("---", 1)
    except ValueError:
        return ["o cabeçalho não fecha: falta a segunda linha ---"]
    c = campos(linhas[1:fim])
    nome, desc = c.get("name", ""), c.get("description", "")
    if not nome:
        problemas.append("falta name no cabeçalho")
    elif len(nome) > 64:
        problemas.append(f"name tem {len(nome)} caracteres; o limite é 64")
    elif nome != pasta.name:
        problemas.append(f'name é "{nome}", mas a pasta se chama "{pasta.name}"; os dois precisam ser iguais')
    if not desc or "<" in desc:
        problemas.append("falta escrever a description (o Claude lê ela para decidir quando usar a skill)")
    elif len(desc) > 200:
        problemas.append(f"description tem {len(desc)} caracteres; o upload no app aceita até 200")
    corpo = "\n".join(linhas[fim + 1:])
    if not corpo.strip():
        problemas.append("o corpo da skill está vazio")
    elif "<" in re.sub(r"`[^`]*`", "", corpo):
        problemas.append("ainda há espaço do modelo para preencher (texto entre < >)")
    return problemas


def main(argv):
    pasta = Path(argv[0]) if argv else PASTA / "cerebro-aurora"
    if not pasta.is_absolute():
        pasta = Path.cwd() / pasta
    problemas = conferir(pasta)
    if problemas:
        print(f"{pasta.name}: a skill ainda não está no formato do upload")
        for p in problemas:
            print("  - " + p)
        return 1
    texto = (pasta / "SKILL.md").read_text(encoding="utf-8")
    c = campos(texto.split("\n")[1:texto.split("\n").index("---", 1)])
    print(f"{pasta.name}: formato ok (name com {len(c['name'])} caracteres, description com {len(c['description'])})")
    print("o formato não diz se as regras estão certas: teste a skill com as perguntas da aula.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
