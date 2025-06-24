import os
import time
import json
import re
from datetime import datetime, timedelta
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from collections import Counter

CLEAN_DIR = os.path.join(os.path.dirname(__file__), 'clean_data')
RAW_DIR = os.path.join(os.path.dirname(__file__), 'raw_data')
os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

def build_search_url(date):
    return f"https://diariooficial.abc.go.gov.br/buscanova/#/p=1&q=licitação&di={date}&df={date}"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver

def save_raw_data(filename, content):
    path = os.path.join(RAW_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def find_edition_codes_by_date(driver, date):
    url = build_search_url(date)
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    save_raw_data(f'busca_{date}.html', driver.page_source)
    codes = []
    for a_tag in soup.find_all('a', href=True):
        match = re.search(r'/ver-html/(\d+)/', a_tag['href'])
        if match:
            code = match.group(1)
            if code not in codes:
                codes.append(code)
    return codes

def extract_materias(driver, edition_code):
    edition_url = f"https://diariooficial.abc.go.gov.br/portal/visualizacoes/view_html_diario/{edition_code}"
    driver.get(edition_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    save_raw_data(f'edition_{edition_code}.html', driver.page_source)

    palavras_chave = [
        "licitação", "pregão", "concorrência", "tomada de preços",
        "dispensa", "inexigibilidade"
    ]
    palavras_indesejadas = ["resultado", "julgamento"]

    materias = []
    for span in soup.find_all('span', class_='file'):
        link = span.find('a', class_='linkMateria')
        if link and link.has_attr('identificador'):
            texto = link.get_text(strip=True)
            texto_lower = texto.lower()

            contem_chave = any(k in texto_lower for k in palavras_chave)
            contem_indesejada = any(p in texto_lower for p in palavras_indesejadas)

            if contem_chave and not contem_indesejada:
                materias.append({
                    'identificador': link['identificador'],
                    'texto': texto
                })

    return materias


def extract_licitacao_details(html_content, ident):
    soup = BeautifulSoup(html_content, 'html.parser')
    full_text = soup.get_text(separator=' ', strip=True)

    # Converte tudo para minúsculo para facilitar a filtragem
    full_text_lower = full_text.lower()

    # Palavras indesejadas — se alguma for encontrada, não retorna nada
    if any(p in full_text_lower for p in ["resultado", "julgamento", "aprovação e ordenação de despesas"]):
        return []

    # Corta no "Protocolo"
    cutoff_match = re.search(r'(?i)(?=\bProtocolo\b)', full_text)
    if cutoff_match:
        full_text = full_text[:cutoff_match.start()]

    keywords_priority = [
        "Pregão",
        "Concorrência",
        "Tomada de Preços",
        "Dispensa",
        "Inexigibilidade",
        "Licitação"
    ]

    tipo_encontrado = None
    for keyword in keywords_priority:
        if re.search(r'\b' + re.escape(keyword) + r'\b', full_text, re.IGNORECASE):
            tipo_encontrado = keyword
            break

    if tipo_encontrado:
        resumo_limpo = re.sub(r'\s+', ' ', full_text).strip()
        return [{
            "identificador": ident,
            "Tipo": tipo_encontrado,
            "Resumo": resumo_limpo
        }]
    return []


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def executar_scraper_doe_go(start_date=None, end_date=None):
    if not start_date or not end_date:
        today = datetime.now()
        start_date = end_date = today
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y%m%d")
        end_date = datetime.strptime(end_date, "%Y%m%d")

    driver = setup_driver()
    try:
        all_results = []
        keywords = ["Licitação", "Pregão", "Concorrência", "Tomada de Preços", "Dispensa", "Inexigibilidade"]

        for date in daterange(start_date, end_date):
            date_str = date.strftime('%Y%m%d')
            print(f"[INFO] Processando data: {date_str}")
            edition_codes = find_edition_codes_by_date(driver, date_str)
            if not edition_codes:
                print(f"[INFO] Nenhuma edição encontrada para {date_str}")
                continue

            for edition_code in edition_codes:
                materias = extract_materias(driver, edition_code)
                materias_filtradas = [m for m in materias
                if any(k.lower() in m['texto'].lower() for k in keywords)
                and not any(excl in m['texto'].lower() for excl in ['julgamento', 'resultado', 'torna público o resultado', 'ratificação']) # palavras a excluir
            ]

                for materia in materias_filtradas:
                    ident = materia['identificador']
                    api_url = f"https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/publicacoes_ver_conteudo/{ident}"
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        detalhes = extract_licitacao_details(response.text, ident)
                        for item in detalhes:
                            item['data_publicacao'] = date.strftime('%d/%m/%Y')
                        all_results.extend(detalhes)
                    else:
                        print(f"[WARN] Falha ao buscar API para identificador {ident}")

        # Salvar arquivo
        filename = f"licitacoes_{start_date.strftime('%Y%m%d')}_a_{end_date.strftime('%Y%m%d')}_doe.json"
        output_path = os.path.join(CLEAN_DIR, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)

        print(f"\n[SCRAPER] JSON salvo em: {output_path}\n")
        return output_path

    finally:
        driver.quit()
