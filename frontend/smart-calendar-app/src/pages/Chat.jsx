import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import EventCards from './EventCard';

const API_BASE_URL = 'http://localhost:3000';

const Chat = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const audioChunks = useRef([]);
  const mediaStreamRef = useRef(null);

  useEffect(() => {
    const initializeMediaRecorder = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaStreamRef.current = stream;
        
        const newMediaRecorder = new MediaRecorder(stream);
        newMediaRecorder.ondataavailable = (e) => {
          audioChunks.current.push(e.data);
        };
        
        newMediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
          setAudioBlob(audioBlob);
          audioChunks.current = [];
        };
        
        setMediaRecorder(newMediaRecorder);
      } catch (err) {
        setError('Microphone access required for audio recording');
      }
    };

    initializeMediaRecorder();

    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now(),
      content: inputText,
      isBot: false,
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    inputRef.current.focus();

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje: inputText })
      });

      if (!response.ok) throw new Error('Server error');

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        content: data.mensaje,
        events: data.eventos || [],
        isBot: true,
        type: 'text'
      }]);
    } catch (err) {
      setError('Error fetching server response');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      mediaRecorder.stop();
    } else {
      audioChunks.current = [];
      mediaRecorder.start();
    }
    setIsRecording(!isRecording);
  };

  const handleAudioSubmit = async () => {
    if (!audioBlob) return;

    const userAudioMessage = {
      id: Date.now(),
      content: URL.createObjectURL(audioBlob),
      isBot: false,
      type: 'audio'
    };

    setMessages(prev => [...prev, userAudioMessage]);
    setIsLoading(true);
    inputRef.current.focus();

    try {
      const formData = new FormData();
      const mimeType = audioBlob.type.split(';')[0];
      const ext = mimeType.split('/')[1] || 'wav';
      formData.append('audio', audioBlob, `recording.${ext}`);

      const response = await fetch(`${API_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Audio processing failed');

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        content: data.response.mensaje,
        events: data.response.eventos || [],
        isBot: true,
        type: 'text'
      }]);
    } catch (err) {
      setError('Error processing audio');
    } finally {
      setAudioBlob(null);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-150 bg-gray-100">
      <header className="bg-blue-600 p-4 text-white flex justify-between items-center shadow-lg">
        <h1 className="text-2xl font-bold">Smart Calendar Assistant</h1>
        <button 
          onClick={() => navigate('/')}
          className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-transform transform hover:scale-105"
          aria-label="Return to home"
        >
          Volver al Inicio
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-blue-50 to-gray-100">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isBot ? 'justify-start' : 'justify-end'} mb-4`}
          >
            <div
              className={`max-w-3xl w-full p-4 rounded-2xl ${
                message.isBot 
                  ? 'bg-white text-gray-800 shadow-md'
                  : 'bg-blue-600 text-white shadow-lg'
              } transition-all duration-200 ease-out`}
            >
              {message.type === 'audio' ? (
                <audio controls className="w-full">
                  <source src={message.content} type="audio/wav" />
                  Your browser does not support HTML5 audio
                </audio>
              ) : (
                <div className="space-y-3">
                  <p className="text-lg">{message.content}</p>
                  {message.events?.length > 0 && <EventCards events={message.events} />}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white p-4 rounded-2xl shadow-md">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-gray-300 rounded-full animate-bounce"></div>
                <div className="w-3 h-3 bg-gray-300 rounded-full animate-bounce delay-100"></div>
                <div className="w-3 h-3 bg-gray-300 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t bg-white p-4 shadow-lg">
        {error && (
          <div className="text-red-500 mb-2 flex justify-between items-center bg-red-50 p-3 rounded-lg">
            <span>{error}</span>
            <button 
              onClick={() => setError('')}
              className="text-red-700 hover:text-red-900 text-xl"
              aria-label="Close error"
            >
              ×
            </button>
          </div>
        )}
        
        <div className="flex items-center gap-4">
          <form onSubmit={handleTextSubmit} className="flex-1">
            <div className="flex gap-4">
              <input
                ref={inputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Escribe tu mensaje..."
                className="flex-1 p-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                disabled={isRecording || isLoading}
                aria-label="Type your message"
                autoFocus
              />
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-all disabled:opacity-50 flex items-center gap-2"
                disabled={isRecording || isLoading}
                aria-label="Send text message"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
                Enviar
              </button>
            </div>
          </form>

          <div className="flex items-center gap-4">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-full ${
                isRecording 
                  ? 'bg-red-500 animate-pulse' 
                  : 'bg-blue-600 hover:bg-blue-700'
              } text-white transition-all transform hover:scale-105 disabled:opacity-50`}
              disabled={isLoading}
              aria-label={isRecording ? "Stop recording" : "Start recording"}
            >
              {isRecording ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                </svg>
              )}
            </button>

            {audioBlob && (
              <button
                onClick={handleAudioSubmit}
                className="bg-green-600 text-white px-6 py-3 rounded-xl hover:bg-green-700 transition-all disabled:opacity-50 flex items-center gap-2"
                disabled={isLoading}
                aria-label="Send audio recording"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
                Enviar Audio
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;