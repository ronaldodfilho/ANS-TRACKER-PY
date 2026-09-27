import argparse
import sys
from datetime import datetime
from pathlib import Path

from analyzer import enriquecer_diff
from comparator import comparar
from fetcher import baixar_snapshot, snapshot_existe, obter_identificador_recente
from loader import carregar_snapshot
from reporter import exportar_csv_diff, imprimir_resumo

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ans-health-tracker",
        description="Analisa mudancas em operadoras de saude suplementar entre dois periodos da ANS.",
    )
    parser.add_argument(
        "periodo_anterior",
        help="Periodo ou data anterior (ex: 2026-06 ou 2026-06-01)",
    )
    parser.add_argument(
        "periodo_atual",
        nargs="?",
        default=None,
        help="Periodo ou data atual (ex: 2026-09 ou 2026-09-28). Padrao: versao mais recente da ANS",
    )
    parser.add_argument(
        "--exportar",
        action="store_true",
        help="Exporta o diff em arquivo CSV na pasta output/diffs/",
    )
    parser.add_argument(
        "--sem-download",
        action="store_true",
        help="Usa apenas snapshots ja baixados localmente, sem tentar download",
    )
    return parser


def _garantir_snapshot(periodo: str, sem_download: bool) -> None:
    if snapshot_existe(periodo):
        return

    if sem_download:
        print(f"Snapshot nao encontrado: data/snapshots/{periodo}.csv")
        print("Use --sem-download apenas quando os arquivos ja estiverem presentes.")
        sys.exit(1)

    print(f"Baixando snapshot {periodo}...")
    try:
        baixar_snapshot(periodo)
    except Exception as erro:
        print(f"Erro ao baixar snapshot {periodo}: {erro}")
        sys.exit(1)


def executar(args: argparse.Namespace) -> None:
    periodo_atual = args.periodo_atual
    if not periodo_atual:
        if args.sem_download:
            pasta = Path("data/snapshots")
            candidatos = sorted([p.stem for p in pasta.glob("*.csv") if p.stem != args.periodo_anterior])
            periodo_atual = candidatos[-1] if candidatos else "2026-09"
        else:
            periodo_atual = obter_identificador_recente()

    _garantir_snapshot(args.periodo_anterior, args.sem_download)
    _garantir_snapshot(periodo_atual, args.sem_download)

    caminho_anterior = Path("data/snapshots") / f"{args.periodo_anterior}.csv"
    caminho_atual = Path("data/snapshots") / f"{periodo_atual}.csv"

    df_anterior = carregar_snapshot(caminho_anterior)
    df_atual = carregar_snapshot(caminho_atual)

    resumo = comparar(df_anterior, df_atual, args.periodo_anterior, periodo_atual)
    resumo = enriquecer_diff(resumo, df_atual)

    imprimir_resumo(resumo)

    if args.exportar:
        caminho_csv = exportar_csv_diff(resumo)
        print(f"Diff exportado: {caminho_csv}\n")


def main() -> None:
    parser = _construir_parser()
    args = parser.parse_args()
    executar(args)


if __name__ == "__main__":
    main()
