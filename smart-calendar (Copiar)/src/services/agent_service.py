from typing import List, Dict, Optional, Any, Union
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from src.smart_calendar.graph import graph
from src.services.evento_service import EventoService
from datetime import datetime
class AgentService:
    """Servicio de agente inteligente con gestión segura de hilos."""
    
    def __init__(self):
        self.evento_service = EventoService()
        self.agent = graph
        self.threads = {}

    def procesar_consulta(self, query: str, chat_history: list, thread_id: str = None):
        from src.smart_calendar.graph import agent_app
        messages = [HumanMessage(content=query)] + chat_history
        config = {"configurable": {"thread_id": thread_id or "default_thread"}}
        response = agent_app.invoke({"messages": messages}, config=config)
        return {"respuesta": response["messages"][-1].content}

    def _convert_to_hashable_id(self, id_value: Union[str, List]) -> str:
        """Convierte listas en strings seguros para usar como claves."""
        if isinstance(id_value, list):
            return "_".join(map(str, id_value))
        return str(id_value)

    def _get_thread_id(self, user_id: str, session_id: Optional[str]) -> str:
        """Genera ID de hilo único y seguro."""
        base_id = f"{user_id}-{session_id}" if session_id else user_id
        
        if base_id not in self.threads:
            self.threads[base_id] = str(uuid4())
            
        return self.threads[base_id]

    def _formatear_respuesta(self, resultado: Dict, thread_id: str) -> Dict[str, Any]:
        """Formatea la respuesta incluyendo metadatos útiles."""
        return {
            "respuesta": resultado["messages"][-1].content,
            "estado": "éxito",
            "metadata": {
                "thread_id": thread_id,
                "timestamp": datetime.now().isoformat(),
                "pasos": len(resultado["messages"])
            }
        }