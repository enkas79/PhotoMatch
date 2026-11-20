# Guida a PhotoMatch

## Indice
1. [Cosa fa PhotoMatch](#1-cosa-fa-photomatch)
2. [Requisiti](#2-requisiti)
3. [Installazione](#3-installazione)
4. [Primo avvio](#4-primo-avvio)
5. [Scegliere le cartelle](#5-scegliere-le-cartelle)
6. [Opzioni di confronto](#6-opzioni-di-confronto)
7. [Leggere i risultati](#7-leggere-i-risultati)
8. [Esportare il report CSV](#8-esportare-il-report-csv)
9. [Recuperare le foto dal report](#9-recuperare-le-foto-dal-report)
10. [Aggiornamenti](#10-aggiornamenti)
11. [Privacy e sicurezza](#11-privacy-e-sicurezza)
12. [Limiti noti](#12-limiti-noti)
13. [Domande frequenti (FAQ)](#13-domande-frequenti-faq)
14. [Sviluppo e build](#14-sviluppo-e-build)

---

## 1. Cosa fa PhotoMatch
PhotoMatch confronta le foto presenti nel **cestino del NAS** (es. Ugreen) con quelle
gia' salvate su **pCloud**, in base a:

- **nome del file**
- **dimensione in byte**
- **data di scatto EXIF** (opzionale)

Per ogni foto del cestino ottieni un esito e puoi esportare tutto in **CSV**.
**Nessuna foto viene mai cancellata o spostata automaticamente**: PhotoMatch legge
soltanto, e l'unico recupero possibile e' una copia *esplicita* che scegli tu.

## 2. Requisiti
- Windows 10/11, macOS 12+, oppure Linux (Debian/Ubuntu e derivate)
- Nessun requisito hardware particolare; la scansione EXIF e' la fase piu' lenta
  su cartelle con migliaia di foto

## 3. Installazione
Scarica l'installer per il tuo sistema dalla pagina
[Releases di PhotoMatch](https://github.com/enkas79/PhotoMatch/releases):

- **Windows**: `PhotoMatch-<versione>-setup.exe` (installer Inno Setup)
- **macOS**: `PhotoMatch-<versione>.dmg`
- **Linux (Debian/Ubuntu)**: `photomatch_<versione>_amd64.deb`
  (`sudo dpkg -i photomatch_<versione>_amd64.deb`)

### Da sorgente (sviluppo)
```
python -m venv venv
venv\Scripts\activate        # oppure: source venv/bin/activate
pip install -r requirements.txt
python -m photomatch
```
Richiede Python 3.11+.

## 4. Primo avvio
Al primo avvio compare un messaggio di benvenuto: la guida completa (questa pagina)
si apre anche da menu **Aiuto > Guida** o con il tasto **F1**.

## 5. Scegliere le cartelle
Nella sezione **Cartelle** puoi aggiungere **piu' cartelle per lato**:

- **Cestino NAS**: una o piu' cartelle (es. `\\NAS\#recycle`, `D:\Cestino_2024`).
  Ogni cartella viene scansionata **ricorsivamente**, incluidas le sottocartelle.
- **pCloud**: una o piu' cartelle della tua libreria pCloud
  (es. `P:\pCloud Drive\Foto`).

Comandi disponibili per ogni lista:
- **Aggiungi...**: scegli una cartella dal selettore (puoi aprirlo piu' volte)
- **Rimuovi selezionata**: elimina la cartella evidenziata dalla lista
- **Svuota**: svuota tutta la lista

Le liste vengono **ricordate** tra un avvio e l'altro. Se una cartella non e'
raggiungibile (NAS offline, disco scollegato), PhotoMatch lo segnala e la salta,
proseguendo con le altre. Se due cartelle si sovrappongono, ogni foto viene
contata **una sola volta**.

Poi premi **Confronta**.

## 6. Opzioni di confronto
- **Confronta data EXIF**: attivo di default. Legge la data di scatto dai metadati
  della foto (piu' lento, ma distingue le foto con lo stesso nome e dimensione).
  Disattivalo per una scansione velocissima basata solo su nome e dimensione.
- **Tolleranza dimensione (byte)**: differenza massima di dimensione ancora
  considerata "uguale" (utile per foto ri-esportate con metadati diversi).

## 7. Leggere i risultati
La tabella mostra una riga per ogni foto trovata nel cestino NAS:

| Colonna | Significato |
|---|---|
| File | Nome del file nel cestino NAS |
| Esito | Uno dei 4 livelli sotto |
| EXIF NAS / EXIF pCloud | Data di scatto letta dai metadati |
| Percorso NAS / Percorso pCloud | Percorsi completi dei due file |

I 4 esiti possibili:
- **Identica (nome + dimensione + data EXIF)**: la foto e' gia' su pCloud, stessa data
- **Nome e dimensione uguali, data EXIF diversa/assente**: quasi certamente la stessa foto
- **Candidata (stesso nome, dimensione diversa)**: da verificare a occhio
- **Non presente su pCloud**: foto unica del cestino, da salvare se la vuoi tenere

La barra di stato in basso resume il conteggio per esito.

## 8. Esportare il report CSV
Con **Esporta CSV** salvi la tabella in un file `.csv` (codifica UTF-8 con BOM,
compatibile con Excel). Le colonne sono:
`exif_nas, exif_pcloud, file, level, level_label, nas_path, pcloud_path, size_bytes`

Il report e' il file che poi usi per il recupero (paragrafo successivo).

## 9. Recuperare le foto dal report
**Recupera foto da CSV...** legge un report esportato in precedenza e copia dal
cestino NAS nella cartella di destinazione che scegli:
- di default copia solo le foto **uniche** (non presenti su pCloud), mantenendo
  la struttura delle sottocartelle
- spuntando **includi le 'candidate'**, copia anche le candidate in una
  sottocartella `_da_verificare`
- i file gia' presenti nel destino non vengono sovrascritti

## 10. Aggiornamenti
Da **Aiuto > Controlla aggiornamenti** PhotoMatch verifica l'ultima release su
GitHub e ti segnala se e' disponibile una versione piu' recente. Gli installer
sono pubblicati nella pagina Releases del progetto.

## 11. Privacy e sicurezza
- Tutta la scansione avviene **in locale**: nessun file viene caricato da nessuna parte
- L'unica connessione di rete e' il controllo aggiornamenti opzionale su GitHub
- Nessuna cancellazione automatica: PhotoMatch puo' solo **leggere** e, su tua
  richiesta esplicita, **copiare** file fuori dal cestino

## 12. Limiti noti
- Il confronto si basa su nome + dimensione (+ EXIF): rinominare un file lo rende
  "unico" o "candidato" anche se il contenuto e' identico
- Foto con EXIF mancante o corrotto vengono confrontate solo per nome e dimensione
- Formati supportati: jpg, jpeg, png, heic, heif, tif, tiff, bmp, gif, webp,
  cr2, nef, arw, dng, avif

## 13. Domande frequenti (FAQ)
**D: PhotoMatch cancella le foto dal cestino?**
R: No. Non cancella mai nulla, automaticamente o meno.

**D: Posso confrontare piu' cartelle NAS insieme?**
R: Si, aggiungile tutte nella lista "Cestino NAS".

**D: Il NAS e' offline, cosa succede?**
R: Le cartelle non raggiungibili vengono segnalate e saltate; il confronto
procede con quelle disponibili.

**D: Due foto con lo stesso nome in pCloud?**
R: Viene scelta la migliore in base a dimensione ed EXIF; il percorso pCloud
mostrato in tabella e' quello del match scelto.

**D: Come faccio una build locale dell'installer?**
R: Vedi il paragrafo [Sviluppo e build](#14-sviluppo-e-build).

## 14. Sviluppo e build
```
pip install -r requirements.txt pytest
pytest tests/                          # test
python -m PyInstaller build.spec       # build PyInstaller (dist\PhotoMatch.exe)
```
Gli installer per tutte le piattaforme vengono generati automaticamente dalla
CI (GitHub Actions, workflow `Build Installers`) quando `version.txt` cambia su
`main`: il tag di release e' `v<versione>` e gli asset sono
`PhotoMatch-<versione>-setup.exe`, `PhotoMatch-<versione>.dmg` e
`photomatch_<versione>_amd64.deb`.
`version.txt` deve restare allineato a `photomatch.__version__`
(verificato da `tests/test_version.py`).
