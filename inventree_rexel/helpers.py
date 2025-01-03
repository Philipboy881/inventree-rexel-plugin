from bs4 import BeautifulSoup
import requests
import sys
import time
from company.models import Company
from part.models import Part, PartParameter, PartParameterTemplate
from company.models import ManufacturerPart, SupplierPart
from InvenTree.helpers_model import download_image_from_url
from django.core.files.base import ContentFile
from common.models import InvenTreeSetting
import io


class RexelHelper:

    def get_model_instance(self, model_class, identifier, defaults, context):
        """
        Haal een modelinstantie op op basis van een identifier (zoals naam of ID) en creëer deze als deze niet bestaat.
        :param model_class: Het model waaraan we willen refereren
        :param identifier: De identifier waarmee we zoeken (bijvoorbeeld een naam)
        :param defaults: Standaardwaarden die we moeten toevoegen als we de instantie creëren
        :param context: Een contextuele string voor foutmeldingen
        :return: De modelinstantie
        """
        try:
            # Zoek het object op, bijvoorbeeld op basis van naam of andere identificatoren
            instance = model_class.objects.get(name=identifier)
        except model_class.DoesNotExist:
            # Als het niet bestaat, maak het dan aan met de standaardwaarden
            instance = model_class.objects.create(name=identifier, **defaults)
        return instance

    def add_or_update_parameters(self, part, parameters):
        """
        Voeg parameters toe aan een part of werk bestaande parameters bij.
        
        :param part: Het part waaraan parameters worden toegevoegd.
        :param parameters: Een dictionary met parameternaam als sleutel en waarde als waarde.
        """
        for name, value in parameters.items():
            # Verkrijg of maak een PartParameterTemplate aan met de gegeven naam
            template = self.get_model_instance(PartParameterTemplate, name, {}, f"for {part.name}")
            
            try:
                # Probeer de PartParameter te verkrijgen of aan te maken
                parameter, created = PartParameter.objects.get_or_create(
                    part=part,
                    template=template,
                    defaults={'data': value}
                )
                
                # Als de parameter al bestaat, werk dan de waarde bij
                if not created:
                    parameter.data = value
                    parameter.save()

            except Exception:
                time.sleep(0.1)  # Wacht een seconde en probeer het opnieuw
                continue
            
            time.sleep(0.1)  # Wacht een seconde en probeer het opnieuw

    def find_or_create_company(self, name):
        manufacturer_name_lower = name.lower()

        if name == "rexel":
            manufacturer, created = Company.objects.get_or_create(
                name__iexact=manufacturer_name_lower,
                defaults={"name": manufacturer_name_lower, "is_manufacturer": True, "is_supplier": True}
            )
        else:
            manufacturer, created = Company.objects.get_or_create(
                name__iexact=manufacturer_name_lower,
                defaults={"name": manufacturer_name_lower, "is_manufacturer": True, "is_supplier": False}
            )

        return manufacturer.id

    def get_or_create_manufacturer_part(self, ipn, mpn, manufacturer_id):
        try:
            part_instance = Part.objects.get(IPN=ipn)
        except Part.DoesNotExist:
            raise ValueError(f"Part with ID '{ipn}' does not exist")
        
        manufacturer_part, created = ManufacturerPart.objects.get_or_create(
            part=part_instance,
            manufacturer_id=manufacturer_id,
            MPN=mpn
        )
        return manufacturer_part

    def create_supplier_part(self, ipn, supplier_id, manufacturer_part, sku):
        try:
            supplier_instance = Company.objects.get(id=supplier_id)
        except Company.DoesNotExist:
            raise ValueError(f"Supplier with ID '{supplier_id}' does not exist")

        try:
            part_instance = Part.objects.get(IPN=ipn)
        except Part.DoesNotExist:
            raise ValueError(f"Part with ID '{ipn}' does not exist")
        
        supplier_part, created = SupplierPart.objects.get_or_create(
            part=part_instance,
            SKU=sku,
            supplier=supplier_instance,
            manufacturer_part=manufacturer_part
        )
        return supplier_part

    def create_part(self, data, manufacturer_id, supplier_id, internal_part_number):
        name = data.get("name", None)
        description = data.get("description", "")
        notes = ""
        if len(description) > 250:
            notes = description
            description = description[:250]
        unit = data.get("unit", None).lower()
        image_url = data.get("image url", None)
        manufacturerpartnr = data.get("product number", None)
        supplierpartnr = data.get("code", None)

        # Download de afbeelding als de URL is opgegeven
        remote_img = None
        if image_url:
            if not InvenTreeSetting.get_setting('INVENTREE_DOWNLOAD_FROM_URL'):
                raise ValueError("Downloading images from remote URL is not enabled")
            try:
                remote_img = download_image_from_url(image_url)
            except Exception as e:
                print(f"Fout bij het downloaden van de afbeelding: {e}")
                
        part = Part.objects.create(
            IPN=internal_part_number,
            name=name,
            description=description,
            notes=notes,
            units=unit
        )

        # Koppel de afbeelding aan het Part-object
        if remote_img:
            fmt = remote_img.format or 'PNG'
            buffer = io.BytesIO()
            remote_img.save(buffer, format=fmt)

            filename = f"part_{part.pk}_image.{fmt.lower()}"
            part.image.save(
                filename,
                ContentFile(buffer.getvalue()),
            )

        manufacturer_part = self.get_or_create_manufacturer_part(internal_part_number, manufacturerpartnr, manufacturer_id)

        supplier_part_instance = self.create_supplier_part(internal_part_number, supplier_id, manufacturer_part, supplierpartnr)

        part.default_supplier = supplier_part_instance
        part.save()

        general_information = data.get("general_information", {})
        self.add_or_update_parameters(part, general_information)

        return part.id

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

    def process_rexel_data(self, data):
        rexel_id = self.find_or_create_company("rexel")

        product_number = data['product_number']
        internal_part_number = data['part_number']

        data = self.get_product("", "", product_number)

        manufacturer = data["brand"]
        manufacturer_id = self.find_or_create_company(manufacturer)

        part_id = self.create_part(data, manufacturer_id, rexel_id, internal_part_number)

        return part_id
