def filter_phone_number(phone_number: str):
    if phone_number is None:
        return None
    
    if phone_number.startswith('54911'):
        # replace 54911 with 5411
        return '5411' + phone_number[5:]
    
    if phone_number.startswith('521'):        
        return phone_number.replace('521', '52')
    
    return phone_number

