import React, { useState, useRef } from 'react';
import { cargarImagenManual } from '../services/api';
import ImagenConDetecciones from '../components/ImagenConDetecciones';
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

const CargarManual = () => {
  const [imageFile, setImageFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [jobId, setJobId] = useState('');
  const [altura, setAltura] = useState(15.0);
  const [fov, setFov] = useState(62.2);
  const [objetivoCm, setObjetivoCm] = useState(15.0);
  const [resultados, setResultados] = useState(null);
  const [coordenadas, setCoordenadas] = useState({ lat: null, lon: null });
  const fileInputRef = useRef();
  const [cargando, setCargando] = useState(false);

  const obtenerUbicacion = () => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoordenadas({ lat: pos.coords.latitude, lon: pos.coords.longitude });
      },
      () => {
        alert('No se pudo obtener la ubicación.');
      }
    );
  };

  const handleImagenChange = (e) => {
    const file = e.target.files[0];
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleEnviar = async () => {
    if (!imageFile) {
      alert('Selecciona una imagen.');
      return;
    }

    if (!coordenadas.lat || !coordenadas.lon) {
      alert('Ubicación no detectada.');
      return;
    }

    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('lat', coordenadas.lat);
    formData.append('lon', coordenadas.lon);
    formData.append('altura_m', altura);
    formData.append('fov', fov);
    formData.append('objetivo_cm', objetivoCm);
    formData.append('job_id', jobId || 1);
    setCargando(true);
    try {
      const response = await cargarImagenManual(formData);
      setResultados(response);
    } catch (err) {
      console.error(err);
      alert('Error al enviar la imagen');
    }
    finally{
        setCargando(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: 'auto', fontFamily: 'sans-serif' }}>
        {cargando && (
  <div
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.6)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9998
    }}
  >
    <div
      style={{
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '10px',
        boxShadow: '0 0 10px black',
        textAlign: 'center'
      }}
    >
      <h3>🧠 Ejecutando inferencia...</h3>
      <p>Esto puede tardar unos segundos ⏳</p>
    </div>
  </div>
)}
      <h2>🖼️ Cargar Imagen Manual para Inferencia</h2>

      <button
        onClick={obtenerUbicacion}
        style={{
          marginBottom: '10px',
          padding: '10px',
          borderRadius: '8px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          cursor: 'pointer'
        }}
        onMouseOver={e => e.currentTarget.style.backgroundColor = '#45a049'}
        onMouseOut={e => e.currentTarget.style.backgroundColor = '#4CAF50'}
      >
        📍 Obtener Ubicación Actual
      </button>

      <div style={{ marginTop: '10px' }}>
        <input type="file" accept="image/*" onChange={handleImagenChange} ref={fileInputRef} />
      </div>

      <div style={{ marginTop: '10px' }}>
        <label>Altura de Vuelo (m):</label>
        <input type="number" value={altura} onChange={(e) => setAltura(e.target.value)} step="0.1" />
      </div>

      <div>
        <label>FOV Horizontal (°):</label>
        <input type="number" value={fov} onChange={(e) => setFov(e.target.value)} step="0.1" />
      </div>

      <div>
        <label>Tamaño objetivo (cm):</label>
        <input type="number" value={objetivoCm} onChange={(e) => setObjetivoCm(e.target.value)} step="0.1" />
      </div>

      <div>
        <label>ID Job (opcional):</label>
        <input type="number" value={jobId} onChange={(e) => setJobId(e.target.value)} />
      </div>

      <button
        onClick={handleEnviar}
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          borderRadius: '8px',
          backgroundColor: '#2196F3',
          color: 'white',
          border: 'none',
          cursor: 'pointer'
        }}
        onMouseOver={e => e.currentTarget.style.backgroundColor = '#1976D2'}
        onMouseOut={e => e.currentTarget.style.backgroundColor = '#2196F3'}
      >
        🚀 Enviar para Inferencia
      </button>

      {preview && (
        <div style={{ marginTop: '20px' }}>
          <h4>📷 Vista previa</h4>
          <img src={preview} alt="preview" style={{ maxWidth: '100%' }} />
        </div>
      )}

      {resultados && resultados.image_url && Array.isArray(resultados.detalles) && (
        <div
          onClick={() => setResultados(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: "white",
              padding: "20px",
              borderRadius: "8px",
              maxWidth: "90vw",
              maxHeight: "90vh",
              overflowY: "auto",
              boxShadow: "0 0 10px black"
            }}
          >
            <h3>🧪 Resultados de Inferencia</h3>
            <TransformWrapper>
                        <TransformComponent>
            <ImagenConDetecciones
              imageUrl={resultados.image_url}
              boundingBoxes={resultados.detalles || []}
            />
            </TransformComponent>
            </TransformWrapper>

            <h4 style={{ marginTop: "20px" }}>🧾 Detalles de detecciones</h4>
            <table style={{ width: "100%", marginTop: "10px", borderCollapse: "collapse" }}>
              <thead style={{ backgroundColor: "#f5f5f5" }}>
                <tr>
                  <th style={{ border: "1px solid #ccc", padding: "8px" }}>Clase</th>
                  <th style={{ border: "1px solid #ccc", padding: "8px" }}>Confianza</th>
                  <th style={{ border: "1px solid #ccc", padding: "8px" }}>x1</th>
                  <th style={{ border: "1px solid #ccc", padding: "8px" }}>y1</th>
                  <th style={{ border: "1px solid #ccc", padding: "8px" }}>x2</th>
                  <th style={{ border: "1px solid #ccc", padding: "8px" }}>y2</th>
                </tr>
              </thead>
              <tbody>
                {resultados.detalles.map((d, i) => (
                  <tr key={i} style={{ textAlign: "center" }}>
                    <td style={{ border: "1px solid #ccc", padding: "6px" }}>{d.class_name}</td>
                    <td style={{ border: "1px solid #ccc", padding: "6px" }}>{d.confidence.toFixed(2)}</td>
                    <td style={{ border: "1px solid #ccc", padding: "6px" }}>{Math.round(d.x1)}</td>
                    <td style={{ border: "1px solid #ccc", padding: "6px" }}>{Math.round(d.y1)}</td>
                    <td style={{ border: "1px solid #ccc", padding: "6px" }}>{Math.round(d.x2)}</td>
                    <td style={{ border: "1px solid #ccc", padding: "6px" }}>{Math.round(d.y2)}</td>
                  </tr>
                ))}
              </tbody>
              {/* <tbody>
                {resultados.detalles.map((d, i) => (
                  <tr key={i}>
                    <td>{d.class_name}</td>
                    <td>{d.confidence.toFixed(2)}</td>
                    <td>{Math.round(d.x1)}</td>
                    <td>{Math.round(d.y1)}</td>
                    <td>{Math.round(d.x2)}</td>
                    <td>{Math.round(d.y2)}</td>
                  </tr>
                ))}
              </tbody> */}
            </table>

            <button
              onClick={() => setResultados(null)}
              style={{
                marginTop: "20px",
                padding: "10px 20px",
                borderRadius: "8px",
                backgroundColor: "#f44336",
                color: "white",
                border: "none",
                cursor: "pointer"
              }}
              onMouseOver={e => e.currentTarget.style.backgroundColor = '#d32f2f'}
              onMouseOut={e => e.currentTarget.style.backgroundColor = '#f44336'}
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CargarManual;