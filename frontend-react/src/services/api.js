import { axiosInstance } from './axiosInstance';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 🔧 fetch centralizado con header para Ngrok
export async function apiFetch(url, options = {}) {
  const headers = {
    'ngrok-skip-browser-warning': 'true',
    ...(options.headers || {})
  };

  const res = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers
  });

  if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
  return await res.json();
}

// 🔹 Funciones con axios (no tocamos esto aún)
export async function getDetecciones(filtros = {}) {
  const filtrosLimpios = Object.fromEntries(
    Object.entries(filtros).filter(([_, val]) => val !== '' && val !== null && val !== undefined)
  );
  const params = new URLSearchParams(filtrosLimpios).toString();

  const response = await axiosInstance.get(`/detecciones/filtro?${params}`);
  return response.data;
}

export const postInferenciaManual = async (formData) => {
  const response = await axiosInstance.post('/detecciones/manual', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};

export const obtenerDetalleDeteccion = async (idDeteccion) => {
  try {
    const response = await axiosInstance.get(`/detecciones/job/detalle/${idDeteccion}`);
    return response.data;
  } catch (error) {
    console.error("❌ Error obteniendo detalle de detección:", error);
    return null;
  }
};

// 🔹 Funciones refactorizadas con apiFetch
export async function cargarImagenManual(data) {
  return await apiFetch('/inferencia/manual', {
    method: 'POST',
    body: data
  });
}

export async function getEstadisticasKPI(filtros = {}) {
  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filtros).filter(([_, v]) => v))
  ).toString();
  return await apiFetch(`/estadisticas/kpi?${params}`);
}

export async function getEstadisticasClases(filtros = {}) {
  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filtros).filter(([_, v]) => v))
  ).toString();
  return await apiFetch(`/estadisticas/clases?${params}`);
}

export async function getEstadisticasTiempo(filtros = {}) {
  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filtros).filter(([_, v]) => v))
  ).toString();
  return await apiFetch(`/estadisticas/tiempo?${params}`);
}

export async function getDronesDisponibles() {
  return await apiFetch('/drones/');
}

export async function getJobsDisponibles() {
  return await apiFetch('/jobs/');
}

export async function crearJob(data) {
  return await apiFetch('/jobs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}

export async function actualizarJob(jobId, data) {
  return await apiFetch(`/jobs/${jobId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}
