import React, { useEffect, useState } from 'react';
import FiltrosDetecciones from '../components/FiltrosDetecciones';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';;

const Dashboard = () => {
  const [filtros, setFiltros] = useState({});
  const [kpis, setKpis] = useState(null);
  const [porClase, setPorClase] = useState([]);
  const [porTiempo, setPorTiempo] = useState([]);

  const colores = ['#8884d8', '#82ca9d', '#ffc658', '#ff6e54', '#a4de6c'];

  useEffect(() => {
    const query = new URLSearchParams(
      Object.fromEntries(
        Object.entries(filtros).filter(([_, val]) => val !== '' && val !== null)
      )
    ).toString();

    fetch(`${API_BASE_URL}/estadisticas/kpi?${query}`)
      .then(res => res.json())
      .then(setKpis);

    fetch(`${API_BASE_URL}/estadisticas/clases?${query}`)
      .then(res => res.json())
      .then(setPorClase);

    fetch(`${API_BASE_URL}/estadisticas/tiempo?${query}`)
      .then(res => res.json())
      .then(setPorTiempo);
  }, [filtros]);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>📊 Panel de Estadísticas</h2>
      <FiltrosDetecciones onFiltrar={setFiltros} />

      {kpis && (
        <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
          <div style={{ background: '#f3f3f3', padding: '15px', borderRadius: '10px' }}>
            <h4>🖼️ Imágenes Procesadas</h4>
            <p>{kpis.total_imagenes}</p>
          </div>
          <div style={{ background: '#f3f3f3', padding: '15px', borderRadius: '10px' }}>
            <h4>📦 Total Detecciones</h4>
            <p>{kpis.total_detecciones}</p>
          </div>
          <div style={{ background: '#f3f3f3', padding: '15px', borderRadius: '10px' }}>
            <h4>🦠 % Enfermas</h4>
            <p>{kpis.porcentaje_enfermas} %</p>
          </div>
          <div style={{ background: '#f3f3f3', padding: '15px', borderRadius: '10px' }}>
            <h4>📅 Última detección</h4>
            <p>{kpis.ultima_deteccion}</p>
          </div>
        </div>
      )}

      <div style={{ marginTop: '40px' }}>
        <h4>📈 Evolución Temporal</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={porTiempo}>
            <XAxis dataKey="periodo" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="total" stroke="#007bff" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: 'flex', gap: '30px', marginTop: '40px' }}>
        <div style={{ flex: 1 }}>
          <h4>🍃 Detecciones por Clase</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={porClase}>
              <XAxis dataKey="class_name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: 1 }}>
          <h4>🎯 Distribución de Clases</h4>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={porClase}
                dataKey="total"
                nameKey="class_name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {porClase.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colores[index % colores.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
