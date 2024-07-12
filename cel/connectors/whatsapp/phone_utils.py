def filter_phone_number(phone_number: str):
    if phone_number is None:
        return None
    
    if phone_number.startswith('54911'):
        # replace 54911 with 5411
        return '5411' + phone_number[5:]
    
    return phone_number

