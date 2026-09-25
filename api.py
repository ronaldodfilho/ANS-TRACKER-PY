from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from analyzer import enriquecer_diff
from comparator import comparar
from config import PASTA_SNAPSHOTS
from fetcher import baixar_snapshot, snapshot_existe
from loader import carregar_snapshot

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def pagina_inicial():
    return FileResponse("static/index.html")


@app.get("/api/periodos")
def listar_periodos():
    pasta = Path(PASTA_SNAPSHOTS)
    if not pasta.exists():
        return []
    arquivos = sorted(pasta.glob("*.csv"))
    return [arq.stem for arq in arquivos]


@app.get("/api/comparar")
def executar_comparacao(periodo_anterior: str, periodo_atual: str):
    for periodo in [periodo_anterior, periodo_atual]:
        if not snapshot_existe(periodo):
            try:
                baixar_snapshot(periodo)
            except Exception as erro:
                raise HTTPException(status_code=400, detail=f"Erro ao obter snapshot {periodo}: {erro}")

    caminho_anterior = Path(PASTA_SNAPSHOTS) / f"{periodo_anterior}.csv"
    caminho_atual = Path(PASTA_SNAPSHOTS) / f"{periodo_atual}.csv"

    df_anterior = carregar_snapshot(caminho_anterior)
    df_atual = carregar_snapshot(caminho_atual)

    resumo = comparar(df_anterior, df_atual, periodo_anterior, periodo_atual)
    resumo = enriquecer_diff(resumo, df_atual)

    return {
        "periodo_anterior": resumo.periodo_anterior,
        "periodo_atual": resumo.periodo_atual,
        "total_adicionados": len(resumo.adicionados),
        "total_removidos": len(resumo.removidos),
        "total_alterados": len(resumo.alteracoes),
        "total_inconsistencias": len(resumo.inconsistencias),
        "alteracoes_criticas": [
            {
                "registro_ans": alt.registro_ans,
                "razao_social": alt.razao_social,
                "campo": alt.campo,
                "valor_anterior": alt.valor_anterior,
                "valor_atual": alt.valor_atual,
            }
            for alt in resumo.alteracoes_criticas
        ],
        "alteracoes": [
            {
                "registro_ans": alt.registro_ans,
                "razao_social": alt.razao_social,
                "campo": alt.campo,
                "valor_anterior": alt.valor_anterior,
                "valor_atual": alt.valor_atual,
            }
            for alt in resumo.alteracoes
        ],
        "adicionados": resumo.adicionados,
        "removidos": resumo.removidos,
        "inconsistencias": [
            {
                "registro_ans": inc.registro_ans,
                "razao_social": inc.razao_social,
                "tipo": inc.tipo,
                "descricao": inc.descricao,
            }
            for inc in resumo.inconsistencias
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

