from .services import get_featured_products, search_product

def extract_info(soup):
    articles = soup.find_all("article")
    for article in articles:
        title = article.find(class_="product-title").text.strip()
        shop = article.find(class_="subtitle").text.strip()
        price_obj = article.find_all(class_="product-price")
        price_text = ' '.join([p.text.strip() for p in price_obj])
        print(f"Titulo: {title}\nPrecio: {price_text}\nTienda: {shop}\n")

async def app():
    featured_products = await get_featured_products()
    print("Productos destacados:")
    extract_info(featured_products)
    
    search_text = input("Ingrese el producto a buscar: ").strip()
    while not search_text:
        search_text = input("Entrada inválida. Ingrese el producto a buscar: ").strip()
    search_results = await search_product(search_text)
    print("\nResultados de busqueda:")
    extract_info(search_results)
