# 📉 PriceWatcher

Sistema de **monitoreo de precios automatizado** con alertas inteligentes. Rastrea productos de HardGamers.com.ar y te notifica cuando los precios bajan según tus criterios.

---

## ✨ Funcionalidades Actuales

### 🔍 **Búsqueda de Productos**
- Consulta automática de productos destacados/en oferta
- Búsqueda manual por texto libre
- Parsing robusto de precios argentinos complejos
- Manejo de múltiples formatos: "$19.999,50", "$ 19999"

### 🚨 **Sistema de Alertas Avanzado**
- **Crear alertas** con precio objetivo personalizado
- **Gestión completa**: activar, desactivar, eliminar alertas  
- **Verificación manual** de todas las alertas activas
- **Sugerencias inteligentes** basadas en precios encontrados
- **Persistencia** en base de datos SQLite

### 💾 **Base de Datos Code-First**
- Models Python definen automáticamente la estructura BD
- Migración automática: `Product` y `Alert` → tablas SQLite
- Manejo preciso de precios con `Decimal`
- Conversiones automáticas Python ↔ SQLite

---

## 🚀 Instalación y Uso

### **Requisitos**
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager

### **Instalación**
```bash
# Clonar repositorio
git clone <repo-url>
cd PriceWatcher

# Instalar dependencias
uv sync

# Ejecutar aplicación
uv run python -m src.app
```

### **Uso**
La aplicación presenta un menú interactivo:

1. **Ver productos destacados** - Ofertas actuales de HardGamers
2. **Buscar productos** - Búsqueda por texto + opción de crear alerta
3. **Gestionar alertas** - CRUD completo de tus alertas
4. **Verificar alertas** - Chequeo manual de todas las alertas activas

---

## 🏗️ Arquitectura

### **Clean Architecture con Separación de Responsabilidades**

```
src/app/
├── models/              # 📊 Datos y validaciones
│   ├── product.py       # Modelo Product con métodos de negocio
│   └── alert.py         # Modelo Alert con lógica de alertas
├── parsers/             # 🔧 Conversión HTML → objetos Python
│   └── hardgamers_parser.py  # Parser específico para HardGamers
├── services/            # 🎯 Lógica de negocio
│   ├── product_service.py    # Búsqueda y obtención de productos
│   └── alert_service.py      # Gestión y verificación de alertas
├── repositories/        # 💾 Acceso a datos
│   ├── product_repository.py # CRUD productos
│   └── alert_repository.py   # CRUD alertas + conversiones
├── database.py          # 🗄️ Sistema Code-First + migraciones
├── core.py             # 🖥️ Interfaz CLI interactiva
└── config.py           # ⚙️ URLs y configuración
```

### **Principios Aplicados**
- **Single Responsibility**: Cada módulo tiene una responsabilidad clara
- **Repository Pattern**: Abstrae el acceso a datos
- **Code-First Database**: Models definen la estructura BD
- **Async/Await**: I/O no bloqueante con aiohttp + aiosqlite
- **Type Hints**: Código autodocumentado y menos propenso a errores

---

## 🔮 Roadmap Futuro

### **🎨 GUI con Flet** (Próximo)
- Interfaz gráfica moderna
- Dashboard de alertas en tiempo real
- Configuración visual de intervalos (3h/6h/12h/24h)

### **⏰ Background Scheduler** 
- Verificación automática de alertas
- Notificaciones push/email
- Histórico de alertas disparadas

### **🌐 Múltiples Sitios**
- CompraGamer, MercadoLibre parsers
- Comparación de precios entre sitios
- Alertas cross-platform

### **📊 Analytics**
- Histórico de precios
- Tendencias y gráficos  
- Predicción de mejores momentos para comprar

---

## 🛠️ Dependencias

```toml
[dependencies]
requests       # HTTP básico (legacy support)
beautifulsoup4 # HTML parsing
lxml          # Parser XML/HTML rápido  
aiohttp       # HTTP requests async
aiosqlite     # SQLite async
```

---

## 📚 Documentación Adicional

- **[CLAUDE.md](CLAUDE.md)** - Guía para Claude Code sobre la arquitectura

---

## 🤝 Contribución

Este proyecto está diseñado como herramienta de aprendizaje. La arquitectura modular permite agregar fácilmente:

- Nuevos parsers para otros sitios web
- Diferentes tipos de alertas  
- Nuevas interfaces (GUI, web, API)
- Sistemas de notificación

---

*PriceWatcher v2.0 - Arquitectura profesional para monitoreo inteligente de precios* 🚀
