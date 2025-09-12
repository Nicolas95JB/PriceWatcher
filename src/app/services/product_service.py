"""
ProductService - Lógica de negocio para productos.

Este service orquesta:
- HTTP requests async para obtener HTML
- Parsers para convertir HTML a objetos Product  
- Retry logic y manejo de errores
- Logging y métricas
"""

import asyncio
import aiohttp
from typing import List, Optional
from bs4 import BeautifulSoup
import logging

from ..models import Product
from ..parsers import HardGamersParser
from ..config import PRICE_DROPPED_URL, SEARCH_URL

logger = logging.getLogger(__name__)

class ProductService:
    """
    Service para gestionar búsqueda y obtención de productos.
    
    Responsabilidades:
    - Realizar HTTP requests de forma async
    - Coordinar con parsers para convertir HTML
    - Implementar retry logic robusto
    - Manejar errores y logging
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Args:
            max_retries: Número máximo de reintentos
            retry_delay: Segundos entre reintentos (exponential backoff)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def get_featured_products(self) -> List[Product]:
        """
        Obtiene productos destacados/en oferta de HardGamers.
        
        Returns:
            Lista de productos en oferta
        """
        logger.info("Obteniendo productos destacados...")
        
        soup = await self._fetch_html(PRICE_DROPPED_URL, "productos destacados")
        if not soup:
            return []
        
        products = HardGamersParser.parse_products(soup)
        logger.info(f"Obtenidos {len(products)} productos destacados")
        return products
    
    async def search_products(self, search_text: str) -> List[Product]:
        """
        Busca productos por texto en HardGamers.
        
        Args:
            search_text: Texto a buscar (ej: "monitor lg 27")
            
        Returns:
            Lista de productos que coinciden con la búsqueda
        """
        if not search_text.strip():
            logger.warning("Texto de búsqueda vacío")
            return []
        
        query = search_text.replace(" ", "+")
        url = f"{SEARCH_URL}{query}"
        
        logger.info(f"Buscando productos: '{search_text}'")
        
        soup = await self._fetch_html(url, f"búsqueda '{search_text}'")
        if not soup:
            return []
        
        products = HardGamersParser.parse_products(soup)
        logger.info(f"Encontrados {len(products)} productos para '{search_text}'")
        return products
    
    async def _fetch_html(self, url: str, operation_name: str) -> Optional[BeautifulSoup]:
        """
        Hace HTTP request con retry logic y devuelve BeautifulSoup.
        
        Args:
            url: URL a consultar
            operation_name: Nombre de la operación para logs
            
        Returns:
            BeautifulSoup object o None si falla
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Intento {attempt}/{self.max_retries} para {operation_name}")
                
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as session:
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, "lxml")
                            logger.info(f"Éxito obteniendo {operation_name}")
                            return soup
                        else:
                            logger.warning(f"HTTP {response.status} para {operation_name}")
                            
            except aiohttp.ClientError as e:
                logger.warning(f"Error de red en intento {attempt}: {e}")
            except Exception as e:
                logger.error(f"Error inesperado en intento {attempt}: {e}")
            
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.info(f"Esperando {delay}s antes del siguiente intento...")
                await asyncio.sleep(delay)
        
        logger.error(f"Falló {operation_name} después de {self.max_retries} intentos")
        return None


product_service = ProductService()