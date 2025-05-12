import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker } from "react-leaflet";
import { getDetecciones, obtenerDetalleDeteccion } from "../services/api";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import ImagenConDetecciones from '../components/ImagenConDetecciones';
import FiltrosDetecciones from '../components/FiltrosDetecciones';
import CentrarEnDeteccion from "../components/CentrarEnDeteccion";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

const VerMapa = () => {
  const [detecciones, setDetecciones] = useState([]);
  const [selectedDeteccion, setSelectedDeteccion] = useState(null);
  const [detalleSeleccionado, setDetalleSeleccionado] = useState(null);
  const [filtros, setFiltros] = useState({});

  /*useEffect(() => {
    const fetchData = () => {
      getDetecciones()
        .then(response => {
          setDetecciones(response);
          if (response.length > 0) {
            //setSelectedDeteccion(response[0]);
          }
        })
        .catch(error => console.error("Error cargando detecciones:", error));
    };*/
    useEffect(() => {
      const fetchData = () => {
        getDetecciones(filtros)
          .then(response => {
            setDetecciones(response);
            // setSelectedDeteccion(response[0]); (si aplica)
          })
          .catch(error => console.error("Error cargando detecciones:", error));
      };
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [filtros]);

  const handleFiltrar = (valores) => {
    setFiltros(valores);
    // Puedes también aquí llamar al backend usando los filtros
  };

  const iconHealthy = new L.Icon({
    iconUrl: "/icons/icono-verde.png",
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
  });

  const iconOther = new L.Icon({
    iconUrl: "/icons/icono-rojo.png",
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
  });

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2 style={{ textAlign: "left" }}>📍 Mapa de Detecciones</h2>
      <FiltrosDetecciones onFiltrar={handleFiltrar} />
      <div style={{
  display: "flex",
  justifyContent: "left",
  gap: "30px",
  marginBottom: "20px",
  flexWrap: "wrap"
}}>
  <div style={{ display: 'flex', flexDirection: 'column', minWidth: '200px' }}>
    <label style={{ marginBottom: '6px', fontWeight: 'bold' }}>Fecha de detección:</label>
    <input
      type="text"
      value={selectedDeteccion ? selectedDeteccion.timestamp : ""}
      placeholder="Fecha"
      readOnly
    />
  </div>

  <div style={{ display: 'flex', flexDirection: 'column', minWidth: '200px' }}>
    <label style={{ marginBottom: '6px', fontWeight: 'bold' }}>Coordenadas:</label>
    <input
      type="text"
      value={selectedDeteccion ? `${selectedDeteccion.lat}, ${selectedDeteccion.lon}` : ""}
      placeholder="Coordenadas"
      readOnly
    />
  </div>
</div>

      <MapContainer center={[4.6352, -74.0820]} zoom={12} style={{ height: "600px", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {/* {selectedDeteccion && (
          <CentrarEnDeteccion coordenadas={[selectedDeteccion.lat, selectedDeteccion.lon]} />
        )} */}
        {detecciones.map((det) => (
          <Marker
            key={det.id}
            position={[det.lat, det.lon]}
            icon={det.es_sano === true ? iconHealthy : iconOther}
            eventHandlers={{
              click: async () => {
                setSelectedDeteccion(det);
                const detalle = await obtenerDetalleDeteccion(det.id);
                setDetalleSeleccionado({ ...detalle, id: det.id });
              },
            }}
          />
        ))}
      </MapContainer>

      {detalleSeleccionado && (
        <div
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
          onClick={() => setDetalleSeleccionado(null)}
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
            <h3 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "10px" }}>🧪 Detección #{detalleSeleccionado.id}</h3>
            <p><strong>Fecha:</strong> {selectedDeteccion?.timestamp}</p>
            <p><strong>Ubicación:</strong> {selectedDeteccion?.lat}, {selectedDeteccion?.lon}</p>
            <TransformWrapper>
            <TransformComponent>
            <ImagenConDetecciones
              imageUrl={detalleSeleccionado.image_url}
              boundingBoxes={detalleSeleccionado.detalles}
            />
              </TransformComponent>
              </TransformWrapper>
            <h4 style={{ marginTop: "20px", fontWeight: "bold" }}>🧾 Detalles de detecciones</h4>
            <table style={{ width: "100%", marginTop: "10px", borderCollapse: "collapse", fontSize: "14px" }}>
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
                {detalleSeleccionado.detalles.map((d, i) => (
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
            </table>

            <div style={{ textAlign: "right", marginTop: "20px" }}>
              <button
                onClick={() => setDetalleSeleccionado(null)}
                style={{
                  backgroundColor: "#d9534f",
                  color: "white",
                  padding: "10px 20px",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer"
                }}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VerMapa;
