"""Check Lab 1 — Chatbot.__init__ + send (SENZA memoria).
Esegui:  python check_lab1.py   (NON serve la chiave API).

Non chiama il modello vero: sostituisce LLMClient.chat con una finta che registra
cosa riceve, così possiamo verificare che il Lab 1 NON abbia ancora memoria.
"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test")   # evita errori all'import; nessuna chiamata reale

from llm_client import LLMClient
from chatbot import Chatbot

_ricevute = []


def _chat_finto(self, messaggi, instructions=None):
    _ricevute.append([m["content"] for m in messaggi])   # cosa ha ricevuto il modello
    self.ultimo_uso = (10, 5, 0.0001)
    self.costo_totale += 0.0001
    return "(risposta finta)"


LLMClient.chat = _chat_finto                             # inietta la finta al posto della vera


def prova(nome, fn):
    try:
        ok = bool(fn())
    except NotImplementedError:
        ok, nome = False, nome + "  (non ancora implementato)"
    except Exception as e:
        ok, nome = False, nome + f"  (errore: {type(e).__name__}: {e})"
    print(f"  [{'OK ' if ok else 'FAIL'}] {nome}")
    return ok


def istruzioni_ok():
    s = Chatbot().istruzioni
    return isinstance(s, str) and "Aiko" in s and "italiano" in s.lower()


def nome_personalizzato():
    return "Pippo" in Chatbot(nome="Pippo").istruzioni


def send_torna_testo():
    return Chatbot().send("ciao") == "(risposta finta)"


def senza_memoria():
    _ricevute.clear()
    b = Chatbot()
    b.send("mi chiamo Marco")
    b.send("come mi chiamo?")
    # SENZA memoria, la seconda chiamata riceve SOLO il messaggio corrente
    return len(_ricevute) == 2 and len(_ricevute[1]) == 1


def main():
    risultati = [
        prova("Chatbot() si costruisce e ha .istruzioni (con 'Aiko' e 'italiano')", istruzioni_ok),
        prova("Chatbot(nome='Pippo') usa il nome passato nelle istruzioni", nome_personalizzato),
        prova("send(...) chiama il modello e torna il testo della risposta", send_torna_testo),
        prova("Lab 1: send NON ha ancora memoria (la 2ª chiamata riceve 1 solo messaggio)", senza_memoria),
    ]
    print("\n" + ("Lab 1 completato! Passa al Lab 2 (diamogli la memoria)."
                  if all(risultati) else "Ancora qualcosa da sistemare — vedi i FAIL sopra."))


if __name__ == "__main__":
    main()
