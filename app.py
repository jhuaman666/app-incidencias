import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Consulta de Tardanzas", layout="centered")
st.title("Consulta de Tardanzas por DNI")

# URL directa de Google Drive
url = "https://drive.google.com/uc?export=download&id=1Bm780WhfDSijVPN4uJA-9qbGbWw3UdMG"

# Descargar archivo
response = requests.get(url)
excel_data = BytesIO(response.content)

# Leer hoja específica desde la fila 5 (índice 4)
df = pd.read_excel(excel_data, sheet_name="Tardanzas", skiprows=4)

# Eliminar filas vacías
df.dropna(how="all", inplace=True)
df = df.loc[:, df.columns.notna()]

# Verifica cómo se llama la columna que contiene el DNI (ajústalo si es necesario)
# Por ejemplo, si dice 'D.N.I.' o 'dni', cambia abajo: df["D.N.I."]
dni_input = st.text_input("Ingrese su DNI")

if st.button("Buscar"):
    if dni_input.isdigit():
        dni = int(dni_input)
        
        if "DNI" in df.columns:
            resultados = df[df["DNI"] == dni]
        elif "D.N.I." in df.columns:
            resultados = df[df["D.N.I."] == dni]
        else:
            st.error("No se encontró una columna llamada 'DNI' en el archivo.")
            st.stop()

        if not resultados.empty:
            st.success(f"Se encontraron {len(resultados)} registros para el DNI {dni}")
            st.dataframe(resultados)
        else:
            st.warning("No se encontraron registros con ese DNI.")
    else:
        st.error("Ingrese un DNI válido (solo números)")
