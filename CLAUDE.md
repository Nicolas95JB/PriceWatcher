# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

Install dependencies and run the application:
```bash
uv sync
uv run python -m src.app
```

## Project Architecture - Clean Architecture with Async/Await

PriceWatcher is a professional Python application for monitoring online product prices with a complete alert system. Uses modern async/await patterns and clean architecture principles.

### Architecture Overview

```
src/app/
├── models/              # Data models with business logic
├── parsers/             # HTML parsing specific to each site
├── services/            # Business logic and orchestration
├── repositories/        # Data access layer (SQLite)
├── database.py          # Code-First database migrations
├── core.py             # CLI interface
└── config.py           # Configuration constants
```

### Key Architectural Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Code-First Database**: Python models define SQLite schema automatically  
3. **Repository Pattern**: Data access is abstracted from business logic
4. **Async/Await**: All I/O operations are non-blocking
5. **Type Hints**: Complete type safety throughout codebase

### Core Components

#### **Models Layer** (`models/`)
- `Product` - Product data with price formatting and search matching
- `Alert` - Alert data with triggering logic and state management
- Uses `Decimal` for precise price handling
- Includes validation in `__post_init__` methods
- Business methods: `display_price()`, `is_triggered_by()`, etc.

#### **Parsers Layer** (`parsers/`)
- `HardGamersParser` - Converts HardGamers HTML to Product objects
- Handles complex Argentine price formats: "$19.999,50", "$ 19999"
- Robust error handling for individual product parsing failures
- Extensible design for additional e-commerce sites

#### **Services Layer** (`services/`)
- `ProductService` - Web scraping with aiohttp, retry logic, error handling
- `AlertService` - Complete alert lifecycle management, verification logic
- Async/await throughout with proper error handling
- Exponential backoff for failed requests
- Designed for future background scheduling integration

#### **Repositories Layer** (`repositories/`)
- `ProductRepository` - CRUD operations for products (historical data)
- `AlertRepository` - CRUD operations for alerts with automatic conversions
- Handles Python object ↔ SQLite conversions automatically
- Type-safe conversion: `Decimal` ↔ `str`, `datetime` ↔ `ISO string`

#### **Database System** (`database.py`)
- **Code-First migrations**: Python dataclasses → SQLite tables automatically
- Type mapping: `str`→`TEXT`, `int`→`INTEGER`, `Decimal`→`TEXT`, etc.
- `Optional[Type]` handling for nullable columns
- Automatic `PRIMARY KEY AUTOINCREMENT` for `id` fields
- Migration command: `await db.migrate(Product, Alert)`

#### **CLI Interface** (`core.py`)
- Complete interactive menu system
- Features:
  1. Browse featured products
  2. Search products with alert creation
  3. Full alert management (CRUD)
  4. Manual alert verification
- Intelligent price suggestions based on search results
- Error handling with user-friendly messages

### Current Functionality

**Implemented Features:**
1. **Product Discovery**: Featured products and manual search
2. **Alert System**: Create, manage, verify price alerts
3. **Database Persistence**: SQLite with automatic migrations
4. **Price Intelligence**: Parsing complex price formats, suggestions
5. **Interactive CLI**: Complete user interface with menus

**Technical Features:**
- Async HTTP requests with aiohttp
- SQLite async operations with aiosqlite  
- Code-First database with automatic schema generation
- Type-safe codebase with comprehensive type hints
- Robust error handling and logging
- Clean architecture enabling easy GUI integration

### Future Development Notes

The architecture is designed for easy extension:
- **GUI Integration**: Services are UI-agnostic, ready for Flet integration
- **Background Scheduling**: AlertService designed for periodic verification
- **Multi-Site Support**: Parser architecture supports additional sites
- **Notification System**: Hooks prepared in AlertService for push notifications

### Dependencies

```toml
[dependencies]
requests = "*"           # Legacy HTTP support
beautifulsoup4 = "*"    # HTML parsing
lxml = "*"              # XML/HTML parser backend
aiohttp = "*"           # Async HTTP client
aiosqlite = "*"         # Async SQLite operations
```

### Testing the Application

The application includes:
- Automatic database initialization
- Comprehensive error handling
- Interactive CLI for all features
- Real-time price parsing and alert verification
- Data persistence across sessions

### Development Patterns

When extending the application:
1. **Models**: Add new dataclasses with `__post_init__` validation
2. **Parsers**: Create site-specific parsers inheriting common patterns
3. **Services**: Use async/await, implement proper error handling
4. **Repositories**: Follow the established conversion patterns
5. **Database**: Use Code-First approach, let migrations handle schema

The codebase follows modern Python practices and is ready for production use or GUI integration.