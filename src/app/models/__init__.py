"""
Models package - Definiciones de datos y validaciones.

Contiene todas las clases que representan entidades de negocio:
- Product: Productos encontrados en las webs
- Alert: Alertas configuradas por el usuario
"""

from .product import Product
from .alert import Alert

__all__ = ["Product", "Alert"]