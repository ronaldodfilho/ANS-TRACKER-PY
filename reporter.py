import csv
import locale
from pathlib import Path

from config import PASTA_DIFFS
from models import ResumoDiff

try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "English_United States.1252")
    except locale.Error:
        pass

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
NEGRITO = "\033[1m"
RESET = "\033[0m"


def _formatar_numero(valor: int) -> str:
    try:
        return locale.format_string("%d", valor, grouping=True)
    except Exception:
        return str(valor)


def imprimir_resumo(resumo: ResumoDiff) -> None:
    cabecalho = f"ANS Health Tracker  |  {resumo.periodo_anterior} -> {resumo.periodo_atual}"
    separador = "=" * len(cabecalho)

    print(f"\n{NEGRITO}{AZUL}{separador}{RESET}")
    print(f"{NEGRITO}{AZUL}{cabecalho}{RESET}")
    print(f"{NEGRITO}{AZUL}{separador}{RESET}\n")

    print(f"  {VERDE}Novos registros:{RESET}    {_formatar_numero(len(resumo.adicionados))}")
    print(f"  {VERMELHO}Removidos:{RESET}          {_formatar_numero(len(resumo.removidos))}")
    print(f"  {AMARELO}Alterados:{RESET}          {_formatar_numero(len(resumo.alteracoes))}")
    print(f"  {VERMELHO}Inconsistencias:{RESET}    {_formatar_numero(len(resumo.inconsistencias))}")

    criticas = resumo.alteracoes_criticas
    if criticas:
        print(f"\n{NEGRITO}--- Mudancas criticas ---{RESET}")
        for alt in criticas:
            print(
                f"  {AMARELO}[!]{RESET} {alt.razao_social} (ANS {alt.registro_ans}): "
                f"{alt.campo}  {VERMELHO}{alt.valor_anterior}{RESET} -> {VERDE}{alt.valor_atual}{RESET}"
            )

    if resumo.inconsistencias:
        print(f"\n{NEGRITO}--- Inconsistencias ---{RESET}")
        for inc in resumo.inconsistencias:
            print(
                f"  {VERMELHO}[x]{RESET} {inc.tipo}: {inc.razao_social} "
                f"(ANS {inc.registro_ans}) -- {inc.descricao}"
            )

    print()


def exportar_csv_diff(resumo: ResumoDiff) -> Path:
    Path(PASTA_DIFFS).mkdir(parents=True, exist_ok=True)

    nome_arquivo = f"diff_{resumo.periodo_anterior}_{resumo.periodo_atual}.csv"
    caminho = Path(PASTA_DIFFS) / nome_arquivo

    cabecalho = ["registro_ans", "razao_social", "tipo_mudanca", "campo", "valor_anterior", "valor_atual"]
    linhas = []

    for registro in resumo.adicionados:
        linhas.append({
            "registro_ans": registro.get("registro_ans", ""),
            "razao_social": registro.get("razao_social", ""),
            "tipo_mudanca": "adicionado",
            "campo": "",
            "valor_anterior": "",
            "valor_atual": "",
        })

    for registro in resumo.removidos:
        linhas.append({
            "registro_ans": registro.get("registro_ans", ""),
            "razao_social": registro.get("razao_social", ""),
            "tipo_mudanca": "removido",
            "campo": "",
            "valor_anterior": "",
            "valor_atual": "",
        })

    for alt in resumo.alteracoes:
        linhas.append({
            "registro_ans": alt.registro_ans,
            "razao_social": alt.razao_social,
            "tipo_mudanca": "alterado",
            "campo": alt.campo,
            "valor_anterior": alt.valor_anterior,
            "valor_atual": alt.valor_atual,
        })

    for inc in resumo.inconsistencias:
        linhas.append({
            "registro_ans": inc.registro_ans,
            "razao_social": inc.razao_social,
            "tipo_mudanca": "inconsistencia",
            "campo": inc.tipo,
            "valor_anterior": "",
            "valor_atual": inc.descricao,
        })

    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=cabecalho)
        escritor.writeheader()
        escritor.writerows(linhas)

    return caminho