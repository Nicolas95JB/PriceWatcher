"""
ProductRepository - Gestión de persistencia para productos.

Nota: Los productos generalmente no se persisten a largo plazo
ya que vienen de scraping en tiempo real. Este repository 
podría usarse para:
- Cache temporal de resultados
- Histórico de precios
- Productos favoritos del usuario
"""

import aiosqlite
from typing import List, Optional
from decimal import Decimal
import logging

from ..models import Product
from ..database import db

logger = logging.getLogger(__name__)

class ProductRepository:
    """
    Repository para operaciones CRUD de productos.
    
    En PriceWatcher, esto podría usarse para:
    - Guardar histórico de precios
    - Cache de búsquedas recientes
    - Lista de productos favoritos
    """
    
    async def save(self, product: Product) -> Product:
        """Guarda un producto en la base de datos."""
        if product.id is None:
            return await self._insert(product)
        else:
            return await self._update(product)
    
    async def _insert(self, product: Product) -> Product:
        """Inserta nuevo producto."""
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                INSERT INTO products (title, price, shop, url)
                VALUES (?, ?, ?, ?)
            """, (
                product.title,
                str(product.price),  # Decimal -> str
                product.shop,
                product.url
            ))
            
            await conn.commit()
            product_id = cursor.lastrowid
            
            logger.info(f"Producto guardado con ID: {product_id}")
            
            return Product(
                id=product_id,
                title=product.title,
                price=product.price,
                shop=product.shop,
                url=product.url
            )
    
    async def _update(self, product: Product) -> Product:
        """Actualiza producto existente."""
        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute("""
                UPDATE products 
                SET title = ?, price = ?, shop = ?, url = ?
                WHERE id = ?
            """, (
                product.title,
                str(product.price),
                product.shop,
                product.url,
                product.id
            ))
            
            await conn.commit()
            logger.info(f"Producto {product.id} actualizado")
            return product
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Busca producto por ID."""
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT id, title, price, shop, url
                FROM products WHERE id = ?
            """, (product_id,))
            
            row = await cursor.fetchone()
            if row:
                return self._row_to_product(row)
            return None
    
    async def search_by_title(self, search_text: str) -> List[Product]:
        """
        Busca productos por título (en BD local, no web scraping).
        
        Útil para búsquedas en histórico o favoritos.
        """
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT id, title, price, shop, url
                FROM products 
                WHERE title LIKE ?
                ORDER BY title
            """, (f"%{search_text}%",))
            
            rows = await cursor.fetchall()
            return [self._row_to_product(row) for row in rows]
    
    async def get_recent_products(self, limit: int = 50) -> List[Product]:
        """Obtiene los productos más recientes guardados."""
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT id, title, price, shop, url
                FROM products 
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            
            rows = await cursor.fetchall()
            return [self._row_to_product(row) for row in rows]
    
    async def delete(self, product_id: int) -> bool:
        """Elimina producto por ID."""
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                DELETE FROM products WHERE id = ?
            """, (product_id,))
            
            await conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_product(self, row: tuple) -> Product:
        """Convierte fila SQLite a objeto Product."""
        return Product(
            id=row[0],
            title=row[1], 
            price=Decimal(row[2]),  # str -> Decimal
            shop=row[3],
            url=row[4]
        )


# Instancia global para usar en toda la app
product_repository = ProductRepository()