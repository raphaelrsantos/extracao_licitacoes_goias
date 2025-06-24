import requests
import json
from datetime import datetime
import os

OUTPUT_DIR = "clean_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def consultar_pncp(data_final, uf="go", pagina=1, tamanho_pagina=50):
    url = (
        f"https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"
        f"?dataFinal={data_final}&uf={uf}&pagina={pagina}&tamanhoPagina={tamanho_pagina}"
    )
    headers = {"accept": "*/*"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao consultar API: {response.status_code}")
        return None

def estruturar_dados_pncp(dados, uf="go"):
    estruturados = []
    for item in dados.get("data", []):
        entidade = item.get("orgaoEntidade", {})
        amparo = item.get("amparoLegal", {})

        estruturado = {
            "objetoCompra": item.get("objetoCompra", "NA"),
            "amparoLegal": {
                "descricao": amparo.get("descricao", "NA"),
                "nome": amparo.get("nome", "NA"),
                "codigo": amparo.get("codigo", "NA"),
            },
            "dataAberturaProposta": item.get("dataAberturaProposta", "NA"),
            "dataEncerramentoProposta": item.get("dataEncerramentoProposta", "NA"),
            "orgaoEntidade": {
                "cnpj": entidade.get("cnpj", "NA"),
                "razaoSocial": entidade.get("razaoSocial", "NA"),
            },
            "anoCompra": item.get("anoCompra", "NA"),
            "unidadeOrgao": item.get("unidadeOrgao", {}),
            "numeroControlePNCP": item.get("numeroControlePNCP", "NA"),
            "valorTotalEstimado": item.get("valorTotalEstimado", "NA"),
            "tipoInstrumentoConvocatorioNome": item.get("tipoInstrumentoConvocatorioNome", "NA"),
            "modalidadeNome": item.get("modalidadeNome", "NA"),
        }

        estruturados.append(estruturado)

    # Salvar como JSON
    output_path = os.path.join(OUTPUT_DIR, f"licitacoes_pncp.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(estruturados, f, ensure_ascii=False, indent=4)

    print(f"Arquivo estruturado salvo em: {output_path}")
    return output_path
