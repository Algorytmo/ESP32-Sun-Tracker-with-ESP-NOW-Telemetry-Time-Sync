ESP32-Sun-Tracker-with-ESP-NOW-Telemetry-Time-Sync

Un nodo solare autonomo a basso consumo con tracking astronomico, monitoraggio della batteria e sincronizzazione wireless.

##########################################################################

__Introduzione__

Questo progetto ha l’obiettivo di creare uno “smart slot” completamente autonomo ed energeticamente efficiente, provando ad alimentare o ospitare qualsiasi tipo di sensore ambientale nel modo più sostenibile possibile.
L’obiettivo è costruire una piattaforma in grado di operare off‑grid, utilizzando esclusivamente energia solare, massimizzando la durata della batteria tramite un design a bassissimo consumo, una gestione intelligente dell’energia e un preciso inseguimento astronomico del sole.
Il sistema è progettato per essere durevole, modulare e adattabile, permettendo installazioni a lungo termine per monitoraggio ambientale, qualità dell’aria, nodi IoT o qualsiasi dispositivo a basso consumo che possa beneficiare di una fonte energetica autosufficiente.

Questo progetto implementa un nodo ESP32 alimentato a energia solare, completamente autonomo, capace di:

- Tracking solare astronomico (azimuth + elevazione)
- Movimento dual‑axis tramite servo (pan/tilt)
- Monitoraggio di batteria, tensione pannello, corrente e potenza
- Funzionamento ultra‑low‑power tramite deep sleep
- Comunicazione ESP‑NOW con una stazione base
- Handshake bloccante per sincronizzazione affidabile di ora e posizione
- Modalità manuale tramite joystick
- Display OLED per diagnostica in tempo reale

Il sistema è progettato per funzionamento outdoor, a lungo termine e con minima manutenzione, alimentato interamente da un piccolo pannello solare e una batteria Li‑ion.

##########################################################################

__Architettura__

Il progetto è composto da due schede ESP32‑32U:

1. Solar Node (ESP32‑Solar)
```
- Alimentato da batteria + pannello solare
- Si risveglia periodicamente
- Invia telemetria alla base
- Attende (bloccante) ora + coordinate GPS
- Aggiorna l’RTC
- Calcola la posizione del sole
- Muove i servo
- Torna in deep sleep
```

2. Base Station (ESP32‑Base)
```
- Connessa al Wi‑Fi, recupera:
  Geolocalizzazione (via IP‑API)
  Ora (via NTP)
- Attende la telemetria
- Invia ora + lat/lon al nodo solare
```

Questo garantisce sincronizzazione perfetta e zero deriva temporale, anche dopo lunghi cicli di deep sleep.

##########################################################################

__Protocollo Di Comunicazione__

Il sistema utilizza un handshake ESP‑NOW deterministico a due fasi:

- SOLARE → BASE: Pacchetto di telemetria  
- BASE → SOLARE: Ora + Latitudine + Longitudine

Il nodo solare non procede finché la base non risponde.
Questo garantisce:
- RTC sempre corretto
- Tracking astronomico accurato
- Nessuna perdita di pacchetti
- Nessuna race condition

##########################################################################

__Componenti Elettronici__

Alimentazione
```
- Batteria Samsung 18650 Li‑ion
    Tensione nominale: 3.7V
    Tensione massima: 4.2V

- Pannello Solare (6W, 6V)
    Fornisce energia per la carica della batteria e il funzionamento del sistema

- Modulo Caricabatteria Solare CN3791
    Comportamento simile a MPPT ottimizzato per pannelli da 6V
    Gestisce input solare variabile senza blocchi
    Carica la 18650 in sicurezza

- Regolatore LDO MCP1700 (3.3V)  
    Corrente di quiescenza ultra‑bassa (~1.6 µA)
    Alimenta ESP32 e sensori
    Richiede condensatori da 1 µF in ingresso e uscita

- Convertitore Step‑Up 5V (Boost Converter)  
    Eleva la tensione della batteria (3.0–4.2V) a 5V stabili
    Alimenta:
      Servo
      Monitoraggio rail 5V
      Stabilizzato con condensatore da 470 µF per gestire i picchi dei servo
```

Componenti di Controllo
```
- ESP32‑WROOM‑32U (con antenna IPEX)  
    Microcontrollore principale
    Antenna esterna per migliore portata ESP‑NOW
    Gestisce:
      Tracking solare
      Telemetria
      Deep sleep
      Modalità manuale joystick
      Display OLED

- Sensore INA219 (Corrente/Tensione)  
    Misura:
      Tensione pannello
      Corrente pannello
      Potenza (mW)
      Include shunt da 0.1 Ω
      Richiede condensatore da 1 µF per stabilità
```

Componenti Utente
```
- Joystick Analogico  
    VRX, VRY, SW
    Utilizzato per la modalità manuale

- Display OLED SSD1306 (I2C)  
    128×64 pixel
    Mostra:
      Modalità (AUTO/MANUAL)
      Tensione, corrente, potenza
      Angoli pan/tilt
```

__Componenti Passivi__
```
Resistenze
- Partitore batteria: 10 kΩ + 10 kΩ
- Partitore rail 5V: 10 kΩ + 10 kΩ
- Partitore rail 3.3V: 10 kΩ + 10 kΩ
- Shunt INA219: 0.1 Ω (integrato nel modulo)

Condensatori
- Ingresso MCP1700: 1 µF
- Uscita MCP1700: 1 µF
- Stabilizzazione BAT IN: 47 µF
- Smorzamento rail 5V servo: 470 µF
- Filtraggio INA219: 1 µF
```

##########################################################################

__Struttura Software__

Il firmware è completamente modulare:
```
/solar/
main.py
config.py
espnow_handler.py
hardware.py
ina219.py
joystick.py
logging.py
logging_utils.py
power.py
ssd1306.py
telemetry.py
tracking.py
```

Moduli

- main.py
  Entry point principale contenente la logica del nodo solare.

- config.py
  Tutte le costanti e parametri configurabili.

- hardware.py
  ADC, INA219, display, servo, letture tensioni.

- tracking.py
  Calcolo della posizione del sole.

- telemetry.py
  Creazione pacchetto telemetria + invio ESP‑NOW.

- espnow_handler.py
  Inizializzazione peer + ricezione bloccante.

- joystick.py
  Modalità manuale.

- power.py
  Funzioni di deep sleep.

- logging_utils.py
  Sistema di logging.

##########################################################################
__Tracking Astronomico__

Il nodo solare calcola:

- Giorno giuliano
- Anomalia solare
- Longitudine eclittica
- Ascensione retta
- Declinazione
- Tempo siderale locale
- Angolo orario
- Azimuth
- Elevazione

Poi mappa:
- azimuth → servo pan  
- elevation → servo tilt

L’elevazione è limitata a 0–90° per evitare puntamenti sotto l’orizzonte.

##########################################################################

__Gestione Energia__

Il nodo solare è ottimizzato per consumi ultra‑bassi:

- Misura potenza tramite INA219
- Monitoraggio batteria via ADC
- Spegnimento OLED prima del deep sleep
- Deinizializzazione PWM servo prima del sonno
- Deep sleep tra un ciclo e l’altro (default: 10 minuti)
- Wake‑on‑joystick

##########################################################################

__Formato Telemetria__

Esempio pacchetto telemetria:
```
{
  "ts": 1,
  "bat_v": 3.32337,
  "bat_raw": 2062,
  "v5": 4.981832,
  "v5_raw": 3091,
  "v33": 3.092894,
  "v33_raw": 1919,
  "panel_v": 3.212,
  "panel_i": 0.0,
  "panel_p": 0.0,
  "pan": 90,
  "tilt": 90
}
```
##########################################################################

__To Do__

- Migliorare la modalità manuale
- Migliorare la modalità automatica
- Aggiungere foto e grafici dei dati
