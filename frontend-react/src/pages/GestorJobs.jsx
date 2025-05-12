import React, { useEffect, useState } from 'react';
import { getDronesDisponibles, getJobsDisponibles, crearJob } from '../services/api';

const GestorJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [drones, setDrones] = useState([]);
  const [form, setForm] = useState({ nombre: '', descripcion: '', dron_id: '' });

  const cargarDrones = async () => {
    const data = await getDronesDisponibles();
    setDrones(data);
  };

  const cargarJobs = async () => {
    const data = await getJobsDisponibles();
    setJobs(data);
  };

  useEffect(() => {
    cargarDrones();
    cargarJobs();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleCrearJob = async () => {
    if (!form.nombre || !form.dron_id) return alert("Faltan campos obligatorios");
    const nuevo = await crearJob({ ...form, dron_id: parseInt(form.dron_id) });
    if (nuevo && nuevo.id) {
      setForm({ nombre: '', descripcion: '', dron_id: '' });
      cargarJobs();
    } else {
      alert("No se pudo crear el job. Es posible que el dron ya tenga un job activo.");
    }
  };

  const renderEstado = (estado) => {
    const estilos = {
      activo: { color: 'green', fontWeight: 'bold' },
      finalizado: { color: 'gray', fontStyle: 'italic' }
    };
    return <span style={estilos[estado] || {}}>{estado}</span>;
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>🚀 Crear nuevo Job</h2>
      <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '400px', gap: '10px', marginBottom: '30px' }}>
        <input name="nombre" placeholder="Nombre del Job" value={form.nombre} onChange={handleChange} />
        <textarea name="descripcion" placeholder="Descripción" value={form.descripcion} onChange={handleChange} />
        <select name="dron_id" value={form.dron_id} onChange={handleChange}>
          <option value="">Seleccione un dron</option>
          {drones.map(d => (
            <option key={d.id} value={d.id}>{`Dron ${d.id} (${d.mac})`}</option>
          ))}
        </select>
        <button onClick={handleCrearJob} style={{ padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '6px' }}>➕ Crear Job</button>
      </div>

      <h3 style={{ marginTop: '20px' }}>📋 Lista de Jobs</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', fontSize: '14px' }}>
        <thead>
          <tr style={{ backgroundColor: '#f2f2f2' }}>
            <th style={{ padding: '8px', border: '1px solid #ddd' }}>ID</th>
            <th style={{ padding: '8px', border: '1px solid #ddd' }}>Nombre</th>
            <th style={{ padding: '8px', border: '1px solid #ddd' }}>Dron</th>
            <th style={{ padding: '8px', border: '1px solid #ddd' }}>Estado</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job, i) => (
            <tr key={job.id} style={{ backgroundColor: i % 2 === 0 ? '#fff' : '#f9f9f9' }}>
              <td style={{ padding: '8px', border: '1px solid #ddd' }}>{job.id}</td>
              <td style={{ padding: '8px', border: '1px solid #ddd' }}>{job.nombre}</td>
              <td style={{ padding: '8px', border: '1px solid #ddd' }}>{job.dron_id}</td>
              <td style={{ padding: '8px', border: '1px solid #ddd' }}>{renderEstado(job.estado)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GestorJobs;
