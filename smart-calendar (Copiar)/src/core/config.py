import os
from dotenv import load_dotenv
from pydantic import BaseModel


# Cargar variables de entorno
load_dotenv()

class Settings(BaseModel):
    """Configuraciones centralizadas de la aplicación"""
    
    # Configuraciones de base de datos
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'agenda.db')
    
    # Configuraciones de API
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', 8000))
    
    # Configuraciones de OpenAI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
       
    # Configuraciones de seguridad
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # Modo de aplicación
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    class Config:
        """Configuración adicional de Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancia global de configuraciones
settings = Settings()