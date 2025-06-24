# Extração de Licitações Goiás

Projeto final da disciplina de Extração Automática de Dados (EAD) do curso de pós-graduação da UFG em Sistemas e Agentes Inteligentes. 
Desenvolvido por Guilherme Ferreira Lucio Lemes, Raphael Rodrigues dos Santos e Thiago Ferreira dos Santos.

Este projeto realiza a extração, estruturação e análise de dados de licitações públicas do estado de Goiás, utilizando dados do Diário Oficial do Estado (DOE-GO) e da API do PNCP (Portal Nacional de Contratações Públicas). A aplicação realiza scraping, processamento com LLM (OpenAI), consulta à API, geração de relatórios HTML e gráficos de insights.

# Engenharia de Dados:
- dados brutos armazenados na pasta **raw_data**;
- dados tratados armazenados na pasta **clean_data**;

---

## Requisitos

- Python 3.8 ou superior
- Google Chrome instalado
- ChromeDriver compatível com a versão do Google Chrome instalada
- Conta e chave de API da OpenAI (para uso do LLM)
- Conexão com a internet para acesso ao Diário Oficial e API PNCP

## Principais Bibliotecas utilizadas

- **selenium**: Automação do navegador para scraping do Diário Oficial do Estado de Goiás.
- **beautifulsoup4 (bs4)**: Parsing e extração de dados HTML.
- **requests**: Realização de requisições HTTP para APIs e obtenção de dados.
- **openai**: Integração com o modelo de linguagem da OpenAI para processamento e extração de dados.
- **pandas**: Manipulação e organização dos dados para geração de relatórios.
- **matplotlib** e **seaborn**: Geração de gráficos e visualizações dos dados.
- **tqdm**: Barra de progresso para processamento dos dados.
- **python-dotenv**: Carregamento de variáveis de ambiente, como a chave da API da OpenAI.
- **datetime**, **json**, **os**, **re**: Utilitários padrão para manipulação de datas, arquivos e expressões regulares.

---

## Instalação

1. Clone este repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd extracao_licitacoes_goias
   ```

2. Crie e ative um ambiente virtual Python (recomendado):
   - No Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - No Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

4. Baixe o ChromeDriver compatível com sua versão do Google Chrome:
   - Acesse: https://sites.google.com/chromium.org/driver/
   - Extraia o executável e coloque-o em um diretório no PATH do sistema ou na raiz do projeto.

5. Configure a variável de ambiente para a chave da API da OpenAI:
   - Crie um arquivo `.env` na raiz do projeto com o conteúdo:
     ```
     OPENAI_API_KEY=sua_chave_aqui
     ```
   - Ou configure a variável de ambiente diretamente no sistema operacional.

---

## Pipeline de Extração

A pipeline de extração é composta pelas seguintes etapas e arquivos Python:

1. **scraper_doe.py**: realiza a extração dos dados do Diário Oficial do Estado de Goiás (DOE-GO) utilizando a biblioteca Selenium para navegação e scraping, e também requisições simples para obter os detalhes dos identificadores encontrados.

2. **llm_extractor.py**: processa os resumos extraídos, organizando as informações em campos estruturados por meio do uso de um modelo de linguagem (LLM) da OpenAI para tratamento e extração dos dados.

3. **api_pncp.py**: realiza a consulta à API do Portal Nacional de Contratações Públicas (PNCP) para obter dados complementares sobre as licitações.

4. **html_report.py**: gera um relatório HTML consolidado com os dados estruturados das etapas anteriores.

5. **graficos.py**: gera gráficos e insights visuais a partir dos dados combinados.

---

## Uso

Execute o pipeline principal com as datas desejadas:

```bash
python main_pipeline.py --start_date YYYYMMDD --end_date YYYYMMDD --data_pncp YYYYMMDD
```

- `--start_date`: Data inicial para extração dos resumos do DOE-GO (formato `YYYYMMDD`)
- `--end_date`: Data final para extração dos resumos do DOE-GO (formato `YYYYMMDD`)
- `--data_pncp`: Data de referência para consulta da API PNCP (formato `YYYYMMDD`)

Exemplo:

```bash
python main_pipeline.py --start_date 20250616 --end_date 20250618 --data_pncp 20250618
```

---

## Saída

- Os dados limpos e estruturados são salvos na pasta `clean_data/`.
- O relatório HTML é gerado em `clean_data/relatorio.html`.
- Os gráficos e insights são salvos na pasta `insights/`.

---

## Observações

- Certifique-se de que o ChromeDriver esteja acessível e compatível com sua versão do Chrome.
- A execução pode levar alguns minutos dependendo do intervalo de datas e da velocidade da internet.
- Para o funcionamento do LLM, é necessário ter uma chave válida da OpenAI configurada.

---
