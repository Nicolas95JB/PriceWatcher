import requests
import asyncio
from bs4 import BeautifulSoup

from .config import FEATURED_PRODUCTS_URL

async def get_featured_products():
    trys = 0
    try:
        while trys < 5:
            trys += 1
            res = requests.get(FEATURED_PRODUCTS_URL)
            if res.status_code == 200:
                return BeautifulSoup(res.text, "lxml")
            await asyncio.sleep(300)
    except requests.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
    finally:
        print(f"Solicitud finalizada. luego de {trys} intengos.")