import json
import os
import openai
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()  # Adicione esta linha ANTES de os.getenv

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


CLEAN_DIR = os.path.join(os.path.dirname(__file__), 'clean_data')
os.makedirs(CLEAN_DIR, exist_ok=True)

def executar_llm_sobre_resumos(input_path):
    with open(input_path, encoding='utf-8') as f:
        dados = json.load(f)

    estruturados = []
    for item in tqdm(dados, desc="🧠 Estruturando com OpenAI SDK 1.x"):
        resumo = item.get("Resumo", "")
        ident = item.get("identificador", "")
        if not resumo:
            continue

        prompt = f"""
Extraia os seguintes campos do texto abaixo. Quando não souber ou não encontrar a informação, preencha com "NA".

Campos:
- objetoCompra
- amparoLegal
- dataAberturaProposta
- dataEncerramentoProposta
- orgaoEntidade: cnpj, razaoSocial
- anoCompra
- unidadeOrgao: ufNome, codigoIbge, ufSigla, municipioNome, codigoUnidade, nomeUnidade
- numeroControlePNCP
- valorTotalEstimado
- tipoInstrumentoConvocatorioNome
- modalidadeNome
- link_resumo

Texto:

{resumo}

- O nome do município deve ser extraído do texto.
- Caso o texto contenha intervalos de datas que sejam destinadas ao recebimento de propostas, considere a data de abertura da proposta como a primeira data do intervalo, e a data de encerramento da proposta como a última data do intervalo.

Exemplo: "...estará recebendo propostas, entre os dias 18/06/2025 a 23/06/2025..." a data de abertura da proposta seria 18/06/2025 e a data de encerramento seria 23/06/2025.

- Caso o conteúdo do resumo trate sobre resultados de licitações e não contenha informações sobre abertura de propostas, desconsisere esse conteúdo e não gere nenhum JSON para ele.

- Campos fixos:
"fonte": "DOE-GO"
"ufNome": "Goiás"
"ufSigla": "GO"
"link_resumo": "https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/publicacoes_ver_conteudo/{ident}"

Exemplo:

Json:
{{
  "identificador": "625710",
  "Tipo": "Concorrência",
  "Resumo": "CONCORRÊNCIA Nº 017/2025/113839 - SEDUC PROCESSO Nº 202500005015845 O Estado de Goiás, por intermédio do(a) SEDUC - SECRETARIA DE ESTADO DA EDUCAÇÃO torna públ...",
  "data_publicacao": "18/06/2025"
}}

Json estruturado:
{{
  "objetoCompra": "Reforma e Ampliação no Colégio Estadual Manoel Libânio da Silva, no município de Abadia Goias-GO, sendo sendo: Bloco 05 - Construção; Executar o reservatório...",
  "amparoLegal": "nos termos do Art. 28, inciso II da Lei Federal nº 14.133, de 1º de abril de 2021 e na forma do Decreto Estadual nº 10.359, de 11 de dezembro de 2023",
  "dataAberturaProposta": "08/07/2025",
  "dataEncerramentoProposta": "NA",
  "orgaoEntidade": {{
    "cnpj": "NA",
    "razaoSocial": "SEDUC - SECRETARIA DE ESTADO DA EDUCAÇÃO"
  }},
  "anoCompra": "2025",
  "unidadeOrgao": {{
    "ufNome": "Goiás",
    "codigoIbge": "NA",
    "ufSigla": "GO",
    "municipioNome": "Abadia Goias",
    "codigoUnidade": "NA",
    "nomeUnidade": "SEDUC"
  }},
  "numeroControlePNCP": "NA",
  "valorTotalEstimado": "R$ 3.120.547,01",
  "tipoInstrumentoConvocatorioNome": "NA",
  "modalidadeNome": "Concorrência",
  "fonte": "DOE-GO",
  "link_resumo": "https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/publicacoes_ver_conteudo/625710", 
}}

Retorne apenas o JSON válido.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            
            json_data = json.loads(content)
            json_data["identificador"] = ident
            estruturados.append(json_data)
        except Exception as e:
            print(f"[ERRO] {ident}: {e}")

    output_path = input_path.replace(".json", "_llm.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(estruturados, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Arquivo estruturado salvo em: {output_path}\n")
    
    return output_path