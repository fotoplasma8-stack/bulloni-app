import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import zipfile
import io
import time

# Configurazione Pagina
st.set_page_config(page_title="Rinomina Bulloni AI", page_icon="🔩")
st.title("🔩 Automazione Bulloni")

# 1. Recupero Chiave API dai Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Chiave API non trovata nei Secrets!")
    st.stop()

# 2. Configurazione Modello (Versione corretta per evitare errore 404)
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_files = st.file_uploader("Carica le foto", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi"):
        zip_buffer = io.BytesIO()
        successo = 0
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress = st.progress(0)
            for i, file in enumerate(uploaded_files):
                try:
                    img_bytes = file.getvalue()
                    
                    # Chiamata con opzione versione specifica
                    response = model.generate_content(
                        [
                            "Scrivi solo i numeri del primo e dell'ultimo bullone (es: 73-75).",
                            {"mime_type": "image/jpeg", "data": img_bytes}
                        ],
                        request_options=RequestOptions(api_version='v1beta') # Forza la versione corretta
                    )
                    
                    testo = response.text.strip().replace(" ", "")
                    nuovo_nome = f"bulloni {testo}.jpg" if "-" in testo else f"controlla_{file.name}"
                    successo += 1
                except Exception as e:
                    st.error(f"Errore su {file.name}: {e}")
                    nuovo_nome = f"errore_{file.name}"

                zip_file.writestr(nuovo_nome, img_bytes)
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(1)

        if successo > 0:
            st.success("Analisi completata!")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni.zip")
