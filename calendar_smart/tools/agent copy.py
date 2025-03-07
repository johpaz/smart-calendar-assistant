import os
import json
import re
from datetime import datetime, timedelta
from dateutil import parser
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
load_dotenv()

class Router:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.prompt = PromptTemplate(
            input_variables=["input"],
            template="""Clasifica la intención del usuario:
1. 'agendar' - Para crear/insertar nuevos eventos.
2. 'consultar' - Para ver la agenda.
3. 'editar' - Para modificar eventos.
4. 'borrar' - Para eliminar eventos.
5. 'chat' - Conversación general.

Ejemplos:
- "Quiero agendar una reunión" -> agendar
- "Muéstrame mi agenda" -> consultar
- "Necesito editar mi evento" -> editar

Input: {input}
Responde únicamente con una de estas palabras: agendar, consultar, editar, borrar, chat."""
        )
    
    def route(self, user_input):
        # Verificación preliminar: si el input es un saludo simple, forzar el intent "chat"
        greetings = {"hola", "buenos días", "buenas tardes", "saludos"}
        if user_input.strip().lower() in greetings:
            print("DEBUG: Input es un saludo simple, forzando intent 'chat'.")
            return "chat"
        
        print("DEBUG: Usando LLM para clasificar el input.")
        chain = self.prompt | self.llm
        response = chain.invoke({"input": user_input})
        intent = response.content.strip().lower()
        
        valid_intents = {"agendar", "consultar", "editar", "borrar", "chat"}
        if intent not in valid_intents:
            print(f"DEBUG: Intención no reconocida: {intent}. Se asigna 'chat' por defecto.")
            intent = "chat"
        return intent

class AgendaAgent:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.router = Router()
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.system_prompt = """
Eres un asistente de agenda inteligente y conversacional llamado Agente Sofía. Tu personalidad es amable, profesional y orientada al servicio al cliente.
Funciones principales:
1. Saludar al usuario de forma cálida 😊.
2. Ayudar en la gestión de la agenda, programando reuniones y verificando conflictos de horario.
3. Responder preguntas generales y brindar asistencia al cliente.
4. Ejecutar operaciones de agenda (agendar, consultar, editar, borrar) utilizando siempre el formato JSON requerido.

Normas:
- Emplea emojis apropiados para transmitir calidez y profesionalismo.
- Sé conciso pero amigable en tus respuestas.
- Incluye tu nombre (Agente Sofía) en las respuestas cuando corresponda.
- Antes de agendar una reunión, verifica la disponibilidad y evita conflictos de horario.
"""
        self.tools = {
            'agendar': self._create_agendar_prompt(),
            'consultar': self._create_consultar_prompt(),
            'editar': self._create_editar_prompt(),
            'borrar': self._create_borrar_prompt()
        }
        self.conversation_context = {}
        self.meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
    
    def _create_agendar_prompt(self):
        # Se escapan las llaves dobles para evitar que se interpreten como variables y se completa el JSON.
        return PromptTemplate(
            input_variables=["input"],
            template="""Extrae SOLO estos campos del input en formato JSON:
{{
  "nombre": "Nombre del evento. Si se menciona 'tema', úsalo como nombre",
  "fecha": "Fecha en formato YYYY-MM-DD. Ejemplo: '10 de marzo' → '2025-03-10'",
  "hora_inicio": "Hora de inicio en formato HH:MM. Ejemplo: '11 am' → '11:00'",
  "hora_fin": "Hora de fin en formato HH:MM"
}}
Input: {input}
Devuelve SOLO el JSON."""
        )
    
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
    
    def _create_editar_prompt(self):
        return PromptTemplate(
            input_variables=["input"],
            template="""Extrae datos para edición:
{{
  "solicitud": "editar",
  "id_evento": "ID del evento",
  "nuevos_datos": {{
    "nombre": "Nuevo nombre",
    "fecha": "Nueva fecha",
    "hora_inicio": "Nueva hora inicio",
    "hora_fin": "Nueva hora fin"
  }}
}}
Input: {input}
Devuelve SOLO el JSON."""
        )
    
    def _create_borrar_prompt(self):
        return PromptTemplate(
            input_variables=["input"],
            template="""Analiza la solicitud y genera JSON con:
- 'tipo': ['todos', 'id', 'rango', 'indefinido']
- 'detalles': información relevante

Input: {input}
Devuelve SOLO el JSON."""
        )
    def _create_agendar_prompt(self):
        return PromptTemplate(
            input_variables=["input"],
            template="""Extrae SOLO estos campos del input en formato JSON:
    {{
    "nombre": "Nombre del evento. Si se menciona 'tema', úsalo como nombre",
    "fecha": "Fecha en formato YYYY-MM-DD. Ejemplo: '10 de marzo' → '2025-03-10'",
    "hora_inicio": "Hora de inicio en formato HH:MM. Ejemplo: '11 am' → '11:00'",
    "hora_fin"
    
  
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
            Devuelve SOLO el JSON"""
        )

    def _create_editar_prompt(self):
        return PromptTemplate(
            input_variables=["input"],
            template="""Extrae datos para edición:
            {{
                "solicitud": "editar",
                "id_evento": "ID del evento",
                "nuevos_datos": {{
                    "nombre": "Nuevo nombre",
                    "fecha": "Nueva fecha",
                    "hora_inicio": "Nueva hora inicio",
                    "hora_fin": "Nueva hora fin"
                }}
            }}

            Input: {input}
            Devuelve SOLO el JSON"""
        )

    def _create_borrar_prompt(self):
        return PromptTemplate(
            input_variables=["input"],
            template="""Analiza la solicitud y genera JSON con:
            - 'tipo': ['todos', 'id', 'rango', 'indefinido']
            - 'detalles': información relevante

            Input: {input}
            Devuelve SOLO el JSON"""
        )

    def process_request(self, user_input):
        print("Input:", user_input)
        if self.conversation_context.get('pending_action'):
            return self._handle_followup(user_input)
        
        self.conversation_context = {}
        intent = self.router.route(user_input)
        print(f"DEBUG: Intención detectada: {intent}")
        
        if intent in self.tools:
            return self._handle_tool(intent, user_input)
        return self._handle_chat(user_input, intent)
    
    def _get_next_prompt(self, field):
        """Prompts más naturales y conversacionales."""
        prompts = {
            "nombre": "¡Genial! ¿Cómo se llamará esa reunión?",
            "fecha": "📅 ¿Para qué día te gustaría programarla? (Ejemplo: '15 de marzo' o 'mañana')",
            "hora_inicio": "⏰ ¿A qué hora empieza? (Ejemplo: '9:00' o '2 pm')",
            "hora_fin": "🕔 ¿Y a qué hora termina? (Ejemplo: '10:00' o '3 pm')"
        }
        return {"status": "info", "mensaje": prompts[field]}

    def _handle_tool(self, intent, user_input):
        try:
            tool_prompt = self.tools[intent]
            chain = tool_prompt | self.llm
            response = chain.invoke({"input": user_input})
            json_data = json.loads(response.content)
            print(f"DEBUG: Datos extraídos: {json_data}")
            
            if intent == 'agendar':
                required_fields = ["nombre", "fecha", "hora_inicio"]
                collected_data = {k: json_data.get(k) for k in required_fields}

                # Si se proporciona 'duracion', calculamos la hora de fin.
                duracion = json_data.get("duracion")
                if duracion and collected_data.get("hora_inicio"):
                    try:
                        if not collected_data.get("nombre") and json_data.get("tema"):
                            collected_data["nombre"] = json_data.get("tema")
                        if isinstance(duracion, str):
                            numeros = re.findall(r'\d+', duracion)
                            if numeros:
                                # Si se menciona "hora", asumimos horas; sino, minutos
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
                        return {"status": "error", "mensaje": f"❌ Error al calcular la hora de finalización: {str(e)}. Soy Agente Sofía, ¿puedes corregirlo?"}
                else:
                    collected_data["hora_fin"] = None

                # Identificar los campos que aún faltan
                missing = [k for k, v in collected_data.items() if v is None]
                self.conversation_context = {
                    "pending_action": "agendar",
                    "collected_data": collected_data,
                    "missing_fields": ["nombre", "fecha", "hora_inicio", "hora_fin"] if user_input.lower().strip() == "agendar" else missing
                }
                
                if self.conversation_context["missing_fields"]:
                    return self._get_next_prompt(self.conversation_context["missing_fields"][0])
                else:
                    result = self._finalize_booking(collected_data)
                    self.conversation_context = {}
                    return {
                        "status": result["status"],
                        "mensaje": f"{result['mensaje']} ¿en qué más puedo ayudarte? 😊"
                    }

                            

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

            elif intent == 'editar':
                if "id_evento" not in json_data or not json_data["id_evento"]:
                    return {"status": "error", "mensaje": "❌ Falta el ID del evento a editar. Soy Agente Sofía."}
                if "nuevos_datos" not in json_data or not json_data["nuevos_datos"]:
                    return {"status": "error", "mensaje": "❌ Falta la información para actualizar. Soy Agente Sofía."}
                result = self.scheduler.update_event(json_data['id_evento'], json_data['nuevos_datos'])
                return {
                    "status": result["status"],
                    "mensaje": f"{result['mensaje']} ¡Hecho! Soy Agente Sofía, ¿qué más necesitas? 😊"
                }

            elif intent == 'borrar':
                return self._handle_delete(json_data)

        except json.JSONDecodeError as e:
            print(f"DEBUG: Error de formato JSON: {str(e)}")
            return {"status": "error", "mensaje": "❌ Ups, parece que algo no salió bien. ¿Puedes darme más detalles para agendar tu reunión?"}
        except Exception as e:
            print(f"DEBUG: Error en _handle_tool: {str(e)}")
            return {"status": "error", "mensaje": f"❌ Error procesando tu solicitud: {str(e)}. ¿Cómo puedo asistirte ahora?"}

    def _handle_followup(self, user_input):
        context = self.conversation_context
        pending_action = context.get("pending_action")

        if pending_action == "confirmar_borrado_total":
            if "sí" in user_input.lower() or "confirmar" in user_input.lower():
                result = self.scheduler.delete_all_events()
                self.conversation_context = {}
                return {
                    "status": "success",
                    "mensaje": f"{result['mensaje']} ¡Agenda limpia! Soy Agente Sofía, ¿en qué más puedo ayudarte? 😊"
                }
            self.conversation_context = {}
            return {"status": "info", "mensaje": "❌ Borrado cancelado. Soy Agente Sofía, ¿qué más necesitas?"}

        elif pending_action == "consultar":
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

    def _process_field(self, field, value):
        if field == "fecha":
            return self._parse_date(value)
        elif field in ["hora_inicio", "hora_fin"]:
            return self._parse_time(value)
        return value

    def _parse_date(self, date_str):
        try:
            parsed = parser.parse(date_str, dayfirst=True, fuzzy=True)
            return parsed.strftime("%Y-%m-%d")
        except:
            try:
                patterns = [
                    r"(?i)(\d{1,2})\s*de\s*([a-z]+)\s*(?:de\s*)?(\d{4})?",
                    r"(?i)(\d{1,2})[/-](\d{1,2})[/-]?(\d{2,4})?"
                ]
                for pattern in patterns:
                    match = re.match(pattern, date_str.strip())
                    if match:
                        groups = match.groups()
                        dia = int(groups[0])
                        mes = groups[1] if len(groups) > 1 else None
                        año = groups[2] if len(groups) > 2 and groups[2] else datetime.now().year
                        
                        if mes and not mes.isdigit():
                            mes = self.meses[mes.lower()]
                        else:
                            mes = int(mes)
                        
                        if not año:
                            año = datetime.now().year
                        elif len(str(año)) == 2:
                            año = 2000 + int(año)
                        
                        return f"{año}-{mes:02d}-{dia:02d}"
                raise ValueError
            except:
                raise ValueError("Formato de fecha no reconocido. Ej: '10 de marzo' o '2025-03-10'")

    def _parse_time(self, time_str):
        try:
            return parser.parse(time_str).strftime("%H:%M")
        except:
            raise ValueError("Formato de hora inválido. Usa 'HH:MM' o 'X am/pm'")

    def _check_conflict(self, fecha, hora_inicio, hora_fin):
        """Verifica si hay conflictos de horario en el rango especificado."""
        try:
            all_events = self.scheduler.get_all_events()
            if not isinstance(all_events, dict) or 'eventos' not in all_events:
                return False  # No hay eventos para validar

            new_start = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
            new_end = datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M")

            for event in all_events['eventos']:
                event_start = datetime.strptime(f"{event['fecha']} {event['hora_inicio']}", "%Y-%m-%d %H:%M")
                event_end = datetime.strptime(f"{event['fecha']} {event['hora_fin']}", "%Y-%m-%d %H:%M")
                
                # Si hay solapamiento
                if event['fecha'] == fecha and (
                    (new_start < event_end and new_end > event_start)
                ):
                    return True  # Conflicto encontrado
            return False
        except Exception as e:
            print(f"DEBUG: Error verificando conflictos: {str(e)}")
            return False
    def _finalize_booking(self, data):
        try:
            # Validamos que se tengan todos los campos y que tengan el formato correcto.
            self._validate_full_data(data)
            print(f"DEBUG: Validando datos para agendar: {data}")

            # Verificar conflictos usando el método del scheduler.
            if self.scheduler.check_conflict(data["fecha"], data["hora_inicio"], data["hora_fin"]):
                return {
                    "status": "error",
                    "mensaje": f"❌ Conflicto de horario detectado para el evento en {data['fecha']} de {data['hora_inicio']} a {data['hora_fin']}."
                }
            # Construir la solicitud (data ya tiene los campos: nombre, fecha, hora_inicio, hora_fin)
            # Llamar a schedule_meeting pasándole la solicitud completa.
            result = self.scheduler.schedule_meeting(data)
            return result
        except ValueError as e:
            return {"status": "error", "mensaje": str(e)}
        except Exception as e:
            return {"status": "error", "mensaje": f"Error al agendar: {str(e)}"}

    def _get_events_in_range(self, fecha_inicio, fecha_fin):
        # Adaptación para Scheduler que no tiene get_events
        try:
            # Si tu Scheduler tiene get_all_events, filtramos manualmente
            all_events = self.scheduler.get_all_events()
            if not isinstance(all_events, dict) or 'eventos' not in all_events:
                raise ValueError("Formato de eventos inválido")
            eventos = [
                e for e in all_events['eventos']
                if fecha_inicio <= e['fecha'] <= fecha_fin
            ]
            return {"status": "success", "eventos": eventos}
        except AttributeError:
            # Si get_all_events no existe, asumimos que Scheduler tiene otra forma de consultar
            return {"status": "error", "mensaje": "Método de consulta no soportado por el Scheduler"}

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

    def _handle_chat(self, user_input, intent):
        messages = [
            ("system", self.system_prompt),
            ("human", user_input)
        ]
        
        response = self.llm.invoke(messages)
        return {"status": "chat", "mensaje": f"{response.content} "}

    def _handle_delete(self, data):
        try:
            delete_type = data.get('tipo', 'indefinido')
            if delete_type == 'todos':
                return self._handle_full_deletion()
            elif delete_type == 'id':
                result = self.scheduler.delete_event(data.get('detalles', {}).get('id'))
                return {
                    "status": result["status"],
                    "mensaje": f"{result['mensaje']} ¡Hecho! Soy Agente Sofía, ¿qué más necesitas? 😊"
                }
            elif delete_type == 'rango':
                return {"status": "info", "mensaje": "📅 Borrado por rango no implementado. Soy Agente Sofía, ¿qué más necesitas?"}
            return {"status": "error", "mensaje": "❌ Tipo de borrado no reconocido. Soy Agente Sofía, ¿puedes intentarlo de nuevo?"}
        except Exception as e:
            return {"status": "error", "mensaje": f"❌ Error procesando borrado: {str(e)}. Soy Agente Sofía, ¿cómo puedo asistirte?"}

    def _handle_full_deletion(self):
        try:
            all_events = self.scheduler.get_all_events()
            total = len(all_events.get('eventos', []))
            if total == 0:
                return {"status": "info", "mensaje": "📭 La agenda ya está vacía. Soy Agente Sofía, ¿en qué puedo ayudarte? 😊"}
            
            self.conversation_context = {
                'pending_action': 'confirmar_borrado_total',
                'total_eventos': total
            }
            return {
                "status": "confirmacion",
                "mensaje": f"⚠️ ¿Estás seguro de borrar los {total} eventos? Soy Agente Sofía, por favor confirma.",
                "opciones": [
                    {"texto": "Sí, eliminar todo", "accion": "confirmar"},
                    {"texto": "No, cancelar", "accion": "cancelar"}
                ]
            }
        except Exception as e:
            return {"status": "error", "mensaje": f"❌ Error al consultar agenda: {str(e)}. Soy Agente Sofía, ¿intentamos de nuevo?"}

