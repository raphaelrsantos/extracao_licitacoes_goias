from scraper_doe import executar_scraper_doe_go
from llm_extractor import executar_llm_sobre_resumos
from api_pncp import consultar_pncp
from api_pncp import estruturar_dados_pncp
from html_report import gerar_relatorio_html
from graficos import gerar_graficos_combinados
import os
from datetime import datetime
import argparse
from time import sleep

parser = argparse.ArgumentParser(description='Pipeline de Extração e Estruturação de Licitações')
parser.add_argument('--start_date', type=str, required=True, help='Data inicial no formato YYYYMMDD')
parser.add_argument('--end_date', type=str, required=True, help='Data final no formato YYYYMMDD')
parser.add_argument('--data_pncp', type=str, required=True, help='Data de referência para consulta da API PNCP (YYYYMMDD)')
args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date

# Diretórios
CLEAN_DIR = os.path.join(os.path.dirname(__file__), 'clean_data')
os.makedirs(CLEAN_DIR, exist_ok=True)

# === Passo 1: Executar Scraper DOE-GO ===
print("\n[1] Iniciando extração de dados do DOE-GO (resumos)...")
caminho_json_resumos = executar_scraper_doe_go(args.start_date, args.end_date)


# === Passo 2: Processar resumos com LLM ===
print("\n[2] Estruturando dados dos resumos com LLM...\n")
caminho_json_llm = executar_llm_sobre_resumos(caminho_json_resumos)

# === Passo 3: Executar API do PNCP ===
print("\n[3] Consultando API do PNCP...\n")
dados_pncp = consultar_pncp(args.data_pncp)
if dados_pncp is None:
    print("\n[ERRO] Falha ao consultar a API do PNCP. Verifique a data ou a disponibilidade da API.\n")
    exit(1)
caminho_json_pncp = estruturar_dados_pncp(dados_pncp)
sleep(2)

# === Passo 4: Gerar relatório HTML ===
print("\n[4] Gerando relatório HTML...\n")
sleep(2)
output_html = os.path.join(CLEAN_DIR, f"relatorio.html")
gerar_relatorio_html(caminho_json_llm, caminho_json_pncp, output_html)

# === Passo 5: Gerar os gráficos e insights ===
gerar_graficos_combinados(
    "clean_data/licitacoes_20250616_a_20250618_doe_llm.json",
    "clean_data/licitacoes_pncp.json"
)


# === Passo 4: Gerar relatório HTML ===
# caminho_json_llm = r"C:\Users\rapha\OneDrive\Área de Trabalho\Pos UFG\EAD - Extr. Aut. Dados\projeto_final\clean_data\licitacoes_20250616_a_20250618_doe_llm.json"
# caminho_json_pncp = r"C:\Users\rapha\OneDrive\Área de Trabalho\Pos UFG\EAD - Extr. Aut. Dados\projeto_final\clean_data\licitacoes_pncp.json"
# output_html = r"C:\Users\rapha\OneDrive\Área de Trabalho\Pos UFG\EAD - Extr. Aut. Dados\projeto_final\clean_data\relatorio.html"
# print("[4] Gerando relatório HTML...")
# output_html = os.path.join(CLEAN_DIR, f"relatorio.html")
# gerar_relatorio_html(caminho_json_llm, caminho_json_pncp, output_html)
# gerar_graficos_combinados(
#     "clean_data/licitacoes_20250616_a_20250618_doe_llm.json",
#     "clean_data/licitacoes_pncp.json"
# )

