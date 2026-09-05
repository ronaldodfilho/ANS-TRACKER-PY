from pathlib import Path

import requests

from config import ARQUIVO_CADOP, PASTA_SNAPSHOTS, URL_ANS


def _montar_url() -> str:
    return f"{URL_ANS}{ARQUIVO_CADOP}"


def _obter_caminho(periodo: str) -> Path:
    return Path(PASTA_SNAPSHOTS) / f"{periodo}.csv"


def snapshot_existe(periodo: str) -> bool:
    return _obter_caminho(periodo).exists()


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
