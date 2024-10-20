import aiohttp
import asyncio

async def get_crypto_price(crypto_symbol, currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_symbol}&vs_currencies={currency}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if crypto_symbol in data:
                    return data[crypto_symbol][currency]
                else:
                    return f"Error: Cryptocurrency '{crypto_symbol}' not found."
            else:
                return f"Error: Unable to fetch data. Status code: {response.status}"

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        crypto_symbol = "cardano"
        currency = "aud"
        price = await get_crypto_price(crypto_symbol, currency)
        print(f"El precio actual de {crypto_symbol} en {currency} es: {price}")

    # Ejecutar el ejemplo
    asyncio.run(main())