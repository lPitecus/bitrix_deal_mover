import json
import math
import os

from dotenv import load_dotenv

import requests
import pandas as pd

load_dotenv()

API_KEY = str(os.getenv('api_key'))
BASE_URL = f"https://ecomax.bitrix24.com.br/rest/1/{API_KEY}"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


# para imprimir ingual ao postman
# parsed = json.loads(response.text)
# print(json.dumps(parsed, indent=4))

def get_categories():
    url = f"{BASE_URL}/crm.category.list"

    payload = json.dumps({
        "entityTypeId": 2
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': 'qmb=0.'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    options = {}
    counter = 1
    for category in response["result"]["categories"]:
        options[counter] = {"name": category["name"], "id": category["id"]}
        counter += 1

    return options


def get_stages(funil_id):
    url = f"{BASE_URL}/crm.status.list"

    payload = json.dumps({
        "FILTER": {
            "ENTITY_ID": f"DEAL_STAGE_{str(funil_id)}"
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': 'qmb=0.'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    options = {}
    counter = 1
    for stage in response["result"]:
        options[counter] = {"name": stage["NAME"], "id": stage["STATUS_ID"]}
        counter += 1
    return options


def get_deals(page: int) -> dict:
    payload = json.dumps({
        "SELECT": [
            "ID",
            "TITLE",
            "STAGE_ID",
            "CATEGORY_ID",
            "UF_CRM_1709212306863"
        ],
        "FILTER": {
            "!=CATEGORY_ID": 14,
            "!=STAGE_ID": None
        },
        "ORDER": {
            "ID": "ASC"
        },
        "start": page * 50
    })

    response = requests.request(
        "POST",
        f"{BASE_URL}/crm.deal.list",
        headers=HEADERS,
        data=payload
    )
    response = response.json()
    return response


print("Funis Disponíveis:")

funis = get_categories()
for funil in funis:
    print(f"{funil}. {funis[funil]['name']}")

funil_escolhido = int(input("\nDigite o numero do funil escolhido: "))
id_funil_escolhido = funis[funil_escolhido]['id']

print("Etapas Disponíveis para o funil escolhido:")

etapas = get_stages(id_funil_escolhido)
for etapa in etapas:
    print(f"{etapa}. {etapas[etapa]['name']}")

etapa_escolhida = int(input("\nDigite o numero da etapa que você quer mover Deals: "))

# # Obtendo o número total de páginas necessárias para a chamada
# totalPages = int(get_deals(0)["total"]) / 50
# totalPages = math.ceil(totalPages)
#
# deals = []
#
# # imprimir apenas as 3 primeiras p[aginas de resultado
# # mudar o 3 para totalPages para pegar todas
# for page in range(3):
#     print(f"Obtendo Dados da página {page + 1}...")
#     for deal in get_deals(page)["result"]:
#         deals.append(deal)
#
#
# print(json.dumps(deals, indent=4))
# print(len(deals))
