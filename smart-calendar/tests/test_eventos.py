import pytest
from datetime import date, time
from src.services.evento_service import EventoService
from src.models.evento import EventoCrear, ConsultaEvento
from src.repositories.evento_repository import EventoRepository

@pytest.fixture
def evento_service():
    """Fixture para crear un servicio de eventos para pruebas"""
    return EventoService()

def test_crear_evento_exitoso(evento_service):
    """Test de creación de evento"""
    evento = EventoCrear(
        nombre="Reunión Test", 
        fecha=date.today(), 
        hora_inicio=time(10, 0), 
        hora_fin=time(11, 0)
    )
    
    resultado = evento_service.crear_evento(evento)
    
    assert resultado.nombre == "Reunión Test"
    assert resultado.id is not None

def test_crear_evento_conflicto_horario(evento_service):
    """Test de conflicto de horario"""
    evento1 = EventoCrear(
        nombre="Reunión 1", 
        fecha=date.today(), 
        hora_inicio=time(10, 0), 
        hora_fin=time(11, 0)
    )
    evento2 = EventoCrear(
        nombre="Reunión 2", 
        fecha=date.today(), 
        hora_inicio=time(10, 30), 
        hora_fin=time(11, 30)
    )
    
    # Crear primer evento
    evento_service.crear_evento(evento1)
    
    # Segundo evento debería lanzar excepción
    with pytest.raises(ValueError):
        evento_service.crear_evento(evento2)

def test_obtener_eventos(evento_service):
    """Test de obtención de eventos"""
    consulta = ConsultaEvento(
        fecha_inicio=date.today(),
        fecha_fin=date.today()
    )
    
    eventos = evento_service.obtener_eventos(consulta)
    
    assert isinstance(eventos, list)

def test_eliminar_evento(evento_service):
    """Test de eliminación de evento"""
    # Crear un evento
    evento = EventoCrear(
        nombre="Evento a Eliminar", 
        fecha=date.today(), 
        hora_inicio=time(14, 0), 
        hora_fin=time(15, 0)
    )
    creado = evento_service.crear_evento(evento)
    
    # Eliminar el evento
    resultado = evento_service.eliminar_evento(creado.id)
    
    assert resultado is True