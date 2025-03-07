import json
from typing import Optional
from langchain_core.tools import tool
from src.models.agent_state import AgendaDB

# Instancia de la base de datos
db = AgendaDB()

@tool
def agendar_reunion(nombre: str, fecha: str, hora_inicio: str, hora_fin: str) -> str:
    """
    Agenda una nueva reunión verificando conflictos.
    
    Args:
        nombre: Nombre de la reunión
        fecha: Fecha en formato YYYY-MM-DD
        hora_inicio: Hora de inicio en formato HH:MM
        hora_fin: Hora de fin en formato HH:MM
    
    Returns:
        Respuesta en formato JSON indicando éxito o conflicto
    """
    conflictos = db.verificar_conflicto(fecha, hora_inicio, hora_fin)
    
    if conflictos:
        return json.dumps({
            "status": "conflict",
            "mensaje": "No se puede agendar la reunión debido a conflictos.",
            "conflictos": conflictos
        }, indent=2)
    
    nuevo_evento = {
        "nombre": nombre,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin
    }
    
    db.agregar_evento(nuevo_evento)
    
    return json.dumps({
        "status": "success",
        "mensaje": "Reunión agendada con éxito.",
        "evento": nuevo_evento
    }, indent=2)

@tool
def consultar_agenda(fecha: Optional[str] = None) -> str:
    """
    Consulta eventos en la agenda, opcionalmente filtrados por fecha.
    
    Args:
        fecha: Fecha opcional en formato YYYY-MM-DD para filtrar
    
    Returns:
        Lista de eventos en formato JSON
    """
    eventos = db.obtener_todos_eventos()
    
    if fecha:
        eventos = [evento for evento in eventos if evento["fecha"] == fecha]
    
    return json.dumps({
        "status": "success",
        "eventos": eventos
    }, indent=2)

@tool
def eliminar_reunion(nombre: str, fecha: str) -> str:
    """
    Elimina una reunión existente.
    
    Args:
        nombre: Nombre de la reunión a eliminar
        fecha: Fecha de la reunión a eliminar
    
    Returns:
        Respuesta en formato JSON indicando éxito o fracaso
    """
    exito = db.eliminar_evento(nombre, fecha)
    
    if exito:
        return json.dumps({
            "status": "success",
            "mensaje": f"Reunión '{nombre}' del {fecha} eliminada con éxito."
        }, indent=2)
    else:
        return json.dumps({
            "status": "error",
            "mensaje": f"No se encontró la reunión '{nombre}' del {fecha}."
        }, indent=2)

@tool
def actualizar_reunion(nombre_original: str, fecha_original: str, nuevo_nombre: str, 
                       nueva_fecha: str, nueva_hora_inicio: str, nueva_hora_fin: str) -> str:
    """
    Actualiza los detalles de una reunión existente.
    
    Args:
        nombre_original: Nombre actual de la reunión
        fecha_original: Fecha actual de la reunión
        nuevo_nombre: Nuevo nombre para la reunión
        nueva_fecha: Nueva fecha para la reunión
        nueva_hora_inicio: Nueva hora de inicio
        nueva_hora_fin: Nueva hora de fin
    
    Returns:
        Respuesta en formato JSON indicando éxito o fracaso
    """
    # Verificar que la reunión original existe
    eventos = db.obtener_todos_eventos()
    reunion_existe = any(e["nombre"] == nombre_original and e["fecha"] == fecha_original for e in eventos)
    
    if not reunion_existe:
        return json.dumps({
            "status": "error",
            "mensaje": f"No se encontró la reunión '{nombre_original}' del {fecha_original}."
        }, indent=2)
    
    # Verificar conflictos para la nueva hora/fecha (excluyendo la reunión actual)
    conflictos = []
    
    # Convertir horas a objetos datetime para comparación
    nuevo_inicio = datetime.strptime(f"{nueva_fecha} {nueva_hora_inicio}", "%Y-%m-%d %H:%M")
    nuevo_fin = datetime.strptime(f"{nueva_fecha} {nueva_hora_fin}", "%Y-%m-%d %H:%M")
    
    for evento in eventos:
        # Excluir el evento que estamos actualizando
        if evento["nombre"] == nombre_original and evento["fecha"] == fecha_original:
            continue
            
        if evento["fecha"] == nueva_fecha:
            evento_inicio = datetime.strptime(f"{nueva_fecha} {evento['hora_inicio']}", "%Y-%m-%d %H:%M")
            evento_fin = datetime.strptime(f"{nueva_fecha} {evento['hora_fin']}", "%Y-%m-%d %H:%M")
            
            # Verificar si hay superposición
            if (nuevo_inicio < evento_fin and nuevo_fin > evento_inicio):
                conflictos.append(evento)
    
    if conflictos:
        return json.dumps({
            "status": "conflict",
            "mensaje": "La actualización genera conflictos con otros eventos.",
            "conflictos": conflictos
        }, indent=2)
    
    evento_actualizado = {
        "nombre": nuevo_nombre,
        "fecha": nueva_fecha,
        "hora_inicio": nueva_hora_inicio,
        "hora_fin": nueva_hora_fin
    }
    
    resultado = db.actualizar_evento(nombre_original, fecha_original, evento_actualizado)
    
    return json.dumps({
        "status": "success",
        "mensaje": f"Reunión actualizada con éxito.",
        "evento": resultado
    }, indent=2)