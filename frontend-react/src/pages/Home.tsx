// src/pages/Home.tsx
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>🚀 Bienvenido al Sistema de Monitoreo de Cultivos</h1>
      <p>Selecciona un módulo:</p>

      <div style={{ marginTop: "40px" }}>
        <button onClick={() => navigate("/mapa")} style={{ margin: "10px" }}>Ver Mapa de Detecciones</button>
        <button onClick={() => navigate("/inferencia")} style={{ margin: "10px" }}>Subir Imagen para Inferencia</button>
        <button onClick={() => navigate("/dashboard")} style={{ margin: "10px" }}>Dashboard de Análisis</button>
      </div>
    </div>
  );
}
