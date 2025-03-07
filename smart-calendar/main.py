from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.init import router as api_router
from src.core.database import DatabaseManager
from src.smart_calendar.graph import create_agenda_graph
from src.core.config import settings

app = FastAPI(title="Smart Calendar Assistant API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes. Ajusta según tus necesidades.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar la base de datos
print("Inicializando la base de datos...")
db_manager = DatabaseManager()
db_manager.init_db()
print(f"Base de datos inicializada correctamente en: {db_manager.db_path}")

# Construir el grafo del agente (RAG)
print("Construyendo el grafo del agente (RAG)...")
agenda_graph = create_agenda_graph
print("Grafo del agente construido correctamente.")

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
