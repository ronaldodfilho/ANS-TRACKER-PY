import re
from typing import List

import pandas as pd

from models import Inconsistencia, ResumoDiff

PADRAO_CNPJ = re.compile(r"^\d{14}$")


def _cnpj_valido(valor: str) -> bool:
    apenas_numeros = re.sub(r"\D", "", valor)
    return bool(PADRAO_CNPJ.match(apenas_numeros))


def _verificar_cnpj_invalido(df: pd.DataFrame) -> List[Inconsistencia]:
    inconsistencias = []
    for _, linha in df.iterrows():
        cnpj = str(linha.get("cnpj", ""))
        if cnpj and not _cnpj_valido(cnpj):
            inconsistencias.append(
                Inconsistencia(
                    registro_ans=linha.get("registro_ans", ""),
                    razao_social=linha.get("razao_social", ""),
                    tipo="cnpj_invalido",
                    descricao=f"CNPJ '{cnpj}' fora do formato esperado (14 digitos)",
                )
            )
    return inconsistencias


def _verificar_duplicatas(df: pd.DataFrame) -> List[Inconsistencia]:
    inconsistencias = []
    duplicados = df[df.duplicated(subset=["registro_ans"], keep=False)]
    for registro_ans, grupo in duplicados.groupby("registro_ans"):
        inconsistencias.append(
            Inconsistencia(
                registro_ans=str(registro_ans),
                razao_social=grupo.iloc[0].get("razao_social", ""),
                tipo="registro_duplicado",
                descricao=f"Registro ANS aparece {len(grupo)}x no mesmo snapshot",
            )
        )
    return inconsistencias


def _verificar_razao_social_vazia(df: pd.DataFrame) -> List[Inconsistencia]:
    inconsistencias = []
    sem_nome = df[df["razao_social"].str.strip() == ""]
    for _, linha in sem_nome.iterrows():
        inconsistencias.append(
            Inconsistencia(
                registro_ans=linha.get("registro_ans", ""),
                razao_social="",
                tipo="razao_social_vazia",
                descricao="Operadora sem razao social cadastrada",
            )
        )
    return inconsistencias


def analisar_inconsistencias(df: pd.DataFrame) -> List[Inconsistencia]:
    resultado = []
    resultado.extend(_verificar_cnpj_invalido(df))
    resultado.extend(_verificar_duplicatas(df))
    resultado.extend(_verificar_razao_social_vazia(df))
    return resultado


def enriquecer_diff(resumo: ResumoDiff, df_atual: pd.DataFrame) -> ResumoDiff:
    resumo.inconsistencias = analisar_inconsistencias(df_atual)
    return resumo
