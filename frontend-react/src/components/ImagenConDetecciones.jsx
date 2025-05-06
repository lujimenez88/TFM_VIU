import React, { useRef, useEffect } from 'react';

const ImagenConDetecciones = ({ imageUrl, boundingBoxes = [] }) => {
  const canvasRef = useRef(null);
  const imgRef = useRef(new Image());

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = imgRef.current;

    img.crossOrigin = "anonymous"; // Necesario si usas signed URLs desde otro dominio
    img.src = imageUrl;
    console.log(imageUrl, boundingBoxes);
    img.onload = () => {
      // Ajustar el tamaño del canvas a la imagen
      canvas.width = img.width;
      canvas.height = img.height;

      // Dibujar imagen
      ctx.drawImage(img, 0, 0);

      // Dibujar cada bounding box
      boundingBoxes.forEach((box) => {
        const { x1, y1, x2, y2, class_name, confidence } = box;

        ctx.strokeStyle = class_name === 'healthy' ? 'green' : 'red';
        ctx.lineWidth = 2;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        // Texto (clase + confianza)
        ctx.font = '14px Arial';
        ctx.fillStyle = class_name === 'healthy' ? 'green' : 'red';
        ctx.fillText(`${class_name} (${confidence.toFixed(2)})`, x1, y1 - 5);
      });
    };

    img.onerror = () => {
      console.error('❌ Error cargando la imagen');
    };
  }, [imageUrl, boundingBoxes]);

  return (
    <div style={{ textAlign: 'center', marginTop: '20px' }}>
      <canvas
  ref={canvasRef}
  style={{ width: "100%", height: "auto", maxWidth: "700px", border: "1px solid #ccc" }}/>
    </div>
  );
};

export default ImagenConDetecciones;
