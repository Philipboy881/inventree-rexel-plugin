def process_rexel_data(data):
    """
    Verwerk Rexel data en geef een resultaat terug.
    """
    product_number = data['product_number']
    part_number = data['part_number']

    # Verwerking (voorbeeld)
    return {
        'product_number': product_number,
        'part_number': part_number,
        'status': 'success',
        'message': f'Processed part {part_number} for product {product_number}.'
    }
