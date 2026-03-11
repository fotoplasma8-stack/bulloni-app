import streamlit as st
import google.generativeai as genai
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

# Configurazione Google AI
genai.configure(api_key=api_key)

# Usiamo il nome modello più specifico possibile
MODEL_ID = 'models/gemini-1.5-flash-latest'

uploaded_files = st.file_uploader("Carica le foto", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi"):
        zip_buffer = io.BytesIO()
        successo = 0
        
        # Inizializzazione modello
        model = genai.GenerativeModel(model_name=MODEL_ID)
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress = st.progress(0)
            status = st.empty()
            
            for i, file in enumerate(uploaded_files):
                try:
                    img_data = file.getvalue()
                    
                    # Prompt ultra-semplice
                    response = model.generate_content([
                        "Analizza l'immagine. Scrivi solo il numero del primo e dell'ultimo bullone visibili separati da un trattino (es: 37-35). Niente altro.",
                        {"mime_type": "image/jpeg", "data": img_data}
                    ])
                    
                    # Estrazione e pulizia testo
                    testo = response.text.strip().replace(" ", "")
                    
                    # Se l'AI risponde correttamente (es 73-75) rinominiamo
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
                time.sleep(1.5)

        if successo > 0:
            st.success(f"Analisi completata! {successo} file rinominati.")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni_finiti.zip")
        else:
            st.error("L'AI non ha riconosciuto i numeri. Controlla che le foto siano chiare.")
