def process_rexel_data(data):
    """
    Verwerk Rexel data en geef een resultaat terug.
    """
    product_number = data['productNumber']
    part_number = data['partNumber']

    # Verwerking (voorbeeld)
    return {
        'productNumber': product_number,
        'partNumber': part_number,
        'status': 'success',
        'message': f'Processed part {part_number} for product {product_number}.'
    }
