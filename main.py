import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query
from typing import List, Dict, Union
import logging
import os
import asyncio
import csv

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
    try:
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

            year_range = label_text.text[label_text.text.find('[') + 1:label_text.text.find(']')]
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

                current_tipo = None

                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        product = cells[0].text.strip()
                        quantity = cells[1].text.strip()

                        if cells[0].has_attr('class') and 'tb_item' in cells[0]['class']:
                            if current_tipo:
                                all_data.append(current_tipo)
                            current_tipo = {
                                'tipo_titulo': product,
                                'Ano': year,
                                'quantidade_total': quantity,
                                'item': []
                            }
                        elif cells[0].has_attr('class') and 'tb_subitem' in cells[0]['class'] and current_tipo:
                            current_tipo['item'].append({
                                'item_titulo': product,
                                'quantidade': quantity,
                                'quantidade_tipo': 'L'
                            })

                if current_tipo:
                    all_data.append(current_tipo)

        final_data = [{
            'categoria_titulo': "Sem Categoria",
            'tipo': all_data
        }]

        return final_data
    except Exception as e:
        logging.error(f"Erro ao raspar dados: {str(e)}")
        if year_selected == '':
            year_selected = list(range(1970, 2024))
        else:
            year_selected = [year_selected]
        return csv_production(year_selected)


async def scrape_data_processing(url_selected: str, year_selected: str, category: int) -> List[dict]:
    try:
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

            year_range = year_range.text[year_range.text.find('[') + 1:year_range.text.find(']')]
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

                current_tipo = None
                categoria_data = {
                    "categoria_titulo": suboption_text,
                    "tipo": []
                }

                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        product = cells[0].text.strip()
                        quantity = cells[1].text.strip()

                        if cells[0].has_attr('class') and 'tb_item' in cells[0]['class']:
                            if current_tipo:
                                categoria_data["tipo"].append(current_tipo)
                            current_tipo = {
                                "tipo_titulo": product,
                                "Ano": year,
                                "quantidade_total": quantity,
                                "item": []
                            }
                        elif cells[0].has_attr('class') and 'tb_subitem' in cells[0]['class'] and current_tipo:
                            current_tipo["item"].append({
                                'item_titulo': product,
                                'quantidade': quantity,
                                'quantidade_tipo': 'Kg'
                            })

                if current_tipo:
                    categoria_data["tipo"].append(current_tipo)

                if categoria_data["tipo"]:
                    all_data.append(categoria_data)

        return all_data
    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        if not category:
            category_v = [1, 2, 3, 4]
        else:
            category_v = [category]
        if year_selected == '':
            year_selected = list(range(1970, 2023))
        else:
            year_selected = [year_selected]
        return csv_processing(year_selected, category_v)


async def scrape_data_commercialization(url_selected: str, year_selected: str) -> List[dict]:
    try:
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

            year_range = label_text.text[label_text.text.find('[') + 1:label_text.text.find(']')]
            start_year, end_year = map(int, year_range.split('-'))
            available_years = range(start_year, end_year + 1) if year_selected.upper() == '' else [int(year_selected)]

            tasks = [(year, fetch_content(session, url_selected, {'ano': year})) for year in available_years]
            responses = await asyncio.gather(*[task[1] for task in tasks])

            categoria_data = {
                "categoria_titulo": "Sem Categoria",
                "tipo": []
            }

            for response_content, (year, _) in zip(responses, tasks):
                if not response_content:
                    continue

                updated_soup = BeautifulSoup(response_content, 'html.parser')
                table = updated_soup.find('table', class_='tb_dados')
                if not table:
                    continue

                current_tipo = None

                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        product = cells[0].text.strip()
                        quantity = cells[1].text.strip()

                        if cells[0].has_attr('class') and 'tb_item' in cells[0]['class']:
                            if current_tipo:
                                categoria_data["tipo"].append(current_tipo)
                            current_tipo = {
                                'tipo_titulo': product,
                                'Ano': year,
                                'quantidade_total': quantity,
                                'item': []
                            }
                        elif cells[0].has_attr('class') and 'tb_subitem' in cells[0]['class'] and current_tipo:
                            current_tipo['item'].append({
                                'item_titulo': product,
                                'quantidade': quantity,
                                'quantidade_tipo': 'L'
                            })

                if current_tipo:
                    categoria_data["tipo"].append(current_tipo)

            if categoria_data["tipo"]:
                all_data.append(categoria_data)

        return all_data
    except Exception as e:
        logging.error(f"Erro na comercialização: {e}")
        if year_selected == '':
            year_selected = list(range(1970, 2023))
        else:
            year_selected = [year_selected]
        return csv_commercialization(year_selected)


async def scrape_data_importation(url_selected: str, year_selected: str, category: int) -> List[dict]:
    try:
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

            year_range = year_range.text[year_range.text.find('[') + 1:year_range.text.find(']')]
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

                current_tipo = None
                categoria_data = {
                    "categoria_titulo": suboption_text,
                    "tipo": []
                }

                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        country = cells[0].text.strip()
                        quantity = cells[1].text.strip()
                        value = cells[2].text.strip()

                        if current_tipo is None:
                            current_tipo = {
                                "tipo_titulo": "Sem Tipo",
                                "Ano": year,
                                "quantidade_total": "0",
                                "item": []
                            }

                        current_tipo["item"].append({
                            'item_titulo': country,
                            'quantidade': quantity,
                            'quantidade_tipo': 'Kg',
                            'valor': value,
                            'valor_tipo': 'US$'
                        })

                if current_tipo:
                    categoria_data["tipo"].append(current_tipo)

                if categoria_data["tipo"]:
                    all_data.append(categoria_data)

        return all_data
    except Exception as e:
        logging.error(f"Erro na importação: {e}")
        if not category:
            category_v = [1, 2, 3, 4, 5]
        else:
            category_v = [category]
        if year_selected == '':
            year_selected = list(range(1970, 2024))
        else:
            year_selected = [year_selected]
        return csv_importing(year_selected, category_v)


async def scrape_data_exportation(url_selected: str, year_selected: str, category: int) -> List[dict]:
    try:
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

            year_range = year_range.text[year_range.text.find('[') + 1:year_range.text.find(']')]
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

                current_tipo = None
                categoria_data = {
                    "categoria_titulo": suboption_text,
                    "tipo": []
                }

                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        country = cells[0].text.strip()
                        quantity = cells[1].text.strip()
                        value = cells[2].text.strip()

                        if current_tipo is None:
                            current_tipo = {
                                "tipo_titulo": "Sem Tipo",
                                "Ano": year,
                                "quantidade_total": "0",
                                "item": []
                            }

                        current_tipo["item"].append({
                            'item_titulo': country,
                            'quantidade': quantity,
                            'quantidade_tipo': 'Kg',
                            'valor': value,
                            'valor_tipo': 'US$'
                        })

                if current_tipo:
                    categoria_data["tipo"].append(current_tipo)

                if categoria_data["tipo"]:
                    all_data.append(categoria_data)

        return all_data
    except Exception as e:
        logging.error(f"Erro na exportação: {e}")
        if not category:
            category_v = [1, 2, 3, 4]
        else:
            category_v = [category]
        if year_selected == '':
            year_selected = list(range(1970, 2024))
        else:
            year_selected = [year_selected]
        return csv_exportation(year_selected, category_v)


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
                             "categoria_titulo": "Vinhos de mesa",
                             "tipo": [{
                                 "tipo_titulo": "VINHO DE MESA",
                                 "Ano": 2024,
                                 "quantidade_total": "217.208.604",
                                 "item": [{
                                     "item_titulo": "Tinto",
                                     "quantidade": "174.224.052",
                                     "quantidade_tipo": "L"
                                 }, {
                                     "item_titulo": "Branco",
                                     "quantidade": "748.400",
                                     "quantidade_tipo": "L"
                                 }, {
                                     "item_titulo": "Rosado",
                                     "quantidade": "42.236.152",
                                     "quantidade_tipo": "L"
                                 }]
                             }]
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_production(year: str = Query('',
                                                       description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis")):
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
                             "categoria_titulo": "Viníferas",
                             "tipo": [{
                                 "tipo_titulo": "VINHO DE MESA",
                                 "Ano": 2024,
                                 "quantidade_total": "217.208.604",
                                 "item": [{
                                     "item_titulo": "Tinto",
                                     "quantidade": "174.224.052",
                                     "quantidade_tipo": "Kg"
                                 }, {
                                     "item_titulo": "Branco",
                                     "quantidade": "748.400",
                                     "quantidade_tipo": "Kg"
                                 }, {
                                     "item_titulo": "Rosado",
                                     "quantidade": "42.236.152",
                                     "quantidade_tipo": "Kg"
                                 }]
                             }]
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_processing(year: str = Query('',
                                                       description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis"),
                                     category: int = Query(None, ge=1, le=4,
                                                           description="Categoria para filtrar os dados, deixe vazio para todas as categorias disponíveis, 1 a 4 para categorias específicas")):
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
                             "categoria_titulo": "Sem Categoria",
                             "tipo": [{
                                 "tipo_titulo": "VINHO DE MESA",
                                 "Ano": 2024,
                                 "quantidade_total": "217.208.604",
                                 "item": [{
                                     "item_titulo": "Tinto",
                                     "quantidade": "174.224.052",
                                     "quantidade_tipo": "L"
                                 }, {
                                     "item_titulo": "Branco",
                                     "quantidade": "748.400",
                                     "quantidade_tipo": "L"
                                 }, {
                                     "item_titulo": "Rosado",
                                     "quantidade": "42.236.152",
                                     "quantidade_tipo": "L"
                                 }]
                             }]
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_commercialization(year: str = Query('',
                                                              description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis")):
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
                             "categoria_titulo": "VINHO DE MESA",
                             "tipo": [{
                                 "tipo_titulo": "Sem Tipo",
                                 "Ano": 2024,
                                 "quantidade_total": "217.208.604",
                                 "item": [{
                                     "item_titulo": "País 1",
                                     "quantidade": "174.224.052",
                                     "quantidade_tipo": "Kg",
                                     "valor": "1000",
                                     "valor_tipo": "US$"
                                 }, {
                                     "item_titulo": "País 2",
                                     "quantidade": "748.400",
                                     "quantidade_tipo": "Kg",
                                     "valor": "500",
                                     "valor_tipo": "US$"
                                 }]
                             }]
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_importation(year: str = Query('',
                                                        description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis"),
                                      category: int = Query(None, ge=1, le=5,
                                                            description="Categoria para filtrar os dados, deixe vazio para todas as categorias disponíveis, 1 a 5 para categorias específicas")):
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
                             "categoria_titulo": "VINHO DE MESA",
                             "tipo": [{
                                 "tipo_titulo": "Sem Tipo",
                                 "Ano": 2024,
                                 "quantidade_total": "217.208.604",
                                 "item": [{
                                     "item_titulo": "País 1",
                                     "quantidade": "174.224.052",
                                     "quantidade_tipo": "Kg",
                                     "valor": "1000",
                                     "valor_tipo": "US$"
                                 }, {
                                     "item_titulo": "País 2",
                                     "quantidade": "748.400",
                                     "quantidade_tipo": "Kg",
                                     "valor": "500",
                                     "valor_tipo": "US$"
                                 }]
                             }]
                         }]
                     }
                 }
             }
         })
async def get_scrape_data_exportation(year: str = Query('',
                                                        description="Ano para filtrar os dados. Deixe vazio para obter todos os dados disponíveis"),
                                      category: int = Query(None, ge=1, le=4,
                                                            description="Categoria para filtrar os dados, deixe vazio para todas as categorias disponíveis, 1 a 4 para categorias específicas")):
    return await scrape_data_exportation(BASE_URL, year, category)


def csv_production(ano):
    data = []
    for elemento in ano:
        with open('CSV\\Producao.csv', 'r', encoding='utf-8') as ficheiro:
            reader = csv.reader(ficheiro)

            # Lendo a primeira linha para obter os títulos das colunas
            colunas = next(reader)[0].split(';')
            #print(colunas)

            # Encontrando a posição do ano nos títulos das colunas
            indice_ano = colunas.index(str(elemento))
            #print(indice_ano)
            tipo_string = ""
            # Iterar sobre as linhas restantes
            for linha in reader:
                # Verificando se a linha não está vazia
                if linha:
                    linha_v = linha[0].split(';')
                    #print(linha_v[1][2])
                    if linha_v[1][2] == "_":
                        # Adicionando os valores necessários ao item
                        # item.append({linha_v[0], tipo_string, linha_v[2], linha_v[indice_ano]})
                        #print(linha_v)
                        data[len(data)-1]['items'].append({'item_titulo': linha_v[2],
                                                           'quantidade': linha_v[indice_ano],
                                                           'quantidade_tipo': '2L'
                                                           })
                    else:
                        data.append({
                            'tipo_titulo': linha_v[1],
                            'ano': elemento,
                            'quantidade_total': linha_v[indice_ano],
                            'items': []
                        })

        #print(data)
    return [{'categoria_titulo':'Sem Categoria','tipo':data}]


def contains_type(data, tipo):
    for item in data:
        if item.get("tipo_titulo") == tipo:
            return True
    return False


def find_position_of_type(data, tipo):
    for index, item in enumerate(data):
        if item.get("tipo_titulo") == tipo:
            return index
    return -1


def csv_processing(ano, cat):
    category_data = []
    data = []
    category = []
    if 1 in cat:
        category.append("Viniferas")
    if 2 in cat:
        category.append("Americanas")
    if 3 in cat:
        category.append("Mesa")
    if 4 in cat:
        category.append("Semclass")
    print(ano)
    for elemento in category:
        for year in ano:
            print(year)
            with open('CSV\\Processa' + elemento + '.csv', 'r', encoding='utf-8') as ficheiro:
                reader = csv.reader(ficheiro, delimiter='\t')

                tipo_string = ""
                # Lendo a primeira linha para obter os títulos das colunas
                colunas = next(reader)
                # Encontrando a posição do ano nos títulos das colunas
                indice_ano = colunas.index(str(year))

                # Iterar sobre as linhas restantes
                for linha in reader:
                    # Verificando se a linha não está vazia
                    if linha:
                        if linha[1][2] == "_":
                            # Adicionando os valores necessários ao item
                            data[find_position_of_type(data, tipo_string)]['items'].append({
                                                            'item_titulo': linha[2],
                                                            'quantidade': linha[indice_ano],
                                                            'quantidade_tipo': 'Kg'
                                                        })
                        else:
                            data.append({
                                'tipo_titulo': linha[1],
                                'ano': year,
                                'quantidade_total': linha[indice_ano],
                                'items': []
                            })
                            tipo_string = linha[1]
            category_data.append({'categoria_titulo': elemento,
                                  'tipo': data})
    return category_data


def csv_commercialization(ano):
    print(ano)
    data = []
    for year in ano:
        with open('CSV\\Comercio.csv', 'r', encoding='utf-8') as ficheiro:
            reader = csv.reader(ficheiro, delimiter=';')

            # Lendo a primeira linha para obter os títulos das colunas
            colunas = next(reader)
            indice_ano = colunas.index(str(year))

            # Iterar sobre as linhas restantes
            for linha in reader:
                # Verificando se a linha não está vazia
                if linha:
                    # Verificando se o terceiro caractere do segundo campo é "_"
                    if linha[1][2] == "_":
                        #print(linha)
                        # Adicionando os valores necessários ao item
                        data[len(data) - 1]['items'].append({'item_titulo': linha[2],
                                                             'quantidade': linha[indice_ano],
                                                             'quantidade_tipo': 'L'
                                                             })
                    else:
                        data.append({
                            'tipo_titulo': linha[1],
                            'ano': year,
                            'quantidade_total': linha[indice_ano],
                            'items': []
                        })
    return [{'categoria_titulo':'Sem Categoria','tipo':data}]


def csv_importing(anos, cat):
    # Definição de categorias correspondentes
    categorias_dict = {
        1: "Vinhos",
        2: "Espumantes",
        3: "Frescas",
        4: "Passas",
        5: "Suco"
    }
    categorias_dict2 = {
        1: "Vinhos de Mesa",
        2: "Espumantes",
        3: "Uvas Frescas",
        4: "Uvas Passas",
        5: "Suco de Uva"
    }

    # Inicialização da estrutura de retorno
    resultado = []

    # Iterar sobre as categorias selecionadas
    for cat_id in cat:
        if cat_id in categorias_dict:
            categoria = categorias_dict[cat_id]
            categoria_titulo = categorias_dict2[cat_id]

            tipo_lista = []

            # Abrir e ler o arquivo CSV correspondente
            with open(f'CSV\\Imp{categoria}.csv', 'r', encoding='utf-8') as ficheiro:
                reader = csv.reader(ficheiro, delimiter=';')

                # Lendo a primeira linha para obter os títulos das colunas
                colunas = next(reader)

                for ano in anos:
                    if str(ano) in colunas:
                        indice_ano = colunas.index(str(ano))
                        quantidade_total = 0

                        tipo = {
                            "tipo_titulo": "Sem Tipo",
                            "ano": ano,
                            "quantidade_total": "0",  # Será atualizado com a soma das quantidades
                            "item": []
                        }

                        # Iterar sobre as linhas restantes
                        for linha in reader:
                            # Verificando se a linha não está vazia
                            if linha:
                                quantidade = int(linha[indice_ano].replace(".", ""))
                                valor = linha[indice_ano + 1]

                                tipo["item"].append({
                                    "item_titulo": linha[1],  # Nome do país
                                    "quantidade": quantidade,
                                    "quantidade_tipo": "Kg",
                                    "valor": valor,
                                    "valor_tipo": "US$"
                                })

                                quantidade_total += quantidade

                        tipo["quantidade_total"] = str(quantidade_total)
                        tipo_lista.append(tipo)

                        # Resetar o ponteiro do arquivo para a segunda linha
                        ficheiro.seek(0)
                        next(reader)  # Ignorar a linha de cabeçalho novamente

            resultado.append({
                "categoria_titulo": categoria_titulo,
                "tipo": tipo_lista
            })
    #print(resultado)
    return resultado


def csv_exportation(anos, cat):
    # Definição de categorias correspondentes
    categorias_dict = {
        1: "Vinhos",
        2: "Espumantes",
        3: "Frescas",
        4: "Suco"
    }
    categorias_dict2 = {
        1: "Vinhos de Mesa",
        2: "Espumantes",
        3: "Uvas Frescas",
        4: "Suco de Uva"
    }

    # Inicialização da estrutura de retorno
    resultado = []

    # Iterar sobre as categorias selecionadas
    for cat_id in cat:
        if cat_id in categorias_dict:
            categoria = categorias_dict[cat_id]
            categoria_titulo = categorias_dict2[cat_id]

            tipo_lista = []

            # Abrir e ler o arquivo CSV correspondente
            with open(f'CSV\\Imp{categoria}.csv', 'r', encoding='utf-8') as ficheiro:
                reader = csv.reader(ficheiro, delimiter=';')

                # Lendo a primeira linha para obter os títulos das colunas
                colunas = next(reader)

                for ano in anos:
                    if str(ano) in colunas:
                        indice_ano = colunas.index(str(ano))
                        quantidade_total = 0

                        tipo = {
                            "tipo_titulo": "Sem Tipo",
                            "ano": ano,
                            "quantidade_total": "0",  # Será atualizado com a soma das quantidades
                            "item": []
                        }

                        # Iterar sobre as linhas restantes
                        for linha in reader:
                            # Verificando se a linha não está vazia
                            if linha:
                                quantidade = int(linha[indice_ano].replace(".", ""))
                                valor = linha[indice_ano + 1]

                                tipo["item"].append({
                                    "item_titulo": linha[1],  # Nome do país
                                    "quantidade": quantidade,
                                    "quantidade_tipo": "Kg",
                                    "valor": valor,
                                    "valor_tipo": "US$"
                                })

                                quantidade_total += quantidade

                        tipo["quantidade_total"] = str(quantidade_total)
                        tipo_lista.append(tipo)

                        # Resetar o ponteiro do arquivo para a segunda linha
                        ficheiro.seek(0)
                        next(reader)  # Ignorar a linha de cabeçalho novamente

            resultado.append({
                "categoria_titulo": categoria_titulo,
                "tipo": tipo_lista
            })
    #print(resultado)
    return resultado



