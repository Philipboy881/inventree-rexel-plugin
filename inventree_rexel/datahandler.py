from bs4 import BeautifulSoup
import requests
import sys


class DataHandler:
    def login(self, session, url, username, password):
        login_data = {"j_username": username, "j_password": password}
        login_response = session.post(url, data=login_data)
        if login_response.status_code != 200:
            return False
        return session

    def get_price(self, session, url):
        response = session.get(url)
        if response.status_code != 200:
            print(f"Error retrieving price: {response.status_code}")
            sys.exit()

        data = response.json()
        return data[0]['price']

    def search_product(self, session, search_data, url):
        response = session.get(url + search_data)
        if response.status_code != 200:
            print(f"Error retrieving product URL: {response.status_code}")
            sys.exit()
    
        data = response.json()
        if 'products' in data and len(data['products']) > 0:
            product = data['products'][0]
            product_code = product.get('code', 'Code not available')
            product_name = product.get('name', 'Name not available')
            product_url = product.get('url', 'URL not available')
            product_image_url = product["images"][3].get('url', 'Image not available')
            product_brandname = product.get('brandName', 'brand not available')
            product_ean = product.get('ean', 'ean not available')
            product_numbercontentunits = product.get('numberContentUnits', 'numbercontentunits not available')
            product_manufactureraid = product.get('manufacturerAID', 'manufactureraid not available')
            product_pricingqty = product.get('pricingQty', 'pricingqty  not available')
            
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
    def get_product_data(self, session, url):
        response = session.get(url)

        if response.status_code != 200:
            print(f"Error retrieving product data: {response.status_code}")
            sys.exit()

        data = response.text
        return data

    # Function to extract general information from product tables
    def extract_table_data(self, tables):
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
    def get_data_from_html(self, html):
        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(html, "html.parser")

        # Extract the product description
        product_description = soup.find("div", class_="long-product-description")
        cleaned_product_description = product_description.get_text(strip=True) if product_description else "Description not available"

        # Use the extract_table_data function to extract general information from the tables
        table1 = soup.find_all("div", class_="col-6 pr-5 px-lg-3")
        table2 = soup.find_all("div", class_="col-6 pl-5 px-lg-4")
        general_info_1 = self.extract_table_data(table1)
        general_info_2 = self.extract_table_data(table2)
        general_info = {**general_info_1, **general_info_2}

        # Return the data in a structured JSON format
        data = {
            "description": cleaned_product_description,
            "general_information": general_info,
        }

        # Convert the data to a JSON string and return it
        return data

    # Main function to get product data and price
    def get_product(self, username, password, product):
        base_url = "https://www.rexel.nl/nln"
        login_url = "https://www.rexel.nl/nln/j_spring_security_check"
        price_url = "https://www.rexel.nl/nln/erp/getPrice.json?products="
        price_url1 = "&isListPage=false&isProductBundle=false&context=PDP&isLeasingProductPresent=false"
        searchbox_url = "https://www.rexel.nl/nln/search/autocomplete/SearchBoxResponsiveComponent?term="

        # Create a session object to manage cookies and headers
        session = requests.Session()

        # Only login if username and password are provided (for price retrieval)
        if username and password:
            session = self.login(session, login_url, username, password)
            if session is False:
                print("Login failed, cannot retrieve price.")
                price = "Price not available"
            else:
                # Retrieve the price with the logged-in session
                price = self.get_price(session, price_url + product + price_url1)
                print("Price:", price)
        else:
            price = "Price not available"  # No login credentials, so no price retrieval

        # Retrieve the product URL and SKU without login
        product_data = self.search_product(session, product, searchbox_url)

        # Retrieve the product data
        product_scraped_data = self.get_product_data(session, base_url + product_data["url"])

        # Convert the data to structured JSON
        product_scraped_data_processed = self.get_data_from_html(product_scraped_data)
        rdata = {**product_data, **product_scraped_data_processed}
        return rdata

    def requestdata(self, product_number, username, password):
        data = self.get_product(username, password, product_number)
        return data
