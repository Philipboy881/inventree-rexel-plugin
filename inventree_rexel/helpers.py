import requests


def search_rexel_api(query):
    """Zoekfunctie die gegevens ophaalt van de externe API (bijvoorbeeld, Rexel API)."""
    # Stel de URL van de externe API in (vervang deze door de werkelijke URL van de API)
    api_url = f"https://api.rexel.com/products?search={query}"

    try:
        # Voer de API-aanroep uit
        response = requests.get(api_url, timeout=10)

        # Controleer de status van de response
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code}")

        # Retourneer de JSON-data van de API
        return response.json()
    
    except Exception as e:
        raise Exception(f"Error while fetching data: {str(e)}")
