"""
Core - Interfaz de línea de comandos de PriceWatcher.

Esta es la capa de presentación que interactúa con el usuario.
Usa los services para la lógica de negocio y mantiene separadas
las responsabilidades.

Diseñado para ser reemplazado por GUI (Flet) en el futuro,
manteniendo los services intactos.
"""

from decimal import Decimal
from typing import List
import logging

from .models import Product, Alert
from .services import ProductService, AlertService
from .database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceWatcherCLI:
    """
    Interfaz de línea de comandos para PriceWatcher.
    
    Responsabilidades:
    - Mostrar menús y opciones al usuario
    - Capturar input del usuario  
    - Formatear y mostrar resultados
    - Coordinar con services para funcionalidad
    
    NO hace:
    - Lógica de negocio (eso es del service)
    - Acceso a datos (eso es del repository)  
    - Parsing HTML (eso es del parser)
    """
    
    def __init__(self):
        self.product_service = ProductService()
        self.alert_service = AlertService()
    
    async def run(self):
        """Punto de entrada principal de la aplicación CLI."""
        print("=== PriceWatcher - Monitor de Precios ===\n")
        
        await self._initialize_database()
        
        while True:
            try:
                self._show_main_menu()
                choice = input("\nSeleccione una opción: ").strip()
                
                if choice == "1":
                    await self._show_featured_products()
                elif choice == "2": 
                    await self._search_products()
                elif choice == "3":
                    await self._manage_alerts()
                elif choice == "4":
                    await self._check_alerts()
                elif choice == "0":
                    print("Hasta luego!")
                    break
                else:
                    print("Opción inválida. Intente nuevamente.")
                    
                input("\nPresione Enter para continuar...")
                print("\n" + "="*50 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nSaliendo...")
                break
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
                print(f"Error: {e}")
    
    async def _initialize_database(self):
        """Inicializa la base de datos con las tablas necesarias."""
        try:
            await db.migrate(Product, Alert)
            logger.info("Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"Error inicializando BD: {e}")
            print(f"Advertencia: Error de BD: {e}")
    
    def _show_main_menu(self):
        """Muestra el menú principal."""
        print("MENU PRINCIPAL:")
        print("1. Ver productos destacados/en oferta")
        print("2. Buscar productos")
        print("3. Gestionar alertas de precio")
        print("4. Verificar alertas activas")
        print("0. Salir")
    
    async def _show_featured_products(self):
        """Muestra productos destacados de HardGamers."""
        print("\n>> Obteniendo productos destacados...")
        
        try:
            products = await self.product_service.get_featured_products()
            
            if not products:
                print("No se encontraron productos destacados.")
                return
            
            print(f"\n=== PRODUCTOS DESTACADOS ({len(products)}) ===")
            self._display_products(products)
            
        except Exception as e:
            logger.error(f"Error obteniendo productos destacados: {e}")
            print(f"Error: {e}")
    
    async def _search_products(self):
        """Maneja la búsqueda de productos."""
        search_text = input("\nIngrese el producto a buscar: ").strip()
        
        if not search_text:
            print("Texto de búsqueda vacío.")
            return
        
        print(f"\n>> Buscando '{search_text}'...")
        
        try:
            products = await self.product_service.search_products(search_text)
            
            if not products:
                print(f"No se encontraron productos para '{search_text}'.")
                return
            
            print(f"\n=== RESULTADOS PARA '{search_text}' ({len(products)}) ===")
            self._display_products(products)
            
            if self._ask_yes_no(f"\n¿Crear alerta para '{search_text}'?"):
                await self._create_alert_for_search(search_text, products)
                
        except Exception as e:
            logger.error(f"Error buscando productos: {e}")
            print(f"Error: {e}")
    
    def _display_products(self, products: List[Product]):
        """Formatea y muestra una lista de productos."""
        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.title}")
            print(f"   Precio: {product.display_price()}")  
            print(f"   Tienda: {product.shop}")
            if product.url:
                print(f"   URL: {product.url}")
    
    async def _manage_alerts(self):
        """Menú de gestión de alertas."""
        while True:
            print("\n=== GESTIÓN DE ALERTAS ===")
            print("1. Crear nueva alerta")
            print("2. Ver mis alertas")
            print("3. Activar/desactivar alerta")
            print("4. Eliminar alerta")
            print("0. Volver al menú principal")
            
            choice = input("\nSeleccione una opción: ").strip()
            
            if choice == "1":
                await self._create_alert()
            elif choice == "2":
                await self._list_alerts()
            elif choice == "3":
                await self._toggle_alert()
            elif choice == "4":
                await self._delete_alert()
            elif choice == "0":
                break
            else:
                print("Opción inválida.")
    
    async def _create_alert(self):
        """Crea una nueva alerta."""
        search_text = input("\nTexto a buscar: ").strip()
        if not search_text:
            print("Texto vacío, cancelando.")
            return
        
        try:
            price_input = input("Precio objetivo (ej: 45000.50): ").strip()
            target_price = Decimal(price_input)
            
            alert = await self.alert_service.create_alert(search_text, target_price)
            print(f"\n✓ Alerta creada con ID: {alert.id}")
            print(f"Buscaremos '{search_text}' y te notificaremos si encuentra productos <= ${target_price}")
            
        except (ValueError, Exception) as e:
            print(f"Error creando alerta: {e}")
    
    async def _create_alert_for_search(self, search_text: str, products: List[Product]):
        """Crea alerta basada en productos encontrados."""
        if not products:
            return
        
        min_price = min(p.price for p in products)
        suggested_price = min_price * Decimal("0.9")
        
        print(f"\nPrecio más bajo encontrado: ${min_price}")
        price_input = input(f"Precio objetivo (sugerido ${suggested_price}): ").strip()
        
        if not price_input:
            target_price = suggested_price
        else:
            try:
                target_price = Decimal(price_input)
            except ValueError:
                print("Precio inválido, usando sugerido.")
                target_price = suggested_price
        
        try:
            alert = await self.alert_service.create_alert(search_text, target_price)
            print(f"\n✓ Alerta creada con ID: {alert.id}")
        except Exception as e:
            print(f"Error creando alerta: {e}")
    
    async def _list_alerts(self):
        """Lista todas las alertas del usuario."""
        try:
            alerts = await self.alert_service.get_all_alerts()
            
            if not alerts:
                print("\nNo tienes alertas configuradas.")
                return
            
            print(f"\n=== TUS ALERTAS ({len(alerts)}) ===")
            for alert in alerts:
                status = "[ACTIVA]" if alert.is_active else "[INACTIVA]"
                print(f"\nID: {alert.id} {status}")
                print(f"Búsqueda: '{alert.search_text}'")
                print(f"Precio objetivo: {alert.target_price}")
                print(f"Creada: {alert.created_at.strftime('%Y-%m-%d %H:%M')}")
                
        except Exception as e:
            print(f"Error listando alertas: {e}")
    
    async def _toggle_alert(self):
        """Activa/desactiva una alerta."""
        await self._list_alerts()
        
        try:
            alert_id = int(input("\nID de alerta a cambiar: ").strip())
            alert = await self.alert_service.toggle_alert(alert_id)
            
            if alert:
                status = "activada" if alert.is_active else "desactivada"
                print(f"\n✓ Alerta {alert_id} {status}")
            else:
                print("Alerta no encontrada.")
                
        except (ValueError, Exception) as e:
            print(f"Error: {e}")
    
    async def _delete_alert(self):
        """Elimina una alerta."""
        await self._list_alerts()
        
        try:
            alert_id = int(input("\nID de alerta a eliminar: ").strip())
            
            if self._ask_yes_no("¿Confirma eliminación?"):
                success = await self.alert_service.delete_alert(alert_id)
                if success:
                    print(f"\n✓ Alerta {alert_id} eliminada")
                else:
                    print("Alerta no encontrada.")
            else:
                print("Cancelado.")
                
        except (ValueError, Exception) as e:
            print(f"Error: {e}")
    
    async def _check_alerts(self):
        """Verifica todas las alertas activas manualmente."""
        print("\n>> Verificando alertas activas...")
        
        try:
            results = await self.alert_service.check_all_active_alerts()
            
            if not results:
                print("No hay alertas activas para verificar.")
                return
            
            total_triggered = 0
            for alert_id, (triggered, all_products) in results.items():
                total_triggered += len(triggered)
                
                if triggered:
                    print(f"\n*** ALERTA {alert_id} DISPARADA ***")
                    self._display_products(triggered)
            
            if total_triggered == 0:
                print("\nNinguna alerta se disparó. Los precios aún están altos.")
            else:
                print(f"\n✓ {total_triggered} productos dispararon alertas!")
                
        except Exception as e:
            logger.error(f"Error verificando alertas: {e}")
            print(f"Error: {e}")
    
    def _ask_yes_no(self, question: str) -> bool:
        """Pregunta sí/no al usuario."""
        while True:
            answer = input(f"{question} (s/n): ").strip().lower()
            if answer in ['s', 'si', 'y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            else:
                print("Responda 's' o 'n'")


async def app():
    """
    Punto de entrada principal de la aplicación.
    
    Esta función reemplaza la anterior app() pero usando
    toda la nueva arquitectura refactorizada.
    """
    cli = PriceWatcherCLI()
    await cli.run()
