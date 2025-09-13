from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Links das cotações no CEPEA
URLS = {
    "Soja": "https://www.cepea.esalq.usp.br/br/indicador/soja.aspx",
    "Milho": "https://www.cepea.esalq.usp.br/br/indicador/milho.aspx",
    "Trigo": "https://www.cepea.esalq.usp.br/br/indicador/trigo.aspx",
}

def pegar_cotacao(nome, url):
    """Extrai a cotação e a data de uma página do CEPEA"""
    resposta = requests.get(url)
    sopa = BeautifulSoup(resposta.text, "html.parser")

    valor = sopa.find("span", {"id": "ctl00_ContentPlaceHolder1_lblValor"}).text.strip()
    data = sopa.find("span", {"id": "ctl00_ContentPlaceHolder1_lblData"}).text.strip()

    return {
        "produto": nome,
        "cotacao_reais_saca": valor,
        "data": data
    }

@app.route("/cotacoes", methods=["GET"])
def cotacoes():
    dados = []
    for nome, url in URLS.items():
        try:
            dados.append(pegar_cotacao(nome, url))
        except Exception as e:
            dados.append({"produto": nome, "erro": str(e)})
    return jsonify(dados)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
