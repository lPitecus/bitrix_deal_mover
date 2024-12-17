import json
import math
import os
import requests

from dotenv import load_dotenv


load_dotenv()

API_KEY = str(os.getenv('api_key'))
BASE_URL = f"https://ecomax.bitrix24.com.br/rest/1/{API_KEY}"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


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

    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    response = response.json()
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

    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    response = response.json()
    options = {}
    counter = 1
    for stage in response["result"]:
        options[counter] = {"name": stage["NAME"], "id": stage["STATUS_ID"], "category_id": stage["CATEGORY_ID"]}
        counter += 1
    return options


def get_deals(page: int, category_id: int, stage_id: int) -> dict:
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
            "!=STAGE_ID": None,
            "STAGE_ID": stage_id,
            "CATEGORY_ID": category_id
        },
        "ORDER": {
            "ID": "ASC"
        },
        "start": (page - 1) * 50
    })

    response = requests.request(
        "POST",
        f"{BASE_URL}/crm.deal.list",
        headers=HEADERS,
        data=payload
    )
    response.raise_for_status()
    response = response.json()
    return response


def update_deals(deal_id_list: list[int], to_category: int, to_stage: str):
    count = 1
    for deal_id in deal_id_list:
        print(f"Atualizando Deal {count} de {len(deal_id_list)}...")
        url = f"{BASE_URL}/crm.deal.update"

        payload = json.dumps({
            "ID": deal_id,
            "FIELDS": {
                "CATEGORY_ID": to_category,
                "STATUS_ID": to_stage
            },
            "PARAMS": {
                "REGISTER_SONET_EVENT": "Y",
                "REGISTER_HISTORY_EVENT": "N"
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cookie': 'qmb=0.'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        count += 1


funis = get_categories()
counter = 1


selected_deals_ids = []
while True:
    if counter == 1:
        print("Funis Disponíveis:")
    else:
        print(f"Nenhum negócio encontrado no funil e etapa selecionados...")
        print("Por favor, escolha outro.")
        print("Funis Disponíveis:")
    for funil in funis:
        print(f"{funil}. {funis[funil]['name']}")

    funil_saida = int(input("\nDe qual funil você deseja tirar os Deals? :"))
    id_funil_saida = funis[funil_saida]['id']
    os.system('cls')

    print(f"Etapas Disponíveis para o funil '{funis[funil_saida]['name']}':")

    etapas = get_stages(id_funil_saida)
    for etapa in etapas:
        print(f"{etapa}. {etapas[etapa]['name']}")

    etapa_saida = int(input("\nDigite o numero da etapa que você quer tirar os Deals: "))
    id_etapa_saida = etapas[etapa_saida]['id']
    os.system('cls')


    response_com_filtros = get_deals(1, id_funil_saida, id_etapa_saida)
    num_deals_saida = response_com_filtros["total"]
    if num_deals_saida == 0:
        counter = 0
        continue
    print(f"{num_deals_saida} Cards encontrados no funil '{funis[funil_saida]['name']}' na etapa '{etapas[etapa_saida]['name']}'")
    totalPages = math.ceil(num_deals_saida / 50)

    for page in range(totalPages):
        for deal in get_deals(page, id_funil_saida, id_etapa_saida)["result"]:
            selected_deals_ids.append(deal["ID"])

    break
print("Funis disponíveis para receber os Deals")

for funil in funis:
    if funil == funil_saida:
        continue
    print(f"{funil}. {funis[funil]['name']}")
funil_entrada = int(input("\nDigite o numero do funil que irá receber os Deals: "))
id_funil_entrada = funis[funil_entrada]['id']

os.system('cls')
print("Etapas disponíveis para receber os Deals")
etapas = get_stages(id_funil_entrada)

for etapa in etapas:
    print(f"{etapa}. {etapas[etapa]['name']}")
etapa_saida = int(input("\nDigite o numero da etapa que você quer inserir os Deals: "))
id_etapa_saida = etapas[etapa_saida]['id']
id_funil_saida = etapas[etapa_saida]['category_id']
os.system('cls')

print(selected_deals_ids)
update_deals(selected_deals_ids, id_funil_saida, id_etapa_saida)
