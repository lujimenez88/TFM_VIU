import React from 'react';
import '../Home.css'; // Importamos estilos propios del Home

function Home() {
  return (
    <div className="home-container">
      <div className="home-content">
        <h1>Bienvenido al Sistema de Detección de Enfermedades en Café</h1>
        <p>Utiliza el menú de navegación para acceder a los módulos.</p>
      </div>
    </div>
  );
}

export default Home;