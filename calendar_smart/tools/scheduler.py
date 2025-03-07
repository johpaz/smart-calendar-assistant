from datetime import datetime, timedelta
import re

class Scheduler:
    def __init__(self, db):
        self.db = db

    def time_to_minutes(self, time_str):
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def check_conflict(self, fecha, hora_inicio, hora_fin, exclude_id=None):
        events = self.db.get_events(fecha, fecha)
        new_start = self.time_to_minutes(hora_inicio)
        new_end = self.time_to_minutes(hora_fin)
        for event in events:
            event_id, _, start, end = event
            if exclude_id and event_id == exclude_id:
                continue
            event_start = self.time_to_minutes(start)
            event_end = self.time_to_minutes(end)
            if not (new_end <= event_start or new_start >= event_end):
                return True
        return False

    def schedule_meeting(self, solicitud):
        nombre = solicitud["nombre"]
        fecha = solicitud["fecha"]
        hora_inicio = solicitud["hora_inicio"]
        hora_fin = solicitud["hora_fin"]
        if self.check_conflict(fecha, hora_inicio, hora_fin):
            return {"status": "conflict", "mensaje": "Conflicto de horario detectado."}
        event_id = self.db.insert_event(nombre, fecha, hora_inicio, hora_fin)
        return {
            "status": "success",
            "mensaje": "Reunión agendada con éxito.",
            "evento": {
                "id": event_id,
                "nombre": nombre,
                "fecha": fecha,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin
            }
        }

    def delete_event(self, event_id):
        try:
            success = self.db.delete_event(event_id)
            if success:
                return {"status": "success", "mensaje": f"Evento {event_id} eliminado correctamente"}
            return {"status": "error", "mensaje": f"No se encontró el evento {event_id}"}
        except Exception as e:
            return {"status": "error", "mensaje": f"Error al eliminar: {str(e)}"}

    def update_event(self, event_id, new_data):
        try:
            updated = self.db.update_event(event_id, new_data)
            if updated:
                return {"status": "success", "mensaje": "Evento actualizado correctamente"}
            return {"status": "error", "mensaje": "No se encontró el evento"}
        except Exception as e:
            return {"status": "error", "mensaje": f"Error al actualizar: {str(e)}"}

    def get_agenda(self, fecha_inicio, fecha_fin=None):
        events = self.db.get_events(fecha_inicio, fecha_fin)
        if not events:
            return {"status": "info", "mensaje": f"No hay eventos programados entre {fecha_inicio} y {fecha_fin or fecha_inicio}."}
        return {
            "status": "success",
            "mensaje": f"Eventos entre {fecha_inicio} y {fecha_fin or fecha_inicio}:",
            "eventos": [
                {"id": e[0], "nombre": e[1], "fecha": e[2], "hora_inicio": e[3], "hora_fin": e[4]}
                for e in events
            ]
        }

    def delete_all_events(self):
        try:
            deleted_count = self.db.delete_all_events()
            if deleted_count > 0:
                return {"status": "success", "mensaje": f"✅ Se eliminaron {deleted_count} eventos correctamente"}
            return {"status": "info", "mensaje": "ℹ️ No había eventos para eliminar"}
        except Exception as e:
            return {"status": "error", "mensaje": f"🔴 Error crítico: {str(e)}"}

    def get_all_events_formatted(self):
        events = self.db.get_all_events()
        return {
            "eventos": [
                {"id": event[0], "nombre": event[1], "fecha": event[2], "hora_inicio": event[3], "hora_fin": event[4]}
                for event in events
            ]
        }

    def get_all_events(self):
        events = self.db.get_events("2000-01-01", "2100-01-01")
        return {
            "eventos": [
                {"id": e[0], "nombre": e[1], "fecha": e[2], "hora_inicio": e[3], "hora_fin": e[4]}
                for e in events
            ]
        }
        
    def schedule_meeting(self, solicitud):
        nombre = solicitud["nombre"]
        fecha = solicitud["fecha"]
        hora_inicio = solicitud["hora_inicio"]
        hora_fin = solicitud["hora_fin"]
        
        # Validar si existe conflicto en ese mismo horario
        if self.check_conflict(fecha, hora_inicio, hora_fin):
            return {"status": "conflict", "mensaje": "Tienes un evento en ese mismo horario"}
        
        # Si no hay conflicto, se agenda el evento
        event_id = self.db.insert_event(nombre, fecha, hora_inicio, hora_fin)
        return {
            "status": "success",
            "mensaje": "Reunión agendada con éxito.",
            "evento": {
                "id": event_id,
                "nombre": nombre,
                "fecha": fecha,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin
            }
        }

