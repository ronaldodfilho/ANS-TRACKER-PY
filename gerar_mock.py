import random
from pathlib import Path
import pandas as pd

from config import CODIFICACAO, SEPARADOR
from loader import carregar_snapshot

MODALIDADES = [
    "Cooperativa Médica",
    "Medicina de Grupo",
    "Seguradora Especializada em Saúde",
    "Cooperativa Odontológica",
    "Odontologia de Grupo",
    "Administradora de Benefícios",
    "Filantropia",
    "Autogestão",
]

UEFS = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "GO", "PE", "CE"]

NOMES_BASE = [
    "SAUDE TOTAL", "VIDA PLENA", "MASTER SAUDE", "UNIMED", "AMIL",
    "BRADESCO SAUDE", "SUL AMERICA", "HAPVIDA", "NOTREDAME", "PREVENT SENIOR",
    "GOLDEN CROSS", "OMINT", "ALLIANZ SAUDE", "PORTO SEGURO SAUDE", "CARE PLUS",
    "INTERMEDIO", "MEDIAL SAUDE", "ASSIM SAUDE", "SANTA CASA", "SAUDE CAIXA",
]


def _gerar_cnpj_valido() -> str:
    return f"{random.randint(10000000, 99999999):08d}0001{random.randint(10, 99):02d}"


def _gerar_registro_ans(indice: int) -> str:
    return str(indice + 300000).zfill(6)


def _gerar_operadora_sintetica(indice: int) -> dict:
    nome = random.choice(NOMES_BASE)
    sufixo = random.choice(["LTDA", "S.A.", "COOPERATIVA", "ASSOCIACAO"])
    modalidade = random.choice(MODALIDADES)
    uf = random.choice(UEFS)

    return {
        "registro_ans": _gerar_registro_ans(indice),
        "cnpj": _gerar_cnpj_valido(),
        "razao_social": f"{nome} {sufixo}",
        "nome_fantasia": nome,
        "modalidade": modalidade,
        "logradouro": f"RUA DAS FLORES, {random.randint(1, 999)}",
        "numero": str(random.randint(1, 9999)),
        "complemento": "",
        "bairro": "CENTRO",
        "cidade": "São Paulo",
        "uf": uf,
        "cep": f"{random.randint(10000000, 99999999):08d}",
        "ddd": str(random.randint(11, 99)),
        "telefone": str(random.randint(10000000, 99999999)),
        "fax": "",
        "endereco_eletronico": f"contato@{nome.lower().replace(' ', '')}.com.br",
        "representante": f"FULANO DE TAL {indice}",
        "cargo_representante": "DIRETOR",
        "regiao_de_comercializacao": str(random.randint(1, 9)),
        "data_registro_ans": f"{random.randint(1990, 2020)}-{random.randint(1, 12):02d}-01",
    }


def gerar_a_partir_de_base(caminho_base: Path, caminho_destino: Path, qtd_alterados: int = 5, qtd_removidos: int = 2, qtd_novos: int = 3) -> None:
    df = carregar_snapshot(caminho_base)

    # Remover alguns registros
    if len(df) > qtd_removidos and qtd_removidos > 0:
        indices_remover = random.sample(list(df.index), qtd_removidos)
        df = df.drop(indices_remover).reset_index(drop=True)

    # Alterar alguns registros
    if "modalidade" in df.columns:
        indices_alterar = random.sample(list(df.index), min(qtd_alterados, len(df)))
        for idx in indices_alterar:
            modalidades_possiveis = [m for m in MODALIDADES if m != df.at[idx, "modalidade"]]
            if modalidades_possiveis:
                df.at[idx, "modalidade"] = random.choice(modalidades_possiveis)
            if "representante" in df.columns:
                df.at[idx, "representante"] = f"NOVO REPRESENTANTE {random.randint(100, 999)}"

    # Adicionar novos registros
    novos = []
    maior_reg = 900000
    for i in range(qtd_novos):
        novo = _gerar_operadora_sintetica(maior_reg + i)
        novos.append(novo)

    if novos:
        df_novos = pd.DataFrame(novos)
        df = pd.concat([df, df_novos], ignore_index=True)

    df.to_csv(caminho_destino, sep=SEPARADOR, encoding=CODIFICACAO, index=False)
    print(f"Snapshot gerado com base em {caminho_base.name}: {caminho_destino} ({len(df)} registros)")


def main() -> None:
    pasta = Path("data/snapshots")
    pasta.mkdir(parents=True, exist_ok=True)
    caminho_junho = pasta / "2026-06.csv"

    if caminho_junho.exists():
        print(f"Base de junho encontrada em: {caminho_junho}")
        caminho_julho = pasta / "2026-07.csv"
        gerar_a_partir_de_base(caminho_junho, caminho_julho, qtd_alterados=10, qtd_removidos=3, qtd_novos=4)
        print("Execucao sugerida:")
        print("  python main.py 2026-06 2026-07 --sem-download --exportar")
    else:
        # Fallback sintético
        caminho_08 = pasta / "2026-08.csv"
        caminho_09 = pasta / "2026-09.csv"
        registros_08 = [_gerar_operadora_sintetica(i) for i in range(120)]
        df_08 = pd.DataFrame(registros_08)
        df_08.to_csv(caminho_08, sep=SEPARADOR, encoding=CODIFICACAO, index=False)
        gerar_a_partir_de_base(caminho_08, caminho_09)
        print("Snapshots sintéticos gerados.")
        print("  python main.py 2026-08 2026-09 --sem-download --exportar")


if __name__ == "__main__":
    main()
