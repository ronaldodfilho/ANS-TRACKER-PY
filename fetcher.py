from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

from config import ARQUIVO_CADOP, PASTA_SNAPSHOTS, URL_ANS


def _montar_url() -> str:
    return f"{URL_ANS}{ARQUIVO_CADOP}"


def _obter_caminho(periodo: str) -> Path:
    return Path(PASTA_SNAPSHOTS) / f"{periodo}.csv"


def snapshot_existe(periodo: str) -> bool:
    return _obter_caminho(periodo).exists()


def obter_identificador_recente() -> str:
    try:
        resposta = requests.head(_montar_url(), timeout=10)
        last_modified = resposta.headers.get("Last-Modified")
        if last_modified:
            data_dt = parsedate_to_datetime(last_modified)
            return data_dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return datetime.now().strftime("%Y-%m-%d")


def garantir_snapshot_recente() -> str:
    identificador = obter_identificador_recente()
    if not snapshot_existe(identificador):
        baixar_snapshot(identificador)
    return identificador


def baixar_snapshot(periodo: str) -> Path:
    caminho = _obter_caminho(periodo)

    if caminho.exists():
        return caminho

    Path(PASTA_SNAPSHOTS).mkdir(parents=True, exist_ok=True)

    url = _montar_url()
    resposta = requests.get(url, timeout=30, stream=True)
    resposta.raise_for_status()

    with open(caminho, "wb") as arquivo:
        for bloco in resposta.iter_content(chunk_size=8192):
            arquivo.write(bloco)

    return caminho
