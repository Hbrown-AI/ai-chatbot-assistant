# app.py
import streamlit as st
import openai
import time

# Legge le chiavi API da Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

st.set_page_config(page_title="ILMAP Chatbot", page_icon="🤖")
st.title("💬 Chatbot ILMAP")
st.write("Fai una domanda sui prodotti, certificazioni o servizi offerti da ILMAP")

# Campo input utente
user_input = st.text_input("Scrivi qui la tua domanda:", "")

if user_input:
    with st.spinner("Sto cercando la risposta..."):
        try:
            # Crea un thread di conversazione
            thread = openai.beta.threads.create()
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )

            # Avvia l'assistente
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )

            # Attendi il completamento
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                time.sleep(1)

            # Recupera la risposta
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            response = messages.data[0].content[0].text.value

            st.success("Risposta:")
            st.write(response)

        except Exception as e:
            st.error(f"Errore: {e}")
