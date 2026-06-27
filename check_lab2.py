"""Check Lab 2 — la memoria di Chatbot (send che tiene la storia).
Esegui:  python check_lab2.py   (NON serve la chiave API).

Sostituisce LLMClient.chat con una finta che registra cosa riceve, per verificare
che ora la storia cresca tra un turno e l'altro.
"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test")   # evita errori all'import; nessuna chiamata reale

from llm_client import LLMClient
from chatbot import Chatbot

_ricevute = []


def _chat_finto(self, messaggi, instructions=None):
    _ricevute.append([m["content"] for m in messaggi])
    self.ultimo_uso = (10, 5, 0.0001)
    self.costo_totale += 0.0001
    return "(risposta finta)"


LLMClient.chat = _chat_finto


def prova(nome, fn):
    try:
        ok = bool(fn())
    except NotImplementedError:
        ok, nome = False, nome + "  (non ancora implementato)"
    except Exception as e:
        ok, nome = False, nome + f"  (errore: {type(e).__name__}: {e})"
    print(f"  [{'OK ' if ok else 'FAIL'}] {nome}")
    return ok


def storia_accumula():
    b = Chatbot()
    b.send("ciao")
    return b.storia == [{"role": "user", "content": "ciao"},
                        {"role": "assistant", "content": "(risposta finta)"}]


def memoria_cresce():
    _ricevute.clear()
    b = Chatbot()
    b.send("mi chiamo Marco")
    b.send("come mi chiamo?")
    # con memoria, la seconda chiamata riceve anche il turno precedente
    return len(_ricevute) == 2 and len(_ricevute[1]) > len(_ricevute[0])


def main():
    risultati = [
        prova("dopo un turno la storia ha utente + assistente, in ordine", storia_accumula),
        prova("la memoria cresce tra un turno e l'altro (send rispedisce la storia)", memoria_cresce),
    ]
    print("\n" + ("Lab 2 completato! Passa al Lab 3 (il loop chat)."
                  if all(risultati) else "Ancora qualcosa da sistemare — vedi i FAIL sopra."))


if __name__ == "__main__":
    main()
