import streamlit as st
import google.generativeai as genai
import zipfile
import io
import time
import os

# Configurazione Pagina
st.set_page_config(page_title="Rinomina Bulloni AI", page_icon="🔩")
st.title("🔩 Automazione Bulloni")
st.write("Carica le foto e scarica lo ZIP con i file rinominati automaticamente.")

# 1. Recupero Chiave API dai Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Chiave API non trovata! Inseriscila nei Secrets di Streamlit.")
    st.stop()

# 2. Configurazione Modello
try:
    genai.configure(api_key=api_key)
    # Usiamo flash per velocità e costi zero
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Errore nella configurazione di Google AI: {e}")
    st.stop()

# 3. Interfaccia Caricamento
uploaded_files = st.file_uploader("Trascina qui le foto dei bulloni", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    if st.button("🚀 Avvia Analisi e Genera ZIP"):
        zip_buffer = io.BytesIO()
        successo_totale = 0
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                nome_originale = file.name
                status_text.text(f"⏳ Analisi in corso: {nome_originale}...")
                
                try:
                    # Lettura dei dati immagine
                    img_bytes = file.getvalue()
                    
                    # Prompt specifico per i tuoi bulloni
                    prompt = "Analizza l'immagine dei bulloni. Scrivi SOLO il numero del primo bullone e dell'ultimo bullone separati da un trattino. Esempio: 73-75. Non aggiungere altre parole."
                    
                    # Chiamata all'AI
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ])
                    
                    # Pulizia testo ricevuto
                    risultato = response.text.strip().replace(" ", "")
                    
                    # Controllo se il risultato sembra un intervallo (es. 10-20)
                    if "-" in risultato:
                        nuovo_nome = f"bulloni {risultato}.jpg"
                        successo_totale += 1
                    else:
                        nuovo_nome = f"controlla_{nome_originale}"
                        st.warning(f"⚠️ Risultato incerto per {nome_originale}: {risultato}")
                        
                except Exception as e:
                    st.error(f"❌ Errore tecnico su {nome_originale}: {e}")
                    nuovo_nome = f"errore_{nome_originale}"

                # Aggiunta allo ZIP
                zip_file.writestr(nuovo_nome, img_bytes)
                
                # Aggiornamento progresso
                progress_bar.progress((i + 1) / len(uploaded_files))
                # Piccola pausa per non bloccare l'API gratuita
                time.sleep(1.2)

            status_text.text("✅ Elaborazione completata!")

        # 4. Tasto di Download
        if successo_totale > 0:
            st.success(f"Analisi completata! {successo_totale} file pronti.")
            st.download_button(
                label="💾 SCARICA ZIP RINOMINATO",
                data=zip_buffer.getvalue(),
                file_name="bulloni_rinominati.zip",
                mime="application/zip"
            )
        else:
            st.error("Non è stato possibile rinominare correttamente i file. Controlla gli errori sopra.")

# Note di utilizzo
st.divider()
st.info("💡 Consiglio: Assicurati che i numeri sui bulloni siano ben visibili e non troppo sfocati.")
