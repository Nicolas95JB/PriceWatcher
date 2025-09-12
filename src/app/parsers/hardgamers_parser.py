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
        
        articles = soup.find_all("article")
        logger.info(f"Encontrados {len(articles)} artículos en la página")
        
        for article in articles:
            try:
                product = cls._parse_single_product(article)
                if product:
                    products.append(product)
            except Exception as e:
                logger.warning(f"Error parseando artículo: {e}")
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
        title = cls._extract_title(article)
        if not title:
            logger.warning("Artículo sin título, saltando")
            return None
        
        price = cls._extract_price(article)
        if not price:
            logger.warning(f"No se pudo extraer precio para: {title}")
            return None
        
        url = cls._extract_url(article)
        
        return Product(
            title=title,
            price=price,
            shop=cls.SHOP_NAME,
            url=url
        )
    
    @classmethod
    def _extract_title(cls, article: Tag) -> Optional[str]:
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
            cleaned = price_text.replace('$', '').replace('ARS', '').replace('USD', '').strip()
            
            if ',' in cleaned and '.' in cleaned:
                parts = cleaned.split(',')
                if len(parts) == 2:
                    integer_part = parts[0].replace('.', '')
                    decimal_part = parts[1]
                    cleaned = f"{integer_part}.{decimal_part}"
            
            elif '.' in cleaned and not ',' in cleaned:
                parts = cleaned.split('.')
                if len(parts[-1]) <= 2:
                    pass
                else:
                    cleaned = cleaned.replace('.', '')
            
            return Decimal(cleaned)
            
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"No se pudo convertir precio '{price_text}': {e}")
            return None
    
    @classmethod
    def _extract_url(cls, article: Tag) -> Optional[str]:
        link = article.find('a', href=True)
        if link:
            href = link['href']
            if href.startswith('/'):
                return f"https://www.hardgamers.com.ar{href}"
            return href
        return None