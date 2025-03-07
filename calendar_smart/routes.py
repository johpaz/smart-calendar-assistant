from fastapi import FastAPI
from pydantic import BaseModel
from tools.database import init_db
from tools.scheduler import Scheduler
from tools.agent import MasterAgent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Calendar Assistant API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes. Ajusta según tus necesidades.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Inicializar la base de datos, scheduler y agente
db = init_db()
scheduler = Scheduler(db)
agent = MasterAgent(scheduler)

class RequestBody(BaseModel):
    user_input: str

@app.post("/process")
def chat_response(request: RequestBody):
    print(request)
    response = agent.process_request(request.user_input)
    return response


