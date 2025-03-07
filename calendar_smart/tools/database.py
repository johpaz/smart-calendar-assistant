import sqlite3

class AgendaDB:
    def __init__(self, db_name="agenda.db"):
        # check_same_thread=False es útil en entornos con múltiples hilos (ej. FastAPI)
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def insert_event(self, nombre, fecha, hora_inicio, hora_fin):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO eventos (nombre, fecha, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)',
            (nombre, fecha, hora_inicio, hora_fin)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_events(self, fecha_inicio, fecha_fin=None):
        cursor = self.conn.cursor()
        if fecha_fin is None:
            fecha_fin = fecha_inicio
        cursor.execute(
            'SELECT * FROM eventos WHERE fecha BETWEEN ? AND ? ORDER BY fecha, hora_inicio',
            (fecha_inicio, fecha_fin)
        )
        return cursor.fetchall()

    def delete_event(self, id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM eventos WHERE id = ?', (id,))
        self.conn.commit()
        return cursor.rowcount

    def update_event(self, event_id, update_data):
        cursor = self.conn.cursor()
        valid_fields = ['nombre', 'fecha', 'hora_inicio', 'hora_fin']
        updates = []
        params = []
        for field in valid_fields:
            if field in update_data:
                updates.append(f"{field} = ?")
                params.append(update_data[field])
        if not updates:
            return False
        params.append(event_id)
        query = f"UPDATE eventos SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_all_events(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM eventos')
        self.conn.commit()
        return cursor.rowcount

    def get_all_events(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM eventos ORDER BY fecha, hora_inicio')
        return cursor.fetchall()

    def close(self):
        self.conn.close()

def init_db():
    db = AgendaDB()
   
    return db
