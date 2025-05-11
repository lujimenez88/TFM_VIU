import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import VerMapa from './pages/VerMapa';
import CargarManual from './pages/CargarManual';
import DashboardBI from './pages/DashboardBI';
import './App.css'; // Nos aseguramos de importar los estilos

function App() {
  return (
    <div>
      <nav className="navbar">
        <div className="navbar-logo">☕ CoffeeAI</div>
        <ul className="navbar-links">
          <li><Link to="/">Inicio</Link></li>
          <li><Link to="/ver-mapa">Ver Mapa</Link></li>
          <li><Link to="/inferencia-manual">Inferencia Manual</Link></li>
          <li><Link to="/dashboard-bi">Dashboard BI</Link></li>
        </ul>
      </nav>

      <div className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/ver-mapa" element={<VerMapa />} />
          <Route path="/inferencia-manual" element={<CargarManual />} />
          <Route path="/dashboard-bi" element={<DashboardBI />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
