import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Consulta de Incidencias", layout="centered")
st.title("Consulta de Incidencias por DNI")

# URL directa de Google Drive
url = "https://drive.google.com/uc?export=download&id=1Bm780WhfDSijVPN4uJA-9qbGbWw3UdMG"

# Cargar datos con manejo de errores
@st.cache_data
def load_data():
    try:
        st.info("Cargando datos desde Google Drive...")
        response = requests.get(url)
        response.raise_for_status()
        excel_data = BytesIO(response.content)
        
        # Leer hoja específica "Datos" desde la fila 3 (índice 2)
        df = pd.read_excel(excel_data, sheet_name="Datos", skiprows=2)
        
        # Eliminar filas y columnas vacías
        df.dropna(how="all", inplace=True)
        df = df.loc[:, df.columns.notna()]
        
        # Seleccionar solo las columnas en las posiciones A, G, J, L, N (índices 0, 6, 9, 11, 13)
        columnas_deseadas = [0, 6, 9, 11, 13]  # A=0, G=6, J=9, L=11, N=13
        columnas_existentes = [col for col in columnas_deseadas if col < len(df.columns)]
        
        if columnas_existentes:
            df = df.iloc[:, columnas_existentes]
        else:
            st.warning("No se encontraron las columnas en las posiciones especificadas")
        
        # Convertir la columna DNI (última columna) a string sin decimales
        if len(df.columns) > 0:
            dni_col = df.columns[-1]  # La columna N (DNI) debería ser la última
            df[dni_col] = df[dni_col].astype(str).str.replace('.0', '', regex=False).str.strip()
        
        # Convertir la primera columna a formato fecha
        if len(df.columns) > 0:
            fecha_col = df.columns[0]  # La columna A (fecha) debería ser la primera
            df[fecha_col] = pd.to_datetime(df[fecha_col], errors='coerce')
            
        # Ordenar por fecha de más reciente a más antigua
        if len(df.columns) > 0:
            df = df.sort_values(by=df.columns[0], ascending=False)
        
        st.success("Datos cargados exitosamente!")
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

# Cargar datos
df = load_data()

if df is not None:
    # Verificar si existe la columna DNI (debería ser la última columna)
    if len(df.columns) == 0:
        st.error("No se encontraron columnas en el archivo.")
        st.stop()
    
    dni_col = df.columns[-1]  # Última columna (N)
    
    # Input para DNI
    dni_input = st.text_input("Ingrese su DNI")
    
    if st.button("Buscar"):
        if dni_input.strip():
            # Normalizar el DNI de entrada (eliminar espacios)
            dni_busqueda = dni_input.strip()
            
            # Buscar registros (comparación exacta como strings)
            resultados = df[df[dni_col] == dni_busqueda]
            
            if not resultados.empty:
                st.success(f"Se encontraron {len(resultados)} registros para el DNI {dni_busqueda}")
                st.dataframe(resultados)
            else:
                st.warning("No se encontraron registros con ese DNI.")
        else:
            st.error("Por favor ingrese un DNI")
else:
    st.error("No se pudieron cargar los datos. Verifique la conexión a internet y el enlace del archivo.")