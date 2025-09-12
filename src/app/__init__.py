"""
PriceWatcher Application Package.

Arquitectura refactorizada con separación de responsabilidades:
- models/: Datos y validaciones (Product, Alert)  
- parsers/: Conversión HTML → objetos Python
- services/: Lógica de negocio y orquestación
- repositories/: Acceso a datos (SQLite)
- core: Interfaz de usuario (CLI)
"""

from .config import BASE_URL, PRICE_DROPPED_URL
from .core import app
from .models import Product, Alert
from .services import ProductService, AlertService

__all__ = ["BASE_URL", "PRICE_DROPPED_URL", "app", "Product", "Alert", "ProductService", "AlertService"]