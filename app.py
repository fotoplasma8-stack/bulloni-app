import streamlit as st
from google import genai
from google.genai import types
import zipfile
import io
import time

st.set_page_config(page_title="Rinomina Bulloni", page_icon="🔩")
st.title("🔩 Automazione Bulloni")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Configura la chiave API nei Secrets!")
    st.stop()

# Inizializzazione standard senza forzare versioni
client = genai.Client(api_key=api_key)

# PROVIAMO IL MODELLO 2.0 (Più recente e spesso risolve i 404 del 1.5)
MODEL_ID = "gemini-2.0-flash" 

# PULSANTE DI DIAGNOSI (Per capire cosa vede la tua chiave)
if st.sidebar.button("🔍 Controlla Modelli Disponibili"):
    try:
        models = client.models.list()
        st.sidebar.write("Modelli che puoi usare:")
        for m in models:
            st.sidebar.code(m.name)
    except Exception as e:
        st.sidebar.error(f"Errore lista: {e}")

uploaded_files = st.file_uploader("Carica le foto", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi"):
        zip_buffer = io.BytesIO()
        successo = 0
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress = st.progress(0)
            status = st.empty()
            
            for i, file in enumerate(uploaded_files):
                try:
                    status.text(f"Analizzando: {file.name}...")
                    img_data = file.getvalue()
                    
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=[
                            "Scrivi solo il numero del primo e dell'ultimo bullone (es: 37-35).",
                            types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
                        ]
                    )
                    
                    testo = response.text.strip().replace(" ", "")
                    nuovo_nome = f"bulloni {testo}.jpg" if "-" in testo else f"controlla_{file.name}"
                    successo += 1
                    
                except Exception as e:
                    st.error(f"Errore su {file.name}: {e}")
                    nuovo_nome = f"errore_{file.name}"

                zip_file.writestr(nuovo_nome, img_data)
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(1)

        if successo > 0:
            st.success("Completato!")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni_finiti.zip")
