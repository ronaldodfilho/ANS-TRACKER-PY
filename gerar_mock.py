import random
from pathlib import Path

MODALIDADES = [
    "Cooperativa Medica",
    "Medicina de Grupo",
    "Seguradora Especializada em Saude",
    "Cooperativa Odontologica",
    "Odontologia de Grupo",
    "Administradora de Beneficios",
    "Filantropia",
    "Autogestao",
]

SITUACOES = ["Ativa", "Ativa", "Ativa", "Ativa", "Cancelada", "Em Liquidacao"]

UEFS = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "GO", "PE", "CE"]

NOMES_BASE = [
    "SAUDE TOTAL", "VIDA PLENA", "MASTER SAUDE", "UNIMED", "AMIL",
    "BRADESCO SAUDE", "SUL AMERICA", "HAPVIDA", "NOTREDAME", "PREVENT SENIOR",
    "GOLDEN CROSS", "OMINT", "ALLIANZ SAUDE", "PORTO SEGURO SAUDE", "CARE PLUS",
    "INTERMEDIO", "MEDIAL SAUDE", "ASSIM SAUDE", "SANTA CASA", "SAUDE CAIXA",
]


def _gerar_cnpj_valido() -> str:
    return str(random.randint(10000000000000, 99999999999999))


def _gerar_registro_ans(indice: int) -> str:
    return str(indice + 300000).zfill(6)


def _gerar_operadora(indice: int, variacao: int = 0) -> dict:
    random.seed(indice)
    nome = random.choice(NOMES_BASE)
    sufixo = random.choice(["LTDA", "S.A.", "COOPERATIVA", "ASSOCIACAO"])
    modalidade = random.choice(MODALIDADES)
    uf = random.choice(UEFS)
    situacao = random.choice(SITUACOES)
    cnpj = _gerar_cnpj_valido()

    if variacao > 0:
        random.seed(indice + variacao * 1000)
        modalidade = random.choice(MODALIDADES)
        situacao = random.choice(SITUACOES)

    return {
        "Registro ANS": _gerar_registro_ans(indice),
        "CNPJ": cnpj,
        "Razao Social": f"{nome} {sufixo}",
        "Nome Fantasia": nome,
        "Modalidade": modalidade,
        "Logradouro": f"Rua das Flores, {random.randint(1, 999)}",
        "Numero": str(random.randint(1, 9999)),
        "Complemento": "",
        "Bairro": "Centro",
        "Cidade": "Sao Paulo",
        "UF": uf,
        "CEP": f"{random.randint(10000000, 99999999):08d}",
        "DDD": str(random.randint(11, 99)),
        "Telefone": f"{random.randint(10000000, 99999999)}",
        "Fax": "",
        "Endereco eletronico": f"contato@{nome.lower().replace(' ', '')}.com.br",
        "Representante": f"Fulano de Tal {indice}",
        "Cargo Representante": "Diretor",
        "Regiao de Comercializacao": str(random.randint(1, 9)),
        "Data Registro ANS": f"{random.randint(1990, 2015)}-{random.randint(1, 12):02d}-01",
        "Situacao": situacao,
    }


def gerar_snapshot(periodo: str, total: int = 120, removidos: list = None, adicionados: list = None, variacao: int = 0) -> None:
    pasta = Path("data/snapshots")
    pasta.mkdir(parents=True, exist_ok=True)

    ids_removidos = set(removidos or [])
    ids_extras = adicionados or []

    registros = []
    for i in range(total):
        if i in ids_removidos:
            continue
        registros.append(_gerar_operadora(i, variacao=variacao))

    for i, extra in enumerate(ids_extras):
        registros.append(_gerar_operadora(total + 100 + i))

    cabecalho = list(registros[0].keys())
    caminho = pasta / f"{periodo}.csv"

    with open(caminho, "w", encoding="latin-1") as arquivo:
        arquivo.write(";".join(cabecalho) + "\n")
        for registro in registros:
            linha = ";".join(str(registro.get(col, "")) for col in cabecalho)
            arquivo.write(linha + "\n")

    print(f"Snapshot gerado: {caminho} ({len(registros)} registros)")


def main() -> None:
    gerar_snapshot("2026-08", total=120)
    gerar_snapshot("2026-09", total=120, removidos=[5, 23], adicionados=["novo_a", "novo_b", "novo_c"], variacao=1)
    print("Snapshots de teste gerados com sucesso.")
    print("Execute: python main.py 2026-08 2026-09 --exportar")


if __name__ == "__main__":
    main()
