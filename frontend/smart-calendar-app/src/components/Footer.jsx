import React from 'react'

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white mt-auto">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h4 className="text-xl font-bold mb-4 text-blue-400">SmartCalendar</h4>
            <p className="text-sm text-gray-300">
              Tu solución inteligente para la gestión del tiempo
            </p>
          </div>
          
          <div>
            <h5 className="font-semibold mb-4">Producto</h5>
            <ul className="space-y-2 text-sm">
              <li><a href="#features" className="hover:text-blue-400 transition">Funcionalidades</a></li>
              <li><a href="#pricing" className="hover:text-blue-400 transition">Precios</a></li>
              <li><a href="#security" className="hover:text-blue-400 transition">Seguridad</a></li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-semibold mb-4">Legal</h5>
            <ul className="space-y-2 text-sm">
              <li><a href="#privacy" className="hover:text-blue-400 transition">Privacidad</a></li>
              <li><a href="#terms" className="hover:text-blue-400 transition">Términos</a></li>
              <li><a href="#cookies" className="hover:text-blue-400 transition">Cookies</a></li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-semibold mb-4">Contacto</h5>
            <ul className="space-y-2 text-sm">
              <li>support@smartcalendar.com</li>
              <li>+34 123 456 789</li>
              <li>Madrid, España</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>©2025 SmartCalendar. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer