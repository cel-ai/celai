def build_headers(token: str):
    
    return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }