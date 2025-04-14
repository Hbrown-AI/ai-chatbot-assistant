
import streamlit as st
import openai
import time
import json
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === CONFIG ===
st.set_page_config(page_title="Assistente Aziendale")

# === LOGO E TITOLO ===
try:
    st.image("logo.png", width=200)
except:
    st.warning("⚠️ Impossibile caricare il logo. Verifica che 'image.png' sia caricato nei file dell'app.")

st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Assistente Aziendale</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Richiedi informazioni su prodotti, servizi o documentazione tecnica aziendale.</p>", unsafe_allow_html=True)

# === STATO INIZIALE ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

# === MOSTRA MESSAGGI DELLA CHAT ===
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === INPUT UTENTE ===
user_input = st.chat_input("Scrivi la tua richiesta...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Sto cercando la risposta..."):
            try:
                openai.api_key = st.secrets["OPENAI_API_KEY"]
                assistant_id = st.secrets["ASSISTANT_ID"]

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
                ai_response = re.sub(r"【\d+:\d+†source】", "", raw_response)

                st.markdown(ai_response)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                st.session_state.last_user_input = user_input
                st.session_state.last_ai_response = ai_response

                # Salvataggio automatico su Google Sheets
                try:
                    def salva_interazione(messaggio, risposta):
                        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
                        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                        client = gspread.authorize(creds)
                        sheet = client.open("Chatbot assistente aziendale").worksheet("Foglio1")
                        sheet.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            messaggio,
                            risposta,
                            "",  # valutazione
                            ""   # commento
                        ])
                    salva_interazione(user_input, ai_response)
                except Exception as e:
                    st.warning(f"⚠️ Interazione non salvata su Google Sheet: {e}")

            except Exception as e:
                st.error(f"Errore durante la risposta: {e}")

# === BLOCCO FEEDBACK SEMPRE IN FONDO ===
if "last_ai_response" in st.session_state and not st.session_state.feedback_given:
    st.divider()
    st.subheader("💬 Lascia un feedback")

    rating = st.slider("Quanto sei soddisfatto della risposta?", 1, 5, 3)
    comment = st.text_area("Hai commenti o suggerimenti?")

    if st.button("✅ Invia feedback"):
        try:
            def aggiorna_feedback(valutazione, commento):
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)
                sheet = client.open("Chatbot assistente aziendale").worksheet("Foglio1")
                records = sheet.get_all_records()
                idx = len(records) + 2
                sheet.update(f"D{idx}", [[rating]])
                sheet.update(f"E{idx}", [[comment]])

            aggiorna_feedback(rating, comment)
            st.success("🎉 Feedback registrato con successo!")
            st.session_state.feedback_given = True
        except Exception as e:
            st.error(f"Errore durante il salvataggio del feedback: {e}")
