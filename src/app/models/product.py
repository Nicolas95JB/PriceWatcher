"""
Product model - Productos encontrados en las webs de e-commerce.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class Product:
    """
    Representa un producto encontrado en la web.
    
    Attributes:
        title: Nombre del producto
        price: Precio como Decimal para manejar centavos correctamente
        shop: Tienda donde se encuentra
        url: Link al producto (opcional)
        id: ID único (opcional, lo asigna la base de datos)
    """
    title: str
    price: Decimal
    shop: str
    url: Optional[str] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Se ejecuta después de crear el objeto para validaciones"""
        if self.price < 0:
            raise ValueError("El precio no puede ser negativo")
        if not self.title.strip():
            raise ValueError("El título no puede estar vacío")
    
    def display_price(self) -> str:
        """Formatea el precio para mostrar al usuario"""
        return f"${self.price:,.2f}"
    
    def matches_search(self, search_text: str) -> bool:
        """
        Verifica si este producto coincide con una búsqueda.
        
        Returns:
            True si el título contiene el texto de búsqueda (case-insensitive)
        """
        return search_text.lower() in self.title.lower()
    
    def __str__(self) -> str:
        """Representación legible del producto"""
        return f"{self.title} - {self.display_price()} ({self.shop})"