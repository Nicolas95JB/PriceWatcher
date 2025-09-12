"""
Repositories package - Acceso a datos y persistencia.

Los repositories encapsulan el acceso a la base de datos:
- ProductRepository: CRUD operations para productos
- AlertRepository: CRUD operations para alertas

Principio: Repository Pattern abstrae el storage, services no saben SQL.
"""

from .product_repository import ProductRepository
from .alert_repository import AlertRepository

__all__ = ["ProductRepository", "AlertRepository"]