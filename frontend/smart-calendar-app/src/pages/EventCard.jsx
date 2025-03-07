import React from 'react';

const EventCards = ({ events = [] }) => {
  // Si no hay eventos, se muestra un mensaje
  if (!events.length) {
    return (
      <div className="p-4 text-center text-gray-600">
        No hay eventos disponibles.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {events.map((event) => (
          <div
            key={event.id}
            className="p-4 border-l-4 border-blue-500 bg-gray-50 hover:bg-gray-100 transition-colors rounded"
          >
            <div className="flex flex-col">
              <h4 className="text-xl font-medium text-gray-800 mb-2">
                {event.nombre}
              </h4>
              <p className="text-sm text-gray-600 mb-2">
                {new Date(event.fecha).toLocaleDateString('es-ES', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                {event.hora_inicio} - {event.hora_fin}
              </p>
              <span className="self-start text-xs bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                ID: {event.id}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EventCards;
