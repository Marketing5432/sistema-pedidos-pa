import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd

# 1. Configuración de la página web
st.set_page_config(page_title="Productora de Alimentos PA", layout="centered")
st.title("Panel de Control - Pedidos PA 🍲")

# 2. Función que genera la imagen con los números
def generar_imagen_bytes(datos_pedidos, ruta_imagen_base):
    imagen = Image.open(ruta_imagen_base)
    dibujo = ImageDraw.Draw(imagen)
    
    try:
        # Intenta usar una fuente de sistema. Si no la encuentra, usa la por defecto.
        fuente = ImageFont.truetype("arial.ttf", 45)
    except:
        fuente = ImageFont.load_default()

    # Coordenadas exactas para tu imagen "menu3 322-07 22-01.jpg"
    coordenadas = {
        "NEA": {"P2": (180, 280), "P1": (430, 280), "SOPAS": (700, 280)},
        "MONASTERY": {"P2": (180, 480), "P1": (430, 480), "SOPAS": (700, 480)},
        "CLEMONT SHOWROOM": {"P2": (180, 680), "P1": (430, 680), "SOPAS": (700, 680)},
        "CLEMONT CEDI": {"P2": (180, 880), "P1": (430, 880), "SOPAS": (700, 880)}
    }

    color_texto = (0, 0, 0)

    for sede, categorias in coordenadas.items():
        if sede in datos_pedidos:
            dibujo.text(categorias["P2"], str(datos_pedidos[sede].get("P2", 0)), fill=color_texto, font=fuente)
            dibujo.text(categorias["P1"], str(datos_pedidos[sede].get("P1", 0)), fill=color_texto, font=fuente)
            dibujo.text(categorias["SOPAS"], str(datos_pedidos[sede].get("SOPAS", 0)), fill=color_texto, font=fuente)

    # Convertir la imagen a bytes para poder descargarla en la web
    buf = io.BytesIO()
    imagen.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    return byte_im

# 3. Simulación de conexión a Google Sheets
# (Aquí es donde enlazaremos la hoja de cálculo real en el siguiente paso)
st.write("### Resumen de pedidos de hoy (Corte 8:30 AM)")

# Datos de ejemplo (Luego los reemplazaremos por la lectura real de Google Sheets)
datos_de_hoy = {
    "NEA": {"P2": 12, "P1": 25, "SOPAS": 30},
    "MONASTERY": {"P2": 8, "P1": 40, "SOPAS": 45},
    "CLEMONT SHOWROOM": {"P2": 5, "P1": 15, "SOPAS": 12},
    "CLEMONT CEDI": {"P2": 22, "P1": 18, "SOPAS": 35}
}

# Mostrar los datos en una tabla limpia para que los revises antes de generar la imagen
df_resumen = pd.DataFrame(datos_de_hoy).T
st.dataframe(df_resumen)

# 4. Botón para generar y descargar la imagen
st.write("---")
st.write("### Generar Imagen para WhatsApp/Cocina")

# Asegúrate de que el archivo "menu3 322-07 22-01.jpg" esté en la misma carpeta que este código
nombre_archivo_base = "menu3 322-07 22-01.jpg"

try:
    imagen_lista_bytes = generar_imagen_bytes(datos_de_hoy, nombre_archivo_base)
    
    # Muestra una vista previa pequeña en la web
    st.image(imagen_lista_bytes, caption="Vista previa de la imagen generada", width=400)
    
    # El botón mágico de descarga
    st.download_button(
        label="📥 Descargar Imagen JPG",
        data=imagen_lista_bytes,
        file_name="resumen_pedidos_hoy.jpg",
        mime="image/jpeg"
    )
except FileNotFoundError:
    st.error(f"⚠️ No se encontró la imagen base. Asegúrate de guardar tu plantilla como '{nombre_archivo_base}' en la misma carpeta.")