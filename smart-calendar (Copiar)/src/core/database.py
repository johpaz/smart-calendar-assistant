import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'agenda.db')
        self.db_path = db_path
        
    def cargar_datos_iniciales(self):
        with open('data/initial_data.sql', 'r') as f:
            sql_script = f.read()
        
        with self.get_connection() as conn:
            conn.executescript(sql_script)
        conn.commit()
    @contextmanager
    def get_connection(self):
        """Gestiona la conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
            
    
    def init_db(self):
        """Inicializa la base de datos con el esquema inicial"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    hora_inicio TEXT NOT NULL,
                    hora_fin TEXT NOT NULL
                )
            ''')
            conn.commit()