import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const elements = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('opacity-100');
        }
      });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return (
    <div className="bg-gradient-to-b from-blue-600 to-blue-700">
      {/* Hero Section */}
      <section className="relative text-white h-screen flex items-center justify-center px-4 overflow-hidden">
        <div className="absolute inset-0 bg-black/60">
          <img 
            src="/background.png" 
            alt="Background" 
            className="w-full h-full object-cover animate-zoom"
          />
        </div>
        
        <div className="relative z-10 max-w-6xl mx-auto text-center space-y-8">
          <h1 className="text-4xl md:text-7xl font-bold mb-6 animate-slide-down bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
            Smart Calendar Assistant
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-0 fade-in transition-opacity duration-1000 md:max-w-2xl mx-auto leading-relaxed">
            Revoluciona tu gestión del tiempo con inteligencia artificial predictiva y automatización inteligente
          </p>
          <button 
            onClick={() => navigate('/chat')}
            className="bg-white/90 text-blue-600 px-8 py-4 rounded-xl font-bold hover:scale-105 transition-all 
                      duration-300 shadow-2xl hover:shadow-blue-500/30 text-lg animate-pulse-slow"
          >
            Comenzar Ahora ➔
          </button>
        </div>

        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce-slow">
          <div className="w-8 h-14 rounded-3xl border-4 border-white flex justify-center p-1">
            <div className="w-2 h-2 bg-white rounded-full animate-scroll-indicator"></div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16 text-blue-600">
            Características Principales
          </h2>
          
          <div className="grid md:grid-cols-3 gap-12">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-white shadow-lg hover:shadow-xl 
                          transition-shadow duration-300 hover:-translate-y-2 group border border-blue-100"
              >
                <div className="w-16 h-16 rounded-xl bg-blue-600 flex items-center justify-center mb-6">
                  <span className="text-3xl text-white">{feature.icon}</span>
                </div>
                <h3 className="text-xl font-bold mb-4 text-blue-900">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
<section className="py-20 bg-blue-50 px-4">
  <div className="max-w-4xl mx-auto">
    <h2 className="text-3xl md:text-4xl font-bold text-center mb-16 text-blue-600">
      Opiniones de Usuarios
    </h2>
    <div className="space-y-12">
      {testimonials.map((testimonial, index) => (
        <div 
          key={index}
          className="bg-white p-8 rounded-2xl shadow-md border-l-4 border-blue-600 opacity-0 fade-in"
        >
          <p className="text-gray-600 italic mb-4">"{testimonial.text}"</p>
          <div className="flex items-center gap-4">
            <img 
              src={testimonial.avatar} 
              alt={testimonial.name} 
              className="w-12 h-12 rounded-full object-cover border-2 border-blue-100 shadow-sm"
              onError={(e) => {
                e.target.onerror = null; 
                e.target.src = 'https://via.placeholder.com/48';
              }}
            />
            <div>
              <p className="font-bold text-blue-900">{testimonial.name}</p>
              <p className="text-sm text-gray-500">{testimonial.role}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
</section>

      {/* CTA Section */}
      <section className="py-20 bg-white px-4">
        <div className="max-w-4xl mx-auto text-center bg-blue-600 rounded-3xl p-12 shadow-2xl">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-8">
            ¿Listo para transformar tu productividad?
          </h2>
          <button
            onClick={() => navigate('/chat')}
            className="bg-white text-blue-600 px-10 py-5 rounded-xl font-bold text-lg
                      hover:scale-105 transition-transform duration-300 shadow-lg hover:shadow-xl"
          >
            Comienza Gratis Hoy Mismo
          </button>
        </div>
      </section>
    </div>
  )
}

const features = [
  {
    icon: '⏳',
    title: "Programación Inteligente",
    description: "Nuestra IA analiza tus patrones y sugiere horarios óptimos para maximizar tu productividad"
  },
  {
    icon: '🤖',
    title: "Asistente Automático",
    description: "Delega reuniones y coordinación de horarios a nuestro asistente virtual inteligente"
  },
  {
    icon: '🔮',
    title: "Predicciones Precisa",
    description: "Anticipa conflictos de horarios y recibe recomendaciones proactivas basadas en tu historial"
  }
]

const testimonials = [
  {
    text: "Este asistente ha cambiado completamente mi forma de trabajar. Ahora tengo un 40% más de tiempo libre!",
    name: "Laura Martínez",
    role: "CEO en TechSolutions",
    avatar: "https://images.pexels.com/photos/53000/girl-beautiful-young-face-53000.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
  },
  {
    text: "La integración perfecta entre IA y calendario que necesitábamos. Increíblemente intuitivo.",
    name: "Carlos Gómez",
    role: "Director de Proyectos",
    avatar: "https://images.pexels.com/photos/7823/selfie.jpg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
  }
]

export default Home;