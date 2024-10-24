import requests


def get_crypto_price(asset: str) -> float:
    url = f"https://api.coinbase.com/v2/prices/{asset}-USD/spot"
    response = requests.get(url)
    data = response.json()
    price = float(data['data']['amount'])
    return price


if __name__ == "__main__":
    print(get_crypto_price("BTC"))
    print(get_crypto_price("ETH"))
    print(get_crypto_price("DOGE"))