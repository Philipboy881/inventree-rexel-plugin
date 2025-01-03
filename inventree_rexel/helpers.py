import time
from company.models import Company
from part.models import Part, PartParameter, PartParameterTemplate
from company.models import ManufacturerPart, SupplierPart
from InvenTree.helpers_model import download_image_from_url
from django.core.files.base import ContentFile
from common.models import InvenTreeSetting
import io

from .datahandler import DataHandler


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

    def process_rexel_data(self, data):
        rexel_id = self.find_or_create_company("rexel")

        product_number = data['product_number']
        internal_part_number = data['part_number']

        datahandler = DataHandler()
        data = datahandler.requestdata(product_number, "", "")

        manufacturer = data["brand"]
        manufacturer_id = self.find_or_create_company(manufacturer)

        part_id = self.create_part(data, manufacturer_id, rexel_id, internal_part_number)

        return part_id
