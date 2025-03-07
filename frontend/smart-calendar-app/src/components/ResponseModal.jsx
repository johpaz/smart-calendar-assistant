import React from 'react'

const ResponseModal = ({ data, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-2xl font-bold text-blue-600">
            {data.status === "success" ? "✅ Operación exitosa" : "⚠️ Error"}
          </h3>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl transition"
          >
            &times;
          </button>
        </div>
        
        <div className="space-y-4">
          <p className="text-gray-600">{data.mensaje}</p>
          
          {data.evento && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">Detalles del evento:</h4>
              <ul className="space-y-1 text-sm">
                <li><strong>Nombre:</strong> {data.evento.nombre}</li>
                <li><strong>Fecha:</strong> {data.evento.fecha}</li>
                <li><strong>Hora inicio:</strong> {data.evento.hora_inicio}</li>
                <li><strong>Hora fin:</strong> {data.evento.hora_fin}</li>
              </ul>
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="mt-6 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Cerrar
        </button>
      </div>
    </div>
  )
}

export default ResponseModal