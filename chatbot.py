"""Il chatbot del corso: una classe sola, costruita a strati nei vari lab.

Lab 1: client + istruzioni + send senza memoria
Lab 2: send con memoria (la storia cresce ad ogni turno)
Lab 3: il loop chat() che usa send() e mostra i costi
Lab 4: send_stream/chat con streaming (risposta a pezzi)
Lab 5: conta_token() + troncamento della storia per budget di token

Verifica:    python check_lab1.py  /  check_lab2.py  /  check_lab3.py  /  check_lab5.py
Prova reale: python chatbot.py   (serve il .env con la chiave)
"""

import tiktoken

from llm_client import LLMClient


def conta_token(messaggi):
    # Lab 5: quanti token "pesa" una lista di messaggi (la storia).
    # Se la lista è vuota, niente da contare: torniamo 0 senza nemmeno
    # caricare l'encoding (più veloce, ed evita un caso limite inutile).
    if not messaggi:
        return 0

    # tiktoken.get_encoding ti dà il "tokenizzatore" giusto: lo stesso
    # concetto già visto in L14 con demo_tokenizzazione.py. "o200k_base" è
    # l'encoding usato dai modelli della famiglia gpt-4o/gpt-4.1.
    encoding = tiktoken.get_encoding("o200k_base")

    totale = 0
    for m in messaggi:
        # encoding.encode(testo) trasforma il testo in una lista di id di
        # token; len(...) ci dice quanti token sono. Sommiamo i token di
        # ogni messaggio (solo il "content", il "role" non viene contato:
        # è solo metadato nostro, non testo mandato/contato dal modello
        # come token separati in questo conteggio semplificato).
        totale += len(encoding.encode(m["content"]))

    return totale


class Chatbot:

    def __init__(self, nome="Aiko", tono="cordiale e conciso", budget_token=None):
        self.llm = LLMClient()
        self.istruzioni = (
            f"Sei {nome}, un assistente che risponde sempre in italiano, "
            f"con un tono {tono}. Non inventare informazioni: se non sai "
            f"qualcosa, dillo chiaramente invece di inventare una risposta."
        )
        self.storia = []

        # Lab 5: il "tetto" di token che la storia può occupare. Se è None
        # (valore di default), il troncamento non scatta mai: il bot si
        # comporta esattamente come nel Lab 2/3 (memoria illimitata).
        self.budget_token = budget_token

    def _tronca_storia(self):
        # Metodo "privato" (per convenzione, nome con _ davanti): serve solo
        # internamente alla classe, non è pensato per essere chiamato da
        # fuori. Si occupa solo di accorciare self.storia se serve.

        # Se non è stato fissato un budget, non c'è nulla da troncare:
        # usciamo subito.
        if self.budget_token is None:
            return

        # "scartiamo i turni più vecchi finché rientra" (dalla slide):
        # ad ogni giro del while togliamo il messaggio più vecchio
        # (storia.pop(0) = il primo della lista, indice 0).
        # "teniamo sempre almeno il messaggio appena arrivato" (dalla slide):
        # per questo la condizione ha "len(self.storia) > 1" -> non
        # svuotiamo mai la lista del tutto, ci fermiamo quando resta 1
        # solo messaggio, anche se quello da solo sfora ancora il budget.
        while len(self.storia) > 1 and conta_token(self.storia) > self.budget_token:
            self.storia.pop(0)

    def send(self, testo):
        self.storia.append({"role": "user", "content": testo})

        # Lab 5: PRIMA di chiamare il modello, controlliamo/accorciamo la
        # storia se ha superato il budget — esattamente come dice la slide:
        # "prima di chiamare il modello, se la storia supera il budget
        # scartiamo i turni più vecchi".
        self._tronca_storia()

        risposta = self.llm.chat(self.storia, instructions=self.istruzioni)
        self.storia.append({"role": "assistant", "content": risposta})

        # Tronchiamo di nuovo anche DOPO aver aggiunto la risposta:
        # la risposta del modello occupa altri token, quindi potrebbe farci
        # risuperare il budget appena fissato sopra. Lo facciamo rientrare
        # di nuovo, così la storia resta sempre sotto controllo per il
        # turno successivo.
        self._tronca_storia()

        return risposta

    def send_stream(self, testo):
        self.storia.append({"role": "user", "content": testo})

        # Stesso principio di send(): tronchiamo prima di interrogare il
        # modello, anche nella versione "a pezzi".
        self._tronca_storia()

        pezzi = []
        for pezzo in self.llm.chat_stream(self.storia, instructions=self.istruzioni):
            pezzi.append(pezzo)
            yield pezzo

        risposta = "".join(pezzi)
        self.storia.append({"role": "assistant", "content": risposta})

        # E di nuovo dopo, per lo stesso motivo di send().
        self._tronca_storia()

    def chat(self):
        print(f"Parli con {self.llm.model}. Scrivi 'exit' per uscire.\n")

        while True:
            testo = input("Tu: ")

            if testo.strip().lower() == "exit":
                print("Alla prossima!")
                break

            print("Bot: ", end="", flush=True)
            for pezzo in self.send_stream(testo):
                print(pezzo, end="", flush=True)
            print()

            _, _, costo_turno = self.llm.ultimo_uso
            print(
                f"  (costo turno: ${costo_turno:.6f} — totale: ${self.llm.costo_totale:.6f})\n"
            )


if __name__ == "__main__":
    Chatbot().chat()
