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


def carregar_snapshot(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(
        caminho,
        sep=SEPARADOR,
        encoding=CODIFICACAO,
        dtype=str,
    )
    df = _normalizar_colunas(df)
    df = _normalizar_valores(df)
    df = _padronizar_chave(df)
    return df