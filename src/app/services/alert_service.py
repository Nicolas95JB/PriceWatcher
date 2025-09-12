"""
AlertService - Lógica de negocio para alertas de precios.

Este service maneja:
- Crear/gestionar alertas del usuario
- Verificar alertas contra productos actuales  
- Lógica de notificaciones (futuro)
- Scheduling de chequeos automáticos (futuro GUI)

Diseñado pensando en la integración futura con:
- GUI en Flet para configuración
- Background tasks cada 3/6/12/24 horas
- Sistema de notificaciones
"""

import asyncio
from typing import List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from ..models import Alert, Product
from ..repositories import AlertRepository
from .product_service import ProductService

logger = logging.getLogger(__name__)

class AlertService:
    """
    Service para gestionar el sistema de alertas de precios.
    
    Responsabilidades actuales:
    - CRUD de alertas (crear, listar, activar/desactivar)
    - Verificar si productos disparan alertas
    - Buscar productos para alertas específicas
    
    Futuras responsabilidades (con GUI):
    - Background scheduling (3h/6h/12h/24h)
    - Push notifications
    - Histórico de alertas disparadas
    """
    
    def __init__(self, 
                 alert_repository: AlertRepository = None,
                 product_service: ProductService = None):
        """
        Args:
            alert_repository: Repository para persistir alertas
            product_service: Service para buscar productos
        """
        from ..repositories import alert_repository as default_alert_repo
        from .product_service import product_service as default_product_service
        
        self.alert_repository = alert_repository or default_alert_repo
        self.product_service = product_service or default_product_service
    
    async def create_alert(self, search_text: str, target_price: Decimal, 
                          check_interval_hours: int = 24) -> Alert:
        """
        Crea una nueva alerta de precio.
        
        Args:
            search_text: Texto a buscar (ej: "monitor lg 27")
            target_price: Precio objetivo para disparar alerta
            check_interval_hours: Cada cuántas horas verificar (3/6/12/24)
            
        Returns:
            Alert creada y guardada en BD
            
        Note: 
            check_interval_hours se guardará en BD cuando agreguemos la columna
            Por ahora solo lo logueamos para el diseño futuro
        """
        logger.info(f"Creando alerta: '{search_text}' <= ${target_price} (cada {check_interval_hours}h)")
        
        alert = Alert(
            search_text=search_text,
            target_price=target_price,
            is_active=True,
            created_at=datetime.now()
        )
        
        saved_alert = await self.alert_repository.save(alert)
        
        logger.info(f"Alerta creada con ID: {saved_alert.id}")
        return saved_alert
    
    async def get_all_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas del usuario."""
        return await self.alert_repository.get_all_alerts()
    
    async def get_active_alerts(self) -> List[Alert]:
        """Obtiene solo las alertas activas."""
        return await self.alert_repository.get_active_alerts()
    
    async def toggle_alert(self, alert_id: int) -> Optional[Alert]:
        """
        Activa/desactiva una alerta.
        
        Returns:
            Alert actualizada o None si no existe
        """
        alert = await self.alert_repository.get_by_id(alert_id)
        if not alert:
            logger.warning(f"Alerta {alert_id} no encontrada")
            return None
        
        if alert.is_active:
            alert.deactivate()
            logger.info(f"Alerta {alert_id} desactivada")
        else:
            alert.activate()
            logger.info(f"Alerta {alert_id} activada")
        
        return await self.alert_repository.save(alert)
    
    async def delete_alert(self, alert_id: int) -> bool:
        """Elimina una alerta permanentemente."""
        success = await self.alert_repository.delete(alert_id)
        if success:
            logger.info(f"Alerta {alert_id} eliminada")
        return success
    
    async def check_alert(self, alert: Alert) -> Tuple[List[Product], List[Product]]:
        """
        Verifica una alerta específica contra productos actuales.
        
        Args:
            alert: Alerta a verificar
            
        Returns:
            (productos_que_disparan_alerta, todos_los_productos_encontrados)
            
        Esta función será llamada por el background scheduler futuro.
        """
        logger.info(f"Verificando alerta: '{alert.search_text}' <= ${alert.target_price}")
        
        products = await self.product_service.search_products(alert.search_text)
        
        if not products:
            logger.info(f"No se encontraron productos para: '{alert.search_text}'")
            return [], []
        
        triggered_products = [
            product for product in products 
            if alert.is_triggered_by(product.price)
        ]
        
        logger.info(f"Encontrados {len(products)} productos, {len(triggered_products)} disparan alerta")
        
        if triggered_products:
            logger.info(f"¡ALERTA DISPARADA! Productos encontrados bajo ${alert.target_price}:")
            for product in triggered_products:
                logger.info(f"  - {product}")
        
        return triggered_products, products
    
    async def check_all_active_alerts(self) -> dict:
        """
        Verifica todas las alertas activas.
        
        Returns:
            Dict con resultados: {alert_id: (triggered_products, all_products)}
            
        Esta será la función principal del background scheduler.
        """
        active_alerts = await self.get_active_alerts()
        
        if not active_alerts:
            logger.info("No hay alertas activas para verificar")
            return {}
        
        logger.info(f"Verificando {len(active_alerts)} alertas activas...")
        
        results = {}
        for alert in active_alerts:
            try:
                triggered, all_products = await self.check_alert(alert)
                results[alert.id] = (triggered, all_products)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error verificando alerta {alert.id}: {e}")
                results[alert.id] = ([], [])
        
        total_triggered = sum(len(triggered) for triggered, _ in results.values())
        logger.info(f"Verificación completada. {total_triggered} productos disparan alertas")
        
        return results
    
    async def get_alert_summary(self) -> dict:
        """
        Obtiene un resumen del estado de las alertas.
        
        Útil para mostrar en la GUI futura.
        """
        all_alerts = await self.get_all_alerts()
        active_alerts = [a for a in all_alerts if a.is_active]
        
        return {
            "total_alerts": len(all_alerts),
            "active_alerts": len(active_alerts),
            "inactive_alerts": len(all_alerts) - len(active_alerts),
            "alerts": all_alerts
        }


alert_service = AlertService()