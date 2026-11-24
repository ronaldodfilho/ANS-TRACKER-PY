import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from comparator import comparar


def _df(rows):
    return pd.DataFrame(rows)


def test_comparar_detecta_adicionados_e_removidos():
    anterior = _df([
        {"registro_ans": "1001", "razao_social": "Operadora A", "modalidade": "Medicina de Grupo", "uf": "SP"},
        {"registro_ans": "1002", "razao_social": "Operadora B", "modalidade": "Cooperativa Médica", "uf": "RJ"},
    ])
    atual = _df([
        {"registro_ans": "1001", "razao_social": "Operadora A", "modalidade": "Medicina de Grupo", "uf": "SP"},
        {"registro_ans": "1003", "razao_social": "Operadora C", "modalidade": "Autogestão", "uf": "MG"},
    ])

    resumo = comparar(anterior, atual, "2026-01-01", "2026-01-02")

    assert len(resumo.adicionados) == 1
    assert resumo.adicionados[0]["registro_ans"] == "1003"
    assert len(resumo.removidos) == 1
    assert resumo.removidos[0]["registro_ans"] == "1002"
    assert resumo.alteracoes == []
    assert resumo.total_mudancas() == 2


def test_comparar_detecta_alteracoes_e_criticas():
    anterior = _df([
        {
            "registro_ans": "2001",
            "razao_social": "Saúde Vida LTDA",
            "modalidade": "Medicina de Grupo",
            "uf": "SP",
        }
    ])
    atual = _df([
        {
            "registro_ans": "2001",
            "razao_social": "Saúde Vida S/A",
            "modalidade": "Seguradora Especializada em Saúde",
            "uf": "SP",
        }
    ])

    resumo = comparar(anterior, atual, "2026-01-01", "2026-01-02")

    campos_alterados = {a.campo: (a.valor_anterior, a.valor_atual) for a in resumo.alteracoes}
    assert campos_alterados["razao_social"] == ("Saúde Vida LTDA", "Saúde Vida S/A")
    assert campos_alterados["modalidade"] == ("Medicina de Grupo", "Seguradora Especializada em Saúde")
    assert len(resumo.alteracoes_criticas) == 1
    assert resumo.alteracoes_criticas[0].campo == "modalidade"
    assert resumo.total_mudancas() == 2


def test_comparar_sem_mudancas():
    dados = _df([
        {"registro_ans": "3001", "razao_social": "Plano Total", "modalidade": "Autogestão", "uf": "GO"}
    ])

    resumo = comparar(dados, dados.copy(), "2026-01-01", "2026-01-02")

    assert resumo.adicionados == []
    assert resumo.removidos == []
    assert resumo.alteracoes == []
    assert resumo.total_mudancas() == 0
