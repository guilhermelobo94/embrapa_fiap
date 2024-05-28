# Embrapa - Tech Challenge Fiap

## 1. Objetivos;

1. Criar uma rest API em Python que faça a consulta no site da Embrapa (http://vitibrasil.cnpuv.embrapa.br/) - FastAPI e documentar a API (Swagger);

2. Criar método de autenticação (recomendável); **Não realizado**

3. Desenhar arquitetura de ingestão e alimentação do modelo (primeira etapa não é necessário a elaboração do modelo);


## 1.1 Acesso a documentação da API e a API que realiza a consulta na embrapa:

http://52.22.130.203/docs

## 1.3 Arquitetura de ingestão de dados e alimentação do modelo

Cenário
Vamos desenvolver uma API para a Embrapa que fornece dados detalhados sobre produção, processamento, comercialização, importação e exportação de vitivinicultura. A API utilizará raspagem de dados do site Vitibrasil usando BeautifulSoup. A arquitetura de ingestão de dados será composta por Apache Kafka, Apache Spark, Amazon S3, Amazon Redshift, FastAPI, Nginx e Amazon Lightsail, com monitoramento e logging realizados pelo Prometheus.

Arquitetura de Ingestão
1. Coleta de Dados
Raspagem de Dados:

Ferramenta de Raspagem: Utilizaremos BeautifulSoup, uma biblioteca Python para extração de dados de arquivos HTML e XML.
Agendamento: Um cron job ou serviço agendado no Amazon Lightsail será configurado para executar a raspagem de dados periodicamente (diariamente, semanalmente, etc.).
2. Pipeline de Ingestão com Apache Kafka
Pipeline de Dados:

Apache Kafka: Os dados raspados serão enviados para Apache Kafka, que atua como o sistema de mensageria de dados. Kafka permite a ingestão contínua e em tempo real de dados, garantindo escalabilidade e alta disponibilidade.
Produtores Kafka: Scripts de raspagem de dados atuam como produtores Kafka, enviando mensagens (dados raspados) para tópicos específicos em Kafka.
3. Processamento de Dados com Apache Spark
ETL (Extract, Transform, Load):

Apache Spark: Um cluster Spark será configurado para processar os dados provenientes dos tópicos do Kafka. O Spark realizará as seguintes etapas:
Extract (Extrair): Consumir dados dos tópicos Kafka.
Transform (Transformar): Limpar, enriquecer e transformar os dados em um formato adequado para análise.
Load (Carregar): Carregar os dados transformados no Amazon S3 e Amazon Redshift.
4. Armazenamento de Dados
Data Lake:

Amazon S3: Dados brutos e transformados são armazenados no Amazon S3, que serve como Data Lake. O S3 é usado para armazenamento durável e altamente disponível de grandes volumes de dados.
Data Warehouse:

Amazon Redshift: Dados transformados e estruturados são carregados no Amazon Redshift, um data warehouse que permite consultas rápidas e eficientes para análise de dados.
5. API de Acesso aos Dados
Desenvolvimento da API:

FastAPI: A API será desenvolvida utilizando FastAPI, um framework web moderno e de alto desempenho para construir APIs com Python.
Uvicorn: Uvicorn será utilizado como servidor ASGI para servir a aplicação FastAPI.
Proxy Reverso:

Nginx: Nginx será configurado como proxy reverso para gerenciar requisições à API, oferecendo balanceamento de carga e maior segurança.
Hospedagem:

Amazon Lightsail: A aplicação será hospedada no Amazon Lightsail, um serviço de computação na nuvem simplificado e de baixo custo da AWS.
6. Monitoramento e Manutenção
Monitoramento e Logging:

Prometheus: Prometheus será utilizado para monitorar a saúde e o desempenho de toda a infraestrutura, bem como para coleta e visualização de logs. Ele coleta métricas e dados de desempenho em tempo real, fornecendo informações detalhadas sobre a operação do sistema.
Grafana: Grafana será utilizado para visualizar as métricas coletadas pelo Prometheus em dashboards intuitivos.
Alertas:

AWS CloudWatch: Configuraremos alertas no AWS CloudWatch para notificar a equipe sobre qualquer anomalia ou falha no sistema.
Fluxo de Dados na Arquitetura
Raspagem de Dados:

Scripts de raspagem coletam dados do site Vitibrasil periodicamente usando BeautifulSoup e os enviam para Apache Kafka.
Ingestão com Kafka:

Apache Kafka recebe os dados raspados e os organiza em tópicos para processamento.
Processamento com Spark:

Apache Spark consome dados dos tópicos Kafka, realiza a limpeza, transformação e enriquece os dados.
Dados processados são carregados no Amazon S3 (Data Lake) e no Amazon Redshift (Data Warehouse).
API:

A API desenvolvida com FastAPI e servida pelo Uvicorn permite que os usuários acessem os dados processados.
Nginx atua como proxy reverso para gerenciar as requisições.
Monitoramento e Manutenção:

Prometheus monitora o desempenho e a saúde do sistema e coleta logs.
Grafana visualiza métricas de desempenho.
AWS CloudWatch configura alertas para notificação de problemas.






1.3.1 Desenho da arquitetura

       +----------------------------+
       |     Raspagem de Dados      |
       |   (BeautifulSoup)          |
       +------------+---------------+
                    |
                    v
       +----------------------------+
       |   Pipeline de Ingestão     |
       |      (Apache Kafka)        |
       +------------+---------------+
                    |
                    v
       +----------------------------+
       |    Processamento ETL       |
       |      (Apache Spark)        |
       +------------+---------------+
         /                  \
        v                    v
+-------------+       +--------------+
|   Data Lake |       | Data Warehouse|
|   (Amazon S3)|       | (Redshift)   |
+-------------+       +--------------+
        |                    |
        v                    v
+----------------------------+
|           API              |
| (FastAPI + Uvicorn + Nginx)|
+------------+---------------+
                    |
                    v
       +----------------------------+
       |    Hospedagem e Deploy     |
       |      (Amazon Lightsail)    |
       +------------+---------------+
                    |
                    v
       +----------------------------+
       |  Monitoramento & Logs      |
       | (Prometheus/Grafana)       |
       +----------------------------+




## 2. Desenvolvedores;

Gabriel Sargeiro (https://www.linkedin.com/in/gabriel-sargeiro/)

Guilherme Lobo (https://www.linkedin.com/in/guilhermegclobo/)

Matheus Moura (https://www.linkedin.com/in/matheus-moura-pinho-55a25b186/)
