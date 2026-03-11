import streamlit as st
from google import genai
from google.genai import types
import zipfile
import io
import time

st.set_page_config(page_title="Rinomina Bulloni", page_icon="🔩")
st.title("🔩 Automazione Bulloni 2026")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Manca la chiave nei Secrets!")
    st.stop()

# Inizializzazione Client
client = genai.Client(api_key=api_key)

# USIAMO IL MODELLO PRESENTE NELLA TUA LISTA (Posizione 2 della tua lista)
MODEL_ID = "models/gemini-2.0-flash" 

uploaded_files = st.file_uploader("Carica le foto", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi"):
        zip_buffer = io.BytesIO()
        successo = 0
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress = st.progress(0)
            status = st.empty()
            
            for i, file in enumerate(uploaded_files):
                img_data = file.getvalue()
                
                # Sistema di RETRY per gestire i limiti del PIANO GRATUITO
                for tentativo in range(3):
                    try:
                        status.text(f"Analizzando {file.name}...")
                        
                        response = client.models.generate_content(
                            model=MODEL_ID,
                            contents=[
                                "Analizza l'immagine. Scrivi solo il numero del primo e dell'ultimo bullone (es: 37-35).",
                                types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
                            ]
                        )
                        
                        testo = response.text.strip().replace(" ", "")
                        if "-" in testo:
                            nome_finale = f"bulloni {testo}.jpg"
                            successo += 1
                        else:
                            nome_finale = f"check_{file.name}"
                        
                        break # Successo, esci dai tentativi
                        
                    except Exception as e:
                        if "429" in str(e):
                            status.warning("Limite raggiunto. Attesa 20 secondi per restare nel piano free...")
                            time.sleep(20)
                        else:
                            st.error(f"Errore su {file.name}: {e}")
                            nome_finale = f"errore_{file.name}"
                            break
                
                zip_file.writestr(nome_finale, img_data)
                progress.progress((i + 1) / len(uploaded_files))
                
                # PAUSA OBBLIGATORIA per non essere bloccati dal piano gratuito
                time.sleep(5)

        status.text("✅ Elaborazione terminata!")
        if successo > 0:
            st.success(f"Completato! {successo} file rinominati.")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni_2026.zip")
