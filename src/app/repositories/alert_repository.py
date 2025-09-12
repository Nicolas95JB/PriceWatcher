"""
AlertRepository - Gestión de persistencia para alertas.

Responsabilidades:
- Guardar/cargar alertas en SQLite
- Consultas específicas (alertas activas, por usuario, etc.)
- Conversión entre objetos Python ↔ filas de BD
"""

import aiosqlite
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import logging

from ..models import Alert
from ..database import db

logger = logging.getLogger(__name__)

class AlertRepository:
    """
    Repository para operaciones CRUD de alertas.
    
    Abstrae completamente el acceso a SQLite - los services
    no necesitan saber SQL ni detalles de la BD.
    """
    
    async def save(self, alert: Alert) -> Alert:
        """
        Guarda una alerta en la base de datos.
        
        Args:
            alert: Alerta a guardar (puede tener id=None para nuevas)
            
        Returns:
            Alert con id asignado por la BD
        """
        if alert.id is None:
            # Es nueva alerta - INSERT
            return await self._insert(alert)
        else:
            # Actualizar existente - UPDATE
            return await self._update(alert)
    
    async def _insert(self, alert: Alert) -> Alert:
        """Inserta nueva alerta y devuelve con ID asignado."""
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                INSERT INTO alerts (search_text, target_price, is_active, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                alert.search_text,
                str(alert.target_price),  # Decimal -> str
                alert.is_active,
                alert.created_at.isoformat()  # datetime -> ISO string
            ))
            
            await conn.commit()
            
            # Obtener el ID generado
            alert_id = cursor.lastrowid
            logger.info(f"Nueva alerta guardada con ID: {alert_id}")
            
            # Devolver copia con ID asignado
            return Alert(
                id=alert_id,
                search_text=alert.search_text,
                target_price=alert.target_price,
                is_active=alert.is_active,
                created_at=alert.created_at
            )
    
    async def _update(self, alert: Alert) -> Alert:
        """Actualiza alerta existente."""
        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute("""
                UPDATE alerts 
                SET search_text = ?, target_price = ?, is_active = ?
                WHERE id = ?
            """, (
                alert.search_text,
                str(alert.target_price),
                alert.is_active,
                alert.id
            ))
            
            await conn.commit()
            logger.info(f"Alerta {alert.id} actualizada")
            return alert
    
    async def get_by_id(self, alert_id: int) -> Optional[Alert]:
        """
        Busca una alerta por su ID.
        
        Returns:
            Alert object o None si no existe
        """
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT id, search_text, target_price, is_active, created_at
                FROM alerts WHERE id = ?
            """, (alert_id,))
            
            row = await cursor.fetchone()
            if row:
                return self._row_to_alert(row)
            return None
    
    async def get_active_alerts(self) -> List[Alert]:
        """
        Obtiene todas las alertas activas.
        
        Returns:
            Lista de alertas con is_active=True
        """
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT id, search_text, target_price, is_active, created_at
                FROM alerts 
                WHERE is_active = 1
                ORDER BY created_at DESC
            """)
            
            rows = await cursor.fetchall()
            return [self._row_to_alert(row) for row in rows]
    
    async def get_all_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas (activas e inactivas)."""
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT id, search_text, target_price, is_active, created_at
                FROM alerts 
                ORDER BY created_at DESC
            """)
            
            rows = await cursor.fetchall()
            return [self._row_to_alert(row) for row in rows]
    
    async def delete(self, alert_id: int) -> bool:
        """
        Elimina una alerta por ID.
        
        Returns:
            True si se eliminó, False si no existía
        """
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                DELETE FROM alerts WHERE id = ?
            """, (alert_id,))
            
            await conn.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Alerta {alert_id} eliminada")
            else:
                logger.warning(f"Alerta {alert_id} no encontrada para eliminar")
            
            return deleted
    
    def _row_to_alert(self, row: tuple) -> Alert:
        """
        Convierte una fila de SQLite en objeto Alert.
        
        Args:
            row: (id, search_text, target_price, is_active, created_at)
        """
        return Alert(
            id=row[0],
            search_text=row[1],
            target_price=Decimal(row[2]),  # str -> Decimal
            is_active=bool(row[3]),        # int -> bool
            created_at=datetime.fromisoformat(row[4])  # str -> datetime
        )


# Instancia global para usar en toda la app
alert_repository = AlertRepository()