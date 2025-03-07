from fastapi import APIRouter, HTTPException, UploadFile, File, Query,Depends
from typing import Optional, Dict, Annotated
import tempfile
import os
from langchain_core.runnables import RunnableConfig
from src.smart_calendar.graph import create_agenda_graph
from src.smart_calendar.utils import procesar_solicitud
from pydantic import BaseModel
import json

# Modelo para las solicitudes de chat
class ChatRequest(BaseModel):
    mensaje: str

# Modelo para las solicitudes de API
class AgendaRequest(BaseModel):
    solicitud: str
    nombre: Optional[str] = None
    fecha: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    nombre_original: Optional[str] = None
    fecha_original: Optional[str] = None
    nuevo_nombre: Optional[str] = None
    nueva_fecha: Optional[str] = None
    nueva_hora_inicio: Optional[str] = None
    nueva_hora_fin: Optional[str] = None
    
    
# Crear el grafo del agente
agenda_graph = create_agenda_graph()

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
     
        respuesta = procesar_solicitud(agenda_graph, request.mensaje)
        return {"respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ruta para la API de agenda (interfaz programática)
@router.post("/api/agenda")
async def api_agenda(request: AgendaRequest):
    try:
        respuesta = procesar_solicitud(agenda_graph, request.dict())
        
        # Intentar convertir la respuesta a JSON si es una cadena
        if isinstance(respuesta, str):
            try:
                respuesta_json = json.loads(respuesta)
                return respuesta_json
            except json.JSONDecodeError:
                return {"respuesta": respuesta}
        
        return {"respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/audio", summary="Generación de reporte por audio")
async def chat_audio_endpoint(audio: UploadFile = File(...)) -> Dict:
    """
    Endpoint para procesar audio y generar reporte estructurado.
    """
    try:
        # Transcribir audio
        audio_bytes = await audio.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1] or ".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        # Aquí iría tu lógica de transcripción real
        transcription = "Implementar transcripción de audio aquí"
        
        # Ejecutar el grafo
        result = await graph.ainvoke(
            {"topic": transcription, "messages": []},
            BASE_CONFIG
        )
        
        return {
            "transcription": transcription,
            "report": result.get("final_report", "Error generando el reporte"),
            "sections": result.get("sections", []),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path:
            os.remove(tmp_path)

@router.post("/feedback", summary="Procesar feedback humano")
async def feedback_endpoint(
    feedback: str = Query(...),
    report_id: str = Query(...)
) -> Dict:
    """
    Endpoint para manejar feedback durante la generación de reportes.
    """
    try:
        # Continuar ejecución del grafo con feedback
        result = await graph.ainvoke(
            {
                "topic": "Continuing report generation",
                "feedback_on_report_plan": feedback,
                "thread_id": report_id
            },
            BASE_CONFIG
        )
        
        return {
            "report_id": report_id,
            "status": "updated",
            "new_sections": result.get("sections", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))