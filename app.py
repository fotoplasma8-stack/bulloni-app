import streamlit as st
from google import genai
from google.genai import types
import zipfile
import io
import time

# Configurazione Pagina
st.set_page_config(page_title="Rinomina Bulloni", page_icon="🔩")
st.title("🔩 Automazione Bulloni")

# Recupero Chiave API
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Configura la chiave API nei Secrets!")
    st.stop()

# INIZIALIZZAZIONE FORZATA SU VERSIONE V1 (Stabile)
# Questo dovrebbe eliminare l'errore 404 della v1beta
client = genai.Client(
    api_key=api_key,
    http_options={'api_version': 'v1'} 
)

MODEL_ID = "gemini-1.5-flash"

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
                    
                    # Chiamata al modello
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=[
                            "Analizza l'immagine. Scrivi solo il numero del primo e dell'ultimo bullone visibili separati da un trattino (es: 37-35).",
                            types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
                        ]
                    )
                    
                    testo = response.text.strip().replace(" ", "")
                    
                    if "-" in testo and len(testo) < 15:
                        nuovo_nome = f"bulloni {testo}.jpg"
                        successo += 1
                    else:
                        nuovo_nome = f"controlla_{file.name}"
                    
                except Exception as e:
                    st.error(f"Errore su {file.name}: {e}")
                    nuovo_nome = f"errore_{file.name}"

                zip_file.writestr(nuovo_nome, img_data)
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(1.2) # Pausa di sicurezza

        status.text("✅ Elaborazione finita!")
        
        if successo > 0:
            st.success(f"Completato! {successo} file pronti.")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni_finiti.zip")
        else:
            st.error("L'AI non ha risposto correttamente. Verifica la tua API Key.")
