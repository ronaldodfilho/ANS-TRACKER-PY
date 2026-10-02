import hashlib
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

import requests

from config import ARQUIVO_CADOP, PASTA_SNAPSHOTS, URL_ANS
from github_sync import salvar_snapshot_github


def _montar_url() -> str:
    return f"{URL_ANS}{ARQUIVO_CADOP}"


def _obter_caminho(periodo: str) -> Path:
    return Path(PASTA_SNAPSHOTS) / f"{periodo}.csv"


def _obter_ultimo_snapshot() -> Optional[Path]:
    pasta = Path(PASTA_SNAPSHOTS)
    if not pasta.exists():
        return None
    arquivos = sorted(pasta.glob("*.csv"))
    return arquivos[-1] if arquivos else None


def _calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


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
        caminho = baixar_snapshot(identificador)
        if caminho is None:
            ultimo = _obter_ultimo_snapshot()
            return ultimo.stem if ultimo else identificador
    return identificador


def baixar_snapshot(periodo: str) -> Optional[Path]:
    caminho = _obter_caminho(periodo)

    if caminho.exists():
        return caminho

    Path(PASTA_SNAPSHOTS).mkdir(parents=True, exist_ok=True)

    url = _montar_url()
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    conteudo = resposta.content

    ultimo = _obter_ultimo_snapshot()
    if ultimo and ultimo.exists():
        if _calcular_hash(conteudo) == _calcular_hash(ultimo.read_bytes()):
            print(f"Conteúdo recebido é idêntico ao snapshot {ultimo.name}. Novo snapshot ignorado.")
            return None

    with open(caminho, "wb") as arquivo:
        arquivo.write(conteudo)

    salvar_snapshot_github(f"{periodo}.csv", conteudo)

    return caminho

