from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# Headers para simular navegador e evitar bloqueio
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Links das cotações no CEPEA
URLS = {
    "Soja": "https://www.cepea.esalq.usp.br/br/indicador/soja.aspx",
    "Milho": "https://www.cepea.esalq.usp.br/br/indicador/milho.aspx",
    "Trigo": "https://www.cepea.esalq.usp.br/br/indicador/trigo.aspx",
}

def pegar_cotacao(nome, url):
    """Extrai a cotação e a data de uma página do CEPEA"""
    try:
        resposta = requests.get(url, headers=HEADERS, timeout=10)
        resposta.raise_for_status()  # Levanta erro para status codes 4xx/5xx
        
        sopa = BeautifulSoup(resposta.text, "html.parser")

        valor = sopa.find("span", {"id": "ctl00_ContentPlaceHolder1_lblValor"})
        data = sopa.find("span", {"id": "ctl00_ContentPlaceHolder1_lblData"})
        
        if not valor or not data:
            return {
                "produto": nome,
                "erro": "Dados não encontrados na página",
                "url": url
            }

        return {
            "produto": nome,
            "cotacao_reais_saca": valor.text.strip(),
            "data": data.text.strip(),
            "moeda": "BRL",
            "unidade": "sc 60kg"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "produto": nome,
            "erro": f"Erro na requisição: {str(e)}",
            "url": url
        }
    except Exception as e:
        return {
            "produto": nome,
            "erro": f"Erro inesperado: {str(e)}",
            "url": url
        }

@app.route("/")
def home():
    return jsonify({
        "message": "API de Cotações Agrícolas - CEPEA/ESALQ",
        "endpoints": {
            "cotacoes": "/cotacoes",
            "soja": "/cotacao/soja",
            "milho": "/cotacao/milho", 
            "trigo": "/cotacao/trigo"
        },
        "docs": "https://github.com/Hawkmdz/api"
    })

@app.route("/cotacoes", methods=["GET"])
def todas_cotacoes():
    """Retorna todas as cotações"""
    dados = []
    for nome, url in URLS.items():
        cotacao = pegar_cotacao(nome, url)
        dados.append(cotacao)
        time.sleep(1)  # Evita muitas requests simultâneas
    return jsonify(dados)

@app.route("/cotacao/<produto>", methods=["GET"])
def cotacao_individual(produto):
    """Retorna cotação de um produto específico"""
    produto = produto.capitalize()
    if produto not in URLS:
        return jsonify({"erro": "Produto não encontrado", "produtos_disponiveis": list(URLS.keys())}), 404
    
    cotacao = pegar_cotacao(produto, URLS[produto])
    return jsonify(cotacao)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # PORT 10000 para o Render
