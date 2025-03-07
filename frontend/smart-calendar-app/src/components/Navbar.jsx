import { Link } from 'react-router-dom';
import './navbar.css';
const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-blue-100 shadow-sm hover:shadow-md transition-shadow duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link 
            to="/" 
            className="flex items-center space-x-2 group"
          >
            <img 
              src="/logo.jpeg" 
              alt="Logo SmartCalendar" 
              className="h-10 w-10 rounded-lg group-hover:rotate-[15deg] transition-all duration-300 hover:shadow-lg"
            />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              SmartCalendar
            </span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className="relative text-gray-600 hover:text-blue-600 px-2 py-1 transition-all duration-300
                         before:content-[''] before:absolute before:bottom-0 before:left-0 before:w-0 before:h-[2px] 
                         before:bg-blue-600 before:transition-all before:duration-300 hover:before:w-full"
            >
              Inicio
            </Link>
            <Link 
              to="/chat" 
              className="relative text-gray-600 hover:text-blue-600 px-2 py-1 transition-all duration-300
                         before:content-[''] before:absolute before:bottom-0 before:left-0 before:w-0 before:h-[2px] 
                         before:bg-blue-600 before:transition-all before:duration-300 hover:before:w-full"
            >
              Chat
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar;

