# 🤖 Chatbot Assistente Aziendale

Questo è un MVP per un chatbot aziendale che risponde a domande su prodotti, certificazioni e servizi della [AZIENDA], sfruttando l'Assistant API di OpenAI e un vector store contenente documentazione aziendale.

## 🚀 Funzionalità

- Interfaccia utente con Streamlit
- Integrazione con OpenAI Assistant API
- Recupero automatico delle risposte da documenti indicizzati

## 🧱 Setup del progetto

1. Clona il repository:
```bash
git clone https://github.com/tuo-username/ilmap-chatbot-mvp.git
cd ilmap-chatbot-mvp
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. USA nella sezione secrets:
OPENAI_API_KEY=sk-...
ASSISTANT_ID=asst-...
```

4. Avvia l'app:
```bash
streamlit run app.py
```

## 🌐 Deployment

Puoi pubblicarlo facilmente su [Streamlit Cloud](https://streamlit.io/cloud) seguendo questi passaggi:
- Collega il tuo repo GitHub
- Aggiungi le variabili d’ambiente `OPENAI_API_KEY` e `ASSISTANT_ID`
- Lancia l'app e condividi il link

---

Se vuoi aggiungere documentazione `.txt` nel tuo vector store, caricala nel Playground di OpenAI associato al tuo assistente.
