# ANS Health Tracker - Monitoramento e Análise Cadastral de Operadoras ANS

Aplicação desenvolvida em Python para monitorar, comparar e analisar snapshots mensais do cadastro de operadoras de planos de saúde da ANS (Agência Nacional de Saúde Suplementar - CADOP).

O projeto possui uma arquitetura modular baseada em Python 3 e Pandas, com interface de linha de comando (CLI) construída via `argparse`, permitindo o download automatizado de snapshots, identificação de movimentações cadastrais, detecção de alterações em colunas estratégicas e validação de inconsistências nos dados da ANS.

## Sobre o projeto

O objetivo principal desta aplicação é disponibilizar uma ferramenta robusta para rastreamento de dados históricos e identificação de divergências entre bases periódicas das operadoras de planos de saúde ativas na ANS.

A aplicação realiza a leitura e normalização de arquivos CSV fornecidos pelo Portal de Dados Abertos da ANS e disponibiliza funcionalidades para:

* Baixar e armazenar snapshots mensais do CADOP automaticamente via FTP/HTTP;
* Utilizar a base histórica de **Junho/2026** (`2026-06.csv`) pré-inclusa como referência cadastral;
* Identificar novas operadoras cadastradas (adicionadas);
* Identificar operadoras canceladas ou removidas da base cadastral;
* Detectar alterações nos atributos de cada operadora (razão social, CNPJ, modalidade, UF, cidade, representante, data de registro);
* Destacar mudanças críticas em campos de alto impacto, como `modalidade` e `situacao`;
* Analisar e reportar inconsistências nos dados (CNPJ fora do padrão de 14 dígitos, registros duplicados e razão social ausente);
* Exibir relatórios detalhados e coloridos no terminal com formatação numérica localizada;
* Exportar o relatório de diferenciação (diff) em formato CSV padronizado.

## Funcionalidades implementadas

### Core & Motor de Análise

* Download automático com streaming de blocos (`requests`) para grandes volumes de dados;
* Cache local de snapshots em `data/snapshots/` evitando requisições redundantes;
* Suporte a modo offline `--sem-download` utilizando snapshots locais previamente baixados;
* Base oficial histórica de Junho/2026 (`2026-06.csv`) já versionada no repositório;
* Leitura e sanitização de CSVs codificados tanto em `utf-8` quanto em `latin-1` com separador `;`;
* Normalização automática dos cabeçalhos do CSV (remoção de acentos, conversão para lowercase e mapeamento automático de `registro_operadora` para `registro_ans`);
* Padronização de chave primária (`registro_ans`) com *zfill* para 6 dígitos;
* Indexação de alta performance e comparação diferencial baseada em conjuntos (`set`);
* Detecção precisa de operadoras adicionadas, removidas e alteradas;
* Identificação de alterações em colunas monitoradas (`razao_social`, `cnpj`, `modalidade`, `uf`, `cidade`, `representante`, `data_registro_ans`);
* Classificação de mudanças críticas para acompanhamento regulatório;
* Motor de auditoria cadastral para identificação de inconsistências de dados;
* Validação de formato de CNPJ utilizando expressões regulares (regex);
* Detecção de duplicidade de registros cadastrais no mesmo período;
* Sinalização de registros sem razão social preenchida.

### Interface de Linha de Comando (CLI) & Relatórios

* CLI desenvolvida com `argparse` oferecendo parâmetros posicionais e flags opcionais;
* Exibição visual no terminal com formatação por cores ANSI (Verde para inserções, Vermelho para remoções/erros, Amarelo para alterações/alertas, Azul para cabeçalhos);
* Formatação nativa de números usando locale para melhor leitura de métricas;
* Exportação do diff completo em CSV estruturado em `output/diffs/` através da flag `--exportar`.

## Estrutura do projeto

```text
.
├── data/
│   └── snapshots/
│       └── 2026-06.csv       # Base de referência histórica oficial
├── analyzer.py               # Motor de análise de consistência cadastral
├── comparator.py             # Comparador diferencial entre períodos
├── config.py                 # Constantes e configurações da aplicação
├── fetcher.py                # Download automatizado da ANS com streaming
├── loader.py                 # Carregamento e sanitização com Pandas
├── main.py                   # Ponto de entrada CLI
├── models.py                 # Dataclasses do domínio
├── reporter.py               # Exibição no terminal e exportação em CSV
├── requirements.txt          # Dependências do projeto
├── .gitignore
└── README.md
```

## Fonte de dados

A aplicação consome os dados cadastrais abertos disponibilizados publicamente pela ANS:

* **URL base do FTP/HTTP:** [Portal de Dados Abertos da ANS](https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/)
* **Arquivo baixado:** `Relatorio_cadop.csv`

Campos primários utilizados no monitoramento cadastral:
* `registro_ans`: Identificador único da operadora na ANS (Chave primária);
* `cnpj`: Cadastro Nacional da Pessoa Jurídica da operadora;
* `razao_social`: Nome empresarial da operadora;
* `modalidade`: Classificação da operadora (ex: Cooperativa Médica, Medicina de Grupo, Autogestão);
* `uf`: Unidade Federativa da sede;
* `cidade`: Município da sede;
* `representante`: Nome do representante legal cadastrado;
* `data_registro_ans`: Data de concessão do registro na agência.

## Como executar

### 1. Pré-requisitos

* Python 3.9 ou superior;
* Gerenciador de pacotes `pip`.

### 2. Instalar as dependências

Abra o terminal no diretório do projeto e instale as bibliotecas requeridas:

```bash
pip install -r requirements.txt
```

### 3. Modo de Execução Online (Download automático da base atual da ANS)

O repositório já inclui a base de Junho/2026 (`2026-06`). Para baixar a base atual mais recente do portal da ANS (por exemplo, `2026-09`) e gerar o relatório comparativo:

```bash
python main.py 2026-06 2026-09 --exportar
```

O sistema fará o download do relatório oficial da ANS em tempo de execução, salvará em `data/snapshots/2026-09.csv` e exportará o diff comparativo em `output/diffs/diff_2026-06_2026-09.csv`.

### 4. Modo de Execução Offline (Com snapshots locais)

Caso você já possua os dois snapshots baixados na pasta `data/snapshots/`:

```bash
python main.py 2026-06 2026-09 --sem-download --exportar
```

## Modos de Uso e Argumentos CLI

Sintaxe básica da linha de comando:

```text
python main.py <periodo_anterior> <periodo_atual> [opcoes]
```

### Argumentos Posicionais

| Argumento          | Obrigatório | Formato   | Descrição                                         |
| ------------------ | ----------- | --------- | ------------------------------------------------- |
| `periodo_anterior` | Sim         | `AAAA-MM` | Identificador do período base de referência       |
| `periodo_atual`    | Sim         | `AAAA-MM` | Identificador do período mais recente para comparar|

### Opções / Flags

| Flag             | Tipo    | Descrição                                                                      |
| ---------------- | ------- | ------------------------------------------------------------------------------ |
| `--exportar`     | Booleano| Exporta o relatório completo de diff em formato CSV na pasta `output/diffs/`   |
| `--sem-download` | Booleano| Força o uso exclusivo de arquivos locais existentes sem tentar requisições HTTP |

## Autor

Ronaldo Dutra Filho
