# src/services/evento_service.py
from typing import List, Optional
from datetime import date, datetime, timedelta

from src.repositories.evento_repository import EventoRepository
from src.models.evento import EventoCrear, EventoRespuesta, EventoActualizar, ConsultaEvento

class EventoService:
    """Servicio de gestión de eventos"""
    
    def __init__(self, repository: Optional[EventoRepository] = None):
        """
        Inicializa el servicio con un repositorio de eventos.
        """
        self.repository = repository or EventoRepository()
    
    def crear_evento(self, evento: EventoCrear) -> EventoRespuesta:
        """
        Crea un nuevo evento.
        """
        # Validar conflictos de horario
        if self.repository.validar_conflicto_horario(
            str(evento.fecha), 
            str(evento.hora_inicio), 
            str(evento.hora_fin)
        ):
            raise ValueError("Existe un conflicto de horario con otro evento")
        
        # Insertar evento
        evento_id = self.repository.insertar_evento(
            nombre=evento.nombre,
            fecha=str(evento.fecha),
            hora_inicio=str(evento.hora_inicio),
            hora_fin=str(evento.hora_fin)
        )
        
        # Retornar evento con ID
        return EventoRespuesta(
            id=evento_id,
            **evento.dict()
        )
    
    def obtener_eventos(self, consulta: ConsultaEvento) -> List[EventoRespuesta]:
        """
        Obtiene eventos según criterios de búsqueda.
        """
        eventos = []
        
        if consulta.fecha_inicio and consulta.fecha_fin:
            # Buscar eventos en un rango de fechas
            for single_date in self._date_range(consulta.fecha_inicio, consulta.fecha_fin):
                eventos.extend(
                    self.repository.obtener_eventos(str(single_date))
                )
        elif consulta.fecha_inicio:
            # Buscar eventos a partir de una fecha
            eventos = self.repository.obtener_eventos(str(consulta.fecha_inicio))
        
        # Filtrar por nombre si se proporciona
        if consulta.nombre:
            eventos = [
                evento for evento in eventos 
                if consulta.nombre.lower() in evento['nombre'].lower()
            ]
        
        return [
            EventoRespuesta(
                id=evento['id'],
                nombre=evento['nombre'],
                fecha=datetime.strptime(evento['fecha'], "%Y-%m-%d").date(),
                hora_inicio=datetime.strptime(evento['hora_inicio'], "%H:%M").time(),
                hora_fin=datetime.strptime(evento['hora_fin'], "%H:%M").time()
            ) for evento in eventos
        ]
    
    def actualizar_evento(self, evento_id: int, evento: EventoActualizar) -> EventoRespuesta:
        """
        Actualiza un evento existente.
        """
        # Lógica de actualización pendiente (implementar según requerimientos)
        pass
    
    def eliminar_evento(self, evento_id: int) -> bool:
        """
        Elimina un evento.
        """
        self.repository.eliminar_evento(evento_id)
        return True
    
    def _date_range(self, start_date: date, end_date: date):
        """
        Genera un rango de fechas.
        """
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)
            
    def actualizar_evento(self, evento_id: int, evento: EventoActualizar) -> EventoRespuesta:
        """
        Actualiza un evento existente.

        :param evento_id: ID del evento a actualizar.
        :param evento: Datos para actualizar (EventoActualizar)
        :return: Evento actualizado.
        :raises ValueError: Si el evento no existe o la actualización falla.
        """
        # Intentar actualizar el evento en el repositorio
        actualizado = self.repository.actualizar_evento(
            evento_id,
            nombre=evento.nombre,
            fecha=str(evento.fecha) if evento.fecha else None,
            hora_inicio=str(evento.hora_inicio) if evento.hora_inicio else None,
            hora_fin=str(evento.hora_fin) if evento.hora_fin else None
        )
        if not actualizado:
            raise ValueError("El evento no existe o no se pudo actualizar")
        
        # Obtener el evento actualizado (se asume que existe el método obtener_evento_por_id)
        evento_actualizado = self.repository.obtener_evento_por_id(evento_id)
        if not evento_actualizado:
            raise ValueError("Error al obtener el evento actualizado")
        
        # Convertir el resultado a EventoRespuesta
        return EventoRespuesta(
            id=evento_actualizado['id'],
            nombre=evento_actualizado['nombre'],
            fecha=datetime.strptime(evento_actualizado['fecha'], "%Y-%m-%d").date(),
            hora_inicio=datetime.strptime(evento_actualizado['hora_inicio'], "%H:%M").time(),
            hora_fin=datetime.strptime(evento_actualizado['hora_fin'], "%H:%M").time()
        )

