URL_ANS = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
ARQUIVO_CADOP = "Relatorio_cadop.csv"
PASTA_SNAPSHOTS = "data/snapshots"
PASTA_DIFFS = "output/diffs"

COLUNA_CHAVE = "registro_ans"

COLUNAS_MONITORADAS = [
    "razao_social",
    "cnpj",
    "modalidade",
    "uf",
    "cidade",
    "representante",
    "data_registro_ans",
]

COLUNAS_CRITICAS = ["modalidade", "situacao"]

SEPARADOR = ";"
CODIFICACAO = "latin-1"
