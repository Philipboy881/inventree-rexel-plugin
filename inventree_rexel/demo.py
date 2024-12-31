from bs4 import BeautifulSoup
import requests
import sys
import json


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
def get_product_url(session, sku, url):
    response = session.get(url + sku)
    if response.status_code != 200:
        print(f"Error retrieving product URL: {response.status_code}")
        sys.exit()

    data = response.json()

    # Check if products exist in the response
    if 'products' in data and len(data['products']) > 0:
        # Get the first product
        product = data['products'][0]

        # Retrieve 'url' and 'code' for the product
        product_url = product.get('url', 'URL not available')
        product_code = product.get('code', 'Code not available')

        # Return the product URL and code
        returndata = {
            "url": product_url,
            "code": product_code
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
def get_data_from_html(html, price, sku):
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Extract the product name
    product_name = soup.find("h1", class_="font-weight-bold mb-1")
    cleaned_product_name = product_name.get_text(strip=True) if product_name else "Name not available"
    
    # Extract the product codes (product code and EAN)
    delivery_numbers = soup.find_all("div", class_="col-auto pl-0 col-md-auto p-md-0 font-weight-bold word-break")
    cleaned_delivery_numbers = [delivery_number.get_text(strip=True) for delivery_number in delivery_numbers]
    
    # Split the delivery numbers into product_code and ean_code
    if len(cleaned_delivery_numbers) > 1:
        product_code = cleaned_delivery_numbers[0]
        ean_code = cleaned_delivery_numbers[1]
    else:
        product_code = cleaned_delivery_numbers[0] if cleaned_delivery_numbers else "Code not available"
        ean_code = "EAN not available"

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
        "name": cleaned_product_name,
        "product_code": product_code,
        "ean_code": ean_code,
        "sku": sku,
        "price": price,
        "description": cleaned_product_description,
        "general_information": general_info,
    }

    # Convert the data to a JSON string and return it
    return json.dumps(data, indent=4)


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
    product_url_sku = get_product_url(session, product, searchbox_url)
    
    # Retrieve the product data
    product_data = get_product_data(session, base_url + product_url_sku["url"])

    # Convert the data to structured JSON
    data = get_data_from_html(product_data, price, product_url_sku['code'])
    
    return data


# Run the program
print(get_product("", "", "2700201612"))


# view the page directly of this product https://www.rexel.nl/nln/Rexel/Industriele-componenten/Transformatoren-en-voedingen/Voedingen/Gelijkstroomvoedingseenheid/Mean-Well-Gelijkstroomvoedingseenheid-sdr20-24-psu-din-24v-5a/p/2700130858
