import json
import os
from collections import Counter
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-muted')

def normalizar_tipo(tipo):
    tipo = tipo.lower().strip()
    if "pregão" in tipo:
        return "Pregão"
    elif "concorrência" in tipo:
        return "Concorrência"
    elif "tomada de preços" in tipo:
        return "Tomada de Preços"
    elif "dispensa" in tipo:
        return "Dispensa"
    elif "inexigibilidade" in tipo:
        return "Inexigibilidade"
    elif "leilão" in tipo:
        return "Leilão"
    elif "convite" in tipo:
        return "Convite"
    else:
        return tipo.title()

def carregar_dados_combinados(caminho_json_llm, caminho_json_pncp):
    with open(caminho_json_llm, encoding='utf-8') as f:
        dados_llm = json.load(f)
    with open(caminho_json_pncp, encoding='utf-8') as f:
        dados_pncp = json.load(f)

    for item in dados_llm + dados_pncp:
        item["Tipo"] = normalizar_tipo(item.get("modalidadeNome", "NA"))
        valor = item.get("valorTotalEstimado")
        if isinstance(valor, str):
            valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                item["valorTotalEstimado"] = float(valor)
            except:
                item["valorTotalEstimado"] = 0.0
        elif isinstance(valor, (int, float)):
            item["valorTotalEstimado"] = float(valor)
        else:
            item["valorTotalEstimado"] = 0.0

    return dados_llm + dados_pncp

def gerar_graficos_combinados(caminho_json_llm, caminho_json_pncp, pasta_saida="insights"):
    os.makedirs(pasta_saida, exist_ok=True)
    dados = carregar_dados_combinados(caminho_json_llm, caminho_json_pncp)

    # === Gráfico 1: Quantidade por tipo ===
    tipos = [item["Tipo"] for item in dados]
    contagem_por_tipo = Counter(tipos)
    grafico_tipo_path = os.path.join(pasta_saida, "grafico_tipos_combinado.png")

    if contagem_por_tipo:
        plt.figure(figsize=(8, 5))
        plt.bar(contagem_por_tipo.keys(), contagem_por_tipo.values(), color="#4e79a7")
        plt.xlabel('Tipo de Licitação')
        plt.ylabel('Quantidade')
        plt.title('Distribuição de Tipos de Licitações (Combinado)')
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig(grafico_tipo_path)
        plt.close()

    # === Gráfico 2: Valor total estimado por tipo (em milhões) ===
    valores_por_tipo = {}
    valores_por_orgao = {}
    for item in dados:
        tipo = item["Tipo"]
        orgao = item.get("orgaoEntidade", {}).get("razaoSocial", "Desconhecido")
        valor = item.get("valorTotalEstimado", 0.0)
        valores_por_tipo[tipo] = valores_por_tipo.get(tipo, 0.0) + valor
        valores_por_orgao[orgao] = valores_por_orgao.get(orgao, 0.0) + valor

    # Gráfico 2 - tipo x valor
    grafico_valor_path = os.path.join(pasta_saida, "grafico_valores_combinado.png")
    if valores_por_tipo:
        plt.figure(figsize=(10, 6))
        tipos = list(valores_por_tipo.keys())
        valores_milhoes = [v / 1_000_000 for v in valores_por_tipo.values()]

        bars = plt.bar(tipos, valores_milhoes, color="#f28e2c")
        plt.xlabel('Tipo de Licitação')
        plt.ylabel('Valor Total Estimado (milhões de R$)')
        plt.title('Valor Total Estimado por Tipo de Licitação (em milhões de R$)')
        plt.xticks(rotation=30)

        for bar, valor in zip(bars, valores_milhoes):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{valor:,.2f}", 
                     ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.savefig(grafico_valor_path)
        plt.close()

    # === Gráfico 3: Top 10 órgãos por valor estimado (em milhões) ===
    orgaos_ordenados = sorted(valores_por_orgao.items(), key=lambda x: x[1], reverse=True)[:10]
    nomes = [o[0] for o in orgaos_ordenados]
    valores = [o[1] / 1_000_000 for o in orgaos_ordenados]

    plt.figure(figsize=(12, 6))
    bars = plt.barh(nomes, valores, color="#59a14f")
    plt.xlabel("Valor Total Estimado (milhões de R$)")
    plt.title("Top 10 Órgãos por Valor Total Estimado")

    for bar, valor in zip(bars, valores):
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f"{valor:,.2f}",
                 va='center', fontsize=8)

    plt.tight_layout()
    grafico_orgaos_path = os.path.join(pasta_saida, "grafico_top10_orgaos.png")
    plt.savefig(grafico_orgaos_path)
    plt.close()


    # === Gráfico 4: Comparativo quantidade x valor médio estimado por tipo ===
    from collections import defaultdict
    resumo_por_tipo = defaultdict(lambda: {"quantidade": 0, "valor_total": 0.0})

    for item in dados:
        tipo = item["Tipo"]
        resumo_por_tipo[tipo]["quantidade"] += 1
        resumo_por_tipo[tipo]["valor_total"] += item.get("valorTotalEstimado", 0.0)

    tipos = []
    quantidades = []
    valores_medios_milhoes = []

    for tipo, resumo in resumo_por_tipo.items():
        tipos.append(tipo)
        quantidades.append(resumo["quantidade"])
        valor_medio = resumo["valor_total"] / resumo["quantidade"] if resumo["quantidade"] > 0 else 0
        valores_medios_milhoes.append(valor_medio / 1_000_000)

    # Ordenar por quantidade
    ordenados = sorted(zip(tipos, quantidades, valores_medios_milhoes), key=lambda x: x[1], reverse=True)
    tipos, quantidades, valores_medios_milhoes = zip(*ordenados)

    fig, ax1 = plt.subplots(figsize=(10, 6))
    cor1 = '#4e79a7'
    cor2 = '#f28e2c'

    ax1.bar(tipos, quantidades, color=cor1)
    ax1.set_xticks(range(len(tipos)))
    ax1.set_xticklabels(tipos, rotation=30, ha='right')
    ax1.tick_params(axis='y', labelcolor=cor1)
    ax1.set_xticklabels(tipos, rotation=30, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(tipos, valores_medios_milhoes, color=cor2, marker='o', linewidth=2)
    ax2.set_ylabel('Valor Médio Estimado (milhões R$)', color=cor2)
    ax2.tick_params(axis='y', labelcolor=cor2)

    plt.title('Comparativo entre Quantidade e Valor Médio por Tipo')
    plt.tight_layout()
    grafico_comparativo_path = os.path.join(pasta_saida, "comparativo_qtd_valor_medio.png")
    plt.savefig(grafico_comparativo_path)
    plt.close()


    return grafico_tipo_path, grafico_valor_path, grafico_orgaos_path, grafico_comparativo_path
