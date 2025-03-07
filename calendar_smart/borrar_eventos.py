# borrar_eventos.py
import argparse
from tools.scheduler import Scheduler, get_db_connection  # Importar tu conexión real

def main():
    parser = argparse.ArgumentParser(description='Gestor de eventos')
    parser.add_argument('--force', action='store_true', help='Borrar sin confirmación')
    
    args = parser.parse_args()
    
    # 1. Obtener conexión a la base de datos
    db = get_db_connection()  # Usar tu método real de conexión
    
    # 2. Inicializar Scheduler con la conexión
    scheduler = Scheduler(db)
    
    # 3. Confirmación
    if args.force or input("¿Borrar TODOS los eventos? [s/N]: ").lower() in ['s', 'si']:
        try:
            result = scheduler.delete_all_events()
            print(f"✅ {result['mensaje']}")
        except Exception as e:
            print(f"🚨 Error: {str(e)}")
    else:
        print("❌ Operación cancelada")

if __name__ == "__main__":
    main()