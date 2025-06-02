import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';

const FiltrosDetecciones = ({ onFiltrar }) => {
  const [drones, setDrones] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [origenes, setOrigenes] = useState([]);
  const [filtros, setFiltros] = useState({ dron_id: '', job_id: '', origen: '' });

  useEffect(() => {
    apiFetch('/disponibles/drones')
      .then(data => setDrones(data))
      .catch(err => console.error("Error drones:", err));
  }, []);

  useEffect(() => {
    const url = filtros.dron_id
      ? `/disponibles/jobs/?dron_id=${filtros.dron_id}`
      : `/disponibles/jobs/`;

    apiFetch(url)
      .then(data => setJobs(data))
      .catch(err => console.error("Error jobs:", err));
  }, [filtros.dron_id]);

  useEffect(() => {
    if (filtros.job_id) {
      apiFetch(`/disponibles/origenes/?job_id=${filtros.job_id}`)
        .then(data => setOrigenes(data))
        .catch(err => console.error("Error origenes:", err));
    } else {
      setOrigenes(['manual', 'dron']);
    }
  }, [filtros.job_id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const actualizados = { ...filtros, [name]: value };
    setFiltros(actualizados);
    onFiltrar(actualizados);
  };

  return (
    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
      <div>
        <label>Dron:</label>
        <select name="dron_id" value={filtros.dron_id} onChange={handleChange}>
          <option value="">Todos</option>
          {drones.map(d => (
            <option key={d.id} value={d.id}>{`Dron ${d.id} (${d.mac})`}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Job:</label>
        <select name="job_id" value={filtros.job_id} onChange={handleChange}>
          <option value="">Todos</option>
          {jobs.map(j => (
            <option key={j.id} value={j.id}>{`Job ${j.id} (${j.nombre})`}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Origen:</label>
        <select name="origen" value={filtros.origen} onChange={handleChange}>
          <option value="">Todos</option>
          {origenes.map((o, i) => (
            <option key={i} value={o}>{o}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FiltrosDetecciones;
