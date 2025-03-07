import json
from langchain_core.messages import HumanMessage

def procesar_solicitud(graph, solicitud):
    """
    Procesa una solicitud y la envía al agente.
    
    Args:
        graph: El grafo compilado del agente
        solicitud: La solicitud a procesar (string o diccionario)
        
    Returns:
        La respuesta del agente
    """
    if isinstance(solicitud, str):
        # Si es una cadena de texto, intentar parsear JSON
        try:
            data = json.loads(solicitud)
        except json.JSONDecodeError:
            # Si no es JSON válido, asumimos que es una consulta en lenguaje natural
            return ejecutar_agente(graph, solicitud)
    else:
        # Si ya es un diccionario
        data = solicitud
    
    # Procesar según el tipo de solicitud
    if "solicitud" in data:
        tipo_solicitud = data.get("solicitud")
        
        if tipo_solicitud == "agendar":
            return ejecutar_agente(graph, f"Quiero agendar una reunión con el nombre '{data.get('nombre')}' para el {data.get('fecha')} desde las {data.get('hora_inicio')} hasta las {data.get('hora_fin')}")
        
        elif tipo_solicitud == "consultar":
            fecha = data.get("fecha", None)
            if fecha:
                return ejecutar_agente(graph, f"Muéstrame las reuniones para el {fecha}")
            else:
                return ejecutar_agente(graph, "Muéstrame todas las reuniones en la agenda")
        
        elif tipo_solicitud == "eliminar":
            return ejecutar_agente(graph, f"Elimina la reunión '{data.get('nombre')}' del {data.get('fecha')}")
        
        elif tipo_solicitud == "actualizar":
            return ejecutar_agente(graph,
                f"Actualiza la reunión '{data.get('nombre_original')}' del {data.get('fecha_original')} "
                f"con nuevo nombre '{data.get('nuevo_nombre')}', nueva fecha {data.get('nueva_fecha')}, "
                f"nueva hora inicio {data.get('nueva_hora_inicio')} y nueva hora fin {data.get('nueva_hora_fin')}"
            )
    
    # Si no se reconoce la solicitud, pasarla como texto al agente
    return ejecutar_agente(graph, json.dumps(data))

def ejecutar_agente(graph, input_text):
    """
    Ejecuta el agente con el texto de entrada proporcionado.
    
    Args:
        graph: El grafo compilado del agente
        input_text: El texto de entrada para el agente
        
    Returns:
        La respuesta del agente
    """
    result = graph.invoke({
        "messages": [HumanMessage(content=input_text)],
        "intermediate_steps": []
    })
    return result["messages"][-1].content