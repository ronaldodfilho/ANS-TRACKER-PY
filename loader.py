import unicodedata
from pathlib import Path

import pandas as pd

from config import CODIFICACAO, COLUNA_CHAVE, SEPARADOR


def _remover_acentos(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    novos_nomes = {}
    for coluna in df.columns:
        nome = coluna.strip().lower().replace(" ", "_").replace("-", "_")
        nome = _remover_acentos(nome)
        if nome == "registro_operadora":
            nome = COLUNA_CHAVE
        novos_nomes[coluna] = nome
    return df.rename(columns=novos_nomes)


def _normalizar_valores(df: pd.DataFrame) -> pd.DataFrame:
    for coluna in df.select_dtypes(include="object").columns:
        df[coluna] = df[coluna].str.strip().fillna("")
    return df


def _padronizar_chave(df: pd.DataFrame) -> pd.DataFrame:
    if COLUNA_CHAVE in df.columns:
        df[COLUNA_CHAVE] = df[COLUNA_CHAVE].astype(str).str.zfill(6)
    return df


MAPA_REGIOES = {
    "1": "Nacional",
    "2": "Grupo de Estados",
    "3": "Estadual",
    "4": "Grupo de Municípios",
    "5": "Intermunicipal",
    "6": "Municipal",
}


def _traduzir_regioes(df: pd.DataFrame) -> pd.DataFrame:
    if "regiao_de_comercializacao" in df.columns:
        df["regiao_de_comercializacao"] = (
            df["regiao_de_comercializacao"]
            .astype(str)
            .str.strip()
            .map(lambda val: MAPA_REGIOES.get(val, val))
        )
    return df


def carregar_snapshot(caminho: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(
            caminho,
            sep=SEPARADOR,
            encoding="utf-8",
            dtype=str,
        )
    except (UnicodeDecodeError, Exception):
        df = pd.read_csv(
            caminho,
            sep=SEPARADOR,
            encoding=CODIFICACAO,
            dtype=str,
        )
    df = _normalizar_colunas(df)
    df = _normalizar_valores(df)
    df = _padronizar_chave(df)
    df = _traduzir_regioes(df)
    return df