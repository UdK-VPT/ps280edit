# Sensorbeschreibung: PIKK Systems PS-280

**Autor**: Werner Kaul-Gothe  
**Department**: VPT  
**Organisation**: Universität der Künste Berlin IAS  
**Datum**: 04. April 2025  

---

## Übersicht

Der Raumklimasensor **PIKK Systems PS-280** ist ein vielseitiger IoT-Sensor zur Überwachung von Raumklimabedingungen. Er misst folgende Umweltgrößen:

- **Raumtemperatur**
- **Relative Luftfeuchtigkeit**
- **CO₂-Gehalt der Luft**

Zusätzlich bietet er umfangreiche Konfigurationsoptionen für Netzwerkeinstellungen, Kommunikationsprotokolle, Logging, Diagnose und Sicherheitsfunktionen. Die Parameter sind nach Modulen gruppiert.

---

## Inhaltsverzeichnis

- [CORE](#core)
- [HUB](#hub)
- [MODEM](#modem)
- [MODBUS](#modbus)
- [MQTT](#mqtt)
- [RUNTIME](#runtime)
- [SEC](#sec)
- [SIG](#sig)
- [THRES](#thres)
- [WIFI](#wifi)

---

## CORE

### `FACTORY_DEFAULTS`
Setzt das Gerät auf Werkseinstellungen zurück.  
**Wertebereich**: 0 (inaktiv) bis 1 (aktiv)  
**Standardwert**: 0

### `FLOG_MAXF`
Maximale Anzahl an Logdateien, die gespeichert werden.  
**Wertebereich**: 0 – 20  
**Standardwert**: 10
**emu Standardwert**: 2

### `SHELL_TO`
Timeout in Sekunden für inaktive Shell-Sitzungen.  
**Wertebereich**: 30 – 300  
**Standardwert**: 30
**emu Standardwert**: 30


### `SHELL_TO_ENA`
Aktiviert oder deaktiviert den Shell-Timeout.  
**Wertebereich**: 0 (aus) – 1 (ein)  
**Standardwert**: 0
**emu Standardwert**: 0


### `WEBCONF`
Legt fest, ob beim Neustart die Webkonfiguration gestartet wird.  
**Wertebereich**: 0 – 1  
**Standardwert**: 0
**emu Standardwert**: 0

---

## HUB

### `EXCH_CNT`
Gerät wechselt nach `EXCH_CNT` Übertragungen in den Austauschmodus.  
**Wertebereich**: 1 – 65535  
**Standardwert**: 10
**emu Standardwert**: 4

### `EXCH_MODE`
Austauschmodus:  
- 0 = deaktiviert  
- 1 = Zähler  
- 2 = Timer (TBD)  
**Standardwert**: 1
**emu Standardwert**: 1

### `EXCH_TIMER`
Zeitgesteuertes Aktivieren des Austauschmodus. Entweder als Liste (`830Z,1615Z`) oder feste Zeitspanne (`1210`).  
**Standardwert**: *leer*
**emu Standardwert**: *leer*

### `EXCH_TO`
Timeout in Sekunden zum Beenden des Austauschmodus bei Inaktivität.  
**Wertebereich**: 5 – 65535  
**Standardwert**: 30
**emu Standardwert**: 20

### `LIFETIME`
Verbindungsdauer in Sekunden.  
**Wertebereich**: 1 – 4294967294  
**Standardwert**: 30
**emu Standardwert**: 10

### `STORE_MAX`
Anzahl an Messzyklen, die gespeichert werden, wenn keine Verbindung besteht.  
**Wertebereich**: 0 – 65535  
**Standardwert**: 250
**emu Standardwert**: 20

### `TO_OVR`
Verbindungstimeout-Überschreibung in Sekunden (0 = deaktiviert).  
**Standardwert**: 0
**emu Standardwert**: 30

### `TSYNC`
Zeitintervall in Minuten für die Zeitsynchronisierung.  
**Standardwert**: 1440
**emu Standardwert**: 1440

### `TSYNC_WAIT`
Legt fest, ob auf Zeitsynchronisation gewartet wird.  
**Standardwert**: 1
**emu Standardwert**: 1

### `TYPE`
Kommunikationsprotokoll.  
**Erlaubte Werte**: `lwm2m`, `mqtt`, `modbus`  
**Standardwert**: `mqtt`
**emu Standardwert**: `mqtt`

### `T_RETRY`
Zeit bis zum nächsten Verbindungsversuch (bei Fehler) in Sekunden.  
**Standardwert**: 60
**emu Standardwert**: 300

### `T_RETRY_MAX`
Maximale Zeit bis zum erneuten Verbindungsversuch bei ansteigendem Intervall.  
**Standardwert**: 43200
**emu Standardwert**: 3600

### `T_RETRY_MODE`
Wiederholmodus:  
- 0 = statisch  
- 1 = exponentiell wachsend  
**Standardwert**: 0
**emu Standardwert**: 1

---

## MODEM

### `APN`
Name des Mobilfunkzugangspunkts.  
**Standardwert**: `gigsky-02`
**emu Standardwert**: `gigsky-02`

### `APN_PW`
Passwort für APN.  
**emu Standardwert**: ``

### `APN_USER`
Benutzername für APN.  
**emu Standardwert**: ``

### `BANDS_LTE`
Verfügbare LTE-M-Bänder.  
**Standardwert**: [20]
**emu Standardwert**: [20]

### `BANDS_NB`
Verfügbare NB-IoT-Bänder.  
**Standardwert**: [8, 20]
**emu Standardwert**: [8,20]

### `CAT`
Netzwerkkategorie:  
- `nb`, `lte-m`, `any`  
**Standardwert**: `any`
**emu Standardwert**: `nb`

### `OP`
Netzbetreiberkennung (MCC|MNC)  
**Standardwert**: 0 (automatisch)
**emu Standardwert**: 0

---

## MODBUS

### `TIMEOUT`
Modbus-Timeout in Minuten.  
**Standardwert**: 120
**emu Standardwert**: 60

---

## MQTT

### `CLIENT_ID`
MQTT-Clientkennung.
**Standardwert**: ``
**emu Standardwert**: ``

### `DIAG_CONN`
Aktiviert Verbindungsdiagnostik.  
**Standardwert**: 0
**emu Standardwert**: 0

### `DIAG_SYS`
Aktiviert Systemdiagnostik.  
**Standardwert**: 0
**emu Standardwert**: 0

### `MAX_RETRY`
Anzahl an Wiederholungsversuchen für Publish.  
**Standardwert**: 1
**emu Standardwert**: ``

### `PL_SIG_ENA`
Aktiviert Payload-Signatur.  
**Standardwert**: 0
**emu Standardwert**: 0

### `PL_SIG_PW`
Passwort für Payload-Signatur.  
**Standardwert**: `psense-client`
**emu Standardwert**: `psense-client`

### `PW`
MQTT-Passwort.

### `QOS`
Quality of Service Level:  
- 0 = at most once  
- 1 = at least once  
- 2 = exactly once  
**Standardwert**: 1
**emu Standardwert**: 0

### `TIMEOUT`
Verbindungs-Timeout in Sekunden.  
**Standardwert**: 15
**emu Standardwert**: 15

---

## RUNTIME

### `IPV4`
Aktuelle IPv4-Adresse  
**Standardwert**: 0.0.0.0
**emu Standardwert**: 0.0.0.0

### `RSSI`
Signalstärke [dBm]  
**Standardwert**: -999
**emu Standardwert**: 15

### `TSYNC`
Laufzeitbasierte Zeitsynchronisation.  
**Standardwert**: 0
**emu Standardwert**: 0

---

## SEC

### `CA_PATH`
Pfad zur CA-Zertifikatsdatei  
**Standardwert**: `/sec/ca.pem`
**emu Standardwert**: `/sec/ca.pem`

### `CC_PATH`
Pfad zum Client-Zertifikat  
**Standardwert**: `/sec/cc.pem`
**emu Standardwert**: `/sec/cc.pem`

### `LOG_LEVEL`
Loglevel der Sicherheitskomponenten (0–4)  
**Standardwert**: 0

### `MODE`
TLS-Modus:  
0 = aus, 1 = keine Validierung, 2 = nur CA, 3 = CA + Client-Zertifikat  
**Standardwert**: 0
**emu Standardwert**: 1

### `SNI_ENA`
Aktiviert Server Name Indication  
**Standardwert**: 0
**emu Standardwert**: 0

### `SNI_HOST`
Servername für SNI  
**Standardwert**: ``
**emu Standardwert**: ``

### `TO_RD`
TLS-Timeout in Sekunden  
**Standardwert**: 3
**emu Standardwert**: 1

### `UK_PATH`
Pfad zum Private Key  
**Standardwert**: `/sec/uk.key`
**emu Standardwert**: `/sec/uk.key`

---

## SIG

### `BOOT_AUR`
Akustische Startmeldung  
**Standardwert**: 1
**emu Standardwert**: 0

### `BOOT_VIS`
Visuelle Startmeldung  
**Standardwert**: 1
**emu Standardwert**: 0

### `REG_VIS`
Visuelle Registrierungsanzeige  
**Standardwert**: 1
**emu Standardwert**: 0

---

## THRES

### `AHT20_HUM_ENA`
Aktiviert Grenzwertüberwachung für Luftfeuchtigkeit  
**Standardwert**: 0
**emu Standardwert**: 0

### `AHT20_HUM_LO` / `AHT20_HUM_HI`
Untere / Obere Grenzwerte für Luftfeuchtigkeit  
**Standardwerte**: -1000 / 1000
**emu Standardwerte**: -1000 / 1000

### `AHT20_TEM_ENA`
Aktiviert Grenzwertüberwachung für Temperatur  
**Standardwert**: 0
**emu Standardwert**: 0

### `AHT20_TEM_LO` / `AHT20_TEM_HI`
Untere / Obere Grenzwerte für Temperatur  
**Standardwerte**: -1000 / 1000
**emu Standardwerte**: -1000 / 1000

### `SUNRISE_CO2_ENA`
Aktiviert Grenzwertüberwachung für CO₂  
**Standardwert**: 0
**emu Standardwert**: 0

### `SUNRISE_CO2_LO` / `SUNRISE_CO2_HI`
Untere / Obere Grenzwerte für CO₂  
**Standardwerte**: 0 / 1000
**emu Standardwerte**: 0 / 1000

---

## WIFI

### `AP_BSSID`
MAC-Adresse des Access Points (hex-String)  
**Standardwert**: ``
**emu Standardwert**: ``

### `AP_PW`
Passwort des WLAN-Zugangs  
**Standardwert**: ``
**emu Standardwert**: ``

### `AP_SEC`
Sicherheitsmodus des WLANs  
**Erlaubt**: `open`, `wpa_psk`, `wpa2_psk`, `wpa3_psk` u.a.  
**Standardwert**: `open`
**emu Standardwert**: `open`

### `AP_SSID`
SSID des Access Points  
**Standardwert**: `default_ap`
**emu Standardwert**: `default_ap`

### `TX_POWER`
Maximale Sendeleistung in dBm  
**Standardwert**: 15
**Standardwert**: 2

---