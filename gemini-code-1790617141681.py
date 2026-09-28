import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd

st.set_page_config(page_title="Productora de Alimentos PA", layout="centered")
st.title("Panel de Control - Pedidos PA 🍲")

# --- 1. CONECTAR A GOOGLE SHEETS (MÉTODO CSV) ---
@st.cache_data(ttl=60) # Actualiza los datos cada 60 segundos
def obtener_datos_google():
    try:
        # AQUÍ ESTÁ TU ENLACE REAL CONECTADO
        URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVsIelpOXv6q2gXZYtkkY_QrjMtaRTIqLR1IdZHYONAlsL4TEEMHIQ9a_CpTOd_m3m35xx2YEHih3h/pub?gid=690889630&single=true&output=csv" 
        
        # Leemos los datos directamente del enlace
        df = pd.read_csv(URL_CSV)
        
        if df.empty:
            return None, None
            
        # --- 2. ORGANIZAR LOS DATOS ---
        # IMPORTANTE: Estos nombres deben ser EXACTAMENTE iguales a los títulos 
        # de las columnas en tu Excel (respeta mayúsculas y tildes).
        COLUMNA_SEDE = "Sede" 
        COLUMNA_PROTEINA = "Proteína" 
        COLUMNA_SOPA = "Sopa" 

        resumen = {
            "NEA": {"P2": 0, "P1": 0, "SOPAS": 0},
            "MONASTERY": {"P2": 0, "P1": 0, "SOPAS": 0},
            "CLEMONT SHOWROOM": {"P2": 0, "P1": 0, "SOPAS": 0},
            "CLEMONT CEDI": {"P2": 0, "P1": 0, "SOPAS": 0}
        }

        # Contar los pedidos
        for index, fila in df.iterrows():
            sede = str(fila.get(COLUMNA_SEDE, "")).strip().upper()
            proteina = str(fila.get(COLUMNA_PROTEINA, "")).strip().upper()
            sopa = str(fila.get(COLUMNA_SOPA, "")).strip().upper()

            if sede in resumen:
                if "1" in proteina:
                    resumen[sede]["P1"] += 1
                elif "2" in proteina:
                    resumen[sede]["P2"] += 1
                
                if sopa == "SÍ" or sopa == "SI" or sopa == "YES":
                    resumen[sede]["SOPAS"] += 1
                    
        return resumen, df
    except Exception as e:
        st.error(f"Error al leer la hoja de cálculo: {e}")
        return None, None

# --- 3. GENERAR IMAGEN ---
def generar_imagen_bytes(datos_pedidos, ruta_imagen_base):
    imagen = Image.open(ruta_imagen_base)
    dibujo = ImageDraw.Draw(imagen)
    try:
        fuente = ImageFont.truetype("arial.ttf", 45)
    except:
        fuente = ImageFont.load_default()

    coordenadas = {
        "NEA": {"P2": (180, 280), "P1": (430, 280), "SOPAS": (700, 280)},
        "MONASTERY": {"P2": (180, 480), "P1": (430, 480), "SOPAS": (700, 480)},
        "CLEMONT SHOWROOM": {"P2": (180, 680), "P1": (430, 680), "SOPAS": (700, 680)},
        "CLEMONT CEDI": {"P2": (180, 880), "P1": (430, 880), "SOPAS": (700, 880)}
    }
    color_texto = (0, 0, 0)
    for sede, categorias in coordenadas.items():
        if sede in datos_pedidos:
            dibujo.text(categorias["P2"], str(datos_pedidos[sede]["P2"]), fill=color_texto, font=fuente)
            dibujo.text(categorias["P1"], str(datos_pedidos[sede]["P1"]), fill=color_texto, font=fuente)
            dibujo.text(categorias["SOPAS"], str(datos_pedidos[sede]["SOPAS"]), fill=color_texto, font=fuente)

    buf = io.BytesIO()
    imagen.save(buf, format="JPEG")
    return buf.getvalue()

# --- 4. INTERFAZ WEB ---
datos_procesados, df_crudo = obtener_datos_google()

if datos_procesados:
    st.success("✅ Conectado a Google Sheets exitosamente")
    st.write("### Resumen de Pedidos Actuales")
    
    df_resumen = pd.DataFrame(datos_procesados).T
    st.dataframe(df_resumen)
    
    st.write("---")
    st.write("### Generar Imagen para Cocina")
    nombre_archivo_base = "menu3 322-07 22-01.jpg"
    
    try:
        imagen_bytes = generar_imagen_bytes(datos_procesados, nombre_archivo_base)
        st.image(imagen_bytes, caption="Vista previa de hoy", width=400)
        st.download_button(label="📥 Descargar Imagen JPG", data=imagen_bytes, file_name="pedidos_hoy.jpg", mime="image/jpeg")
    except FileNotFoundError:
        st.error("No se encontró la plantilla de la imagen.")
