from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Definición del estado del agente para LangGraph
    Mantiene el seguimiento de la conversación y los pasos intermedios
    """
    input: str
    chat_history: List[BaseMessage]
    intermediate_steps: List[str]
    response: str | None