from fastapi import APIRouter, HTTPException, Query
from src.services.evento_service import EventoService
from src.models.evento import EventoSolicitud, EventoActualizar

router = APIRouter(
    prefix="/events",
    tags=["Eventos"]
)

evento_service = EventoService()

@router.get("/", summary="Listar eventos")
async def list_events(fecha: str = Query(None, description="Filtrar por fecha (YYYY-MM-DD)")):
    """
    Endpoint para obtener la lista de eventos.
    Si se proporciona una fecha, filtra los eventos de esa fecha.
    """
    try:
        if fecha:
            # Se usa el método 'obtener_eventos' para filtrar por fecha
            eventos = evento_service.obtener_eventos({"fecha_inicio": fecha, "fecha_fin": fecha})
        else:
            # Asumimos que existe un método 'listar_eventos' para devolver todos los eventos.
            eventos = evento_service.listar_eventos()
        return {"eventos": eventos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", summary="Agendar un evento")
async def create_event(evento_solicitud: EventoSolicitud):
    """
    Endpoint para agendar un nuevo evento.

    La solicitud debe tener el siguiente formato:
    {
      "solicitud": "agendar",
      "nombre": "Reunión de equipo",
      "fecha": "2025-03-10",
      "hora_inicio": "14:00",
      "hora_fin": "15:00"
    }
    """
    if evento_solicitud.solicitud.lower() != "agendar":
        raise HTTPException(status_code=400, detail="Tipo de solicitud no soportado. Debe ser 'agendar'.")
    try:
        # Excluir el campo 'solicitud' y convertir el resto a datos para crear el evento.
        evento_crear_data = evento_solicitud.dict(exclude={"solicitud"})
        resultado = evento_service.crear_evento(evento_crear_data)
        return {
            "status": "success",
            "mensaje": "Reunión agendada con éxito.",
            "evento": {
                "nombre": resultado.nombre,
                "fecha": resultado.fecha.isoformat(),
                "hora_inicio": resultado.hora_inicio.strftime("%H:%M"),
                "hora_fin": resultado.hora_fin.strftime("%H:%M")
            }
        }
    except ValueError as ve:
        return {"status": "error", "mensaje": str(ve)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{evento_id}", summary="Modificar un evento")
async def update_event(evento_id: int, evento_actualizar: EventoActualizar):
    """
    Endpoint para modificar un evento existente.
    """
    try:
        resultado = evento_service.actualizar_evento(evento_id, evento_actualizar)
        return {
            "status": "success",
            "mensaje": "Evento actualizado con éxito.",
            "evento": {
                "nombre": resultado.nombre,
                "fecha": resultado.fecha.isoformat(),
                "hora_inicio": resultado.hora_inicio.strftime("%H:%M"),
                "hora_fin": resultado.hora_fin.strftime("%H:%M")
            }
        }
    except ValueError as ve:
        return {"status": "error", "mensaje": str(ve)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{evento_id}", summary="Eliminar un evento")
async def delete_event(evento_id: int):
    """
    Endpoint para eliminar un evento.
    """
    try:
        resultado = evento_service.eliminar_evento(evento_id)
        if resultado:
            return {"status": "success", "mensaje": "Evento eliminado con éxito."}
        else:
            return {"status": "error", "mensaje": "No se pudo eliminar el evento."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
