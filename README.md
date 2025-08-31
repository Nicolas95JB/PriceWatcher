# 📉 PriceWatcher

Un proyecto para **monitorear precios de productos online**, con posibilidad de búsqueda, alertas y seguimiento de bajadas/subidas de precio.

---

## 🚀 Funcionalidad (casos de uso)

1. **Home**: Obtener automáticamente la sección  
   - "BAJARON DE PRECIO"  
   - "PRODUCTOS DESTACADOS"  
   (se debe poder definir cuántas páginas consultar).

2. **Búsqueda manual**:
   - Permitir al usuario buscar productos.
   - Manejar el caso de **sin resultados**.

3. **(CORE) Alertas y tracking**:
   - Definir una búsqueda que se ejecuta periódicamente (ej: cada 6h, 12h o 1 día).  
   - Se puede establecer un **presupuesto de alerta**.  
   - El sistema trackea el **precio más bajo** encontrado y notifica cuando:  
     - 🔼 el precio sube  
     - 🔽 el precio baja

**Ejemplo de alerta**:  
```text
busqueda: "monitor lg 27"
presupuesto: "400k"
lapso: "1d"
```

**Comandos a correr**
```text
pip install -r requirements.txt
python -m src.price_watcher
```

**Estructura posible al momento de integrar interfaz grafica**
```
mi_app/
├── main.py            # Punto de entrada: arranca la GUI
├── app/               # Código de la aplicación
│   ├── __init__.py
│   ├── gui/           # Todo lo relacionado a la interfaz
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── widgets.py
│   ├── controllers/   # Lógica que conecta UI y modelo
│   │   └── main_controller.py
│   ├── models/        # Representación de datos / lógica
│   │   └── vehicle_model.py
│   ├── utils/         # Funciones auxiliares
│   │   └── helpers.py
│   └── config.py      # Parámetros, rutas, constantes globales
├── tests/             # Tests unitarios (misma estructura que app/)
│   └── ...
├── requirements.txt   # Dependencias del proyecto
└── README.md
```
