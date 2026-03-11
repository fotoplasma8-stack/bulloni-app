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
    st.error("Manca la chiave nei Secrets!")
    st.stop()

# Inizializzazione Client
client = genai.Client(api_key=api_key)

# USIAMO IL NOME COMPLETO DEL MODELLO
# A volte scrivere 'models/gemini-1.5-flash' risolve il 404 rispetto a 'gemini-1.5-flash'
MODEL_ID = "models/gemini-1.5-flash"

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
                    
                    # Chiamata al modello
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=[
                            "Scrivi solo i numeri del primo e dell'ultimo bullone (es: 10-12).",
                            types.Part.from_bytes(data=file.getvalue(), mime_type="image/jpeg")
                        ]
                    )
                    
                    testo = response.text.strip().replace(" ", "")
                    nuovo_nome = f"bulloni {testo}.jpg" if "-" in testo else f"controlla_{file.name}"
                    successo += 1
                    
                except Exception as e:
                    # Se dà ancora 404, stampiamo i modelli che la tua chiave PUÒ vedere
                    if "404" in str(e):
                        st.error("Il modello non viene trovato. Provo a elencare quelli disponibili per la tua chiave...")
                        try:
                            available = [m.name for m in client.models.list()]
                            st.write("Modelli disponibili per te:", available)
                        except:
                            pass
                    st.error(f"Errore su {file.name}: {e}")
                    nuovo_nome = f"errore_{file.name}"

                zip_file.writestr(nuovo_nome, file.getvalue())
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(5) # RISPETTO LIMITI PIANO FREE

        if successo > 0:
            st.success("Fatto!")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni.zip")
            
