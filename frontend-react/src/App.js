import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import VerMapa from './pages/VerMapa';
import CargarManual from './pages/CargarManual';
import DashboardBI from './pages/DashboardBI';
import GestorJobs from './pages/GestorJobs';
import './App.css'; // Nos aseguramos de importar los estilos
import './theme.css';

function App() {
  return (
    <div>
      <nav className="navbar">
        <div className="navbar-logo">☕ De la hoja a la nube </div>
        <ul className="navbar-links">
          <li><Link to="/">Inicio</Link></li>
          <li><Link to="/gestor-jobs">Gestor de Jobs</Link></li>
          <li><Link to="/ver-mapa">Ver Mapa</Link></li>
          <li><Link to="/inferencia-manual">Inferencia Manual</Link></li>
          <li><Link to="/dashboard-bi">Dashboard BI</Link></li>
        </ul>
      </nav>

      <div className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/gestor-jobs" element={<GestorJobs />} />
          <Route path="/ver-mapa" element={<VerMapa />} />
          <Route path="/inferencia-manual" element={<CargarManual />} />
          <Route path="/dashboard-bi" element={<DashboardBI />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
