import base64
import os
from pathlib import Path
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _obter_cabecalhos(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ANS-TRACKER-PY",
    }


def salvar_snapshot_github(nome_arquivo: str, conteudo: bytes) -> bool:
    token = os.getenv("GITHUB_TOKEN")
    repositorio = os.getenv("GITHUB_REPO")

    if not token or not repositorio:
        return False

    url = f"https://api.github.com/repos/{repositorio}/contents/data/snapshots/{nome_arquivo}"
    cabecalhos = _obter_cabecalhos(token)

    try:
        resposta_checagem = requests.get(url, headers=cabecalhos, timeout=10)
        if resposta_checagem.status_code == 200:
            return True

        dados = {
            "message": f"backup: {nome_arquivo}",
            "content": base64.b64encode(conteudo).decode("utf-8"),
        }

        resposta_envio = requests.put(url, headers=cabecalhos, json=dados, timeout=30)
        return resposta_envio.status_code in (200, 201)
    except Exception:
        return False


def baixar_snapshots_github(pasta_destino: str = "data/snapshots") -> None:
    token = os.getenv("GITHUB_TOKEN")
    repositorio = os.getenv("GITHUB_REPO")

    if not token or not repositorio:
        return

    url = f"https://api.github.com/repos/{repositorio}/contents/data/snapshots"
    cabecalhos = _obter_cabecalhos(token)

    try:
        resposta = requests.get(url, headers=cabecalhos, timeout=10)
        if resposta.status_code != 200:
            return

        caminho_pasta = Path(pasta_destino)
        caminho_pasta.mkdir(parents=True, exist_ok=True)

        for item in resposta.json():
            if isinstance(item, dict) and item.get("name", "").endswith(".csv"):
                caminho_arquivo = caminho_pasta / item["name"]
                if not caminho_arquivo.exists() and item.get("download_url"):
                    resposta_arquivo = requests.get(item["download_url"], headers=cabecalhos, timeout=30)
                    if resposta_arquivo.status_code == 200:
                        caminho_arquivo.write_bytes(resposta_arquivo.content)
    except Exception:
        pass


def enviar_snapshots_locais_github(pasta_origem: str = "data/snapshots") -> None:
    token = os.getenv("GITHUB_TOKEN")
    repositorio = os.getenv("GITHUB_REPO")

    if not token or not repositorio:
        return

    caminho_pasta = Path(pasta_origem)
    if not caminho_pasta.exists():
        return

    for arquivo in caminho_pasta.glob("*.csv"):
        salvar_snapshot_github(arquivo.name, arquivo.read_bytes())
