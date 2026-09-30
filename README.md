# ANS Health Tracker - Monitoramento e Análise Cadastral de Operadoras ANS

> **Demo online:** [web-production-a3f77.up.railway.app](https://web-production-a3f77.up.railway.app/)

Aplicação desenvolvida em Python para monitorar, comparar e analisar snapshots periódicos do cadastro de operadoras de planos de saúde da ANS (Agência Nacional de Saúde Suplementar - CADOP).

O projeto conta com interface de linha de comando (CLI) e uma API web com FastAPI e interface Vue.js para visualização interativa das métricas e alterações.

## Sobre o projeto

O objetivo principal desta aplicação é disponibilizar uma ferramenta para rastreamento de dados históricos e identificação de divergências entre bases periódicas das operadoras de planos de saúde ativas na ANS.

A aplicação realiza a leitura e normalização de arquivos CSV fornecidos pelo Portal de Dados Abertos da ANS e disponibiliza funcionalidades para:

* **Detecção e download automático:** Consulta a data exata da última modificação (`Last-Modified`) no portal da ANS e armazena os snapshots com suporte a granularidade diária (`AAAA-MM-DD`) e mensal (`AAAA-MM`);
* **Rastreamento de histórico:** Comparação flexível entre quaisquer períodos cadastrados (ex: `2026-01-10`, `2026-06`, `2026-07`, etc.);
* **Identificação de movimentações:**
  * Novas operadoras cadastradas (adicionadas);
  * Operadoras canceladas ou removidas da base cadastral;
  * Alterações cadastrais (razão social, CNPJ, modalidade, UF, cidade, representante, data de registro);
* **Destaque para mudanças críticas:** Alertas para alterações de alto impacto em modalidade e situação;
* **Análise de inconsistências cadastrais:** Validação de integridade e consistência dos registros;
* **Relatórios flexíveis:** Visualização formatada no terminal ou em painel web interativo;
* **Exportação:** Geração de relatórios de diferenciação (diff) em formato CSV padronizado.

## Estrutura do projeto

```text
.
├── data/
│   └── snapshots/
│       ├── 2026-01-10.csv    # Snapshot de Janeiro/2026
│       ├── 2026-06.csv       # Snapshot de Junho/2026
│       └── 2026-07.csv       # Snapshot de Julho/2026
├── static/
│   └── index.html            # Interface web com Vue.js
├── analyzer.py               # Motor de análise cadastral
├── api.py                    # Servidor FastAPI e rotas web
├── comparator.py             # Comparador diferencial entre períodos
├── config.py                 # Configurações globais
├── fetcher.py                # Download automatizado e detecção de versão da ANS
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

Para comparar uma base anterior com a **versão mais recente disponível** da ANS de forma automática:

```bash
python main.py 2026-06 --exportar
```

Para comparar entre duas datas ou períodos específicos:

```bash
python main.py 2026-01-10 2026-07 --exportar
```

Caso queira usar apenas arquivos locais já existentes (sem realizar chamadas de rede):

```bash
python main.py 2026-06 2026-07 --sem-download --exportar
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
