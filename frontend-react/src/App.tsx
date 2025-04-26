// src/App.tsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import MapView from "./pages/MapView";
import Inferencia from "./pages/Inferencia";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />          {/* Home es la página inicial */}
        <Route path="/mapa" element={<MapView />} />    {/* Módulo de mapa */}
        <Route path="/inferencia" element={<Inferencia />} /> {/* Módulo de subir imagen */}
        <Route path="/dashboard" element={<Dashboard />} />  {/* Módulo de dashboard */}
      </Routes>
    </Router>
  );
}
