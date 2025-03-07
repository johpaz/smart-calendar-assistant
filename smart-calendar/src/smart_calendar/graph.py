from langgraph.graph import END, StateGraph
from langchain.agents import create_openai_functions_agent
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgentOutputParser
from langchain.agents.agent import AgentExecutor
from langchain_core.messages import AIMessage
from smart_calendar.state import AgentState
from smart_calendar.tools import agendar_reunion, consultar_agenda, eliminar_reunion, actualizar_reunion
from smart_calendar.prompts import SYSTEM_PROMPT
from smart_calendar.configuration import get_llm
from langchain_core.prompts import ChatPromptTemplate



agenda_prompt = ChatPromptTemplate.from_messages(
    [
        {"role": "system", "content": SYSTEM_PROMPT + " You have access to the following tools: {tools}.\\System Time: {time}"},
        {"role": "user", "content": "{mensaje}"}
       
    ]
)

    

def create_agenda_agent():
    """
    Crea y devuelve un agente de agenda con las herramientas necesarias.
    
    Returns:
        Un agente configurado para gestionar la agenda
    """
    # Obtener el LLM configurado
    llm = get_llm()
    
    # Configurar las herramientas
    tools = [agendar_reunion, consultar_agenda, eliminar_reunion, actualizar_reunion]
    
    # Crear el agente
    agent = create_openai_functions_agent(llm, tools, agenda_prompt)
    
    return agent

def create_agenda_graph():
    """
    Crea y compila el grafo para el flujo del agente.
    
    Returns:
        Un grafo compilado listo para ser ejecutado
    """
    # Crear el agente
    agent = create_agenda_agent()
    
    # Define la función para procesar las acciones del agente
    def run_agent(state):
        agent_outcome = agent.invoke(state)
        return {"messages": [agent_outcome]}
    
    # Crear el grafo para el flujo del agente
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", run_agent)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    
    # Compilar el grafo
    return workflow.compile()