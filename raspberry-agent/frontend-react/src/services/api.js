import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';;

/*export const getDetecciones = async () => {
  const response = await axios.get(`${API_BASE_URL}/detecciones/job/1`);
  return response.data;
};*/

export async function getDetecciones(filtros = {}) {
  // Eliminar claves vacías o nulas
  const filtrosLimpios = Object.fromEntries(
    Object.entries(filtros).filter(([_, val]) => val !== '' && val !== null && val !== undefined)
  );
  const params = new URLSearchParams(filtrosLimpios).toString();
  const response = await axios.get(`${API_BASE_URL}/detecciones/filtro?${params}`);

  return response.data;
}

export const postInferenciaManual = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/detecciones/manual`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// 🚀 Consulta detalle de una detección por ID
export const obtenerDetalleDeteccion = async (idDeteccion) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/detecciones/job/detalle/${idDeteccion}`);
    return response.data;
  } catch (error) {
    console.error("❌ Error obteniendo detalle de detección:", error);
    return null;
  }
};
export async function cargarImagenManual(data) {
  const response = await fetch(`${API_BASE_URL}/inferencia/manual`, {
    method: 'POST',
    body: data // debe ser FormData
  });
  if (!response.ok) throw new Error('Error en la inferencia');
  return await response.json();
}

export async function getEstadisticasKPI(filtros = {}) {
  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filtros).filter(([_, v]) => v))
  ).toString();
  const res = await fetch(`${API_BASE_URL}/estadisticas/kpi?${params}`);
  return await res.json();
}

export async function getEstadisticasClases(filtros = {}) {
  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filtros).filter(([_, v]) => v))
  ).toString();
  const res = await fetch(`${API_BASE_URL}/estadisticas/clases?${params}`);
  return await res.json();
}

export async function getEstadisticasTiempo(filtros = {}) {
  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filtros).filter(([_, v]) => v))
  ).toString();
  const res = await fetch(`${API_BASE_URL}/estadisticas/tiempo?${params}`);
  return await res.json();
}

export async function getDronesDisponibles() {
  const res = await fetch(`${API_BASE_URL}/drones/`);
  return await res.json();
}

export async function getJobsDisponibles() {
  const res = await fetch(`${API_BASE_URL}/jobs/`);
  return await res.json();
}

export async function crearJob(data) {
  const res = await fetch(`${API_BASE_URL}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await res.json();
}

export async function actualizarJob(jobId, data) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await res.json();
}
