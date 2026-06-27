"""Check Lab 5 — il troncamento della storia per budget di token.
Esegui:  python check_lab5.py   (NON serve la chiave API).

Sostituisce LLMClient.chat con una finta, riempie la storia di messaggi lunghi con
un budget minuscolo e verifica che i turni più vecchi vengano scartati.
"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test")   # evita errori all'import; nessuna chiamata reale

from llm_client import LLMClient
from chatbot import Chatbot, conta_token


def _chat_finto(self, messaggi, instructions=None):
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


def conta_token_ok():
    return (isinstance(conta_token([{"role": "user", "content": "ciao"}]), int)
            and conta_token([{"role": "user", "content": "ciao"}]) > 0
            and conta_token([]) == 0)


def tronca():
    b = Chatbot(budget_token=5)                  # budget minuscolo: forza il taglio
    for i in range(6):
        b.send(f"messaggio abbastanza lungo numero {i}")
    return len(b.storia) <= 4                     # senza taglio sarebbero 12


def main():
    risultati = [
        prova("conta_token misura i token della storia (intero > 0; vuota = 0)", conta_token_ok),
        prova("la storia viene troncata oltre il budget (scarta i turni più vecchi)", tronca),
    ]
    print("\n" + ("Lab 5 completato! Il chatbot ora resta nel budget."
                  if all(risultati) else "Ancora qualcosa da sistemare — vedi i FAIL sopra."))


if __name__ == "__main__":
    main()
