import os
import json
import re
from datetime import datetime, timedelta
from dateutil import parser
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

load_dotenv()

##############################################
# Agente para Evaluar y Ejecutar Comandos    #
##############################################

class CommandEvaluatorAgent:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        # Definición de herramientas (prompts) para cada acción
        self.tools = {
            'agendar': self._create_agendar_prompt(),
            'consultar': self._create_consultar_prompt(),
           
        }
        self.meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
    
    def _create_agendar_prompt(self):
        return PromptTemplate(
            input_variables=["input"],
            template="""Extrae SOLO estos campos del input en formato JSON:
{{
  "nombre": "Nombre del evento. Si se menciona 'tema', úsalo como nombre",
  "fecha": "Fecha en formato YYYY-MM-DD. Ejemplo: '10 de marzo' → '2025-03-10'",
  "hora_inicio": "Hora de inicio en formato HH:MM. Ejemplo: '11 am' → '11:00'",
  "hora_fin": "Hora de fin en formato HH:MM",
  "duracion": "Duración opcional (ej: '1 hora')"
}}
Input: {input}
Devuelve SOLO el JSON."""
        )
    def _get_next_prompt(self, field):
        """Prompts más naturales y conversacionales."""
        prompts = {
            "nombre": "¡Genial! ¿Cómo se llamará esa reunión?",
            "fecha": "📅 ¿Para qué día te gustaría programarla? (Ejemplo: '15 de marzo' o 'mañana')",
            "hora_inicio": "⏰ ¿A qué hora empieza? (Ejemplo: '9:00' o '2 pm')",
            "hora_fin": "🕔 ¿Y a qué hora termina? (Ejemplo: '10:00' o '3 pm')"
        }
        return {"status": "info", "mensaje": prompts[field]}
    
    
    def _create_consultar_prompt(self):
        return PromptTemplate(
            input_variables=["input"],
            template="""Extrae fechas o períodos:
Si el input contiene fechas, devuelve:
{{
  "solicitud": "consultar",
  "fecha_inicio": "YYYY-MM-DD",
  "fecha_fin": "YYYY-MM-DD"
}}

Si no hay fechas claras, devuelve:
{{
  "solicitud": "consultar",
  "mensaje": "Por favor especifica un rango de fechas (ej: 'del 10 al 15 de marzo')"
}}

Input: {input}
Devuelve SOLO el JSON."""
        )
    
    def _validate_full_data(self, data):
        required_fields = ["nombre", "fecha", "hora_inicio", "hora_fin"]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Faltan campos obligatorios: {', '.join(missing)}")
        
        try:
            datetime.strptime(data['fecha'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Formato de fecha incorrecto. Usa YYYY-MM-DD")
        
        for field in ["hora_inicio", "hora_fin"]:
            try:
                datetime.strptime(data[field], '%H:%M')
            except ValueError:
                raise ValueError(f"Formato de hora en {field} incorrecto. Usa HH:MM")
        
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
        if hora_inicio >= hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

    
    def process_command(self, user_input):
        """Evalúa si el input contiene un comando relacionado con la agenda.
           Se utiliza una verificación simple de palabras clave."""
        user_lower = user_input.lower()
        print(user_lower)
        if any(kw in user_lower for kw in ["agendar", "programar", "crear reunión"]):
            return self._handle_tool("agendar", user_input)
        elif any(kw in user_lower for kw in ["consultar", "mostrar agenda", "ver agenda"]):
            return self._handle_tool("consultar", user_input)
       
        else:
            return None  # No se detectó un comando específico

    
    def extract_dates(self, text):
        try:
            text = text.lower().strip()
            if "mañana" in text:
                date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                return date, date
            if "hoy" in text:
                date = datetime.now().strftime("%Y-%m-%d")
                return date, date
            if "próxima semana" in text or "semana próxima" in text:
                start = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
                end = start + timedelta(days=6)
                return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
                
            range_patterns = [
                (r"del\s*(\d{1,2})\s*al\s*(\d{1,2})\s*de\s*(\w+)",
                 lambda m: (
                     datetime(datetime.now().year, self.meses[m.group(3).lower()], int(m.group(1))),
                     datetime(datetime.now().year, self.meses[m.group(3).lower()], int(m.group(2)))
                 )),
                (r"entre\s*(\d{1,2})\s*y\s*(\d{1,2})\s*de\s*(\w+)",
                 lambda m: (
                     datetime(datetime.now().year, self.meses[m.group(3).lower()], int(m.group(1))),
                     datetime(datetime.now().year, self.meses[m.group(3).lower()], int(m.group(2)))
                 ))
            ]
            
            for pattern, date_creator in range_patterns:
                match = re.search(pattern, text)
                if match:
                    fecha_inicio, fecha_fin = date_creator(match)
                    if fecha_inicio > fecha_fin:
                        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio
                    return fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d")
                    
            date_candidates = re.findall(r"\b(\d{1,2})\s+(?:de\s+)?(\w+)\b", text)
            if date_candidates:
                day, month_str = date_candidates[0]
                month = self.meses[month_str.lower()]
                year = datetime.now().year
                date = datetime(year, month, int(day))
                return date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")
                    
            return None, None
        except Exception:
            return None, None

    def _handle_tool(self, intent, user_input):
        try:
            tool_prompt = self.tools[intent]
            chain = tool_prompt | self.llm
            response = chain.invoke({"input": user_input})
            json_data = json.loads(response.content)
            print(f"DEBUG: Datos extraídos para '{intent}': {json_data}")

            if intent == 'agendar':
                required_fields = ["nombre", "fecha", "hora_inicio"]
                collected_data = {k: json_data.get(k) for k in required_fields}
                # Si se provee duración, se calcula hora_fin; de lo contrario se usa el campo
                duracion = json_data.get("duracion")
                if duracion and collected_data.get("hora_inicio"):
                    try:
                        if not collected_data.get("nombre") and json_data.get("tema"):
                            collected_data["nombre"] = json_data.get("tema")
                        if isinstance(duracion, str):
                            numeros = re.findall(r'\d+', duracion)
                            if numeros:
                                if "hora" in duracion.lower():
                                    duracion_min = int(numeros[0]) * 60
                                else:
                                    duracion_min = int(numeros[0])
                            else:
                                duracion_min = None
                        else:
                            duracion_min = int(duracion)
                        
                        if duracion_min is None:
                            raise ValueError("No se pudo interpretar la duración.")
                        
                        start_time = datetime.strptime(collected_data["hora_inicio"], "%H:%M")
                        end_time = start_time + timedelta(minutes=duracion_min)
                        collected_data["hora_fin"] = end_time.strftime("%H:%M")
                    except Exception as e:
                        return {"status": "error", "mensaje": f"Error al calcular la hora de finalización: {str(e)}."}
                else:
                    collected_data["hora_fin"] = json_data.get("hora_fin")
                
                missing = [k for k, v in collected_data.items() if not v]
                if missing:
                    return {"status": "error", "mensaje": f"Faltan los siguientes campos: {', '.join(missing)}."}
                result = self._finalize_booking(collected_data)
                return {"status": result["status"], "mensaje": result["mensaje"]}
            
            elif intent == 'consultar':
                if 'fecha_inicio' in json_data and 'fecha_fin' in json_data:
                    # Usar get_all_events si get_events no existe, ajustando para rango
                    result = self._get_events_in_range(json_data['fecha_inicio'], json_data['fecha_fin'])
                    eventos = result.get('eventos', [])
                    if eventos:
                        mensaje = "📅 Aquí está tu agenda:\n" + "\n".join(
                            [f"- {e['nombre']} el {e['fecha']} de {e['hora_inicio']} a {e['hora_fin']}" for e in eventos]
                        ) + "\n ¿en qué más puedo ayudarte? 😊"
                    else:
                        mensaje = "📅 No tienes eventos en ese período. ¿qué más puedo hacer por ti? 😊"
                    return {"status": "success", "mensaje": mensaje }
                self.conversation_context = {'pending_action': 'consultar'}
                return {"status": "info", "mensaje": "📅¿Para qué período quieres consultar tu agenda? (Ej: 'mañana' o 'del 10 al 15 de marzo')"}
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: Error de formato JSON: {str(e)}")
            return {"status": "error", "mensaje": "Error al procesar el comando. Verifica la información."}
        except Exception as e:
            print(f"DEBUG: Error en _handle_tool: {str(e)}")
            return {"status": "error", "mensaje": f"Error procesando tu solicitud: {str(e)}."}
        
    def _handle_followup(self, user_input):
            context = self.conversation_context
            pending_action = context.get("pending_action")

           

            if pending_action == "consultar":
                fecha_inicio, fecha_fin = self.extract_dates(user_input)
                if fecha_inicio and fecha_fin:
                    result = self._get_events_in_range(fecha_inicio, fecha_fin)
                    eventos = result.get('eventos', [])
                    if eventos:
                    
                        mensaje = "📅 Aquí está tu agenda:\n" + "\n".join(
                            [f"- {e['nombre']} el {e['fecha']} de {e['hora_inicio']} a {e['hora_fin']}" for e in eventos]
                        ) + "\nSoy Agente Sofía, ¿en qué más puedo ayudarte? 😊"
                    else:
                        mensaje = "📅 No tienes eventos en ese período. ¿qué más puedo hacer por ti? 😊"
                    self.conversation_context = {}
                    return {"status": "success", "mensaje": mensaje, "eventos": eventos}
                self.conversation_context = {}
                return {"status": "error", "mensaje": "❌ No pude reconocer las fechas. Usa 'del 10 al 15 de marzo' o 'mañana'. Soy Agente Sofía, ¿intentamos de nuevo?"}

            elif pending_action == "agendar":
                current_field = context.get("missing_fields", [None])[0]
                if not current_field:
                    self.conversation_context = {}
                    return {"status": "error", "mensaje": "❌ Error interno. Soy Agente Sofía, ¿puedes empezar de nuevo?"}
                
                try:
                    processed_value = self._process_field(current_field, user_input)
                    context["collected_data"][current_field] = processed_value
                    remaining = context["missing_fields"][1:]
                    
                    if remaining:
                        self.conversation_context["missing_fields"] = remaining
                        return self._get_next_prompt(remaining[0])
                
                    result = self._finalize_booking(context["collected_data"])
                    print(result)
                    self.conversation_context = {}
                    return {
                        "status": result["status"],
                        "mensaje": f"{result['mensaje']} ¡Listo! Soy Agente Sofía, ¿en qué más puedo ayudarte? 😊"
                    }
                except ValueError as e:
                    return {"status": "error", "mensaje": f"❌ {str(e)} Soy Agente Sofía, ¿puedes corregirlo?"}

            self.conversation_context = {}
            return {"status": "error", "mensaje": "❌ Error interno. Soy Agente Sofía, ¿en qué puedo ayudarte ahora?"}    
    def _validate_full_data(self, data):
        required_fields = ["nombre", "fecha", "hora_inicio", "hora_fin"]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Faltan campos obligatorios: {', '.join(missing)}")
        try:
            datetime.strptime(data['fecha'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Formato de fecha incorrecto. Usa YYYY-MM-DD")
        for field in ["hora_inicio", "hora_fin"]:
            try:
                datetime.strptime(data[field], '%H:%M')
            except ValueError:
                raise ValueError(f"Formato de hora en {field} incorrecto. Usa HH:MM")
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
        if hora_inicio >= hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

    def _finalize_booking(self, data):
        try:
            self._validate_full_data(data)
            print(f"DEBUG: Datos para agendar: {data}")
            if self.scheduler.check_conflict(data["fecha"], data["hora_inicio"], data["hora_fin"]):
                return {"status": "error", "mensaje": f"Conflicto de horario detectado para {data['fecha']}."}
            result = self.scheduler.schedule_meeting(data)
            return result
        except ValueError as e:
            return {"status": "error", "mensaje": str(e)}
        except Exception as e:
            return {"status": "error", "mensaje": f"Error al agendar: {str(e)}"}

    def _get_events_in_range(self, fecha_inicio, fecha_fin):
        try:
            all_events = self.scheduler.get_all_events()
            if not isinstance(all_events, dict) or 'eventos' not in all_events:
                raise ValueError("Formato de eventos inválido")
            eventos = [e for e in all_events['eventos'] if fecha_inicio <= e['fecha'] <= fecha_fin]
            return {"status": "success", "eventos": eventos}
        except Exception as e:
            return {"status": "error", "mensaje": f"Error al consultar: {str(e)}"}

    def _handle_delete(self, data):
        try:
            delete_type = data.get('tipo', 'indefinido')
            if delete_type == 'todos':
                return self._handle_full_deletion()
            elif delete_type == 'id':
                result = self.scheduler.delete_event(data.get('detalles', {}).get('id'))
                return {"status": result["status"], "mensaje": result["mensaje"]}
            elif delete_type == 'rango':
                return {"status": "info", "mensaje": "Borrado por rango no implementado."}
            else:
                return {"status": "error", "mensaje": "Tipo de borrado no reconocido."}
        except Exception as e:
            return {"status": "error", "mensaje": f"Error procesando borrado: {str(e)}"}

    def _handle_full_deletion(self):
        try:
            all_events = self.scheduler.get_all_events()
            total = len(all_events.get('eventos', []))
            if total == 0:
                return {"status": "info", "mensaje": "La agenda ya está vacía."}
            return {"status": "confirmacion", "mensaje": f"¿Confirma borrar los {total} eventos?"}
        except Exception as e:
            return {"status": "error", "mensaje": f"Error al consultar agenda: {str(e)}"}

##############################################
# Agente Conversacional con Memoria (Chat)    #
##############################################

class ConversationalAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.system_prompt = """
Eres Agente Sofía, un asistente de agenda inteligente.
Tu personalidad es amable, profesional y siempre buscas ayudar al cliente.
Mantén el contexto de la conversación y responde de forma cálida.
"""
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def chat_response(self, user_input):
        history = self.memory.load_memory_variables({}).get("chat_history", [])
        messages = [{"role": "system", "content": self.system_prompt}] + history + [{"role": "user", "content": user_input}]
        response = self.llm.invoke(messages)
        self.memory.save_context({"input": user_input}, {"output": response.content})
        return {"status": "chat", "mensaje": response.content}

##############################################
# Master Agent: Decide qué agente usar        #
##############################################

class MasterAgent:
    def __init__(self, scheduler):
        self.command_agent = CommandEvaluatorAgent(scheduler)
        self.chat_agent = ConversationalAgent()

    def process_request(self, user_input):
        print(user_input)
        # Primero, se evalúa si el input es un comando de agenda.
        command_result = self.command_agent.process_command(user_input)
        if command_result is not None:
            return command_result
        # Si no, se delega al agente conversacional.
        return self.chat_agent.chat_response(user_input)
