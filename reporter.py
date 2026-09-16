import locale
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