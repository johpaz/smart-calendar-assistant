from typing import Optional
from datetime import date, time
from pydantic import BaseModel, Field, validator

class EventoBase(BaseModel):
    """Modelo base para eventos"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del evento")
    fecha: date = Field(..., description="Fecha del evento")
    hora_inicio: time = Field(..., description="Hora de inicio del evento")
    hora_fin: time = Field(..., description="Hora de fin del evento")

    @validator('hora_fin')
    def validar_hora_fin(cls, hora_fin, values):
        """Validar que la hora de fin sea posterior a la hora de inicio"""
        if 'hora_inicio' in values and hora_fin <= values['hora_inicio']:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return hora_fin

class EventoCrear(EventoBase):
    """Modelo para crear un nuevo evento"""
    pass

class EventoRespuesta(EventoBase):
    """Modelo para respuesta de evento, incluye ID"""
    id: int

class EventoActualizar(BaseModel):
    """Modelo para actualizar un evento existente"""
    nombre: Optional[str] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None

class ConsultaEvento(BaseModel):
    """Modelo para consultas de eventos"""
    nombre: Optional[str] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None


# Nuevo modelo para solicitudes de agendamiento
class EventoSolicitud(EventoBase):
    """Modelo para solicitudes de agendamiento, incluye el campo 'solicitud'."""
    solicitud: str = Field(..., description="Tipo de solicitud. Debe ser 'agendar'.")
