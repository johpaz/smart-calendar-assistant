const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs');
const { procesarMensaje } = require('./chat');
const db = require('./database');
require('dotenv').config();
const path = require('path');
const ffmpeg = require('fluent-ffmpeg');
const OpenAI = require('openai');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const openai = new OpenAI({ apiKey: process.env.API_KEY });
// Configurar multer para guardar archivos temporalmente en la carpeta "uploads/"
const upload = multer({ dest: 'uploads/' });

// Tu endpoint /chat existente
app.post('/chat', async (req, res) => {
  const { mensaje } = req.body;
  
  if (!mensaje) {
    return res.json({ status: 'error', mensaje: 'Envía un mensaje, ¡soy Agente Sofía y quiero ayudarte! 😊' });
  }
  
  try {
    const respuesta = await procesarMensaje(mensaje);
    res.json(respuesta);
  } catch (err) {
    console.error('Error detallado:', err);
    res.json({ status: 'error', mensaje: `Error procesando la solicitud, lo siento 😔. Detalle: ${err.message}` });
  }
});

// Nuevo endpoint para consultar eventos directamente
app.get('/eventos', (req, res) => {
  const { fechaInicio, fechaFin } = req.query;
  const inicio = fechaInicio || '2025-01-01';
  const fin = fechaFin || '2025-12-31';
  
  const query = 'SELECT * FROM eventos WHERE fecha BETWEEN ? AND ? ORDER BY fecha, hora_inicio';
  db.all(query, [inicio, fin], (err, rows) => {
    if (err) {
      console.error('Error al consultar la BD:', err);
      return res.status(500).json({ status: 'error', mensaje: 'Error al consultar la base de datos.' });
    }
    res.json({
      status: 'success',
      mensaje: 'Eventos encontrados.',
      eventos: rows
    });
  });
});

/// Endpoint para transcribir audio y procesarlo en el flujo de conversación
// Endpoint para transcribir audio, convirtiéndolo a WAV si es necesario
app.post('/transcribe', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ status: 'error', mensaje: 'No se recibió archivo de audio.' });
    }
    const originalPath = req.file.path;
    // Definir ruta de salida: convertiremos el archivo a formato WAV
    const outputPath = `${originalPath}.wav`;

    // Convertir el audio a WAV usando ffmpeg
    ffmpeg(originalPath)
      .toFormat('wav')
      .on('end', async () => {
        try {
          // Se utiliza el modelo "whisper-1" para la transcripción con el archivo convertido
          const transcriptionResponse = await openai.audio.transcriptions.create({
            file: fs.createReadStream(outputPath),
            model: 'whisper-1'
          });
          
          // Eliminamos los archivos temporales (original y convertido)
          fs.unlink(originalPath, (err) => { if (err) console.error('Error eliminando el archivo original:', err); });
          fs.unlink(outputPath, (err) => { if (err) console.error('Error eliminando el archivo convertido:', err); });
          
          const transcribedText = transcriptionResponse.text;
          console.log('Transcripción:', transcribedText);
          
          // Integramos la transcripción al flujo de conversación
          const respuesta = await procesarMensaje(transcribedText);
          res.json({
            status: 'success',
            transcribedText,
            response: respuesta
          });
        } catch (err) {
          console.error('Error en la transcripción:', err);
          res.status(500).json({ status: 'error', mensaje: 'Error en la transcripción.', error: err.message });
        }
      })
      .on('error', (err) => {
        console.error('Error al convertir el audio:', err);
        res.status(500).json({ status: 'error', mensaje: 'Error al convertir el audio.', error: err.message });
      })
      .save(outputPath);
  } catch (err) {
    console.error('Error en el endpoint /transcribe:', err);
    res.status(500).json({ status: 'error', mensaje: 'Error en la transcripción.', error: err.message });
  }
});

app.listen(3000, () => {
  console.log('Servidor corriendo en puerto 3000');
});
