"""Client LLM: parla col modello, tiene il conto della spesa, regge gli errori.

Modulo a sé, separato dal chatbot: ogni chiamata al modello passa di qui.
Contiene due modi di parlare col modello:
- chat()        -> aspetta tutta la risposta e la torna in un colpo (Lab 1-3)
- chat_stream() -> torna la risposta a pezzi, man mano che arriva (Lab 4)
"""

from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError

from pricing import cost_usd

# Legge il file .env e carica le variabili d'ambiente (es. OPENAI_API_KEY)
# nell'ambiente di sistema, così OpenAI() qui sotto le trova da sola senza
# che tu debba scrivere la chiave dentro il codice.
load_dotenv()


class LLMClient:

    def __init__(self, model="gpt-4.1-mini", temperature=0.7):
        # Quale modello usare (puoi cambiarlo passando un altro valore,
        # es. LLMClient(model="gpt-4.1")).
        self.model = model

        # "Creatività" delle risposte: valori bassi (vicino a 0) = risposte
        # più prevedibili e ripetibili; valori alti (vicino a 1-2) = risposte
        # più varie/creative ma meno coerenti.
        self.temperature = temperature

        # Il client ufficiale OpenAI: si occupa lui di parlare con i server
        # OpenAI via internet. max_retries=3 -> se una richiesta fallisce per
        # un problema temporaneo, la ritenta automaticamente fino a 3 volte.
        # timeout=30 -> se non arriva risposta in 30 secondi, si arrende.
        self._client = OpenAI(max_retries=3, timeout=30)

        # Contatori che teniamo noi (non li calcola OpenAI): quanto abbiamo
        # spinto in totale e quante chiamate abbiamo fatto da quando questo
        # oggetto esiste.
        self.costo_totale = 0.0
        self.n_chiamate = 0

        # Tupla (token in input, token in output, costo) della SOLA ultima
        # chiamata fatta — utile per stampare "quanto è costato questo turno"
        # senza dover ricalcolare nulla.
        self.ultimo_uso = (0, 0, 0.0)

    def chat(self, messaggi, instructions=None):
        # try/except: proviamo a chiamare il modello, ma siamo pronti a
        # gestire alcuni errori prevedibili invece di far crashare tutto.
        try:
            # responses.create() è la funzione OpenAI che manda davvero la
            # richiesta al modello e aspetta la risposta completa.
            r = self._client.responses.create(
                model=self.model,
                instructions=instructions,  # il "system prompt" (es. self.istruzioni)
                input=messaggi,  # la lista di messaggi {"role":..., "content":...}
                temperature=self.temperature,
            )
        except AuthenticationError:
            # Se la chiave API è sbagliata o assente, OpenAI risponde con
            # questo errore specifico. SystemExit interrompe il programma
            # con un messaggio chiaro, invece di un traceback confuso.
            raise SystemExit("Chiave API non valida o assente: controlla il file .env")
        except APIError as e:
            # Altri errori lato OpenAI (es. server sovraccarico, problemi
            # temporanei): non blocchiamo il programma, ma azzeriamo il
            # conteggio dell'ultima chiamata (fallita = nessun costo) e
            # restituiamo un messaggio di errore leggibile al posto della
            # risposta vera.
            self.ultimo_uso = (0, 0, 0.0)
            return f"[errore API: {type(e).__name__} — riprova tra poco]"

        # Se siamo arrivati qui, la chiamata è andata a buon fine.
        # r.usage contiene quanti token ha "mangiato" questa chiamata.
        u = r.usage

        # cost_usd (definita in pricing.py) trasforma i token in dollari,
        # secondo il prezzo per milione di token di quel modello specifico.
        costo = cost_usd(self.model, u.input_tokens, u.output_tokens)

        # Aggiorniamo i contatori cumulativi dell'intero oggetto LLMClient.
        self.costo_totale += costo
        self.n_chiamate += 1

        # Salviamo i dati di QUESTA chiamata, per chi vuole leggerli subito
        # dopo (es. chat() in chatbot.py stampa il costo del turno appena fatto).
        self.ultimo_uso = (u.input_tokens, u.output_tokens, costo)

        # output_text è già il testo pronto della risposta del modello,
        # senza dover scavare dentro la struttura della risposta OpenAI.
        return r.output_text

    def chat_stream(self, messaggi, instructions=None):
        """Come chat(), ma restituisce la risposta a PEZZI, man mano che arrivano."""
        try:
            # Stessa chiamata di prima, con UNA differenza: stream=True.
            # Questo dice a OpenAI "non aspettare di avere tutta la risposta
            # pronta: mandamela a pezzettini, appena li generi".
            stream = self._client.responses.create(
                model=self.model,
                instructions=instructions,
                input=messaggi,
                temperature=self.temperature,
                stream=True,
            )
        except AuthenticationError:
            raise SystemExit("Chiave API non valida o assente: controlla il file .env")
            # Nota: qui non gestiamo APIError come in chat(), perché con lo
            # streaming gli errori arrivano dentro il ciclo "for" sotto,
            # non al momento della chiamata stessa.

        # "stream" non è la risposta finita: è una sequenza di EVENTI che
        # arrivano nel tempo. Il for li scorre uno per uno, appena arrivano.
        for evento in stream:

            # Questo tipo di evento contiene un pezzetto di TESTO nuovo
            # generato dal modello (un "delta" = una piccola differenza
            # rispetto a prima).
            if evento.type == "response.output_text.delta":
                # yield (non return!) restituisce questo pezzetto SUBITO a
                # chi ha chiamato chat_stream, e poi la funzione "aspetta"
                # qui finché non le viene richiesto il prossimo pezzo.
                # Questo è ciò che rende chat_stream un GENERATORE.
                yield evento.delta

            # Questo tipo di evento arriva una sola volta, alla FINE dello
            # stream, quando la risposta è completa: contiene le statistiche
            # finali (quanti token sono stati usati in tutto).
            elif evento.type == "response.completed":
                u = evento.response.usage

                # Stesso calcolo costo di chat(): qui lo facciamo solo
                # quando arriva questo evento finale, perché solo a quel
                # punto conosciamo il totale dei token usati.
                costo = cost_usd(self.model, u.input_tokens, u.output_tokens)
                self.costo_totale += costo
                self.n_chiamate += 1
                self.ultimo_uso = (u.input_tokens, u.output_tokens, costo)
