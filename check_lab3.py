"""Check Lab 3 — il loop Chatbot.chat().   Esegui:  python check_lab3.py   (no chiave API).

Verifica che il loop assembli davvero i pezzi — senza chiamare il modello vero:
sostituiamo LLMClient.chat con uno finto e simuliamo due turni + 'exit'.
Per la prova REALE (con risposte vere) serve la chiave: `python chatbot.py`.
"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test")   # evita errori all'import; nessuna chiamata reale

import builtins

from llm_client import LLMClient
from chatbot import Chatbot

_chiamate = []


def _chat_finto(self, messaggi, instructions=None):
    _chiamate.append(list(messaggi))         # registriamo la storia ricevuta
    self.ultimo_uso = (10, 5, 0.0001)
    self.costo_totale += 0.0001
    return "(risposta finta)"


LLMClient.chat = _chat_finto


def prova(nome, ok):
    print(f"  [{'OK ' if ok else 'FAIL'}] {nome}")
    return ok


def main():
    turni = iter(["mi chiamo Marco", "come mi chiamo?", "exit"])
    input_originale = builtins.input
    builtins.input = lambda *a, **k: next(turni)
    errore = None
    try:
        Chatbot().chat()
    except StopIteration:
        pass                                 # se 'exit' non è gestito, esauriamo gli input
    except Exception as e:
        errore = e
    finally:
        builtins.input = input_originale

    if errore is not None:
        print(f"  [FAIL] il chatbot è andato in errore: {type(errore).__name__}: {errore}")

    risultati = [
        prova("il loop chiama il modello a ogni turno", len(_chiamate) >= 2),
        prova("la memoria cresce tra un turno e l'altro (i messaggi si accumulano)",
              len(_chiamate) >= 2 and len(_chiamate[1]) > len(_chiamate[0])),
    ]
    print("\n" + ("Struttura OK! Ora provalo davvero con la chiave: python chatbot.py"
                  if all(risultati) else "Ancora qualcosa da sistemare — vedi i FAIL sopra."))


if __name__ == "__main__":
    main()
