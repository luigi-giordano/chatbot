# 🤖 OOP Chatbot con Memoria e Cost-Tracking (Pure Python)

Questo repository contiene un'applicazione conversazionale AI avanzata sviluppata interamente in **Python nativo**, senza l'ausilio di framework esterni (come LangChain o LlamaIndex). Il progetto è stato sviluppato come laboratorio pratico per comprendere le logiche di basso livello che governano l'integrazione dei Large Language Models (LLM) all'interno di software enterprise.

L'obiettivo principale dell'esercizio è stato superare la natura *stateless* delle API dei modelli linguistici, implementando un sistema di memoria storica locale e un monitoraggio finanziario asimmetrico dei token in tempo reale.

---

## 🏗️ Architettura del Sistema

Il software è stato ingegnerizzato seguendo i principi della programmazione a oggetti (OOP), separando nettamente la gestione della rete e dei costi dalla logica interna del flusso di conversazione.



### 1. Il Client Wrapper (`AIClient`)
Questo componente funge da gateway unificato per le richieste HTTP verso i server del provider (es. OpenAI).
* **Gestione dello Stato**: Mantiene in memoria variabili persistenti che accumulano il costo economico totale della sessione e il costo specifico dell'ultimo turno di conversazione.
* **Resilienza (Fail-Safe)**: Incapsula le chiamate all'SDK all'interno di costrutti `try/except` per intercettare preventivamente errori di rete, problemi di autenticazione (Errori 401) o superamento dei limiti di traffico (Rate Limit - Errori 429).
* **Cost-Tracking Nativo**: Esegue il parsing del dizionario JSON di risposta (`usage`) applicando tariffe asimmetriche (il costo dei token di Output è calcolato con un moltiplicatore maggiore rispetto a quelli di Input a causa del calcolo auto-regressivo della GPU).

### 2. L'Orchestratore (`Chatbot`)
Gestisce il comportamento dell'agente conversazionale e la sottomissione del contesto.
* **Memoria Multi-Turno**: Alimenta una lista locale di messaggi (`self.history`) che registra la cronologia sotto forma di dizionari strutturati con ruoli espliciti (`system`, `user`, `assistant`).
* **Politica di Gestione del Budget**: Include un algoritmo di troncamento automatico del contesto per evitare lo sforamento della *Context Window* del modello e l'esplosione dei costi. Se il computo stimato dei token storici supera una soglia prefissata, il chatbot scarta le coppie di messaggi più vecchie, preservando intatto il *System Prompt* iniziale e l'ultimo input dell'utente.

---

## 🚀 Fasi di Sviluppo (Ciclo dei Laboratori)

Il progetto è stato sviluppato in modalità incrementale attraverso 5 step evolutivi:

| Fase | Titolo | Descrizione Tecnica |
| :--- | :--- | :--- |
| **Lab 1** | *Il Bot Parla* | Inizializzazione della classe con iniezione delle istruzioni di sistema (*System Prompt*) per risposte single-turn. |
| **Lab 2** | *Farlo Ricordare* | Implementazione dello stack di memoria locale per memorizzare e rispedire l'intera cronologia ad ogni chiamata HTTP `POST`. |
| **Lab 3** | *Il Loop Operativo* | Creazione dell'interfaccia a riga di comando (REPL) in grado di ciclare l'input utente, stampare l'output e mostrare i metadati finanziari (`$[costo]`). |
| **Lab 4** | *Streaming Emulato* | Ottimizzazione della UX tramite l'attivazione di `stream=True`. I token vengono stampati a terminale in tempo reale tramite buffer flussato (`flush=True`), posticipando il calcolo dei costi alla fine del flusso dei chunk. |
| **Lab 5** | *Gestione del Budget* | Integrazione dell'algoritmo di ottimizzazione della memoria con politiche di scarto controllato sui token accumulati. |

---
