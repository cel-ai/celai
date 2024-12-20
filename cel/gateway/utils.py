import json
import secrets
import time
import jwt
import datetime
from cryptography.fernet import Fernet
import base64


def generate_encryption_key():
    return secrets.token_bytes(32)

def generate_secret_key():
    return secrets.token_hex(32)



def create_jwt(data: dict, secret_key, encryption_key, ttl=180):
    """
    Creates an encrypted JWT (JSON Web Token).

    Args:
        data (dict): Data to include in the JWT.
        secret_key (str): Secret key to sign the JWT.
        encryption_key (str): Key to encrypt the JWT.
        ttl (int, optional): Token time-to-live in seconds. Default is 180 seconds.

    Returns:
        str: Encrypted JWT as a string.
    """    
    # Calculate the expiration time
    expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl)

    try:
        payload = data or {}
    except ValueError as e:
        raise ValueError("El string proporcionado no es un JSON válido.") from e

    # Add expiration time to the payload
    payload['exp'] = expiration

    # Sign the JWT with the secret key using the HS256 algorithm
    encoded_jwt = jwt.encode(payload, secret_key, algorithm='HS256')

    # Encrypt the JWT with the encryption key
    fernet = Fernet(base64.urlsafe_b64encode(encryption_key.ljust(32, b'\0')))
    encrypted_jwt = fernet.encrypt(encoded_jwt.encode())

    # Return the encrypted JWT as a string
    return encrypted_jwt.decode()


def decode_jwt(jwt_token, secret_key, encryption_key):
    """
    Decodes a JWT token using the provided secret key and encryption key.

    Args:
        jwt_token (str): The JWT token to decode.
        secret_key (str): The secret key used to verify the JWT signature.
        encryption_key (bytes): The encryption key used to decrypt the JWT.

    Returns:
        dict: The decoded JWT payload.

    Raises:
        ValueError: If the token has expired or is invalid.
    """

    # Unencrypt the JWT
    fernet = Fernet(base64.urlsafe_b64encode(encryption_key.ljust(32, b'\0')))
    decrypted_jwt = fernet.decrypt(jwt_token.encode())

    # Verify the JWT signature, exp date and decode it
    try:
        decoded_jwt = jwt.decode(decrypted_jwt, secret_key, algorithms=['HS256'])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        raise ValueError("El token ha expirado.")
    except jwt.InvalidTokenError as e:
        raise ValueError("El token no es válido.") from e
    

def generate_link(base_url: str, secret_key: str, encryption_key: bytes, data: dict = None, ttl=180):
    """
    Generates a URL with a JWT token as a query parameter.

    Args:
        base_url (str): The base URL to which the JWT token will be appended.
        secret_key (str): The secret key used to sign the JWT.
        encryption_key (bytes): The encryption key used to encrypt the JWT.
        data (dict, optional): The data to include in the JWT payload. Defaults to None.
        ttl (int, optional): The time-to-live for the JWT token in seconds. Defaults to 180.

    Returns:
        str: The generated URL with the JWT token as a query parameter.
    """    
    
    assert isinstance(base_url, str), "base_url must be a string"
    assert isinstance(secret_key, str), "secret_key must be a string"
    assert isinstance(encryption_key, bytes), "encryption_key must be a bytes object"
    assert isinstance(data, dict) or None, "data must be a dictionary"
    

    # Create the JWT token
    jwt_token = create_jwt(data, secret_key, encryption_key, ttl)

    # Return the URL with the JWT token as a query parameter
    return f"{base_url}/{jwt_token}"



if __name__ == "__main__":
    
    # Use example
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    
    data = {"user_id": "123", "name": "John Doe"}

    jwt_token = create_jwt(data, secret_key, encryption_key, ttl=1)
    print(jwt_token)

    time.sleep(2)

    # Decodificar el JWT
    try:
        decoded_token = decode_jwt(jwt_token, secret_key, encryption_key)
        print(decoded_token)
    except ValueError as e:
        print(f"Error: {e}")
    

    # Generate a link
    base_url = "https://example.com"
    data = {"user_id": "123", "name": "John Doe"}
    link = generate_link(base_url, secret_key, encryption_key, data)
    print(link)
    

