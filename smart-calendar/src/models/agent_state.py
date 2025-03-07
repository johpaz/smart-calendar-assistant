from datetime import datetime
from typing import Dict, List, Optional

class AgendaDB:
    def __init__(self):
        # Inicialización con eventos predeterminados
        self.eventos = [
            {
                "nombre": "Llamada con cliente",
                "fecha": "2025-03-10",
                "hora_inicio": "13:30",
                "hora_fin": "14:30"
            },
            {
                "nombre": "Revisión de código",
                "fecha": "2025-03-10",
                "hora_inicio": "15:00",
                "hora_fin": "16:00"
            }
        ]
    
    def obtener_todos_eventos(self) -> List[Dict]:
        """Devuelve todos los eventos en la agenda."""
        return self.eventos
    
    def agregar_evento(self, evento: Dict) -> Dict:
        """Agrega un nuevo evento a la agenda."""
        self.eventos.append(evento)
        return evento
    
    def eliminar_evento(self, nombre: str, fecha: str) -> bool:
        """Elimina un evento de la agenda por nombre y fecha."""
        for i, evento in enumerate(self.eventos):
            if evento["nombre"] == nombre and evento["fecha"] == fecha:
                del self.eventos[i]
                return True
        return False
    
    def actualizar_evento(self, nombre_original: str, fecha_original: str, evento_actualizado: Dict) -> Optional[Dict]:
        """Actualiza un evento existente."""
        for i, evento in enumerate(self.eventos):
            if evento["nombre"] == nombre_original and evento["fecha"] == fecha_original:
                self.eventos[i] = evento_actualizado
                return evento_actualizado
        return None
    
    def verificar_conflicto(self, fecha: str, hora_inicio: str, hora_fin: str) -> List[Dict]:
        """Verifica si hay conflictos de horario con eventos existentes."""
        conflictos = []
        
        # Convertir horas a objetos datetime para comparación
        nuevo_inicio = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
        nuevo_fin = datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M")
        
        for evento in self.eventos:
            if evento["fecha"] == fecha:
                evento_inicio = datetime.strptime(f"{fecha} {evento['hora_inicio']}", "%Y-%m-%d %H:%M")
                evento_fin = datetime.strptime(f"{fecha} {evento['hora_fin']}", "%Y-%m-%d %H:%M")
                
                # Verificar si hay superposición
                if (nuevo_inicio < evento_fin and nuevo_fin > evento_inicio):
                    conflictos.append(evento)
        
        return conflictos