from bs4 import BeautifulSoup
import requests
import json
import sys
from company.models import Company
from part.models import Part
from company.models import ManufacturerPart, SupplierPart


# Functie om een fabrikant-ID op te zoeken op basis van naam
def find_or_create_company(name):
    # Zet de naam om naar kleine letters voor hoofdletterongevoelige zoekopdracht
    manufacturer_name_lower = name.lower()

    # Zoek naar de fabrikant op basis van de naam (hoofdletterongevoelig)
    manufacturer, created = Company.objects.get_or_create(
        name__iexact=manufacturer_name_lower,  # case-insensitive match voor de naam
        defaults={"name": manufacturer_name_lower, "is_manufacturer": True, "is supplier": False}  # Voeg standaardwaarden toe als de fabrikant nieuw is
    )

    return manufacturer.id  # Retourneer de id van de fabrikant


def get_or_create_manufacturer_part(ipn, mpn, manufacturer_id):
    """
    Zoek de ManufacturerPart op basis van mpn (Manufacturer Part Number) en fabrikant ID.
    Als het niet bestaat, maak het dan aan.
    """
    # Zoek of maak het Part object op basis van 'ipn'
    try:
        part_instance = Part.objects.get(IPN=ipn)  # Pas 'id' aan op basis van je model
    except Part.DoesNotExist:
        raise ValueError(f"Part with ID '{ipn}' does not exist")
    
    manufacturer_part, created = ManufacturerPart.objects.get_or_create(
        part=part_instance,
        manufacturer_id=manufacturer_id,
        MPN=mpn
    )
    return manufacturer_part


def create_supplier_part(ipn, supplier_id, manufacturer_part, sku):
    """
    Maak een SupplierPart aan en koppel deze aan de juiste ManufacturerPart.
    """
    
    try:
        supplier_instance = Company.objects.get(id=supplier_id)
    except Company.DoesNotExist:
        raise ValueError(f"Supplier with ID '{supplier_id}' does not exist")

    try:
        part_instance = Part.objects.get(IPN=ipn)  # Pas 'id' aan op basis van je model
    except Part.DoesNotExist:
        raise ValueError(f"Part with ID '{ipn}' does not exist")
    
    supplier_part, created = SupplierPart.objects.get_or_create(
        part=part_instance,
        SKU=sku,
        supplier=supplier_instance,
        manufacturer_part=manufacturer_part
    )
    return supplier_part


# functie voor onderdelen aan te maken in het systeem
def create_part(data, manufacturer_id, supplier_id, internal_part_number):
    """
    Maak een nieuw onderdeel aan in het systeem op basis van de ontvangen data.
    De Internal Part Number (IPN) wordt toegevoegd, evenals de EAN als scan code.
    Zorg ervoor dat je de fabrikant- en leverancier-ID doorgeeft.
    """

    # Verkrijg de productinformatie uit de data
    name = data.get("name", None)
    description = data.get("description", "")
    unit = data.get("unit", None).lower()
    image_url = data.get("image url", None)
    manufacturerpartnr = data.get("product number", None)
    supplierpartnr = data.get("code", None)

    # Maak het onderdeel aan in je systeem (bijv. door een database model te gebruiken)
    part = Part.objects.create(
        IPN=internal_part_number,  # Internal Part Number (IPN)
        name=name,
        description=description,
        units=unit,
        image=image_url
    )

    manufacturer_part = get_or_create_manufacturer_part(internal_part_number, manufacturerpartnr, manufacturer_id)

    # Maak het SupplierPart aan (gebruik het juiste manufacturer_part)
    supplier_part_instance = create_supplier_part(internal_part_number, supplier_id, manufacturer_part, supplierpartnr)

    part.default_supplier = supplier_part_instance
    part.save()  # Zorg ervoor dat de wijziging wordt opgeslagen in de database

    return part.id  # Retourneer de ID van het aangemaakte part


# Login function to authenticate the user
def login(session, url, username, password):
    # Define login URL, username, and password
    login_data = {
        "j_username": username,
        "j_password": password
    }
    login_response = session.post(url, data=login_data)
    # If login fails (status code is not 200), return False
    if login_response.status_code != 200:
        return False
    return session


# Function to get the product price
def get_price(session, url):
    response = session.get(url)

    if response.status_code != 200:
        print(f"Error retrieving price: {response.status_code}")
        sys.exit()

    data = response.json()
    return data[0]['price']


# Function to get the product URL and SKU from the search result
def search_product(session, search_data, url):
    response = session.get(url + search_data)
    if response.status_code != 200:
        print(f"Error retrieving product URL: {response.status_code}")
        sys.exit()

    data = response.json()
    # Check if products exist in the response
    if 'products' in data and len(data['products']) > 0:
        # Get the first product
        product = data['products'][0]

        # Retrieve 'url' and 'code' for the product
        product_code = product.get('code', 'Code not available')
        product_name = product.get('name', 'Name not available')
        product_url = product.get('url', 'URL not available')
        product_image_url = product["images"][0].get('url', 'Image not available')
        product_brandname = product.get('brandName', 'brand not available')
        product_ean = product.get('ean', 'ean not available')
        product_numbercontentunits = product.get('numberContentUnits', 'numbercontentunits not available')  # eenheid
        product_manufactureraid = product.get('manufacturerAID', 'manufactureraid not available')  # product type
        product_pricingqty = product.get('pricingQty', 'pricingqty  not available')
        # Return the product URL and code
        returndata = {
            "code": product_code,
            "name": product_name,
            "url": product_url,
            "image url": product_image_url,
            "brand": product_brandname,
            "ean": product_ean,
            "unit": product_numbercontentunits,
            "product number": product_manufactureraid,
            "number of units": product_pricingqty
        }
        return returndata
    else:
        print("No product data found in the response.")
        sys.exit()


# Function to get the product data from the provided URL
def get_product_data(session, url):
    response = session.get(url)

    if response.status_code != 200:
        print(f"Error retrieving product data: {response.status_code}")
        sys.exit()

    data = response.text
    return data


# Function to extract general information from product tables
def extract_table_data(tables):
    """
    Function to extract data from tables containing general information.
    Returns a dictionary with key-value pairs from the table.
    """
    general_info = {}

    # Iterate through each table to extract relevant information
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            # Look for 'th' and 'td' tags within the row
            th = row.find("th")
            td = row.find("td")

            # If both 'th' and 'td' are found
            if th and td:
                attribute_name = th.get_text(strip=True)

                # Look for the value in the span tag to avoid duplicates
                span = td.find("span", class_="tech-table-values-text")
                if span:
                    attribute_value = span.get_text(strip=True)
                else:
                    attribute_value = td.get_text(strip=True)

                # Add the name and value to the dictionary if both are not empty
                if attribute_name and attribute_value:
                    general_info[attribute_name] = attribute_value

    return general_info


# Function to get structured data from the product HTML
def get_data_from_html(html):
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Extract the product description
    product_description = soup.find("div", class_="long-product-description")
    cleaned_product_description = product_description.get_text(strip=True) if product_description else "Description not available"

    # Use the extract_table_data function to extract general information from the tables
    table1 = soup.find_all("div", class_="col-6 pr-5 px-lg-3")
    table2 = soup.find_all("div", class_="col-6 pl-5 px-lg-4")
    general_info_1 = extract_table_data(table1)
    general_info_2 = extract_table_data(table2)
    general_info = {**general_info_1, **general_info_2}

    # Return the data in a structured JSON format
    data = {
        "description": cleaned_product_description,
        "general_information": general_info,
    }

    # Convert the data to a JSON string and return it
    return data


# Main function to get product data and price
def get_product(username, password, product):
    base_url = "https://www.rexel.nl/nln"
    login_url = "https://www.rexel.nl/nln/j_spring_security_check"
    price_url = "https://www.rexel.nl/nln/erp/getPrice.json?products="
    price_url1 = "&isListPage=false&isProductBundle=false&context=PDP&isLeasingProductPresent=false"
    searchbox_url = "https://www.rexel.nl/nln/search/autocomplete/SearchBoxResponsiveComponent?term="

    # Create a session object to manage cookies and headers
    session = requests.Session()

    # Only login if username and password are provided (for price retrieval)
    if username and password:
        session = login(session, login_url, username, password)
        if session is False:
            print("Login failed, cannot retrieve price.")
            price = "Price not available"
        else:
            # Retrieve the price with the logged-in session
            price = get_price(session, price_url + product + price_url1)
            print("Price:", price)
    else:
        price = "Price not available"  # No login credentials, so no price retrieval

    # Retrieve the product URL and SKU without login
    product_data = search_product(session, product, searchbox_url)

    # Retrieve the product data
    product_scraped_data = get_product_data(session, base_url + product_data["url"])

    # Convert the data to structured JSON
    product_scraped_data_processed = get_data_from_html(product_scraped_data)
    rdata = {**product_data, **product_scraped_data_processed}
    return rdata


# Functie om Rexel data te verwerken en productinformatie op te halen
def process_rexel_data(data):
    """
    Verwerk Rexel data en geef een resultaat terug.
    """
    # rexel id
    rexel_id = find_or_create_company("rexel")

    product_number = data['product_number']
    internal_part_number = data['part_number']

    data = get_product("", "", product_number)

    # Zoek een fabrikant op basis van naam en anders creeren
    manufacturer = data["brand"]
    manufacturer_id = find_or_create_company(manufacturer)

    part_id = create_part(data, manufacturer_id, rexel_id, internal_part_number)

    return part_id
    return json.dumps(data, indent=4, ensure_ascii=False)
