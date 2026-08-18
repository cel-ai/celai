import re


# Meta Business-Scoped User ID: two-letter country code + '.' + opaque id
# e.g. US.13491208655302741918, MX.1507950994201523
_BSUID_RE = re.compile(r"^[A-Z]{2}\.")


def is_bsuid(value: str) -> bool:
    """Return True if value looks like a WhatsApp Business-Scoped User ID."""
    if not value or not isinstance(value, str):
        return False
    return bool(_BSUID_RE.match(value))


def filter_phone_number(phone_number: str):
    if phone_number is None:
        return None

    if is_bsuid(phone_number):
        return phone_number

    if phone_number.startswith('54911'):
        # replace 54911 with 5411
        return '5411' + phone_number[5:]

    if phone_number.startswith('521'):
        return phone_number.replace('521', '52')

    return phone_number
