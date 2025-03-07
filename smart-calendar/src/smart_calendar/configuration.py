from langchain_openai import ChatOpenAI

# Configuración del modelo de lenguaje
def get_llm(model_name="gpt-4o-mini", temperature=0):
    """
    Crea y devuelve una instancia del modelo de lenguaje configurado.
    
    Args:
        model_name: El nombre del modelo a utilizar
        temperature: Valor de temperatura para la generación de texto
        
    Returns:
        Una instancia configurada del modelo LLM
    """
    return ChatOpenAI(temperature=temperature, model=model_name)