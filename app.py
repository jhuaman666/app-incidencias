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
        
        # Convertir columna DNI a string para manejar DNIs que empiezan con 0
        if "DNI" in df.columns:
            df["DNI"] = df["DNI"].astype(str).str.strip()
        
        st.success("Datos cargados exitosamente!")
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

# Cargar datos
df = load_data()

if df is not None:
    # Mostrar información de la tabla para debugging
    st.write("**Información de la tabla cargada:**")
    st.write(f"- Número de filas: {len(df)}")
    st.write(f"- Número de columnas: {len(df.columns)}")
    st.write(f"- Columnas disponibles: {', '.join(df.columns.astype(str))}")
    
    # Mostrar primeras filas para verificar que se cargó correctamente
    with st.expander("Ver primeras 5 filas de la tabla"):
        st.dataframe(df.head())
    
    # Verificar si existe la columna DNI
    if "DNI" not in df.columns:
        st.error("No se encontró la columna 'DNI' en el archivo.")
        st.stop()
    
    # Mostrar algunos ejemplos de DNI para debugging
    with st.expander("Ejemplos de DNI en la tabla"):
        sample_dnis = df["DNI"].dropna().head(10).tolist()
        st.write(f"Primeros 10 DNIs: {sample_dnis}")
    
    # Input para DNI
    dni_input = st.text_input("Ingrese su DNI (incluyendo ceros iniciales si los tiene)")
    
    if st.button("Buscar"):
        if dni_input.strip():  # Verificar que no esté vacío
            # Normalizar el DNI de entrada (eliminar espacios)
            dni_busqueda = dni_input.strip()
            
            # Buscar registros (comparación exacta como strings)
            resultados = df[df["DNI"] == dni_busqueda]
            
            if not resultados.empty:
                st.success(f"Se encontraron {len(resultados)} registros para el DNI {dni_busqueda}")
                st.dataframe(resultados)
            else:
                st.warning("No se encontraron registros con ese DNI.")
                # Mostrar sugerencias si no encuentra coincidencias exactas
                similar_dnis = df[df["DNI"].str.contains(dni_busqueda, case=False, na=False)]
                if not similar_dnis.empty:
                    st.info("¿Tal vez quisiste decir alguno de estos?")
                    st.write(similar_dnis["DNI"].unique()[:5].tolist())
        else:
            st.error("Por favor ingrese un DNI")
else:
    st.error("No se pudieron cargar los datos. Verifique la conexión a internet y el enlace del archivo.")
