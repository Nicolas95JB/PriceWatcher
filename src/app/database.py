"""
Sistema Code-First para SQLite con aiosqlite.
Genera automáticamente las tablas basándose en los modelos Python.
"""

import aiosqlite
import dataclasses
from typing import Type, get_type_hints, get_origin, get_args
from decimal import Decimal
from datetime import datetime
import logging

# Configurar logging para ver lo que hace
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestiona la conexión a SQLite y las migraciones automáticas.
    
    Code-First significa:
    1. Defines tus modelos Python (Product, Alert)
    2. Este manager genera las tablas SQL automáticamente
    3. Si cambias los modelos, actualiza la BD automáticamente
    """
    
    def __init__(self, db_path: str = "pricewatcher.db"):
        self.db_path = db_path
    
    async def connect(self) -> aiosqlite.Connection:
        """Conecta a SQLite de forma asíncrona"""
        return await aiosqlite.connect(self.db_path)
    
    def _get_sql_type(self, python_type) -> str:
        """
        Convierte tipos Python a tipos SQLite.
        
        Esta es la magia del Code-First:
        str -> TEXT
        int -> INTEGER  
        Decimal -> TEXT (por precisión)
        datetime -> TEXT (formato ISO)
        """
        # Manejar Optional[tipo] -> tipo
        origin = get_origin(python_type)
        if origin is not None:
            # Es un tipo genérico como Optional[int] o Union[int, None]
            args = get_args(python_type)
            if len(args) == 2 and type(None) in args:
                # Es Optional[SomeType] = Union[SomeType, None]
                python_type = next(arg for arg in args if arg is not type(None))
        
        # Mapeo de tipos Python -> SQLite
        type_mapping = {
            str: "TEXT",
            int: "INTEGER", 
            float: "REAL",
            bool: "INTEGER",  # SQLite no tiene BOOLEAN
            Decimal: "TEXT",  # Guardamos como string para precisión
            datetime: "TEXT"  # ISO format: "2024-01-01 12:30:00"
        }
        
        result = type_mapping.get(python_type, "TEXT")
        logger.info(f"Tipo Python {python_type} -> SQL {result}")
        return result
    
    def _generate_create_table_sql(self, model_class: Type) -> str:
        """
        Genera SQL CREATE TABLE desde una dataclass.
        
        Ejemplo:
        @dataclass
        class Product:
            title: str
            price: Decimal
            id: Optional[int] = None
            
        Genera:
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT NOT NULL
        );
        """
        
        if not dataclasses.is_dataclass(model_class):
            raise ValueError(f"{model_class} no es una dataclass")
        
        table_name = model_class.__name__.lower() + "s"  # Product -> products
        fields = dataclasses.fields(model_class)
        type_hints = get_type_hints(model_class)
        
        columns = []
        
        for field in fields:
            column_name = field.name
            python_type = type_hints[field.name]
            sql_type = self._get_sql_type(python_type)
            
            # Construir definición de columna
            column_def = f"{column_name} {sql_type}"
            
            # PRIMARY KEY para 'id'
            if column_name == "id":
                column_def += " PRIMARY KEY AUTOINCREMENT"
            else:
                # NOT NULL si no tiene default value y no es Optional
                if field.default == dataclasses.MISSING and field.default_factory == dataclasses.MISSING:
                    if not (get_origin(python_type) is type(None) or str(python_type).startswith('typing.Union')):
                        column_def += " NOT NULL"
            
            columns.append(column_def)
        
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {','.join(columns)}
        );
        """.strip()
        
        logger.info(f"SQL generado para {model_class.__name__}: {sql}")
        return sql
    
    async def migrate(self, *model_classes):
        """
        Crea/actualiza las tablas basándose en los modelos.
        
        Uso:
        await db.migrate(Product, Alert)
        """
        async with aiosqlite.connect(self.db_path) as conn:
            for model_class in model_classes:
                sql = self._generate_create_table_sql(model_class)
                await conn.execute(sql)
            
            await conn.commit()
            logger.info(f"Migración completada para {len(model_classes)} modelos")


# Instancia global para usar en toda la app
db = DatabaseManager()