from typing import List

import pandas as pd

from config import COLUNA_CHAVE, COLUNAS_MONITORADAS
from models import Alteracao, ResumoDiff


def _indexar_por_chave(df: pd.DataFrame) -> dict:
    return {row[COLUNA_CHAVE]: row.to_dict() for _, row in df.iterrows()}


def _detectar_adicionados(anterior: dict, atual: dict) -> List[dict]:
    chaves_novas = set(atual) - set(anterior)
    return [atual[chave] for chave in sorted(chaves_novas)]


def _detectar_removidos(anterior: dict, atual: dict) -> List[dict]:
    chaves_removidas = set(anterior) - set(atual)
    return [anterior[chave] for chave in sorted(chaves_removidas)]


def _detectar_alteracoes(anterior: dict, atual: dict) -> List[Alteracao]:
    chaves_comuns = set(anterior) & set(atual)
    alteracoes = []

    for chave in sorted(chaves_comuns):
        registro_antes = anterior[chave]
        registro_depois = atual[chave]
        razao_social = registro_depois.get("razao_social", "")

        for campo in COLUNAS_MONITORADAS:
            valor_antes = str(registro_antes.get(campo, ""))
            valor_depois = str(registro_depois.get(campo, ""))

            if valor_antes != valor_depois:
                alteracoes.append(
                    Alteracao(
                        registro_ans=chave,
                        razao_social=razao_social,
                        campo=campo,
                        valor_anterior=valor_antes,
                        valor_atual=valor_depois,
                    )
                )

    return alteracoes


def comparar(
    df_anterior: pd.DataFrame,
    df_atual: pd.DataFrame,
    periodo_anterior: str,
    periodo_atual: str,
) -> ResumoDiff:
    registros_anterior = _indexar_por_chave(df_anterior)
    registros_atual = _indexar_por_chave(df_atual)

    return ResumoDiff(
        periodo_anterior=periodo_anterior,
        periodo_atual=periodo_atual,
        adicionados=_detectar_adicionados(registros_anterior, registros_atual),
        removidos=_detectar_removidos(registros_anterior, registros_atual),
        alteracoes=_detectar_alteracoes(registros_anterior, registros_atual),
    )
