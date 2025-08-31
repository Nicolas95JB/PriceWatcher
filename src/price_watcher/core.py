from .services import get_featured_products

async def run():
    response = await get_featured_products()
    extract_info(response)

def extract_info(soup):
    articles = soup.find_all("article")
    for article in articles:
        title = article.find(class_="product-title").text.strip()
        shop = article.find(class_="subtitle").text.strip()
        price_obj = article.find_all(class_="product-price")
        price_text = ' '.join([p.text.strip() for p in price_obj])
        print(f"Titulo: {title}\nPrecio: {price_text}\nTienda: {shop}\n")
