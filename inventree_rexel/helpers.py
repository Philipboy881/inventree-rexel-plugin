import time
from company.models import Company
from part.models import Part, PartParameter, PartParameterTemplate
from company.models import ManufacturerPart, SupplierPart
from InvenTree.helpers_model import download_image_from_url
from django.core.files.base import ContentFile
from common.models import InvenTreeSetting
from django.db import OperationalError, transaction
import io
from .datahandler import DataHandler
import threading


class RexelHelper():
    @staticmethod
    def retry_database_operation(func, retries=5, delay=0.5):
        """
        Probeer een database-operatie opnieuw uit te voeren als er een OperationalError optreedt.
        """
        for attempt in range(retries):
            try:
                return func()
            except OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(delay)
                else:
                    raise
        raise OperationalError(f"Exceeded maximum retries ({retries}) for database operation")

    def get_model_instance(self, model_class, identifier, defaults, context):
        # Probeer de instantie op te halen of te creëren
        try:
            # Gebruik get_or_create voor eenvoudiger ophalen of creëren
            instance, created = model_class.objects.get_or_create(name=identifier, defaults=defaults)
            return instance
        except Exception as e:
            # Log de fout, zodat je kunt zien waarom dit misgaat
            print(f"Fout bij ophalen/creëren van model: {e}")
            raise e

    def add_or_update_parameters(self, part, parameters):
        """
        Voeg parameters toe aan een Part of werk bestaande parameters bij.
        """
        # Verzamel alle parameters in een lijst
        to_create_or_update = []
        with transaction.atomic():
            for name, value in parameters.items():
                template = self.get_model_instance(PartParameterTemplate, name, {}, f"for {part.name}")
                to_create_or_update.append((part, template, value))

        # Nu pas daadwerkelijk in de database schrijven in één transactie
        with transaction.atomic():
            for part, template, value in to_create_or_update:
                parameter, created = PartParameter.objects.get_or_create(
                    part=part,
                    template=template,
                    defaults={'data': value}
                )
                if not created:
                    parameter.data = value
                    parameter.save()

    def find_or_create_company(self, name):
        """
        Zoek of maak een bedrijf aan op basis van de naam.
        """
        name_lower = name.lower()
        is_supplier = name == "rexel"
        return Company.objects.get_or_create(
            name__iexact=name_lower,
            defaults={"name": name_lower, "is_manufacturer": True, "is_supplier": is_supplier}
        )[0].id

    def get_or_create_manufacturer_part(self, ipn, mpn, manufacturer_id):
        """
        Zoek of maak een ManufacturerPart aan.
        """
        part_instance = Part.objects.filter(IPN=ipn).first()
        if not part_instance:
            raise ValueError(f"Part with IPN '{ipn}' does not exist")
        return ManufacturerPart.objects.get_or_create(
            part=part_instance,
            manufacturer_id=manufacturer_id,
            MPN=mpn
        )[0]

    def create_supplier_part(self, ipn, supplier_id, manufacturer_part, sku):
        """
        Zoek of maak een SupplierPart aan.
        """
        supplier_instance = Company.objects.filter(id=supplier_id).first()
        if not supplier_instance:
            raise ValueError(f"Supplier with ID '{supplier_id}' does not exist")

        part_instance = Part.objects.filter(IPN=ipn).first()
        if not part_instance:
            raise ValueError(f"Part with IPN '{ipn}' does not exist")

        return SupplierPart.objects.get_or_create(
            part=part_instance,
            SKU=sku,
            supplier=supplier_instance,
            manufacturer_part=manufacturer_part
        )[0]

    def create_part(self, data, manufacturer_id, supplier_id, internal_part_number):
        """
        Maak een nieuw Part-object en koppel relevante gegevens zoals manufacturer en supplier.
        """
        name = data.get("name")
        description = data.get("description", "")[:250]
        notes = data.get("description", "")
        unit = data.get("unit", "").lower()
        image_url = data.get("image url")
        manufacturer_part_number = data.get("product number")
        supplier_part_number = data.get("code")

        if not name:
            raise ValueError("Part name is required")

        remote_img = None
        if image_url and InvenTreeSetting.get_setting('INVENTREE_DOWNLOAD_FROM_URL'):
            try:
                remote_img = download_image_from_url(image_url)
            except Exception as e:
                print(f"Error downloading image: {e}")
        part = Part.objects.create(
            IPN=internal_part_number,
            name=name,
            description=description,
            notes=notes,
            units=unit
        )

        if remote_img:
            buffer = io.BytesIO()
            fmt = remote_img.format or "PNG"
            remote_img.save(buffer, format=fmt)
            filename = f"part_{part.pk}_image.{fmt.lower()}"
            part.image.save(filename, ContentFile(buffer.getvalue()))

        manufacturer_part = self.get_or_create_manufacturer_part(internal_part_number, manufacturer_part_number, manufacturer_id)
        supplier_part = self.create_supplier_part(internal_part_number, supplier_id, manufacturer_part, supplier_part_number)

        try:
            part.default_supplier = supplier_part
            part.save()
        except Exception as e:
            print(f"Error asving data: {e}")

        general_info = data.get("general_information", {})
        threading.Thread(target=self._process_data_in_background, args=(part, general_info,)).start()
        return part.id

    def _process_data_in_background(self, part, general_info):
        """
        Verwerk de Rexel data in de achtergrond (achtergrond thread).
        Dit is de werkelijke verwerking die in een aparte thread draait.
        """
        try:
            # Je verwerking van de Rexel data hier
            self.add_or_update_parameters(part, general_info)

            raise ValueError("part created and saved")
        except Exception as e:
            print(f"Fout bij het verwerken van de Rexel data: {e}")

    def process_rexel_data(self, data):
        """
        Verwerk Rexel-productgegevens en maak de benodigde database-objecten aan.
        """
        product_number = data.get("product_number")
        datahandler = DataHandler()
        rexel_data = datahandler.requestdata(product_number, "", "")

        rexel_id = self.find_or_create_company("rexel")
        internal_part_number = Part.objects.count() + 2400001

        manufacturer_name = rexel_data.get("brand", "Unknown")
        manufacturer_id = self.find_or_create_company(manufacturer_name)

        self.create_part(rexel_data, manufacturer_id, rexel_id, str(internal_part_number))

        return rexel_data.get("name") + " word toegevoegd"
