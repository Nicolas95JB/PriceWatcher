"""
Services package - Lógica de negocio y orquestación.

Los services coordinan entre parsers, repositories y modelos:
- ProductService: Buscar y obtener productos desde webs
- AlertService: Gestionar alertas y notificaciones

Principio: Services contienen la lógica de negocio, no detalles técnicos.
"""

from .product_service import ProductService
from .alert_service import AlertService

__all__ = ["ProductService", "AlertService"]