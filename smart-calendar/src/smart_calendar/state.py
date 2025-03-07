import operator
from typing import Annotated, Sequence, TypedDict, List, Tuple, Any
from langchain_core.messages import BaseMessage

# Definir el estado para el flujo del agente
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intermediate_steps: List[Tuple[Any, str]]