"""
Alert model - Alertas de precios configuradas por el usuario.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

@dataclass
class Alert:
    """
    Representa una alerta de precio que el usuario configuró.
    
    Attributes:
        search_text: Texto de búsqueda (ej: "monitor lg 27")
        target_price: Precio objetivo para la alerta
        is_active: Si la alerta está activa o pausada
        created_at: Cuándo se creó la alerta
        id: ID único (opcional, lo asigna la base de datos)
    """
    search_text: str
    target_price: Decimal
    is_active: bool = True
    created_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones y valores por defecto"""
        if not self.search_text.strip():
            raise ValueError("El texto de búsqueda no puede estar vacío")
        if self.target_price <= 0:
            raise ValueError("El precio objetivo debe ser mayor a 0")
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def is_triggered_by(self, product_price: Decimal) -> bool:
        """
        Verifica si esta alerta debería dispararse con el precio dado.
        
        Returns:
            True si el precio es <= al precio objetivo
        """
        return product_price <= self.target_price
    
    def activate(self):
        """Activa la alerta"""
        self.is_active = True
    
    def deactivate(self):
        """Desactiva la alerta"""
        self.is_active = False