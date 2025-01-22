import re


def format_to_e164(phone_number):
    # Eliminar todos los caracteres que no sean dígitos
    digits_only = re.sub(r'\D', '', phone_number)
    
    # Agregar el signo '+' al inicio
    return f'+{digits_only}'

