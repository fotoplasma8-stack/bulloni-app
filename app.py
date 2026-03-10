import streamlit as st
import google.generativeai as genai
import zipfile
import io
import time

st.set_page_config(page_title="Rinomina Bulloni", page_icon="🔩")
st.title("🔩 Automazione Bulloni")

# Recupera la chiave dai Secrets di Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("Configura la chiave API nei Secrets di Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

files = st.file_uploader("Carica le foto dei bulloni", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if files and st.button("Rinomina e Genera ZIP"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        progress = st.progress(0)
        for i, file in enumerate(files):
            img_data = file.getvalue()
            try:
                res = model.generate_content([
                    "Dimmi solo il numero del primo e dell'ultimo bullone visibili (es: 73-75).",
                    {"mime_type": "image/jpeg", "data": img_data}
                ])
                nuovo_nome = f"bulloni {res.text.strip()}.jpg"
            except:
                nuovo_nome = f"errore_{file.name}"
            
            zip_file.writestr(nuovo_nome, img_data)
            progress.progress((i + 1) / len(files))
            time.sleep(1) # Rispetto limiti free

    st.success("Completato!")
    st.download_button("💾 Scarica ZIP Rinominato", zip_buffer.getvalue(), "bulloni_finiti.zip")
