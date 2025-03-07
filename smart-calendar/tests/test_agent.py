import pytest
from src.smart_calendar.graph import create_agent_chain, AgentState
from langchain_core.messages import HumanMessage

@pytest.fixture
def agent_graph():
    """Fixture para crear el grafo del agente"""
    return create_agent_chain()

def test_agent_initialization(agent_graph):
    """Test de inicialización del agente"""
    assert agent_graph is not None

def test_agent_response(agent_graph):
    """Test de respuesta del agente"""
    initial_state = AgentState(
        input="Agendar una reunión mañana a las 10 AM",
        chat_history=[],
        intermediate_steps=[],
        response=None
    )
    
    result = agent_graph.invoke(initial_state)
    
    assert 'response' in result
    assert result['response'] is not None
    assert len(result['response']) > 0

def test_agent_chat_history(agent_graph):
    """Test de manejo de historial de chat"""
    state1 = AgentState(
        input="Quiero agendar una reunión",
        chat_history=[],
        intermediate_steps=[],
        response=None
    )
    
    result1 = agent_graph.invoke(state1)
    
    state2 = AgentState(
        input="¿Puedes ayudarme a confirmar la hora?",
        chat_history=[
            HumanMessage(content=state1['input']),
            AIMessage(content=result1['response'])
        ],
        intermediate_steps=[],
        response=None
    )
    
    result2 = agent_graph.invoke(state2)
    
    assert result2['response'] is not None