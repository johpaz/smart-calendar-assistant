# src/services/transcription_service.py
import logging
import os

class TranscriptionService:
    """
    Servicio de transcripción con manejo de diferentes backends.
    """
    def __init__(self, model_size: str = "base"):
        """
        Inicializar servicio de transcripción.
        """
        self.model = None
        self.model_size = model_size
        self._initialize_model()
    
    def _initialize_model(self):
        """
        Inicializar el modelo de transcripción con manejo de errores.
        Verifica si el módulo Whisper tiene la función load_model.
        """
        try:
            import whisper as openai_whisper
            if hasattr(openai_whisper, "load_model"):
                self.model = openai_whisper.load_model(self.model_size)
            else:
                logging.error("El módulo 'whisper' no tiene el atributo 'load_model'. " \
                              "Asegúrate de instalar la versión correcta de openai/whisper.")
                self.model = None
        except ImportError:
            logging.warning("Whisper no está instalado. Usando transcripción de respaldo.")
            self.model = None
        except Exception as e:
            logging.error(f"Error al cargar modelo Whisper: {e}")
            self.model = None
    
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribir archivo de audio.
        """
        # Validar existencia del archivo
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")
        
        # Usar Whisper si está disponible
        if self.model:
            try:
                result = self.model.transcribe(audio_path)
                return result.get("text", "")
            except Exception as e:
                logging.error(f"Error en transcripción con Whisper: {e}")
                return self._transcribe_fallback(audio_path)
        
        # Método de respaldo si Whisper no está disponible
        return self._transcribe_fallback(audio_path)
    
    def _transcribe_fallback(self, audio_path: str) -> str:
        """
        Método de transcripción de respaldo.
        """
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language='es-ES')
                return text
        except ImportError:
            logging.warning("La librería speech_recognition no está instalada.")
            return "Transcripción no disponible. Por favor, proporcione texto."
        except Exception as e:
            logging.error(f"Error en transcripción de respaldo: {e}")
            return "No se pudo transcribir el audio."
    
    def validate_audio(self, audio_path: str) -> bool:
        """
        Validar si el archivo de audio es compatible.
        """
        valid_extensions = ['.wav', '.mp3', '.flac', '.ogg']
        if not os.path.exists(audio_path):
            return False
        
        _, ext = os.path.splitext(audio_path)
        return ext.lower() in valid_extensions
