from .config import PRICE_DROPPED_URL, FEATURED_PRODUCTS_URL

from bs4 import BeautifulSoup
import sys
import requests
import asyncio

async def run():
    trys = 0
    try:
        while trys < 5:
            trys += 1
            res = requests.get("https://www.hardgamers.com.ar/deals?page=1")
            if res.status_code == 200:
                return extract_info(BeautifulSoup(res.text, "lxml"))
            await asyncio.sleep(300)
    except requests.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
    finally:
        print(f"Solicitud finalizada. luego de {trys} intengos.")

def extract_info(soup):
    articles = soup.find_all("article")
    for article in articles:
        title = article.find(class_="product-title").text.strip()
        shop = article.find(class_="subtitle").text.strip()
        price_obj = article.find_all(class_="product-price")
        price_text = ' '.join([p.text.strip() for p in price_obj])
        print(f"Titulo: {title}\nPrecio: {price_text}\nTienda: {shop}\n")
