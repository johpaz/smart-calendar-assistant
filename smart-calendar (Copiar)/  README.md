# **Proyecto: Asistente de Agenda Inteligente con RAG**

Este proyecto implementa un **Asistente de Agenda Inteligente** utilizando la técnica **RAG (Retrieval-Augmented Generation)**. El sistema combina la recuperación de información relevante desde una base de datos SQLite con la generación de respuestas naturales usando un modelo de lenguaje avanzado. Para la recuperación, se utiliza **Pinecone** como índice vectorial.

---

## **Tabla de Contenidos**
1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Requisitos Previos](#requisitos-previos)
3. [Instalación](#instalación)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Configuración](#configuración)
6. [Ejecución](#ejecución)
7. [Contribuciones](#contribuciones)
8. [Licencia](#licencia)

---

## **Descripción del Proyecto**

El **Asistente de Agenda Inteligente** permite a los usuarios interactuar con su agenda mediante mensajes de texto. Utiliza la técnica **RAG** para:
- Recuperar eventos relevantes de una base de datos SQLite.
- Almacenar embeddings de eventos en **Pinecone** para búsquedas rápidas.
- Generar respuestas naturales basadas en los datos recuperados.

El sistema está diseñado para manejar consultas como:
- "¿Qué reuniones tengo hoy?"
- "Cancela la reunión de equipo."
- "Agenda una nueva reunión."

---

## **Requisitos Previos**

Antes de comenzar, asegúrate de tener instalado lo siguiente:

### **Software**
1. **Python 3.13** o superior.
2. Pip (gestor de paquetes de Python).
3. Una base de datos SQLite.
4. Una cuenta en **Pinecone** para el almacenamiento vectorial.
5. Una API de modelo de lenguaje (por ejemplo, OpenAI API).

### **API Keys**
- Si usas OpenAI, necesitarás una clave de API. Puedes obtenerla en [OpenAI](https://platform.openai.com/).
- Necesitarás una clave de API de Pinecone. Regístrate en [Pinecone](https://www.pinecone.io/).

### **Bibliotecas Requeridas**
Instala las dependencias necesarias ejecutando:
```bash
pip install -r requirements.txt

Instalación
1 Clona este repositorio:
git clone https://github.com/tu-usuario/asistente-agenda-rag.git
cd asistente-agenda-rag
2.Instala las dependencias:
pip install -r requirements.txt
3.Configura las variables de entorno (ver sección de configuración).

Estructura del Proyecto
El proyecto está organizado de la siguiente manera:
/proyecto-agenda-rag
    /data               # Datos iniciales (agenda simulada, embeddings)
        agenda.csv      # Datos de ejemplo
    /db                 # Código relacionado con la base de datos
        database.py     # Conexión y consultas SQL
    /langgraph          # Código relacionado con LangGraph
        agent.py        # Definición del agente conversacional
        retrieval.py    # Componente de recuperación (Pinecone)
        generation.py   # Componente de generación (OpenAI)
    /api                # API REST (opcional)
        app.py          # Servidor Flask/FastAPI
    README.md           # Documentación del proyecto
    requirements.txt    # Dependencias del proyecto
    .env                # Variables de entorno


Configuración
1. Base de Datos (SQLite)
Crea una base de datos SQLite y configura la tabla de eventos. Ejecuta el siguiente script SQL:
CREATE TABLE eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    fecha TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fin TEXT NOT NULL
);
Inserta algunos eventos iniciales para probar el sistema:
INSERT INTO eventos (nombre, fecha, hora_inicio, hora_fin)
VALUES
('Reunión de equipo', '2025-03-10', '14:00', '15:00'),
('Llamada con cliente', '2025-03-10', '13:30', '14:30');

2. Pinecone
    1. Regístrate en Pinecone y obtén tu API Key .
    2.Crea un índice en Pinecone para almacenar los embeddings de tus eventos.
    3.Configura Pinecone en el archivo .env (ver más abajo).
3. Variables de Entorno
Crea un archivo .env en la raíz del proyecto y configura las siguientes variables:
OPENAI_API_KEY=tu_api_key_de_openai
PINECONE_API_KEY=tu_api_key_de_pinecone
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=nombre_del_indice
DATABASE_URL=sqlite:///db/agenda.db

4. Embeddings
Genera embeddings para tus eventos usando un modelo preentrenado (por ejemplo, Sentence Transformers). Guarda los embeddings en Pinecone.

Ejecución
1. Iniciar el Agente Conversacional
Ejecuta el siguiente comando para iniciar el agente:

python langgraph/agent.py
2. Interactuar con el Sistema
Abre una terminal y envía consultas al sistema. Por ejemplo:
Usuario: ¿Qué reuniones tengo hoy?
Asistente: Hoy tienes las siguientes reuniones:
- Reunión de equipo de 14:00 a 15:00.
- Llamada con cliente de 13:30 a 14:30.
3. (Opcional) Desplegar la API REST
Si deseas exponer el sistema como un servicio web, ejecuta:
python api/app.py
Contribuciones
¡Las contribuciones son bienvenidas! Si deseas mejorar este proyecto, sigue estos pasos:

Haz un fork del repositorio.
Crea una rama para tu feature (git checkout -b feature/nueva-funcionalidad).
Realiza tus cambios y haz commit (git commit -m "Añade nueva funcionalidad").
Sube tus cambios (git push origin feature/nueva-funcionalidad).
Abre un pull request.

Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.


---

### **Cómo Usarlo**
1. Copia el contenido anterior en un archivo llamado `README.md` en la raíz de tu proyecto.
2. Asegúrate de actualizar los valores de las variables de entorno en el archivo `.env` con tus claves reales.
3. Sigue las instrucciones de instalación y configuración para ejecutar el proyecto.

Con este archivo `README.md`, tienes una guía completa y profesional para estructurar y documentar tu proyecto RAG.

**Respuesta final:** **{Archivo README.md proporcionado en formato Markdown listo para usar.}**

