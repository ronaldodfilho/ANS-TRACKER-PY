import base64
import os
from pathlib import Path
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def salvar_snapshot_github(nome_arquivo: str, conteudo: bytes) -> bool:
    token = os.getenv("GITHUB_TOKEN")
    repositorio = os.getenv("GITHUB_REPO")

    if not token or not repositorio:
        return False

    url = f"https://api.github.com/repos/{repositorio}/contents/data/snapshots/{nome_arquivo}"
    cabecalhos = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

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
    cabecalhos = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

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
                    resposta_arquivo = requests.get(item["download_url"], timeout=30)
                    if resposta_arquivo.status_code == 200:
                        caminho_arquivo.write_bytes(resposta_arquivo.content)
    except Exception:
        pass
