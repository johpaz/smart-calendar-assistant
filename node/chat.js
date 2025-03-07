const OpenAI = require('openai');
const { agendarEvento, consultarAgenda } = require('./agenda');
require('dotenv').config();

const openai = new OpenAI({
  apiKey: process.env.API_KEY,
});

const systemPrompt = `
Eres un asistente de agenda inteligente y conversacional llamado Agente Sofía. Tu personalidad es amable, profesional y orientada al servicio al cliente.
Funciones principales:
1. Saludar al usuario de forma cálida 😊 (solo una vez por conversación, a menos que se reinicie el contexto).
2. Ayudar en la gestión de la agenda, programando reuniones y verificando conflictos de horario.
3. Responder preguntas generales y brindar asistencia al cliente.
4. Ejecutar operaciones de agenda (agendar, consultar, editar, borrar) utilizando siempre el formato JSON requerido.

Normas:
- Emplea emojis apropiados para transmitir calidez y profesionalismo.
- Sé conciso pero amigable en tus respuestas.
- Incluye tu nombre (Agente Sofía) en las respuestas cuando corresponda.
- Antes de agendar una reunión, verifica la disponibilidad y evita conflictos de horario.
- Si el usuario quiere consultar la agenda y no especifica un rango de fechas, pídele un rango (ej. "del 10 al 15 de marzo").
- Interpreta términos como "hoy", "mañana" o rangos como "del 10 al 15 de marzo" basándote en la fecha actual (6 de marzo de 2025).
- Si no hay eventos en el rango consultado, responde amablemente y ofrece agendar uno.
`;

const meses = {
  'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
  'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
  'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
};

let conversationContext = {};

/**
 * Devuelve una fecha en formato YYYY-MM-DD a partir de un objeto Date.
 */
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Parsea fechas a partir de un texto.
 * Soporta:
 *  - "hoy" o "mañana"
 *  - Fecha única: "el 10 de marzo", "10 de marzo" o "el 10 de marzo de 2025"
 *  - Rango simple: "del 10 al 15 de marzo" (año por defecto)
 *  - Rango con año: "del 8 al 15 de marzo de 2025"
 *  - Rango con meses distintos: "del 10 de marzo al 15 de abril" (año por defecto)
 */
function parseFecha(texto, baseDate = new Date('2025-03-06')) {
  texto = texto.toLowerCase().trim();

  // Casos "hoy" y "mañana"
  if (texto.includes('hoy')) return formatDate(baseDate);
  if (texto.includes('mañana')) {
    const tomorrow = new Date(baseDate);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return formatDate(tomorrow);
  }

  // Rango: "del 8 al 15 de marzo de 2025"
  const rangoPattern1 = /del\s+(\d{1,2})\s+al\s+(\d{1,2})\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?/;
  const rangoMatch1 = texto.match(rangoPattern1);
  if (rangoMatch1) {
    const diaInicio = rangoMatch1[1].padStart(2, '0');
    const diaFin = rangoMatch1[2].padStart(2, '0');
    const mes = meses[rangoMatch1[3]];
    const year = rangoMatch1[4] ? rangoMatch1[4] : String(baseDate.getFullYear());
    return { inicio: `${year}-${mes}-${diaInicio}`, fin: `${year}-${mes}-${diaFin}` };
  }

  // Rango: "del 10 de marzo al 15 de abril" (año por defecto)
  const rangoPattern2 = /del\s+(\d{1,2})\s+de\s+(\w+)\s+al\s+(\d{1,2})\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?/;
  const rangoMatch2 = texto.match(rangoPattern2);
  if (rangoMatch2) {
    const diaInicio = rangoMatch2[1].padStart(2, '0');
    const mesInicio = meses[rangoMatch2[2]];
    const diaFin = rangoMatch2[3].padStart(2, '0');
    const mesFin = meses[rangoMatch2[4]];
    const year = rangoMatch2[5] ? rangoMatch2[5] : String(baseDate.getFullYear());
    return { inicio: `${year}-${mesInicio}-${diaInicio}`, fin: `${year}-${mesFin}-${diaFin}` };
  }

  // Fecha única: permite "el" opcional. Ejemplos: "el 10 de marzo", "10 de marzo de 2025"
  const singlePattern = /(?:el\s+)?(\d{1,2})\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?/;
  const singleMatch = texto.match(singlePattern);
  if (singleMatch) {
    const dia = singleMatch[1].padStart(2, '0');
    const mes = meses[singleMatch[2]];
    const year = singleMatch[3] ? singleMatch[3] : String(baseDate.getFullYear());
    return `${year}-${mes}-${dia}`;
  }

  return null;
}

/**
 * Parsea la hora a partir de un texto.
 * Se acepta con o sin "a las". Ejemplos válidos:
 * "a las 14:00", "14:00", "a las 2 pm", "2pm".
 */
function parseHora(texto) {
  const regex = /^(?:a\s+las\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$/;
  const match = texto.match(regex);
  if (!match) return null;

  let hour = parseInt(match[1], 10);
  let minutes = match[2] ? match[2] : "00";
  const meridiem = match[3];
  
  if (meridiem === 'pm' && hour < 12) {
    hour += 12;
  }
  if (meridiem === 'am' && hour === 12) {
    hour = 0;
  }
  
  return `${String(hour).padStart(2, '0')}:${minutes}`;
}

/**
 * Parsea la duración (en horas) a partir de un texto.
 * Ejemplo: "1 hora", "2 horas", "3h", etc.
 */
function parseDuration(texto) {
  const regex = /(\d+)\s*(hora|horas|h)/;
  const match = texto.match(regex);
  if (match) {
    return parseInt(match[1], 10);
  }
  return 1; // Valor por defecto: 1 hora
}

/**
 * Función principal que procesa el mensaje del usuario.
 * Se manejan dos grandes flujos: consultar y agendar.
 */
async function procesarMensaje(mensaje, userId = 'default') {
  console.log('Procesando:', mensaje);
  const texto = mensaje.toLowerCase().trim();

  try {
    // Primero, revisamos si estamos en el flujo de confirmación de agendamiento.
    if (conversationContext[userId]?.pendingAction === 'confirmar_agendar') {
      if (texto === 'si' || texto === 'sí') {
        let pendingData = conversationContext[userId].pendingData;
        // Se procede a agendar el evento
        return new Promise((resolve) => {
          agendarEvento(
            pendingData.nombre,
            pendingData.fecha,
            pendingData.hora_inicio,
            pendingData.hora_fin,
            (err, resultado) => {
                console.log(resultado.status);
                
              if (resultado.status==="error") {
                resolve({ status: 'error', mensaje: 'La fecha y hora seleccionadas tienen un conflicto selecciona otro horario.' });
              } else {
                delete conversationContext[userId];
                resolve({
                  status: 'success',
                  mensaje: `¡Listo! Se ha agendado el evento "${pendingData.nombre}" para el ${pendingData.fecha} a las ${pendingData.hora_inicio} con duración de ${pendingData.duration} hora(s).`
                });
              }
            }
          );
        });
      } else {
        return { status: 'pending', mensaje: 'Entendido. Si deseas modificar o cancelar el agendamiento, por favor indícame.' };
      }
    }

    // Si hay otra acción pendiente (por ejemplo, consulta) se procesa.
    if (conversationContext[userId]?.pendingAction) {
      if (conversationContext[userId].pendingAction === 'consultar') {
        const fechas = parseFecha(mensaje);
        if (!fechas) {
          return {
            status: 'pending',
            mensaje: 'No entendí las fechas, por favor dime un rango como "del 10 al 15 de marzo" o una fecha como "hoy", ¡soy Agente Sofía y quiero ayudarte! 😊'
          };
        }
        const fechaInicio = fechas.inicio || fechas;
        const fechaFin = fechas.fin || fechas;
        delete conversationContext[userId];
        return new Promise((resolve) => {
          consultarAgenda(fechaInicio, fechaFin, (err, resultado) => {
            if (err) resolve({ status: 'error', mensaje: 'Error interno, lo siento 😔.' });
            else if (resultado.eventos.length === 0) {
              resolve({
                status: 'success',
                mensaje: 'No tienes eventos en ese rango, ¡soy Agente Sofía! 😊 ¿Deseas agendar uno?',
                eventos: []
              });
            } else {
              resolve({
                status: 'success',
                mensaje: 'Aquí tienes tus eventos, ¡soy Agente Sofía! 😊',
                eventos: resultado.eventos
              });
            }
          });
        });
      }
      else if (conversationContext[userId].pendingAction === 'agendar') {
        let pendingData = conversationContext[userId].pendingData || {};

        // Si se espera auto-parsing (mensaje con comas)
        if (!pendingData.autoParsed && mensaje.includes(',')) {
          pendingData.autoParsed = true;
          const parts = mensaje.split(',');
          if (parts.length > 0) {
            pendingData.nombre = parts[0].trim();
          }
          if (parts.length > 1) {
            const secondPart = parts[1].trim();
            const fecha = parseFecha(secondPart);
            if (fecha) {
              pendingData.fecha = (typeof fecha === 'object' ? fecha.inicio : fecha);
            }
            // Extraer duración (ej.: "10 de marzo 1 hora")
            const dur = parseDuration(secondPart);
            pendingData.duration = dur;
          }
          conversationContext[userId].pendingData = pendingData;
        }

        // Si falta el nombre, se utiliza el mensaje actual y se pregunta por la fecha.
        if (!pendingData.nombre) {
          pendingData.nombre = mensaje.trim();
          conversationContext[userId].pendingData = pendingData;
          return { 
            status: 'pending', 
            mensaje: `Perfecto, se registró el nombre "${pendingData.nombre}". ¿Cuál es la fecha del evento? (ej. "10 de marzo", "el 10 de marzo" o "hoy")` 
          };
        }
        // Si falta la fecha, se intenta parsearla desde el mensaje.
        if (!pendingData.fecha) {
          const fecha = parseFecha(mensaje);
          if (fecha) {
            pendingData.fecha = (typeof fecha === 'object' ? fecha.inicio : fecha);
            conversationContext[userId].pendingData = pendingData;
            return { 
              status: 'pending', 
              mensaje: `Entendido, el evento será para el ${pendingData.fecha}. ¿A qué hora comienza? (ej. "a las 14:00" o "a las 2 pm")` 
            };
          } else {
            return { 
              status: 'pending', 
              mensaje: 'No entendí la fecha. Por favor, indica una fecha válida (ej. "10 de marzo", "el 10 de marzo" o "hoy").' 
            };
          }
        }
        // Si falta la hora de inicio, se intenta parsearla.
        if (!pendingData.hora_inicio) {
          const hora = parseHora(mensaje);
          if (hora) {
            pendingData.hora_inicio = hora;
            conversationContext[userId].pendingData = pendingData;
            if (!pendingData.duration) {
              return { 
                status: 'pending', 
                mensaje: `Perfecto, se registró el horario de inicio "${pendingData.hora_inicio}". ¿Cuál es la duración del evento? (ej. "1 hora" o "2 horas")` 
              };
            }
          } else {
            return { 
              status: 'pending', 
              mensaje: 'No entendí la hora. Por favor, indica un horario válido (ej. "a las 14:00" o "a las 2 pm").' 
            };
          }
        }
        // Si falta la duración, se intenta parsearla.
        if (!pendingData.duration) {
          const dur = parseDuration(mensaje);
          if (dur) {
            pendingData.duration = dur;
            conversationContext[userId].pendingData = pendingData;
          } else {
            return { 
              status: 'pending', 
              mensaje: 'No entendí la duración. Por favor, indica la duración del evento (ej. "1 hora" o "2 horas").' 
            };
          }
        }
        // Con hora de inicio y duración definidas, calculamos la hora final.
        if (!pendingData.hora_fin) {
          const startParts = pendingData.hora_inicio.split(':');
          const startHour = parseInt(startParts[0], 10);
          const minutes = startParts[1];
          const duration = pendingData.duration;
          const endHour = startHour + duration;
          pendingData.hora_fin = `${String(endHour).padStart(2, '0')}:${minutes}`;
          conversationContext[userId].pendingData = pendingData;
        }

        // En este punto, ya se tienen todos los datos. Se muestra un mensaje de confirmación.
        conversationContext[userId].pendingAction = 'confirmar_agendar';
        return { 
          status: 'pending', 
          mensaje: `Vas a agendar el evento "${pendingData.nombre}" para el ${pendingData.fecha} a las ${pendingData.hora_inicio} con duración de ${pendingData.duration} hora(s). ¿Confirmas?` 
        };
      }
    }

    // --- Detección del intent del usuario ---
    let accion = null;
    if (texto.includes('consultar') || texto.includes('ver')) {
      accion = 'consultar';
    } else if (texto.includes('agendar')) {
      accion = 'agendar';
    } else if (texto.includes('edita') || texto.includes('cambia')) {
      accion = 'editar';
    } else if (texto.includes('borra') || texto.includes('elimina')) {
      accion = 'borrar';
    }

    // Inicializar el contexto si es el primer mensaje del usuario.
    if (!conversationContext[userId]) {
      conversationContext[userId] = { greeted: false };
    }
    let saludo = '';
    if (!conversationContext[userId].greeted) {
      saludo = '¡Hola! Soy Agente Sofía 😊. ';
      conversationContext[userId].greeted = true;
    }

    // Flujo para agendar: iniciar el proceso interactivo.
    if (accion === 'agendar') {
      conversationContext[userId].pendingAction = 'agendar';
      conversationContext[userId].pendingData = {};
      return { status: 'pending', mensaje: `${saludo}Para agendar tu reunión, por favor indícame el nombre del evento.` };
    }

    // Flujo para consultar (se mantiene igual).
    if (accion === 'consultar') {
      const fechaTexto = parseFecha(mensaje);
      if (!fechaTexto) {
        conversationContext[userId].pendingAction = 'consultar';
        return {
          status: 'pending',
          mensaje: `${saludo}¿Para qué fechas quieres consultar tu agenda? Puedes decirme un rango como "del 10 al 15 de marzo" o una fecha como "hoy", ¡soy Agente Sofía y estoy aquí para ayudarte! 😊`
        };
      }
      const fechaInicio = fechaTexto.inicio || fechaTexto;
      const fechaFin = fechaTexto.fin || fechaTexto;
      return new Promise((resolve) => {
        consultarAgenda(fechaInicio, fechaFin, (err, resultado) => {
          if (err) resolve({ status: 'error', mensaje: `${saludo}Error interno, lo siento 😔.` });
          else if (resultado.eventos.length === 0) {
            resolve({
              status: 'success',
              mensaje: `${saludo}No tienes eventos en ese rango, ¡soy Agente Sofía! 😊 ¿Deseas agendar uno?`,
              eventos: []
            });
          } else {
            resolve({
              status: 'success',
              mensaje: `${saludo}Aquí tienes tus eventos, ¡soy Agente Sofía! 😊`,
              eventos: resultado.eventos
            });
          }
        });
      });
    }

    // Si no se detecta ningún intent, se delega a OpenAI.
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: mensaje }
      ],
      max_tokens: 512,
      temperature: 0.1
    });
    const respuestaTexto = completion.choices[0].message.content;
    console.log('Respuesta de OpenAI:', respuestaTexto);
    return { status: 'success', mensaje: `${respuestaTexto}` };

  } catch (err) {
    console.error('Error en chat:', err);
    throw err;
  }
}

module.exports = { procesarMensaje };
