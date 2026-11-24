import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyzer import analisar_inconsistencias, enriquecer_diff
from models import ResumoDiff


def test_analisar_dataset_limpo_retorna_vazio():
    df = pd.DataFrame([
        {"registro_ans": "1001", "razao_social": "Operadora A", "cnpj": "12345678000199"},
        {"registro_ans": "1002", "razao_social": "Operadora B", "cnpj": "12.345.678/0001-99"},
    ])

    assert analisar_inconsistencias(df) == []


def test_analisar_detecta_cnpj_invalido():
    df = pd.DataFrame([
        {"registro_ans": "1001", "razao_social": "Operadora Curta", "cnpj": "12345"},
    ])

    inconsistencias = analisar_inconsistencias(df)

    assert len(inconsistencias) == 1
    assert inconsistencias[0].tipo == "cnpj_invalido"
    assert inconsistencias[0].registro_ans == "1001"


def test_analisar_detecta_duplicatas():
    df = pd.DataFrame([
        {"registro_ans": "9999", "razao_social": "Dup 1", "cnpj": "12345678000199"},
        {"registro_ans": "9999", "razao_social": "Dup 2", "cnpj": "98765432000100"},
    ])

    inconsistencias = analisar_inconsistencias(df)

    assert len(inconsistencias) == 1
    assert inconsistencias[0].tipo == "registro_duplicado"
    assert inconsistencias[0].registro_ans == "9999"


def test_analisar_detecta_razao_social_vazia():
    df = pd.DataFrame([
        {"registro_ans": "5555", "razao_social": "   ", "cnpj": "12345678000199"},
    ])

    inconsistencias = analisar_inconsistencias(df)

    assert len(inconsistencias) == 1
    assert inconsistencias[0].tipo == "razao_social_vazia"
    assert inconsistencias[0].registro_ans == "5555"


def test_enriquecer_diff_popula_inconsistencias():
    df = pd.DataFrame([
        {"registro_ans": "1001", "razao_social": "", "cnpj": "123"},
    ])
    resumo = ResumoDiff(periodo_anterior="2026-01-01", periodo_atual="2026-01-02")

    enriquecido = enriquecer_diff(resumo, df)

    tipos = {i.tipo for i in enriquecido.inconsistencias}
    assert tipos == {"cnpj_invalido", "razao_social_vazia"}
