import json
import pandas as pd

def gerar_relatorio_html(caminho_llm_json, caminho_pncp_json, caminho_saida_html):
    def carregar_dados(caminho):
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)

    def montar_tabela_pandas(dados, titulo, id_tabela):
        if not dados:
            return f"<h2>{titulo}</h2><p>Nenhum dado encontrado.</p>"

        df = pd.DataFrame(dados)

        # Converte dicionários em strings legíveis
        for col in df.columns:
            df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else x)

        # Reorganiza colunas com prioridade
        colunas_prioritarias = ['objetoCompra', 'amparoLegal', 'anoCompra']
        outras_colunas = [c for c in df.columns if c not in colunas_prioritarias]
        colunas_ordenadas = colunas_prioritarias + sorted(outras_colunas)
        df = df[colunas_ordenadas]

        tabela_html = df.to_html(index=False, classes='display', table_id=id_tabela, escape=False)
        return f"<h2>{titulo}</h2>\n{tabela_html}"

    dados_llm = carregar_dados(caminho_llm_json)
    dados_pncp = carregar_dados(caminho_pncp_json)

    html_content = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Relatório de Licitações</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.css">
        <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background-color: #f9f9f9;
            }}
            h1, h2 {{
                color: #333;
            }}
            table.dataTable {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 40px;
            }}
            table.dataTable th, table.dataTable td {{
                padding: 8px 10px;
                border: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <h1>Relatório de Licitações</h1>

        {montar_tabela_pandas(dados_llm, "Licitações - DOE - LLM", "tabela_llm")}
        {montar_tabela_pandas(dados_pncp, "Licitações - API PNCP", "tabela_pncp")}

        <script>
            $(document).ready(function() {{
                $('#tabela_llm').DataTable({{ pageLength: 10, language: {{ url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json' }} }});
                $('#tabela_pncp').DataTable({{ pageLength: 10, language: {{ url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json' }} }});
            }});
        </script>
    </body>
    </html>
    """

    with open(caminho_saida_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[RELATÓRIO] HTML salvo em: {caminho_saida_html}\n")

