
import streamlit as st
import openai
import time
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# === CONFIGURAZIONE INIZIALE ===
st.set_page_config(page_title="Chatbot Assistente Aziendale", page_icon="🤖", layout="centered")

# === LOGO AZIENDALE ===
st.image("image.png", width=100)

# === HEADER CENTRALE CON TITOLO ===
st.markdown("<h1 style='text-align: center;'>🤖 Chatbot Assistente Aziendale</h1>", unsafe_allow_html=True)

# === DESCRIZIONE BREVE ===
st.markdown("""
<div style='text-align: center; padding-bottom: 1em; font-size: 18px;'>
Benvenuto! Questo assistente è in grado di fornirti informazioni sui <strong>prodotti, servizi e caratteristiche dell’azienda ILMAP</strong>.<br>
Scrivi la tua domanda e riceverai una risposta dettagliata in pochi secondi.
</div>
""", unsafe_allow_html=True)

# === CAMPO DI INPUT ===
user_input = st.text_input("Scrivi la tua richiesta...", "")
ai_response = None

# === SEZIONE RISPOSTA AI ===
if user_input:
    with st.spinner("Sto generando la risposta..."):
        try:
            openai.api_key = st.secrets["OPENAI_API_KEY"]
            assistant_id = st.secrets["ASSISTANT_ID"]

            # Crea un nuovo thread
            thread = openai.beta.threads.create()
            openai.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_input)
            run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run_status.status == "completed":
                    break
                time.sleep(1)

            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            raw_response = messages.data[0].content[0].text.value

            # Rimozione citazioni tipo 【4:1†source】
            ai_response = re.sub(r"【\d+:\d+†source】", "", raw_response)

            # Visualizza la risposta
            st.markdown(f"""<div style='background-color: #F0F8FF; padding: 1em; border-radius: 10px; margin-top: 1em;'>{ai_response}</div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Errore: {e}")

# === SEZIONE FEEDBACK ===
if ai_response:
    st.markdown("---")
    st.subheader("💬 Lascia un feedback sul risultato")

    valutazione = st.slider("Quanto sei soddisfatto del risultato?", 1, 5, 3)
    commento = st.text_area("Hai suggerimenti o commenti?")

    if st.button("✅ Invia feedback"):
        try:
            def salva_feedback_su_google_sheet(messaggio, risposta, valutazione, commento):
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)
                sheet = client.open("Chatbot assistente aziendale").worksheet("Foglio1")

                nuova_riga = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    messaggio,
                    risposta,
                    valutazione,
                    commento
                ]
                sheet.append_row(nuova_riga)

            salva_feedback_su_google_sheet(user_input, ai_response, valutazione, commento)
            st.success("Grazie per il tuo feedback! È stato registrato con successo.")
        except Exception as e:
            st.error(f"Errore durante il salvataggio del feedback: {e}")
