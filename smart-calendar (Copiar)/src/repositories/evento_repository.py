# src/repositories/evento_repository.py
from src.core.database import DatabaseManager
from datetime import datetime

class EventoRepository:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def insertar_evento(self, nombre, fecha, hora_inicio, hora_fin):
        """Inserta un nuevo evento en la tabla 'eventos'."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO eventos (nombre, fecha, hora_inicio, hora_fin) 
                VALUES (?, ?, ?, ?)
            ''', (nombre, fecha, hora_inicio, hora_fin))
            conn.commit()
            return cursor.lastrowid
    
    def obtener_eventos(self, fecha):
        """Obtiene eventos para una fecha específica (formato 'YYYY-MM-DD')."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nombre, hora_inicio, hora_fin 
                FROM eventos 
                WHERE fecha = ?
            ''', (fecha,))
            return [
                {
                    'id': row[0], 
                    'nombre': row[1], 
                    'hora_inicio': row[2], 
                    'hora_fin': row[3]
                } 
                for row in cursor.fetchall()
            ]
    
    def eliminar_evento(self, evento_id):
        """Elimina un evento por su ID."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM eventos WHERE id = ?', (evento_id,))
            conn.commit()
    
    def validar_conflicto_horario(self, fecha, hora_inicio, hora_fin):
        """
        Valida si existe algún conflicto de horario para la fecha dada.
        Se asume que 'hora_inicio' y 'hora_fin' están en un formato comparable (por ejemplo, "HH:MM").
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM eventos 
                WHERE fecha = ? 
                  AND (? < hora_fin AND ? > hora_inicio)
            ''', (fecha, hora_inicio, hora_fin))
            return cursor.fetchone()[0] > 0

    def obtener_evento_por_id(self, evento_id):
        """Obtiene los datos de un evento a partir de su ID."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nombre, fecha, hora_inicio, hora_fin
                FROM eventos
                WHERE id = ?
            ''', (evento_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'nombre': row[1],
                    'fecha': row[2],
                    'hora_inicio': row[3],
                    'hora_fin': row[4]
                }
            return None
