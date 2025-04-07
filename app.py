
import streamlit as st
import openai
import time
import json
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === CONFIG ===
st.set_page_config(page_title="Chatbot Assistente Aziendale", page_icon="🤖")

# === LOGO E TITOLO ===
st.image("logo.png", width=200)
st.markdown("<h1 style='text-align: center;'>🤖 Chatbot Assistente Aziendale</h1>", unsafe_allow_html=True)

# === MESSAGGIO DI BENVENUTO (UNA TANTUM) ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.welcome_shown = False

if not st.session_state.welcome_shown:
    with st.chat_message("assistant"):
        st.markdown("""
👋 Ciao! Sono il tuo assistente aziendale.

Posso aiutarti a reperire rapidamente informazioni su **prodotti, servizi, certificazioni** e altri aspetti dell’azienda.

Scrivi qui sotto la tua richiesta e ti risponderò in modo chiaro e dettagliato.
""")
    st.session_state.welcome_shown = True

# === GESTIONE CHAT CONVERSAZIONALE ===
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === INPUT UTENTE ===
user_input = st.chat_input("Scrivi la tua richiesta...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Sto cercando la risposta..."):
            try:
                # OpenAI credentials
                openai.api_key = st.secrets["OPENAI_API_KEY"]
                assistant_id = st.secrets["ASSISTANT_ID"]

                # Assistant call
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

            except Exception as e:
                st.error(f"Errore: {e}")

# === FEEDBACK POST-RISPOSTA ===
if "last_ai_response" in st.session_state:
    st.divider()
    st.subheader("💬 Lascia un feedback")

    rating = st.slider("Quanto sei soddisfatto della risposta?", 1, 5, 3)
    comment = st.text_area("Hai commenti o suggerimenti?")

    if st.button("✅ Invia feedback"):
        try:
            def salva_feedback(messaggio, risposta, valutazione, commento):
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

            salva_feedback(
                st.session_state.last_user_input,
                st.session_state.last_ai_response,
                rating,
                comment
            )
            st.success("🎉 Feedback registrato con successo!")
            del st.session_state.last_user_input
            del st.session_state.last_ai_response
        except Exception as e:
            st.error(f"Errore durante il salvataggio del feedback: {e}")
