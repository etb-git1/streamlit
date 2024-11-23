import streamlit as st
import pandas as pd
import json
import os
import requests
import time
import subprocess
import base64
import plotly.graph_objects as go

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build





# Función para codificar la imagen en base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Ruta de la imagen local
image_path = r"C:\Users\michped1\Documents\demo\Auditoria-Inteligente-y-Personalizada-para-Contact-Centers-18.png"  # Cambia esta ruta a la ubicación de tu imagen
image_base64 = get_base64_of_bin_file(image_path)

st.set_page_config(layout="wide")
# CSS para agregar el fondo y cambiar el color y estilo de los encabezados
st.markdown(f"""
    <style>
        /* Fondo general con imagen */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{image_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-color: #f8f9fa; /* Color de respaldo */
        }}
        
        /* Encabezados principales */
        .main-header {{
            font-size: 2.5em;
            font-weight: bold;
            color: white;  /* Cambiar el color a blanco */
            text-align: center;
            margin-bottom: 0.5em;
        }}
        .subtitle {{
            color: white;  /* Cambiar el color a blanco */
            font-size: 1.2em;
            text-align: center;
            margin-top: -10px;
        }}

        /* Caja de carga de archivo (alineada a la izquierda) */
        .stFileUploader {{
            width: 300px;  /* Cambiar el ancho */
            display: block;  /* Para asegurar que se muestre en bloque */
            margin-left: 0;  /* Alineada a la izquierda */
        }}

        /* Botones */
        .stButton button {{
            background-color: white;
            color: black;  /* Cambiar el color del texto a negro */
            font-size: 1.1em;
            font-weight: bold;
            padding: 0.75em 1.5em;
            border-radius: 8px;
            border: none;
        }}
        .stButton button:hover {{
            background-color: #0a58ca;
            transition: 0.3s;
        }}

        /* Estilos de transcripción */
        .speaker0 {{ color: green; font-weight: bold; }}
        .speaker2 {{ color: blue; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# Encabezados principales

st.markdown('<div class="main-header">🎙️ LEXI SPEECH</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🚀 Producto realizado por LEXI ANALYTICS</div>', unsafe_allow_html=True)

# Agregar espacio después del subtítulo
st.markdown("<br>", unsafe_allow_html=True)



### librerias 



# Scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@st.cache_data
def authenticate_with_oauth():
    """Authenticate the user and return a Google Drive API service."""
    # Path to your OAuth 2.0 client credentials
    CREDENTIALS_FILE = r"C:\Users\michped1\Documents\demo\client_secret_127548066523-cr3lp3b42gup5sh655c5m1ari1qblb6s.apps.googleusercontent.com.json"

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=credentials)
    return service

def read_file_from_drive(_service, file_name):
    """Read the content of a file from Google Drive."""
    # Search for the file by name
    results = _service.files().list(
        q=f"name='{file_name}'",
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    if not items:
        st.error(f"File not found: {file_name}")
        return None

    file_id = items[0]['id']

    # Download the file content
    request = _service.files().get_media(fileId=file_id)
    file_content = request.execute()
    return file_content.decode('utf-8')

def display_transcription(content):
    """Display transcription content by speaker, limited to 20 lines."""
    st.markdown("<h2 style='color: white; font-weight: bold;'>📄 Resultados de la transcripción</h2>", unsafe_allow_html=True)

    # Split content into lines
    lines = content.split("\n")
    
    if lines:
        # Limit to the first 20 lines
        limited_lines = lines[:20]
        for line in limited_lines:
            if line.startswith("Speaker 2:"):
                st.markdown(f"<span style='color: blue; font-weight: bold;'>{line}</span>", unsafe_allow_html=True)
            elif line.startswith("Speaker 0:"):
                st.markdown(f"<span style='color: green; font-weight: bold;'>{line}</span>", unsafe_allow_html=True)
            else:
                st.text(line)
        
        st.success("Mostrando las primeras 20 líneas de la transcripción.")
        
        if len(lines) > 20:
            st.info(f"Transcripción truncada. Hay {len(lines) - 20} líneas adicionales.")
    else:
        st.warning("No hay transcripción disponible.")



def load_data_from_drive(service, file_name):
    """Load JSON data from a file in Google Drive."""
    file_content = read_file_from_drive(service, file_name)
    if file_content:
        return json.loads(file_content)
    return None



# Función para cargar los datos del archivo JSON (código de la visualización de emociones)
def load_data(file_path):
    import json
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)



file_path = r"C:\Users\michped1\Documents\demo\felipe.json"  # Cambia esta ruta según tu archivo

# Leer los datos
data = load_data(file_path)

service = authenticate_with_oauth()


data = load_data_from_drive(service, "resumen.json")


# Datos de la conversación
conversation = data["conversation"]

# Mapeo de emociones a valores numéricos y emojis
emotion_value_map = {
    "feliz": 1,
    "curioso": 2,
    "neutral": 3,
    "molesto": 4,
    "indeciso": 5
}

emotion_emoji_map = {
    "feliz": "😊",
    "curioso": "🤔",
    "neutral": "😐",
    "molesto": "😡",
    "indeciso": "😕"
}

# Extraer emociones, participantes y resúmenes
emotions = [c["emotion"] for c in conversation]
speakers = [c["speaker"] for c in conversation]
summaries = [c["summary"] for c in conversation]  # Suponiendo que el JSON tiene este campo

# Crear listas para las emociones del Asesor y Cliente
advisor_emotions = []
client_emotions = []
timeline = []
advisor_emojis = []
client_emojis = []
advisor_summaries = []
client_summaries = []

# Recorrer las conversaciones para asignar las emociones a los respectivos participantes
for idx, (emotion, speaker, summary) in enumerate(zip(emotions, speakers, summaries)):
    timeline.append(f"Turno {idx + 1}")
    emoji = emotion_emoji_map[emotion]  # Asignar emoji basado en la emoción
    if speaker == "Asesor":
        advisor_emotions.append(emotion_value_map[emotion])  # Asignamos valor numérico de emoción
        client_emotions.append(None)  # El Cliente no habla en este turno
        advisor_emojis.append(emoji)  # Añadir el emoji del Asesor
        client_emojis.append(None)  # El Cliente no tiene emoji
        advisor_summaries.append(summary)  # Resumen del Asesor
        client_summaries.append(None)
    else:
        client_emotions.append(emotion_value_map[emotion])  # Asignamos valor numérico de emoción
        advisor_emotions.append(None)  # El Asesor no habla en este turno
        client_emojis.append(emoji)  # Añadir el emoji del Cliente
        advisor_emojis.append(None)  # El Asesor no tiene emoji
        client_summaries.append(summary)  # Resumen del Cliente
        advisor_summaries.append(None)

# Crear el gráfico de líneas para la evolución de las emociones
fig = go.Figure()

# Añadir las emociones del Asesor
fig.add_trace(go.Scatter(
    x=timeline,
    y=advisor_emotions,
    mode='lines+markers+text',  # Añadimos 'text' para los emojis
    name="Asesor",
    line=dict(color="blue", width=2),
    marker=dict(symbol="circle", size=16),  # Hacemos los puntos más grandes
    text=advisor_emojis,  # Asignamos los emojis del Asesor
    textposition="top center",  # Colocamos los emojis encima de los puntos
    hovertext=advisor_summaries,  # Resumen como información flotante
    hoverinfo="text+x+name",  # Mostrar resumen, nombre y eje X
))

# Añadir las emociones del Cliente
fig.add_trace(go.Scatter(
    x=timeline,
    y=client_emotions,
    mode='lines+markers+text',  # Añadimos 'text' para los emojis
    name="Cliente",
    line=dict(color="green", width=2),
    marker=dict(symbol="circle", size=12),  # Hacemos los puntos más grandes
    text=client_emojis,  # Asignamos los emojis del Cliente
    textposition="top center",  # Colocamos los emojis encima de los puntos
    hovertext=client_summaries,  # Resumen como información flotante
    hoverinfo="text+x+name",  # Mostrar resumen, nombre y eje X
))

# Actualizar el layout para mayor tamaño
fig.update_layout(
    height=700,
    width=1000,
    title="Evolución de las Emociones del Asesor y Cliente",
    xaxis=dict(title="Turno de la Conversación"),
    yaxis=dict(
        title="Emociones",
        tickvals=[1, 2, 3, 4, 5],
        ticktext=["Feliz", "Curioso", "Neutral", "Molesto", "Indeciso"],
        tickfont=dict(
            family="Arial, sans-serif",
            size=12,
            color="white",
            weight="bold"
        )
    ),
    legend=dict(
        font=dict(
            color="white",
            size=14
        ),
        bgcolor="rgba(0, 0, 0, 0.3)",
    ),
    showlegend=True,
    plot_bgcolor="rgba(150, 150, 150, 0.7)",
    paper_bgcolor="rgba(30, 30, 30, 0.5)",
    xaxis_tickangle=-45,
)




fig.show()


# Uso de contenedor para las columnas
with st.container():
    col1, col2 = st.columns([4, 5],gap="large")  # Ajuste de proporciones para distribuir mejor el espacio

    # Separar las columnas y añadir margen entre ellas
    with col1:
        # === SECCIÓN 1: Carga de audio ===
        st.markdown('<h3 style="color: white; font-weight: bold;">🎙️ Cargar archivo de audio</h3>', unsafe_allow_html=True)

        # Caja de carga de archivo (alineada a la izquierda)
        uploaded_file = st.file_uploader("Selecciona un archivo de audio para cargar (MP3 o WAV):", type=["mp3", "wav"])

    with col2:
        # === SECCIÓN 4: Gráfico de emociones ===
        st.plotly_chart(fig, use_container_width=True)

    # === SECCIÓN 2: Ejecutar y monitorear trabajo en Databricks ===
    with col1:
        st.markdown('<h3 style="color: white; font-weight: bold;">🚀 Ejecutar Procesamiento </h3>', unsafe_allow_html=True)

        if uploaded_file:
            file_name = os.path.basename(uploaded_file.name)
            st.success(f"Archivo cargado: {file_name}")
        # Aquí puedes agregar la lógica para subir a Azure Blob Storage

        # Botón para ejecutar el trabajo
        if st.button("Ejecutar trabajo"):
            run_id = "12345"  # Aquí va la lógica real para iniciar el trabajo
            st.info(f"Trabajo iniciado con run_id: {run_id}")
            with st.spinner("Monitoreando el estado del trabajo..."):
                time.sleep(5)  # Simulación del monitoreo
                st.success("Trabajo completado exitosamente.")

    # === SECCIÓN 3: Visualización de resultados ===
    with col1:
        st.markdown("<h2 style='color: white; font-weight: bold;'>📄 Resultados de la transcripción</h2>",unsafe_allow_html=True)
        # Simulación de contenido de transcripción
        service = authenticate_with_oauth()

    # File name to read from Google Drive
        #file_name = st.text_input("Enter file name:", "AUDIO.txt")

        if st.button("Read File"):
            content = read_file_from_drive(service, "AUDIO.txt")  # Pass the service object
            if content:
                display_transcription(content)
