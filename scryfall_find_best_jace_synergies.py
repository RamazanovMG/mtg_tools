import requests
import json
import re


def search_scryfall(query):
    url = "https://api.scryfall.com/cards/search"
    response = requests.get(url, params={"q": query})

    if response.status_code == 200:
        data = response.json()
#        card_names = [card['name'] for card in data.get('data', [])]
        card_dict = {}
        for card in data.get('data', []):
            card_dict[card['name']] = card['card_faces'][1].get('mana_cost', '')
        return card_dict
    else:
        return None


def reformat_result(result):
    for key, value in result.items():
        value = re.sub(r'{[A-Za-z]}', '{1}', value)
        numbers = re.findall(r'{(\d+)}', value)
        total = sum(int(num) for num in numbers)
        result[key] = total

    return {k: v for k, v in sorted(result.items(), key=lambda item: item[1], reverse=True) if v >= 4}


def main():
    query = r'name:/\/\// -is:transform game:arena cmc<=3 -t:land'
    result = search_scryfall(query)

    print(json.dumps(reformat_result(result), indent=4))


if __name__ == "__main__":
    main()
