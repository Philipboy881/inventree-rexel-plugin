from bs4 import BeautifulSoup
import requests
import json


# Functie om product URL en SKU op te halen (ook van de Rexel-site)
def get_product_url(sku, url):
    response = requests.get(url + sku)
    if response.status_code != 200:
        return {"error": f"Error retrieving product URL: {response.status_code}"}
    
    data = response.json()

    if 'products' in data and len(data['products']) > 0:
        product = data['products'][0]
        product_url = product.get('url', 'URL not available')
        product_code = product.get('code', 'Code not available')

        return {"url": product_url, "code": product_code}
    else:
        return {"error": "No product data found in the response."}


# Functie om productgegevens op te halen van een URL
def get_product_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": f"Error retrieving product data: {response.status_code}"}
    
    return response.text  # Dit is de HTML van de pagina


# Functie om tabeldata van de productpagina te extraheren
def extract_table_data(tables):
    general_info = {}
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            td = row.find("td")

            if th and td:
                attribute_name = th.get_text(strip=True)
                span = td.find("span", class_="tech-table-values-text")
                attribute_value = span.get_text(strip=True) if span else td.get_text(strip=True)

                if attribute_name and attribute_value:
                    general_info[attribute_name] = attribute_value
    return general_info


# Functie om gestructureerde productdata te verkrijgen van de HTML
def get_data_from_html(html, sku):
    soup = BeautifulSoup(html, "html.parser")
    product_name = soup.find("h1", class_="font-weight-bold mb-1")
    cleaned_product_name = product_name.get_text(strip=True) if product_name else "Name not available"
    
    delivery_numbers = soup.find_all("div", class_="col-auto pl-0 col-md-auto p-md-0 font-weight-bold word-break")
    cleaned_delivery_numbers = [delivery_number.get_text(strip=True) for delivery_number in delivery_numbers]
    
    if len(cleaned_delivery_numbers) > 1:
        product_code = cleaned_delivery_numbers[0]
        ean_code = cleaned_delivery_numbers[1]
    else:
        product_code = cleaned_delivery_numbers[0] if cleaned_delivery_numbers else "Code not available"
        ean_code = "EAN not available"

    product_description = soup.find("div", class_="long-product-description")
    cleaned_product_description = product_description.get_text(strip=True) if product_description else "Description not available"
    
    table1 = soup.find_all("div", class_="col-6 pr-5 px-lg-3")
    table2 = soup.find_all("div", class_="col-6 pl-5 px-lg-4")
    general_info_1 = extract_table_data(table1)
    general_info_2 = extract_table_data(table2)
    general_info = {**general_info_1, **general_info_2}

    data = {
        "name": cleaned_product_name,
        "product_code": product_code,
        "ean_code": ean_code,
        "sku": sku,
        "description": cleaned_product_description,
        "general_information": general_info,
    }

    return data


# Functie om Rexel data te verwerken en productinformatie op te halen
def process_rexel_data(data):
    """
    Verwerk Rexel data en geef een resultaat terug.
    """
    product_number = data['product_number']
    part_number = data['part_number']

    # URL's voor het ophalen van de productgegevens
    base_url = "https://www.rexel.nl/nln"
    searchbox_url = "https://www.rexel.nl/nln/search/autocomplete/SearchBoxResponsiveComponent?term="

    # Haal de product URL en SKU op
    product_url_sku = get_product_url(product_number, searchbox_url)
    if "error" in product_url_sku:
        return {
            'status': 'error in search',
            'message': product_url_sku['error']
        }

    # Haal de productgegevens op van de URL
    product_data = get_product_data(base_url + product_url_sku["url"])

    # Controleer of we een foutmelding hebben ontvangen (bijvoorbeeld geen geldige HTML)
    if isinstance(product_data, str) and "error" in product_data:
        return {
            'status': 'error in product data',
            'message': product_data  # Geef de foutmelding van de HTML terug
        }

    # Verkrijg gestructureerde gegevens van de HTML
    data_from_html = get_data_from_html(product_data, part_number)

    # Voeg de productinformatie toe aan de oorspronkelijke data
    result = {
        'product_number': product_number,
        'part_number': part_number,
        'status': 'success',
        'message': f'Processed part {part_number} for product {product_number}.',
        'product_info': json.loads(data_from_html)  # Voeg de opgehaalde data toe
    }

    return result
