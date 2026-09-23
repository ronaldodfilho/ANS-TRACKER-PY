# ANS Health Tracker - Monitoramento e Análise Cadastral de Operadoras ANS

Aplicação desenvolvida em Python para monitorar, comparar e analisar snapshots mensais do cadastro de operadoras de planos de saúde da ANS (Agência Nacional de Saúde Suplementar - CADOP).

O projeto possui uma arquitetura modular baseada em Python 3 e Pandas, com interface de linha de comando (CLI) construída via `argparse`, permitindo o download automatizado de snapshots, identificação de movimentações cadastrais, detecção de alterações em colunas estratégicas e validação de inconsistências nos dados da ANS.

## Sobre o projeto

O objetivo principal desta aplicação é disponibilizar uma ferramenta robusta para rastreamento de dados históricos e identificação de divergências entre bases periódicas das operadoras de planos de saúde ativas na ANS.

A aplicação realiza a leitura e normalização de arquivos CSV fornecidos pelo Portal de Dados Abertos da ANS e disponibiliza funcionalidades para:

* Baixar e armazenar snapshots mensais do CADOP automaticamente via FTP/HTTP;
* Identificar novas operadoras cadastradas (adicionadas);
* Identificar operadoras canceladas ou removidas da base cadastral;
* Detectar alterações nos atributos de cada operadora (razão social, CNPJ, modalidade, UF, cidade, representante, data de registro);
* Destacar mudanças críticas em campos de alto impacto, como `modalidade` e `situacao`;
* Analisar e reportar inconsistências nos dados (CNPJ fora do padrão de 14 dígitos, registros duplicados e razão social ausente);
* Exibir relatórios detalhados e coloridos no terminal com formatação numérica localizada;
* Exportar o relatório de diferenção (diff) em formato CSV padronizado.

Este repositório fornece uma solução completa de linha de comando, apta a operar tanto em modo de produção (com downloads de dados reais da ANS) quanto em modo offline para testes (utilizando geradores de mock).

## Funcionalidades implementadas

### Core & Motor de Análise

* Download automático com streaming de blocos (`requests`) para grandes volumes de dados;
* Cache local de snapshots em `data/snapshots/` evitando requisições redundantes;
* Suporte a modo offline `--sem-download` utilizando snapshots locais previamente baixados;
* Leitura e sanitização de CSVs codificados em `latin-1` com separador `;`;
* Normalização automática dos cabeçalhos do CSV (remoção de acentos, conversão para lowercase e substituição de caracteres por `_`);
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
* Exportação do diff completo em CSV estruturado em `output/diffs/` através da flag `--exportar`;
* Gerador de dados de teste cadastrais (`gerar_mock.py`) para testes e simulações.

### Documentação e Scripts

* Leitura e documentação detalhada das regras de negócio e estrutura do projeto;
* Gerador mock para simulação de cenários de inclusão, exclusão, alteração e inconsistência.

## Estrutura do projeto

```text
.
├── analyzer.py
├── comparator.py
├── config.py
├── fetcher.py
├── gerar_mock.py
├── loader.py
├── main.py
├── models.py
├── reporter.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Principais arquivos

#### `main.py`

Ponto de entrada da interface de linha de comando (CLI). Configura o `argparse`, valida os parâmetros de entrada, orquestra o fluxo de download/verificação de snapshots, aciona os módulos de carregamento, comparação, enriquecimento e exibição dos relatórios.

#### `config.py`

Centraliza as configurações globais da aplicação. Define a URL base do Portal de Dados Abertos da ANS, os nomes de diretórios (`data/snapshots`, `output/diffs`), a coluna chave (`registro_ans`), as listas de colunas monitoradas e críticas, além dos parâmetros de encoding (`latin-1`) e separador (`;`).

#### `models.py`

Define as estruturas de dados do domínio utilizando `dataclasses` do Python:
* `Alteracao`: Armazena divergências em campos de uma operadora (registro ANS, razão social, campo, valor anterior e valor atual);
* `Inconsistencia`: Registra erros cadastrais encontrados (registro ANS, razão social, tipo de inconsistência e descrição);
* `ResumoDiff`: Contém o resultado consolidado da comparação entre dois períodos (adicionados, removidos, alterações e inconsistências), fornecendo métodos auxiliares como `alteracoes_criticas` e `total_mudancas`.

#### `fetcher.py`

Gerencia o download de snapshots diretamente do FTP/HTTP da ANS. Implementa streaming de arquivos em blocos de 8KB para otimização de memória e evita downloads desnecessários quando o snapshot já se encontra salvo localmente.

#### `loader.py`

Responsável pelo carregamento dos arquivos CSV usando `pandas`. Executa a sanitização do dataframe, removendo acentos dos nomes das colunas, convertendo-os para minúsculas com underline, limpando espaços em branco nos valores de texto e garantindo o formato de 6 dígitos no `registro_ans`.

#### `comparator.py`

Executa a comparação lógica entre dois dataframes indexados pelo `registro_ans`. Identifica quais registros foram incluídos, quais foram removidos e itera sobre as colunas monitoradas para registrar todas as alterações de valores entre o período anterior e o atual.

#### `analyzer.py`

Módulo de inteligência cadastral. Executa regras de validação sobre o snapshot atual para identificar inconsistências, tais como CNPJs que não atendem ao padrão de 14 dígitos numéricos, registros duplicados com o mesmo código ANS e cadastros com razão social em branco.

#### `reporter.py`

Formatador de saída dos resultados. Exibe o resumo estatístico no terminal com destaque por cores ANSI e formatação de números pelo locale do sistema. Também contém a função para gravar o diff detalhado em um arquivo CSV padronizado.

#### `gerar_mock.py`

Script utilitário para criar arquivos CSV sintéticos em `data/snapshots/2026-08.csv` e `data/snapshots/2026-09.csv`. Permite testar todos os cenários de alteração, inserção, remoção e inconsistência sem depender da conexão com a internet ou da disponibilidade dos servidores da ANS.

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

Para executar o projeto, são necessários:

* Python 3.9 ou superior;
* Gerenciador de pacotes `pip`.

### 2. Instalar as dependências

Abra o terminal no diretório do projeto e instale as bibliotecas requeridas:

```bash
pip install -r requirements.txt
```

Bibliotecas utilizadas:
* `pandas`: Manipulação e sanitização de dados estruturados;
* `requests`: Download de arquivos via HTTP/FTP;
* `python-dotenv`: Suporte a variáveis de ambiente (se aplicável).

### 3. Modo de Execução Offline (Com dados Mock)

Para testar a aplicação imediatamente sem realizar downloads externos da ANS:

#### Passo 3.1: Gerar os dados sintéticos de teste

```bash
python gerar_mock.py
```

Isso criará os arquivos `2026-08.csv` e `2026-09.csv` no diretório `data/snapshots/`.

#### Passo 3.2: Executar a análise com a flag `--sem-download`

```bash
python main.py 2026-08 2026-09 --sem-download
```

#### Passo 3.3: Executar a análise e exportar o relatório em CSV

```bash
python main.py 2026-08 2026-09 --sem-download --exportar
```

O arquivo retornado será salvo em `output/diffs/diff_2026-08_2026-09.csv`.

### 4. Modo de Execução Online (Com dados reais da ANS)

Para baixar e analisar snapshots diretamente do portal da ANS:

```bash
python main.py 2026-08 2026-09 --exportar
```

A aplicação fará o download automatizado do relatório cadastral mais recente e executará o pipeline completo de comparação.

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

### Exemplo de Saída no Terminal

```text
===================================================
ANS Health Tracker  |  2026-08 -> 2026-09
===================================================

  Novos registros:    3
  Removidos:          2
  Alterados:          14
  Inconsistencias:    1

--- Mudancas criticas ---
  [!] UNIMED LTDA (ANS 300005): modalidade  Cooperativa Medica -> Medicina de Grupo

--- Inconsistencias ---
  [x] cnpj_invalido: VIDA PLENA S.A. (ANS 300042) -- CNPJ '123' fora do formato esperado
```

### Exemplo do Arquivo CSV Exportado (`output/diffs/diff_2026-08_2026-09.csv`)

```csv
registro_ans,razao_social,tipo_mudanca,campo,valor_anterior,valor_atual
300099,NOVA OPERADORA SAUDE,adicionado,,,
300010,OPERADORA ANTIGA LTDA,removido,,,
300005,UNIMED LTDA,alterado,modalidade,Cooperativa Medica,Medicina de Grupo
300042,VIDA PLENA S.A.,inconsistencia,cnpj_invalido,,CNPJ '123' fora do formato esperado (14 digitos)
```

## Fluxo de funcionamento

1. O usuário invoca o script `main.py` passando os períodos de referência.
2. O `main.py` aciona a verificação no módulo `fetcher.py`.
3. Se a flag `--sem-download` estiver ativa, o sistema verifica a existência dos arquivos em `data/snapshots/`.
4. Caso a flag `--sem-download` não seja informada e o arquivo não exista localmente, o `fetcher.py` realiza o download com streaming do servidor da ANS.
5. Os arquivos CSV são lidos e processados pelo `loader.py`, onde os cabeçalhos são sanitizados (remoção de acentos e espaços), os textos normalizados e os códigos `registro_ans` padronizados para 6 dígitos com zeros à esquerda.
6. O `comparator.py` indexa os dataframes pelo `registro_ans`, compara os conjuntos de chaves para identificar inserções e exclusões, e verifica divergências campo a campo nas colunas monitoradas.
7. O `analyzer.py` executa testes de integridade no snapshot mais recente, identificando CNPJs com formatação inválida, duplicações de `registro_ans` e razões sociais ausentes.
8. Os resultados são agregados no objeto `ResumoDiff`.
9. O `reporter.py` formata o relatório, imprime as estatísticas com destaque de cores no terminal e, se a flag `--exportar` estiver presente, gera o arquivo CSV final na pasta `output/diffs/`.

## Decisões técnicas

### Escolha da Biblioteca Pandas para Manipulação de Dados

**Escolha:** Pandas (`pd.read_csv`).

**Motivo:** Os relatórios cadastrais da ANS possuem formatos de colunas legados, variações de espaçamento e caracteres acentuados. A biblioteca Pandas permite aplicar transformações em lote de maneira expressiva e rápida.

**Ponto positivo:** Simplifica operações de busca, filtragem e rebatismo de colunas com sintaxe limpa.

**Limitação:** Para arquivos com dezenas de gigabytes, a leitura completa em memória exige atenção. No escopo do CADOP (alguns megabytes), a performance é instantânea.

### Padronização da Chave Primária por `zfill`

**Escolha:** Aplicação de `str.zfill(6)` na coluna `registro_ans`.

**Motivo:** O código de operadora ANS possui exatamente 6 caracteres numéricos. Ferramentas como Excel ou interpretadores padrão de CSV convertem números com zeros à esquerda em inteiros (ex: `001234` vira `1234`), gerando falsos positivos na comparação de snapshots.

**Ponto positivo:** Garante a acurácia de 100% no confronto de registros entre arquivos de datas distintas.

**Limitação:** Exige que a função de carga seja aplicada obrigatoriamente antes de qualquer tentativa de cruzamento de dados.

### Modelagem de Domínio com Dataclasses

**Escolha:** Uso de `dataclasses` em `models.py`.

**Motivo:** Manter a camada de apresentação e comparação desvinculada de tipos primitivos ou dicionários soltos.

**Ponto positivo:** Melhora o autocompletar da IDE, previne erros de digitação em chaves de dicionário e fornece tipagem estática clara.

**Limitação:** Adiciona uma etapa leve de conversão de dados entre os DataFrames do Pandas e as instâncias da classe.

### Destaque Terminal com Sequências ANSI Nativas

**Escolha:** Códigos de formatação de terminal ANSI sem dependências externas.

**Motivo:** Evita poluir o `requirements.txt` com bibliotecas adicionais, mantendo o projeto leve e de fácil portabilidade.

**Ponto positivo:** Instalação limpa e rápida em qualquer ambiente.

**Limitação:** Requer suporte a ANSI no console executador.

## Tratamento de inconsistências

### Parâmetros de Entrada Inválidos

O parser `argparse` valida a obrigatoriedade dos parâmetros posicionais `periodo_anterior` e `periodo_atual`. Se omitidos, o script apresenta a ajuda resumida da CLI.

### Snapshot Não Encontrado sem Download

Quando a flag `--sem-download` é passada e o arquivo CSV não se encontra no caminho local `data/snapshots/`, o script interrompe a execução graciosamente com código de saída 1 e mensagem explicativa.

### Validação de CNPJs

CNPJs que não atendem à máscara de 14 dígitos numéricos são identificados por regex e reportados como `cnpj_invalido` no sumário do relatório.

### Duplicidade de Chaves no Registro ANS

Caso existam múltiplos registros com o mesmo `registro_ans` em um mesmo snapshot, a anomalia é detectada e sinalizada como `registro_duplicado`.

## Limitações atuais

* A busca online depende da disponibilidade do servidor FTP/HTTP público da Agência Nacional de Saúde Suplementar (ANS);
* O analisador valida o formato e extensão do CNPJ, mas não efetua o cálculo formal dos dígitos verificadores (módulo 11);
* A comparação é realizada em memória RAM.

## Possíveis melhorias

Uma possível melhoria seria a adição da verificação matemática completa dos dígitos verificadores do CNPJ.

Uma possível melhoria seria a criação de um Dashboard web interativo (utilizando FastAPI + Vue.js ou Streamlit) para exibição gráfica das mudanças ao longo do tempo.

O sistema poderia ser integrado a um banco de dados relacional para persistência dos diffs e histórico de auditoria.

## Autor

Ronaldo Dutra Filho
