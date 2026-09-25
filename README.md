# ANS Health Tracker - Monitoramento e Análise Cadastral de Operadoras ANS

Aplicação desenvolvida em Python para monitorar, comparar e analisar snapshots mensais do cadastro de operadoras de planos de saúde da ANS (Agência Nacional de Saúde Suplementar - CADOP).

O projeto conta com interface de linha de comando (CLI) e uma API web com FastAPI e interface Vue.js para visualização das métricas e alterações no navegador.

## Sobre o projeto

O objetivo principal desta aplicação é disponibilizar uma ferramenta para rastreamento de dados históricos e identificação de divergências entre bases periódicas das operadoras de planos de saúde ativas na ANS.

A aplicação realiza a leitura e normalização de arquivos CSV fornecidos pelo Portal de Dados Abertos da ANS e disponibiliza funcionalidades para:

* Baixar e armazenar snapshots mensais do CADOP automaticamente via HTTP;
* Utilizar a base histórica de Junho/2026 (`2026-06.csv`) como referência cadastral;
* Identificar novas operadoras cadastradas (adicionadas);
* Identificar operadoras canceladas ou removidas da base cadastral;
* Detectar alterações nos atributos de cada operadora (razão social, CNPJ, modalidade, UF, cidade, representante, data de registro);
* Destacar mudanças críticas em campos de alto impacto, como modalidade e situação;
* Analisar e reportar inconsistências nos dados cadastrais;
* Exibir relatórios no terminal ou via painel web interativo;
* Exportar o relatório de diferenciação (diff) em formato CSV padronizado.

## Estrutura do projeto

```text
.
├── data/
│   └── snapshots/
│       └── 2026-06.csv       # Base de referência histórica
├── static/
│   └── index.html            # Interface web com Vue.js
├── analyzer.py               # Motor de análise cadastral
├── api.py                    # Servidor FastAPI e rotas web
├── comparator.py             # Comparador diferencial entre períodos
├── config.py                 # Configurações globais
├── fetcher.py                # Download automatizado da ANS
├── loader.py                 # Carregamento e sanitização de CSV
├── main.py                   # Interface CLI de terminal
├── models.py                 # Dataclasses de domínio
├── reporter.py               # Relatórios no terminal e CSV
├── requirements.txt          # Dependências do projeto
├── .gitignore
└── README.md
```

## Como executar

### 1. Pré-requisitos e Dependências

Instale as dependências requeridas:

```bash
pip install -r requirements.txt
```

### 2. Execução pelo Terminal (CLI)

Para comparar a base de referência (Junho/2026) com o snapshot atual baixado da ANS e exportar o CSV:

```bash
python main.py 2026-06 2026-09 --exportar
```

Caso queira usar apenas arquivos locais já existentes:

```bash
python main.py 2026-06 2026-09 --sem-download --exportar
```

### 3. Execução da Interface Web (FastAPI + Vue.js)

Inicie o servidor web com:

```bash
python api.py
```

Ou através do módulo uvicorn:

```bash
python -m uvicorn api:app --reload
```

Em seguida, acesse no navegador: `http://localhost:8000`

## Autor

Ronaldo Dutra Filho
