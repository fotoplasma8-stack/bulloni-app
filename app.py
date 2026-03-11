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
    st.error("❌ Chiave API non trovata nei Secrets!")
    st.stop()

# 3. Inizializzazione Google AI (Semplificata)
genai.configure(api_key=api_key)

# Caricamento file
uploaded_files = st.file_uploader("Carica le foto dei bulloni", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi"):
        zip_buffer = io.BytesIO()
        successo = 0
        
        # Inizializziamo il modello qui dentro
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress = st.progress(0)
            status = st.empty()
            
            for i, file in enumerate(uploaded_files):
                nome_originale = file.name
                status.text(f"Analizzando: {nome_originale}...")
                
                try:
                    img_bytes = file.getvalue()
                    
                    # Chiamata pulita senza parametri v1beta che creano errori
                    response = model.generate_content([
                        "Analizza l'immagine. Scrivi SOLO il numero del primo bullone e dell'ultimo separati da trattino (es: 73-75). Niente altro.",
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ])
                    
                    # Prendiamo il testo e puliamolo
                    risultato = response.text.strip().replace(" ", "")
                    
                    if "-" in risultato:
                        nuovo_nome = f"bulloni {risultato}.jpg"
                        successo += 1
                    else:
                        nuovo_nome = f"controlla_{nome_originale}"
                        
                except Exception as e:
                    st.error(f"Errore su {nome_originale}: {e}")
                    nuovo_nome = f"errore_{nome_originale}"

                zip_file.writestr(nuovo_nome, img_bytes)
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(1) # Pausa per evitare blocchi della versione free

        status.text("✅ Elaborazione finita!")
        
        if successo > 0:
            st.success(f"Analisi completata! {successo} file rinominati correttamente.")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni_rinominati.zip")
        else:
            st.error("L'AI non ha restituito i numeri nel formato corretto. Riprova con foto più nitide.")
