# Embrapa - Tech Challenge Fiap - Desenvolvedores

- Gabriel Sargeiro ([LinkedIn](https://www.linkedin.com/in/gabriel-sargeiro/))
- Guilherme Lobo ([LinkedIn](https://www.linkedin.com/in/guilhermegclobo/))
- Matheus Moura ([LinkedIn](https://www.linkedin.com/in/matheus-moura-pinho-55a25b186/))

# Projeto Embrapa Vitivinicultura

Este projeto consiste em uma API pública para consulta de dados de vitivinicultura da Embrapa. A API coleta dados de produção, processamento, comercialização, importação e exportação de produtos vinícolas.

- Dados disponiveis em:
   - http://vitibrasil.cnpuv.embrapa.br

## Estrutura do Projeto

embrapa_fiap/

    ├── CSV/
    │ ├── comercio.csv
    │ ├── ExpEspumantes.csv
    │ ├── ExpSuco.csv
    │ ├── ExpUva.csv
    │ ├── ExpVinho.csv
    │ ├── ImpEspumantes.csv
    │ ├── ImpFrescas.csv
    │ ├── ImpPassas.csv
    │ ├── ImpSuco.csv
    │ ├── ImpVinhos.csv
    │ ├── ProcessaAmericanas.csv
    │ ├── ProcessaMesa.csv
    │ ├── ProcessaSemclass.csv
    │ ├── ProcessaViniferas.csv
    │ └── Producao.csv
    ├── .gitignore
    ├── main.py
    ├── project_links.md
    ├── README.md
    └── requirements.txt

## Dependências
- annotated-types==0.6.0
- anyio==3.7.1
- beautifulsoup4==4.12.3
- certifi==2024.2.2
- charset-normalizer==3.3.2
- click==8.1.7
- fastapi==0.103.2
- h11==0.14.0
- httpcore==1.0.5
- httpx==0.26.0
- idna==3.7
- pydantic==2.7.1
- pydantic_core==2.18.2
- requests==2.31.0
- sniffio==1.3.1
- soupsieve==2.5
- starlette==0.27.0
- typing_extensions==4.11.0
- urllib3==2.2.1
- uvicorn==0.29.0

## Configuração do Ambiente
1. Clone o repositório:
   ```sh
   git clone https://github.com/guilhermelobo94/embrapa_fiap.git
   cd embrapa_fiap
   python -m venv venv

## Ative o ambiente virtual:
1. No Windows:
   ```sh
   venv\Scripts\activate
2. No macOS/Linux:
   ```sh
   source venv/bin/activate

## Instale as dependências:
1. Executar:
   ```sh
   pip install -r requirements.txt

## Executando a API

1. No PyCharm, configure o projeto para rodar o servidor FastAPI:
   - Vá em Run > Edit Configurations...
   - Clique no + para adicionar uma nova configuração.
   - Selecione Python.
   - Defina um nome para a configuração (ex: FastAPI).
   - Em Script Path, selecione o arquivo main.py.
   - Em Parameters, adicione uvicorn main:app --reload.
   - Configure o Working Directory para a pasta do projeto.
   - Clique em Apply e depois em OK.
2. Execute a configuração criada.

## Endpoints da API

- **/scrape_data_production**
   - Descrição: Raspa dados de produção da Embrapa por ano.
   - Exemplo de Uso: `GET /scrape_data_production?year=`

- **/scrape_data_processing**
   - Descrição: Raspa dados de processamento da Embrapa por ano e categoria.
   - Exemplo de Uso: `GET /scrape_data_processing?year=&category=`

- **/scrape_data_commercialization**
   - Descrição: Raspa dados de comercialização da Embrapa por ano.
   - Exemplo de Uso: `GET /scrape_data_commercialization?year=`

- **/scrape_data_importation**
   - Descrição: Raspa dados de importação da Embrapa por ano e categoria.
   - Exemplo de Uso: `GET /scrape_data_importation?year=&category=`

- **/scrape_data_exportation**
   - Descrição: Raspa dados de exportação da Embrapa por ano e categoria.
   - Exemplo de Uso: `GET /scrape_data_exportation?year=&category=`

## Cenário de Utilização da API com Machine Learning
### Descrição do Cenário
A API de vitivinicultura será usada para coletar dados de produção, processamento, comercialização, importação e exportação de produtos vinícolas. Esses dados serão armazenados em um banco de dados SQL para posterior análise e uso em modelos de Machine Learning. A seguir está um cenário detalhado que descreve a arquitetura do projeto desde a ingestão dos dados até a alimentação do modelo de ML.

### Arquitetura do Projeto
1. **Ingestão de Dados**
    - A API coleta dados das diversas abas do site da Embrapa.
    - Esses dados são extraídos e estruturados em formato JSON.


2. **Armazenamento dos Dados**
    - Os dados JSON são enviados para um banco de dados SQL, recomendado PostgreSQL pela sua robustez e suporte a operações complexas.
    - Uma alternativa é usar um data warehouse como Amazon Redshift para grandes volumes de dados.


3. **Pré-processamento dos Dados**
    - Os dados armazenados são limpos e transformados.
    - Técnicas de limpeza podem incluir a remoção de duplicatas, tratamento de valores nulos e normalização.
    - Transformações podem incluir agregações, cálculos de novas métricas e formatação dos dados para uso em modelos de ML.


4. **Pipeline de Machine Learning**
    - **Treinamento:** Os dados pré-processados são usados para treinar modelos de Machine Learning. Isso pode incluir modelos de regressão, classificação ou séries temporais, dependendo dos objetivos específicos.
    - **Validação:** Os modelos treinados são validados com um conjunto de dados de teste para garantir sua precisão e capacidade de generalização.


5. **Deploy do Modelo**
    - **Serviço de Previsão:** Os modelos treinados são implantados em um serviço de previsão que pode ser acessado via API.
    - **Integração:** A API pode ser integrada com outros sistemas para fornecer previsões em tempo real ou em lote.
    - **Monitoramento e Atualização:** O desempenho do modelo é monitorado continuamente e os modelos são re-treinados periodicamente com novos dados para manter a precisão.

### Ferramentas Utilizadas
1. **API:** FastAPI para a coleta de dados.
2. **Banco de Dados:** SQL (ainda não implementado).
3. **Machine Learning:** Frameworks como scikit-learn ou TensorFlow (ainda não implementado).
4. **Deploy:** Uvicorn para rodar a API e serviços AWS para o deploy do modelo.

## Deploy da API
- Link do deploy da API: http://52.22.130.203/docs

## Repositório GitHub
- Link do repositório GitHub: https://github.com/guilhermelobo94/embrapa_fiap.git