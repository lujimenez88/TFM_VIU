import { useMap } from "react-leaflet";
import { useEffect } from "react";

const CentrarEnDeteccion = ({ coordenadas }) => {
  const map = useMap();

  useEffect(() => {
    if (coordenadas) {
      map.setView(coordenadas, 15); // 15 es el nivel de zoom
    }
  }, [coordenadas, map]);

  return null;
};

export default CentrarEnDeteccion;