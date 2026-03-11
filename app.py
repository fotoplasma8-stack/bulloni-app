import streamlit as st
from google import genai
from google.genai import types
import zipfile
import io
import time

st.set_page_config(page_title="Rinomina Bulloni", page_icon="🔩")
st.title("🔩 Automazione Bulloni (Piano Free)")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Manca la chiave nei Secrets!")
    st.stop()

client = genai.Client(api_key=api_key)

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
                nome_finale = f"errore_{file.name}"
                
                # Sistema di RETRY per il piano gratuito
                for tentativo in range(3):
                    try:
                        status.text(f"Analizzando {file.name} (Tentativo {tentativo+1})...")
                        
                        response = client.models.generate_content(
                            model="gemini-1.5-flash",
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
                        
                        break # Usciamo dal ciclo dei tentativi se ha funzionato
                        
                    except Exception as e:
                        if "429" in str(e):
                            status.warning(f"Quota raggiunta. Attesa di 30 secondi per sblocco...")
                            time.sleep(30)
                        else:
                            status.error(f"Errore: {e}")
                            break
                
                zip_file.writestr(nome_finale, img_data)
                progress.progress((i + 1) / len(uploaded_files))
                
                # PAUSA DI SICUREZZA tra una foto e l'altra (Piano Free)
                time.sleep(5) 
        
        status.text("✅ Elaborazione terminata!")
        if successo > 0:
            st.success(f"Analisi completata! {successo} file rinominati.")
            st.download_button("💾 SCARICA ZIP", zip_buffer.getvalue(), "bulloni.zip")

st.info("Nota: Con il piano gratuito carichiamo un'immagine ogni 5-10 secondi per evitare blocchi.")
