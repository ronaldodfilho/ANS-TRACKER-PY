import unicodedata
from pathlib import Path

import pandas as pd

from config import COLUNA_CHAVE, SEPARADOR


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


def _padronizar_chave(df: pd.DataFrame) -> pd.DataFrame:
    if COLUNA_CHAVE in df.columns:
        df[COLUNA_CHAVE] = df[COLUNA_CHAVE].astype(str).str.zfill(6)
    return df


def carregar_snapshot(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho, sep=SEPARADOR, dtype=str)
    df = _normalizar_colunas(df)
    df = _padronizar_chave(df)
    return df