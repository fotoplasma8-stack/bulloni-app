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

# Configurazione diretta
genai.configure(api_key=api_key)

# Caricamento file
uploaded_files = st.file_uploader("Carica le foto", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi"):
        zip_buffer = io.BytesIO()
        successo = 0
        
        # Inizializziamo il modello con il nome semplificato
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                try:
                    # Lettura immagine
                    img_data = file.getvalue()
                    
                    # Chiamata pulita
                    response = model.generate_content([
                        "Analizza l'immagine dei bulloni. Scrivi SOLO il primo numero e l'ultimo numero visibili separati da trattino (es: 73-75). Non scrivere altro.",
                        {"mime_type": "image/jpeg", "data": img_data}
                    ])
                    
                    # Pulizia testo
                    risultato = response.text.strip().replace(" ", "")
                    
                    # Se il risultato è valido rinomina, altrimenti tieni nome originale
                    nuovo_nome = f"bulloni {risultato}.jpg" if "-" in risultato else f"controlla_{file.name}"
                    successo += 1
                    
                except Exception as e:
                    st.error(f"Errore su {file.name}: {e}")
                    nuovo_nome = f"errore_{file.name}"

                zip_file.writestr(nuovo_nome, img_data)
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(1)

        if successo > 0:
            st.success("Analisi completata!")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni_finiti.zip")
