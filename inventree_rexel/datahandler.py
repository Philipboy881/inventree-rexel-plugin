from bs4 import BeautifulSoup
import requests


class DataHandler:
    def login(self, session, url, username, password):
        """
        Log in to the provided URL with the given session, username, and password.
        """
        try:
            login_data = {"j_username": username, "j_password": password}
            response = session.post(url, data=login_data, timeout=10)
            response.raise_for_status()
            return session
        except requests.RequestException:
            return None

    def get_price(self, session, url):
        """
        Retrieve the price of a product from the given URL using a logged-in session.
        """
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0].get('price', "Price not available")
        except requests.RequestException:
            return "Price not available"

    def search_product(self, session, search_data, url):
        """
        Search for a product by its identifier and return relevant product details.
        """
        try:
            response = session.get(url + search_data, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'products' in data and len(data['products']) > 0:
                product = data['products'][0]
                images = product.get('images', [])
                # Controleer of de [3] afbeelding bestaat, anders gebruik [0]
                image_url = images[3].get('url') if len(images) > 3 and 'url' in images[3] else (
                    images[0].get('url') if len(images) > 0 and 'url' in images[0] else 'Image not available')

                return {
                    "code": product.get('code', 'Code not available'),
                    "name": product.get('name', 'Name not available'),
                    "url": product.get('url', 'URL not available'),
                    "image url": image_url,
                    "brand": product.get('brandName', 'Brand not available'),
                    "ean": product.get('ean', 'EAN not available'),
                    "unit": product.get('numberContentUnits', 'Unit not available'),
                    "product number": product.get('manufacturerAID', 'Manufacturer AID not available'),
                    "number of units": product.get('pricingQty', 'Pricing Quantity not available')
                }
            return {}
        except requests.RequestException:
            return {}

    # Function to get the product data from the provided URL
    def get_product_data(self, session, url):
        """
        Retrieve raw HTML data for a product from the given URL.
        """
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return ""

    # Function to extract general information from product tables
    def extract_table_data(self, tables):
        """
        Extract key-value pairs from HTML tables.
        """
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
    
    # Function to get structured data from the product HTML
    def get_data_from_html(self, html):
        """
        Parse HTML data and extract product description and general information.
        """
        soup = BeautifulSoup(html, "html.parser")
        product_description = soup.find("div", class_="long-product-description")
        cleaned_description = product_description.get_text(strip=True) if product_description else "Description not available"

        table1 = soup.find_all("div", class_="col-6 pr-5 px-lg-3")
        table2 = soup.find_all("div", class_="col-6 pl-5 px-lg-4")
        general_info_1 = self.extract_table_data(table1)
        general_info_2 = self.extract_table_data(table2)

        return {
            "description": cleaned_description,
            "general_information": {**general_info_1, **general_info_2}
        }
    
    # Main function to get product data and price
    def get_product(self, username, password, product):
        """
        Retrieve product details and price, combining data from multiple sources.
        """
        base_url = "https://www.rexel.nl/nln"
        login_url = f"{base_url}/j_spring_security_check"
        price_url = f"{base_url}/erp/getPrice.json?products={product}&isListPage=false&isProductBundle=false&context=PDP&isLeasingProductPresent=false"
        searchbox_url = f"{base_url}/search/autocomplete/SearchBoxResponsiveComponent?term="

        session = requests.Session()
        price = "Price not available"

        if username and password:
            session = self.login(session, login_url, username, password)
            if session:
                price = self.get_price(session, price_url)

        product_data = self.search_product(session, product, searchbox_url)
        if not product_data:
            return {}

        product_html = self.get_product_data(session, base_url + product_data.get("url", ""))
        product_scraped_data = self.get_data_from_html(product_html)

        return {**product_data, **product_scraped_data, "price": price}

    def requestdata(self, product_number, username, password):
        return self.get_product(username, password, product_number)
