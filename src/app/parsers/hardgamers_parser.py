"""
Parser específico para HardGamers.com.ar

Este parser conoce la estructura HTML específica de HardGamers
y convierte elementos HTML en objetos Product.
"""

from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from decimal import Decimal, InvalidOperation
import logging

from ..models import Product

logger = logging.getLogger(__name__)

class HardGamersParser:
    """
    Parser especializado en la estructura HTML de HardGamers.
    
    Responsabilidades:
    - Conocer las clases CSS específicas de HardGamers
    - Extraer datos desde elementos HTML
    - Convertir strings de precios a Decimal
    - Manejar casos edge (productos sin precio, etc.)
    """
    
    SHOP_NAME = "HardGamers"
    
    @classmethod
    def parse_products(cls, soup: BeautifulSoup) -> List[Product]:
        """
        Extrae todos los productos de una página de HardGamers.
        
        Args:
            soup: BeautifulSoup object con el HTML de la página
            
        Returns:
            Lista de objetos Product extraídos
        """
        products = []
        
        # HardGamers usa <article> para cada producto
        articles = soup.find_all("article")
        logger.info(f"Encontrados {len(articles)} artículos en la página")
        
        for article in articles:
            try:
                product = cls._parse_single_product(article)
                if product:
                    products.append(product)
            except Exception as e:
                logger.warning(f"Error parseando artículo: {e}")
                # Continuamos con el siguiente artículo
                continue
        
        logger.info(f"Parseados exitosamente {len(products)} productos")
        return products
    
    @classmethod
    def _parse_single_product(cls, article: Tag) -> Optional[Product]:
        """
        Parsea un solo artículo HTML y lo convierte en Product.
        
        Args:
            article: Tag <article> de BeautifulSoup
            
        Returns:
            Product object o None si no se puede parsear
        """
        # Extraer título
        title = cls._extract_title(article)
        if not title:
            logger.warning("Artículo sin título, saltando")
            return None
        
        # Extraer precio
        price = cls._extract_price(article)
        if not price:
            logger.warning(f"No se pudo extraer precio para: {title}")
            return None
        
        # Extraer URL (opcional)
        url = cls._extract_url(article)
        
        return Product(
            title=title,
            price=price,
            shop=cls.SHOP_NAME,
            url=url
        )
    
    @classmethod
    def _extract_title(cls, article: Tag) -> Optional[str]:
        """Extrae el título del producto desde el artículo HTML."""
        title_element = article.find(class_="product-title")
        if title_element:
            return title_element.text.strip()
        return None
    
    @classmethod
    def _extract_price(cls, article: Tag) -> Optional[Decimal]:
        """
        Extrae y convierte el precio desde el artículo HTML.
        
        HardGamers puede tener múltiples elementos de precio,
        tomamos todos y los combinamos.
        """
        price_elements = article.find_all(class_="product-price")
        if not price_elements:
            return None
        
        # Combinar todos los textos de precio
        price_text = ' '.join([elem.text.strip() for elem in price_elements])
        
        return cls._parse_price_text(price_text)
    
    @classmethod
    def _parse_price_text(cls, price_text: str) -> Optional[Decimal]:
        """
        Convierte texto de precio en Decimal.
        
        Ejemplos de formatos que maneja:
        - "$19.999,50"
        - "$ 19999"  
        - "19.999,50 ARS"
        - "$19,999.50" (formato US)
        """
        if not price_text:
            return None
        
        try:
            # Limpiar el texto: quitar símbolos y espacios
            cleaned = price_text.replace('$', '').replace('ARS', '').replace('USD', '').strip()
            
            # Manejar formato argentino: 19.999,50
            if ',' in cleaned and '.' in cleaned:
                # Formato: 19.999,50 -> 19999.50
                parts = cleaned.split(',')
                if len(parts) == 2:
                    integer_part = parts[0].replace('.', '')  # Quitar separadores de miles
                    decimal_part = parts[1]
                    cleaned = f"{integer_part}.{decimal_part}"
            
            # Manejar formato sin decimales: 19.999 -> 19999
            elif '.' in cleaned and not ',' in cleaned:
                # Verificar si es separador de miles o decimal
                parts = cleaned.split('.')
                if len(parts[-1]) <= 2:  # Últimos 2 dígitos = decimales
                    # Es decimal: 19.50
                    pass  # Mantener como está
                else:
                    # Es separador de miles: 19.999
                    cleaned = cleaned.replace('.', '')
            
            return Decimal(cleaned)
            
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"No se pudo convertir precio '{price_text}': {e}")
            return None
    
    @classmethod
    def _extract_url(cls, article: Tag) -> Optional[str]:
        """Extrae la URL del producto si está disponible."""
        # Buscar enlaces dentro del artículo
        link = article.find('a', href=True)
        if link:
            href = link['href']
            # Si es URL relativa, agregar dominio
            if href.startswith('/'):
                return f"https://www.hardgamers.com.ar{href}"
            return href
        return None