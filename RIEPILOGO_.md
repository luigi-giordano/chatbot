# Riepilogo — Costruzione del Chatbot (Lab 1-5)

> Appunti di ripasso: schema mentale del progetto, spiegazione di ogni Lab e dei file coinvolti.

---

## 1. Struttura del progetto

```
chatbot/
├── .env                  # chiave OpenAI vera (NON va su Git/condiviso)
├── env.example           # modello del .env, senza chiave vera
├── requirements.txt      # dipendenze: openai, tiktoken, python-dotenv
├── pricing.py            # prezzi dei modelli + calcolo costo
├── llm_client.py         # il "telefono" che parla con OpenAI
├── chatbot.py            # il "cervello": personalità, memoria, loop
├── check_lab1.py          
├── check_lab2.py          # check automatici (no chiave API richiesta)
├── check_lab3.py
└── check_lab5.py
```

**Setup ambiente (PowerShell, Windows):**
```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt   # SEMPRE con "python -m", non solo pip
copy env.example .env                        # poi inserire la chiave vera dentro .env
```

---

## 2. I tre file, in breve

| File | Ruolo |
|---|---|
| `pricing.py` | Solo dati: prezzo per milione di token di ogni modello, e la funzione `cost_usd()` che calcola il costo di una chiamata. |
| `llm_client.py` | La classe `LLMClient`: parla davvero con OpenAI, tiene il conto della spesa (`costo_totale`, `ultimo_uso`), gestisce gli errori (chiave sbagliata, problemi API). |
| `chatbot.py` | La classe `Chatbot`: usa `LLMClient`, ci aggiunge personalità (istruzioni), memoria (`storia`), il loop interattivo (`chat()`), lo streaming e il budget di token. |

---

## 3. I 5 Lab, uno strato sopra l'altro

| Lab | Obiettivo | Cosa cambia nel codice | Verifica |
|---|---|---|---|
| **1** | Far parlare il bot, **senza memoria** | `__init__` crea client + istruzioni + storia vuota; `send()` manda solo il messaggio corrente | `check_lab1.py` |
| **2** | Dare **memoria** al bot | `send()` aggiunge ogni messaggio (utente e bot) a `self.storia` e rimanda **tutta** la storia ad ogni turno | `check_lab2.py` |
| **3** | Il **loop** interattivo | `chat()`: ciclo `while True`, legge input, chiama `send()`, stampa risposta e costi, esce con `exit` | `check_lab3.py` |
| **4** | Risposta **in streaming** (a pezzi) | `chat_stream()` in `llm_client.py` (usa `yield`); `send_stream()` e `chat()` aggiornati per stampare pezzo per pezzo | a occhio (`python chatbot.py`) |
| **5** | **Budget di token** sulla memoria | `conta_token()` (con `tiktoken`) + `_tronca_storia()` che scarta i turni più vecchi se si supera il budget | `check_lab5.py` |

> Nota: una volta completato un Lab successivo, il check di un Lab precedente può iniziare a fallire — è normale, perché testa un comportamento ("senza memoria", "senza streaming") che è stato volutamente superato.

---

## 4. Concetti chiave da fissare

### `self.qualcosa` — i nomi sono scelte tue (quasi sempre)
`self.llm`, `self.istruzioni`, `self.storia` sono nomi scelti per leggibilità — non hanno un significato speciale per Python. Le uniche cose "fisse" per contratto sono le chiavi dei messaggi richieste dall'API OpenAI: `"role"` e `"content"`.

### `raise NotImplementedError(...)`
Un errore standard di Python, usato come "segnaposto parlante" per i metodi non ancora scritti. Va sempre **rimosso** una volta scritto il codice vero, altrimenti blocca l'esecuzione anche se il resto del metodo è corretto.

### `return` vs `yield`
- `return` → la funzione finisce e dà **un solo risultato finito**.
- `yield` → la funzione restituisce **un pezzo alla volta** e si "metta in pausa", diventando un *generatore*. Va sempre scorsa con un `for`, non assegnata direttamente a una variabile.

Usato in:
- `chat_stream()` (in `llm_client.py`) → un pezzo di testo alla volta, appena arriva da OpenAI
- `send_stream()` (in `chatbot.py`) → ripassa i pezzi a chi lo chiama, e in più gestisce la memoria

### Indentazione
In Python l'indentazione **è** la struttura del codice (non solo estetica). Dopo un copia-incolla, conviene sempre selezionare il blocco e formattare (`Shift+Alt+F`, con l'estensione **Black Formatter** installata) per evitare `IndentationError`.

---

## 5. Schema riassuntivo di `send` (Lab 1 → Lab 5)

```python
def send(self, testo):
    self.storia.append({"role": "user", "content": testo})   # Lab 2
    self._tronca_storia()                                      # Lab 5 (prima della chiamata)
    risposta = self.llm.chat(self.storia, instructions=self.istruzioni)  # Lab 1
    self.storia.append({"role": "assistant", "content": risposta})       # Lab 2
    self._tronca_storia()                                      # Lab 5 (dopo la chiamata)
    return risposta
```

---

## 6. Cosa abbiamo costruito, in una frase

Un **chatbot da riga di comando** che parla con un modello OpenAI, ha una personalità configurabile (nome/tono), **ricorda** la conversazione, **risponde in streaming** (a pezzi, come ChatGPT), **calcola i costi** in tempo reale e **resta dentro un budget di token** scartando automaticamente i turni più vecchi quando serve — una mini-versione di ChatGPT costruita pezzo per pezzo, capendo il "perché" di ogni passaggio.
