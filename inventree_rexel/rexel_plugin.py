# Django stuff
from django.utils.translation import gettext_lazy as _  # type: ignore

# InvenTree plugin libs
from plugin import InvenTreePlugin  # type: ignore
from .version import REXEL_PLUGIN_VERSION
from bs4 import BeautifulSoup

import requests
import sys
import json


class RexelPlugin(InvenTreePlugin):
    AUTHOR = "Philip van der honing"
    DESCRIPTION = "rexel parts import plugin"
    VERSION = REXEL_PLUGIN_VERSION
    NAME = "rexel"
    SLUG = "rexel"
    PUBLISH_DATE = "2024-12-28"
    TITLE = "Rexel part import"

    SETTINGS = {
        'USERNAME': {
            'name': _('username'),
            'description': _('username van je rexel account'),
            'default': '',
        },
        'PASSWORD': {
            'name': _('IP Address'),
            'description': _('password van je rexel account'),
            'default': '',
        },
    }

    # login functie
    def login(self, session, url, username, password):

        # Definieer je login URL, gebruikersnaam en wachtwoord
        login_data = {
            "j_username": username,
            "j_password": password
        }
        login_response = session.post(url, data=login_data)
        if login_response.status_code != 200:
            return False
        return session

    # get price function
    def get_price(self, session, url):

        response = session.get(url)

        if response.status_code != 200:
            print(f"Fout bij ophalen prijs: {response.status_code}")
            sys.exit()
        # print("Prijs succesvol opgehaald!")
        data = response.json()
        # print(response.text)
        return data[0]['price']

    def get_product_url(self, session, sku, url):
        response = session.get(url + sku)
        if response.status_code != 200:
            print(f"Fout bij ophalen product URL: {response.status_code}")
            sys.exit()

        data = response.json()

        # Controleer of de producten aanwezig zijn in de response
        if 'products' in data and len(data['products']) > 0:
            # Pak het eerste product
            product = data['products'][0]

            # Haal de 'url' en 'code' op
            product_url = product.get('url', 'URL niet beschikbaar')
            product_code = product.get('code', 'Code niet beschikbaar')

            # Voeg de URL en code toe aan de list
            returndata = {
                "url": product_url,
                "code": product_code
            }

            return returndata
        else:
            print("Geen productgegevens gevonden in de response.")
            sys.exit()

    def get_product_data(self, session, url):
        # print(url)
        response = session.get(url)

        if response.status_code != 200:
            print(f"Fout bij ophalen product data: {response.status_code}")
            sys.exit()
        # print("url succesvol opgehaald!")
        data = response.text
        return data

    def extract_table_data(self, tables):
        """
        Functie om de gegevens uit de tabellen te extraheren die 'algemene informatie' bevatten.
        Dit retourneert een dictionary met de naam-waarde paren van de tabel.
        """
        algemene_info = {}

        # Zoek naar de divs die de tabellen bevatten
        # print("Aantal tabellen gevonden voor algemene informatie:", len(tables))  # Debugging output

        # Loop door elke tabel om de relevante informatie te extraheren
        for table in tables:
            # print("Tabel inhoud:", table.prettify())  # Debugging output, om de inhoud van de tabel te zien

            # Zoek naar alle rijen in de tabel
            rows = table.find_all("tr")
            for row in rows:
                # Zoek naar de 'th' en 'td' tags in de rij
                th = row.find("th")
                td = row.find("td")

                # Als we zowel een th als een td vinden
                if th and td:
                    attribute_name = th.get_text(strip=True)  # Naam van het attribuut (bijv. "Conditie/kortingsgroep")

                    # Zoek de waarde in de span tag om dubbele waarden te vermijden
                    span = td.find("span", class_="tech-table-values-text")
                    if span:
                        attribute_value = span.get_text(strip=True)  # We nemen alleen de tekst uit de span
                    else:
                        attribute_value = td.get_text(strip=True)  # Als er geen span is, nemen we de volledige inhoud van de td

                    # print(f"Gevonden waarde voor {attribute_name}: {attribute_value}")  # Debugging output

                    # Voeg de naam en waarde toe aan de dictionary als beide niet leeg zijn
                    if attribute_name and attribute_value:
                        algemene_info[attribute_name] = attribute_value

        return algemene_info

    def get_data_from_html(self, html, price, sku):
        # Hoofdfunctie om gegevens uit de HTML te extraheren, inclusief productnaam, omschrijving, etc.

        # Maak een BeautifulSoup object van de HTML
        soup = BeautifulSoup(html, "html.parser")

        # Zoek naar de productnaam
        productnaam = soup.find("h1", class_="font-weight-bold mb-1")  # Voor productnaam
        cleaned_productnaam = productnaam.get_text(strip=True) if productnaam else "Naam niet beschikbaar"
        # Zoek naar de levernummers (productcode en EAN)
        levernr = soup.find_all("div", class_="col-auto pl-0 col-md-auto p-md-0 font-weight-bold word-break")  # Voor productnummer
        cleaned_levernr = [levernr.get_text(strip=True) for levernr in levernr]
        # Splits de leverNr in product_code en ean_code
        if len(cleaned_levernr) > 1:
            product_code = cleaned_levernr[0]
            ean_code = cleaned_levernr[1]
        else:
            product_code = cleaned_levernr[0] if cleaned_levernr else "Code niet beschikbaar"
            ean_code = "EAN niet beschikbaar"

        # Zoek naar de productomschrijving
        productomschrijving = soup.find("div", class_="long-product-description")  # Voor productomschrijving
        cleaned_productomschrijving = productomschrijving.get_text(strip=True) if productomschrijving else "Omschrijving niet beschikbaar"
        # Gebruik de extract_table_data functie om algemene informatie uit de tabellen te halen
        tabel1 = soup.find_all("div", class_="col-6 pr-5 px-lg-3")
        tabel2 = soup.find_all("div", class_="col-6 pl-5 px-lg-4")
        algemene_informatie_1 = self.extract_table_data(self, tabel1)
        algemene_informatie_2 = self.extract_table_data(self, tabel2)
        algemene_informatie = {**algemene_informatie_1, **algemene_informatie_2}

        # Zet alles in een gestructureerde JSON
        data = {
            "naam": cleaned_productnaam,
            "product_code": product_code,
            "ean_code": ean_code,
            "sku": sku,
            "price": price,
            "omschrijving": cleaned_productomschrijving,
            "algemene_informatie": algemene_informatie,
        }
        # Zet de data om in JSON-formaat en retourneer deze
        return json.dumps(data, indent=4)

    def get_product(self, username, password, product):
        base_url = "https://www.rexel.nl/nln"
        login_url = "https://www.rexel.nl/nln/j_spring_security_check"
        price_url = "https://www.rexel.nl/nln/erp/getPrice.json?products="
        price_url1 = "&isListPage=false&isProductBundle=false&context=PDP&isLeasingProductPresent=false"
        searchbox_url = "https://www.rexel.nl/nln/search/autocomplete/SearchBoxResponsiveComponent?term="

        # Maak een sessie-object om cookies en headers automatisch te beheren
        session = requests.Session()

        # log gebruiker in
        session = self.login(self, session, login_url, username, password)

        # verkrijg url en sku
        product_url_sku = self.get_product_url(self, session, self.productcode, searchbox_url)
        # print (product_url_sku)

        # verkijg de user prijs
        if session is not False:
            price = self.get_price(self, session, price_url + product_url_sku['code'] + price_url1)
            # print("Price", price)

        # verkrijg de product data
        product_data = self.get_product_data(self, session, base_url + product_url_sku["url"])

        # converteer de data
        data = self.get_data_from_html(product_data, price, product_url_sku['code'])
        return data
