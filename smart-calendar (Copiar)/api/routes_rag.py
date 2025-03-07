from fastapi import APIRouter, HTTPException, UploadFile, File, Query,Depends
from typing import Optional, Dict, Annotated
import tempfile
import os
from langchain_core.runnables import RunnableConfig
from src.smart_calendar.graph import graph
from src.smart_calendar.state import State
from src.smart_calendar.tools import upsert_memory
import logging
from loguru import logger
from langgraph.store.base import BaseStore


router = APIRouter()

# Dependencia para obtener el store (ajusta según tu implementación real)
async def get_store() -> BaseStore:
    from langgraph.store.memory import MemoryStore
    return MemoryStore()

@router.get("/chat", summary="Interacción conversacional (texto)")
async def chat_interaction(
    user_id: Annotated[str, Query(description="ID del usuario")] = "default",
    model: Annotated[str, Query(description="Modelo de lenguaje a utilizar")] = "gpt-4o-mini",
    message: Annotated[str, Query(description="Mensaje del usuario")] = ...,
    store: Annotated[BaseStore, Depends(get_store)] = None,
):
    # Crear configuración
    config = Configuration(user_id=user_id, model=model)
    runnable_config = RunnableConfig(configurable=config.__dict__)
    
    # Crear estado inicial con el mensaje del usuario
    initial_state = graph.State(messages=[HumanMessage(content=message)])
    
    # Ejecutar el grafo con el estado y el store
    result = await graph.graph.ainvoke(
        initial_state,
        config=runnable_config,
        store=store  # Inyecta el store en los nodos que lo requieren
    )
    
    # Extraer la respuesta del asistente
    assistant_response = result.messages[-1].content
    
    return {"response": assistant_response}

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