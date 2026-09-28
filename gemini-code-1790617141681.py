import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd

st.set_page_config(page_title="Productora de Alimentos PA", layout="centered")
st.title("Panel de Control - Pedidos PA 🍲")

# --- 1. CONECTAR A GOOGLE SHEETS (MÉTODO CSV) ---
# Hemos quitado el caché para que siempre lea los datos más frescos al instante
def obtener_datos_google():
    try:
        URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmR3f2NpHbmtE_FLibPWnnrOC4zODWLK9boy0Oer1UtiPpZMo9ph77AsOJWJaeHBcjNC_nLnwcgXQV/pub?gid=698961945&single=true&output=csv" 
        
        df = pd.read_csv(URL_CSV)
        
        if df.empty:
            return None, None
            
        # SOLUCIÓN: Limpiamos los títulos de las columnas (quitamos espacios invisibles y forzamos mayúsculas)
        df.columns = df.columns.str.strip().str.upper()

        # Al estar limpios, podemos buscarlos con seguridad
        COLUMNA_SEDE = "SEDE" 
        COLUMNA_PROTEINA = "MENU" 
        COLUMNA_SOPA = "SOPA" 

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

# --- 3. GENERAR IMAGEN INTELIGENTE ---
def generar_imagen_bytes(datos_pedidos, ruta_imagen_base):
    imagen = Image.open(ruta_imagen_base)
    dibujo = ImageDraw.Draw(imagen)
    
    ancho, alto = imagen.size
    
    # Descargar fuente Roboto Black directamente de Google
    try:
        url_fuente = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf"
        req = urllib.request.Request(url_fuente, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        
        # El tamaño de la letra será el 4% del ancho de la imagen (gigante y proporcional)
        tamano_letra = int(ancho * 0.04) 
        fuente = ImageFont.truetype(io.BytesIO(res.read()), tamano_letra)
    except:
        fuente = ImageFont.load_default()

    # Coordenadas por porcentajes matemáticos (X, Y)
    coordenadas = {
        "NEA":              {"P2": (ancho * 0.21, alto * 0.29), "P1": (ancho * 0.50, alto * 0.29), "SOPAS": (ancho * 0.81, alto * 0.29)},
        "MONASTERY":        {"P2": (ancho * 0.21, alto * 0.45), "P1": (ancho * 0.50, alto * 0.45), "SOPAS": (ancho * 0.81, alto * 0.45)},
        "CLEMONT SHOWROOM": {"P2": (ancho * 0.21, alto * 0.61), "P1": (ancho * 0.50, alto * 0.61), "SOPAS": (ancho * 0.81, alto * 0.61)},
        "CLEMONT CEDI":     {"P2": (ancho * 0.21, alto * 0.77), "P1": (ancho * 0.50, alto * 0.77), "SOPAS": (ancho * 0.81, alto * 0.77)}
    }
    
    color_texto = (0, 0, 0) # Negro
    
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
    
    # Botón para forzar recarga manual de datos
    if st.button("🔄 Actualizar Datos Ahora"):
        st.rerun()

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
