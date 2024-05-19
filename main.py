import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query
from typing import List
import logging
import os
import asyncio

# uvicorn main:app --reload

logging.basicConfig(level=logging.DEBUG)
app = FastAPI()
BASE_URL = os.getenv("BASE_URL", "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_0")

timeout_config = httpx.Timeout(
    connect=20.0,
    read=120.0,
    write=30.0,
    pool=60.0
)


async def fetch_content(session: httpx.AsyncClient, url: str, params: dict = None):
    try:
        response = await session.get(url, params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        logging.error(f"Erro ao acessar URL: {e.response.status_code}")
        return ""


async def scrape_data_production(url_selected: str, year_selected: str) -> List[dict]:
    logging.debug(f"URL acessada: {url_selected}{2}")
    url_selected = f"{url_selected}{2}"
    all_data = []

    async with httpx.AsyncClient(timeout=timeout_config) as session:
        content = await fetch_content(session, url_selected)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        label_text = soup.find('label', class_='lbl_pesq')
        if not label_text:
            logging.error("Label com a classe 'lbl_pesq' não encontrada.")
            return []

        year_range = label_text.text[label_text.text.find('[')+1:label_text.text.find(']')]
        start_year, end_year = map(int, year_range.split('-'))
        available_years = range(start_year, end_year + 1) if year_selected.upper() == '' else [int(year_selected)]

        tasks = [(year, fetch_content(session, url_selected, {'ano': year})) for year in available_years]
        responses = await asyncio.gather(*[task[1] for task in tasks])

        for response_content, (year, _) in zip(responses, tasks):
            if not response_content:
                continue

            updated_soup = BeautifulSoup(response_content, 'html.parser')
            table = updated_soup.find('table', class_='tb_dados')
            if not table:
                continue

            tipo = 'Desconhecido'
            data = []
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    product = cells[0].text.strip()
                    quantity = cells[1].text.strip()

                    if cells[0].has_attr('class') and 'tb_item' in cells[0]['class']:
                        tipo = product
                    elif cells[0].has_attr('class') and 'tb_subitem' in cells[0]['class']:
                        data.append({
                            'Ano': year,
                            'Tipo': tipo,
                            'Produto': product,
                            'Quantidade': quantity,
                            'Quantidade tipo': 'L'
                        })

            if data:
                all_data.extend(data)

    return all_data


async def scrape_data_processing(url_selected: str, year_selected: str, category: int) -> List[dict]:
    logging.debug(f"URL acessada: {url_selected}{3}")
    url_selected = f"{url_selected}{3}"
    all_data = []

    async with httpx.AsyncClient(timeout=timeout_config) as session:
        content = await fetch_content(session, url_selected)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        suboptions = soup.find_all('button', class_='btn_sopt')
        if category is not None:
            suboptions = [so for so in suboptions if so['value'].endswith(str(category))]

        year_range = soup.find('label', class_='lbl_pesq')
        if not year_range:
            logging.error("Label com a classe 'lbl_pesq' não encontrada.")
            return []

        year_range = year_range.text[year_range.text.find('[')+1:year_range.text.find(']')]
        start_year, end_year = map(int, year_range.split('-'))
        available_years = range(start_year, end_year + 1) if year_selected.upper() == '' else [int(year_selected)]

        tasks = []
        for button in suboptions:
            suboption_value = button['value']
            suboption_text = button.text.strip()
            for year in available_years:
                updated_url = f"{url_selected}&subopcao={suboption_value}&ano={year}"
                tasks.append((year, suboption_text, fetch_content(session, updated_url)))

        responses = await asyncio.gather(*[task[2] for task in tasks])

        for response_content, (year, suboption_text, _) in zip(responses, tasks):
            if not response_content:
                continue

            updated_soup = BeautifulSoup(response_content, 'html.parser')
            table = updated_soup.find('table', class_='tb_dados')
            if not table:
                continue

            tipo = 'Desconhecido'
            data = []
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    product = cells[0].text.strip()
                    quantity = cells[1].text.strip()

                    if cells[0].has_attr('class') and 'tb_item' in cells[0]['class']:
                        tipo = product
                    elif cells[0].has_attr('class') and 'tb_subitem' in cells[0]['class']:
                        data.append({
                            'Ano': year,
                            'Categoria': suboption_text,
                            'Tipo': tipo,
                            'Produto': product,
                            'Quantidade': quantity,
                            'Quantidade tipo': 'Kg'
                        })

            if data:
                all_data.extend(data)

    return all_data


async def scrape_data_commercialization(url_selected: str, year_selected: str) -> List[dict]:
    logging.debug(f"URL acessada: {url_selected}{4}")
    url_selected = f"{url_selected}{4}"
    all_data = []

    async with httpx.AsyncClient(timeout=timeout_config) as session:
        content = await fetch_content(session, url_selected)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        label_text = soup.find('label', class_='lbl_pesq')
        if not label_text:
            logging.error("Label com a classe 'lbl_pesq' não encontrada.")
            return []

        year_range = label_text.text[label_text.text.find('[')+1:label_text.text.find(']')]
        start_year, end_year = map(int, year_range.split('-'))
        available_years = range(start_year, end_year + 1) if year_selected.upper() == '' else [int(year_selected)]

        tasks = [(year, fetch_content(session, url_selected, {'ano': year})) for year in available_years]
        responses = await asyncio.gather(*[task[1] for task in tasks])

        for response_content, (year, _) in zip(responses, tasks):
            if not response_content:
                continue

            updated_soup = BeautifulSoup(response_content, 'html.parser')
            table = updated_soup.find('table', class_='tb_dados')
            if not table:
                continue

            tipo = 'Desconhecido'
            data = []
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    product = cells[0].text.strip()
                    quantity = cells[1].text.strip()

                    if cells[0].has_attr('class') and 'tb_item' in cells[0]['class']:
                        tipo = product
                    elif cells[0].has_attr('class') and 'tb_subitem' in cells[0]['class']:
                        data.append({
                            'Ano': year,
                            'Tipo': tipo,
                            'Produto': product,
                            'Quantidade': quantity,
                            'Quantidade tipo': 'L'
                        })

            if data:
                all_data.extend(data)

    return all_data


async def scrape_data_importation(url_selected: str, year_selected: str, category: int) -> List[dict]:
    logging.debug(f"URL acessada: {url_selected}{5}")
    url_selected = f"{url_selected}{5}"
    all_data = []

    async with httpx.AsyncClient(timeout=timeout_config) as session:
        content = await fetch_content(session, url_selected)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        suboptions = soup.find_all('button', class_='btn_sopt')
        if category is not None:
            suboptions = [so for so in suboptions if so['value'].endswith(str(category))]

        year_range = soup.find('label', class_='lbl_pesq')
        if not year_range:
            logging.error("Label com a classe 'lbl_pesq' não encontrada.")
            return []

        year_range = year_range.text[year_range.text.find('[')+1:year_range.text.find(']')]
        start_year, end_year = map(int, year_range.split('-'))
        available_years = range(start_year, end_year + 1) if year_selected.upper() == '' else [int(year_selected)]

        tasks = []
        for button in suboptions:
            suboption_value = button['value']
            suboption_text = button.text.strip()
            for year in available_years:
                updated_url = f"{url_selected}&subopcao={suboption_value}&ano={year}"
                tasks.append((year, suboption_text, fetch_content(session, updated_url)))

        responses = await asyncio.gather(*[task[2] for task in tasks])

        for response_content, (year, suboption_text, _) in zip(responses, tasks):
            if not response_content:
                continue

            updated_soup = BeautifulSoup(response_content, 'html.parser')
            table = updated_soup.find('table', class_='tb_dados')
            if not table:
                continue

            tbody = table.find('tbody')
            if not tbody:
                continue

            data = []
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    country = cells[0].text.strip()
                    quantity = cells[1].text.strip()
                    value = cells[2].text.strip()

                    data.append({
                        'Ano': year,
                        'Categoria': suboption_text,
                        'País': country,
                        'Quantidade': quantity,
                        'Quantidade tipo': 'Kg',
                        'Valor': value,
                        'Valor tipo': 'US$',
                    })

            if data:
                all_data.extend(data)

    return all_data


async def scrape_data_exportation(url_selected: str, year_selected: str, category: int) -> List[dict]:
    logging.debug(f"URL acessada: {url_selected}{6}")
    url_selected = f"{url_selected}{6}"
    all_data = []

    async with httpx.AsyncClient(timeout=timeout_config) as session:
        content = await fetch_content(session, url_selected)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        suboptions = soup.find_all('button', class_='btn_sopt')
        if category is not None:
            suboptions = [so for so in suboptions if so['value'].endswith(str(category))]

        year_range = soup.find('label', class_='lbl_pesq')
        if not year_range:
            logging.error("Label com a classe 'lbl_pesq' não encontrada.")
            return []

        year_range = year_range.text[year_range.text.find('[')+1:year_range.text.find(']')]
        start_year, end_year = map(int, year_range.split('-'))
        available_years = range(start_year, end_year + 1) if year_selected.upper() == '' else [int(year_selected)]

        tasks = []
        for button in suboptions:
            suboption_value = button['value']
            suboption_text = button.text.strip()
            for year in available_years:
                updated_url = f"{url_selected}&subopcao={suboption_value}&ano={year}"
                tasks.append((year, suboption_text, fetch_content(session, updated_url)))

        responses = await asyncio.gather(*[task[2] for task in tasks])

        for response_content, (year, suboption_text, _) in zip(responses, tasks):
            if not response_content:
                continue

            updated_soup = BeautifulSoup(response_content, 'html.parser')
            table = updated_soup.find('table', class_='tb_dados')
            if not table:
                continue

            tbody = table.find('tbody')
            if not tbody:
                continue

            data = []
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    country = cells[0].text.strip()
                    quantity = cells[1].text.strip()
                    value = cells[2].text.strip()

                    data.append({
                        'Ano': year,
                        'Categoria': suboption_text,
                        'País': country,
                        'Quantidade': quantity,
                        'Quantidade tipo': 'Kg',
                        'Valor': value,
                        'Valor tipo': 'US$',
                    })

            if data:
                all_data.extend(data)

    return all_data


@app.get("/scrape_data_production", summary="Dados de Produção",
         response_description="Os dados extraídos no formato JSON",
         description="Raspa dados sobre a produção do site da Embrapa com base no ano especificado. Retorna os dados em um formato JSON estruturado.",
         response_model=List[dict],
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": [{
                             "Ano": 2024,
                             "Tipo": "VINHO DE MESA",
                             "Produto": "Tinto",
                             "Quantidade": "139.320.884",
                             "Quantidade tipo": "L"
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_production(year: str = Query('', description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis")):
    return await scrape_data_production(BASE_URL, year)


@app.get("/scrape_data_processing", summary="Dados de Processamento",
         response_description="Os dados extraídos no formato JSON",
         description="Raspa dados sobre o processamento do site da Embrapa com base no ano e categoria especificados. Retorna os dados em um formato JSON estruturado.",
         response_model=List[dict],
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": [{
                             "Ano": 2024,
                             "Categoria": "Viníferas",
                             "Tipo": "Tintas",
                             "Produto": "Alicante Bouschet",
                             "Quantidade": "811.140",
                             "Quantidade tipo": "Kg"
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_processing(year: str = Query('', description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis"),
                                     category: int = Query(None, ge=1, le=4, description="Categoria para filtrar os dados, deixe vazio para todas as categorias disponíveis, 1 a 4 para categorias específicas")):
    return await scrape_data_processing(BASE_URL, year, category)


@app.get("/scrape_data_commercialization", summary="Dados de Comercialização",
         response_description="Os dados extraídos no formato JSON",
         description="Raspa dados sobre a produção do site da Embrapa com base no ano especificado. Retorna os dados em um formato JSON estruturado.",
         response_model=List[dict],
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": [{
                             "Ano": 2024,
                             "Tipo": "VINHO DE MESA",
                             "Produto": "Tinto",
                             "Quantidade": "139.320.884",
                             "Quantidade tipo": "L"
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_commercialization(year: str = Query('', description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis")):
    return await scrape_data_commercialization(BASE_URL, year)


@app.get("/scrape_data_importation", summary="Dados de Importação",
         response_description="Os dados extraídos no formato JSON",
         description="Raspa dados sobre o processamento do site da Embrapa com base no ano e categoria especificados. Retorna os dados em um formato JSON estruturado.",
         response_model=List[dict],
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": [{
                             "Ano": 2024,
                             "Categoria": "Vinhos de mesa",
                             "País": "Africa do Sul",
                             "Quantidade": "811.140",
                             "Quantidade tipo": "Kg",
                             "Valor": "811.140",
                             "Valor tipo": "US$"
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_importation(year: str = Query('', description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis"),
                                     category: int = Query(None, ge=1, le=5, description="Categoria para filtrar os dados, deixe vazio para todas as categorias disponíveis, 1 a 5 para categorias específicas")):
    return await scrape_data_importation(BASE_URL, year, category)


@app.get("/scrape_data_exportation", summary="Dados de Exportação",
         response_description="Os dados extraídos no formato JSON",
         description="Raspa dados sobre o processamento do site da Embrapa com base no ano e categoria especificados. Retorna os dados em um formato JSON estruturado.",
         response_model=List[dict],
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": [{
                             "Ano": 2024,
                             "Categoria": "Vinhos de mesa",
                             "País": "Africa do Sul",
                             "Quantidade": "811.140",
                             "Quantidade tipo": "Kg",
                             "Valor": "811.140",
                             "Valor tipo": "US$"
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_exportation(year: str = Query('', description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis"),
                                     category: int = Query(None, ge=1, le=5, description="Categoria para filtrar os dados, deixe vazio para todas as categorias disponíveis, 1 a 5 para categorias específicas")):
    return await scrape_data_exportation(BASE_URL, year, category)