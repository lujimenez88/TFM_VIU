import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';;

export const getDetecciones = async () => {
  const response = await axios.get(`${API_BASE_URL}/detecciones/job/1`);
  return response.data;
};

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