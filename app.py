import streamlit as st
import google.generativeai as genai
import zipfile
import io
import time

# 1. Configurazione Pagina
st.set_page_config(page_title="Rinomina Bulloni AI", page_icon="🔩")
st.title("🔩 Automazione Bulloni")

# 2. Recupero Chiave API dai Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Chiave API non trovata nei Secrets! Controlla le impostazioni di Streamlit.")
    st.stop()

# 3. Configurazione Google AI con nome modello universale
genai.configure(api_key=api_key)

# Proviamo a usare il nome completo del modello per evitare l'errore 404
MODEL_NAME = 'gemini-1.5-flash' 

uploaded_files = st.file_uploader("Carica le foto dei bulloni", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi"):
        zip_buffer = io.BytesIO()
        successo = 0
        
        # Inizializzazione modello
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress = st.progress(0)
            status = st.empty()
            
            for i, file in enumerate(uploaded_files):
                nome_originale = file.name
                status.text(f"Analizzando: {nome_originale}...")
                
                try:
                    img_bytes = file.getvalue()
                    
                    # Chiamata standard
                    response = model.generate_content([
                        "Analizza l'immagine dei bulloni. Scrivi SOLO il numero del primo bullone e dell'ultimo separati da trattino (es: 73-75). Non aggiungere altro testo.",
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ])
                    
                    # Pulizia testo
                    risultato = response.text.strip().replace(" ", "")
                    
                    if "-" in risultato:
                        nuovo_nome = f"bulloni {risultato}.jpg"
                        successo += 1
                    else:
                        nuovo_nome = f"controlla_{nome_originale}"
                        
                except Exception as e:
                    # Se l'errore persiste, mostriamo esattamente cosa dice l'API
                    st.error(f"Errore su {nome_originale}: {e}")
                    nuovo_nome = f"errore_{nome_originale}"

                zip_file.writestr(nuovo_nome, img_bytes)
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(1.5) # Pausa leggermente più lunga per stabilità

        status.text("✅ Elaborazione finita!")
        
        if successo > 0:
            st.success(f"Analisi completata! {successo} file rinominati.")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni_rinominati.zip")
        else:
            st.error("L'AI non è riuscita a leggere i numeri. Verifica che la tua API Key sia attiva su Google AI Studio.")
