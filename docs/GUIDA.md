# Guida a PhotoMatch

## Indice
1. [Cosa fa PhotoMatch](#1-cosa-fa-photomatch)
2. [Requisiti](#2-requisiti)
3. [Installazione](#3-installazione)
4. [Primo avvio](#4-primo-avvio)
5. [Scegliere le cartelle A e B](#5-scegliere-le-cartelle-a-e-b)
6. [Opzioni di confronto](#6-opzioni-di-confronto)
7. [Leggere i risultati](#7-leggere-i-risultati)
8. [Esportare il report CSV](#8-esportare-il-report-csv)
9. [Copiare i file non presenti in B](#9-copiare-i-file-non-presenti-in-b)
10. [Aggiornamenti](#10-aggiornamenti)
11. [Privacy e sicurezza](#11-privacy-e-sicurezza)
12. [Limiti noti](#12-limiti-noti)
13. [Domande frequenti (FAQ)](#13-domande-frequenti-faq)
14. [Sviluppo e build](#14-sviluppo-e-build)

---

## 1. Cosa fa PhotoMatch
PhotoMatch confronta i file di **una o piu' cartelle A** con quelli di **una o piu'
cartelle B**, in base a:

- **nome del file**
- **dimensione in byte**
- **data di scatto EXIF** (opzionale, solo per le foto)

Per ogni file di A ottieni un esito e puoi esportare tutto in **CSV**.
**Nessun file viene mai cancellato o spostato automaticamente**: PhotoMatch legge
soltanto, e l'unica copia possibile e' quella *esplicita* che scegli tu.

> **Caso d'uso tipico**: A = cestino del NAS (foto "da buttare"), B = backup su
> pCloud. Prima di svuotare il cestino sai quali foto sono gia' al sicuro.
> Ma funziona con qualsiasi cartella: locale, di rete (NAS), disco USB.

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

## 5. Scegliere le cartelle A e B
Nella sezione **Cartelle** puoi aggiungere **piu' cartelle per lato**:

- **Cartelle A**: le foto/file qui dentro vengono **elencati nei risultati**
  (es. `\\NAS\#recycle`, `D:\Cestino_2024`)
- **Cartelle B**: il **riferimento** del confronto (es. `P:\pCloud Drive\Foto`)

Ogni cartella viene scansionata **ricorsivamente**, incluse le sottocartelle.

Comandi disponibili per ogni lista:
- **Aggiungi...**: scegli una cartella dal selettore (puoi aprirlo piu' volte)
- **Rimuovi selezionata**: elimina la cartella evidenziata dalla lista
- **Svuota**: svuota tutta la lista

Le liste vengono **ricordate** tra un avvio e l'altro. Se una cartella non e'
raggiungibile (disco scollegato, NAS offline), PhotoMatch lo segnala e la salta,
proseguendo con le altre. Se due cartelle si sovrappongono, ogni file viene
contato **una sola volta**.

Poi premi **Confronta**.

## 6. Opzioni di confronto
- **Confronta data EXIF**: attivo di default. Legge la data di scatto dai metadati
  della foto (piu' lento, ma distingue i file con lo stesso nome e dimensione).
  Disattivalo per una scansione velocissima basata solo su nome e dimensione.
- **Tolleranza dimensione (byte)**: differenza massima di dimensione ancora
  considerata "uguale" (utile per file ri-esportati con metadati diversi).

## 7. Leggere i risultati
La tabella mostra una riga per ogni file trovato nelle cartelle A:

| Colonna | Significato |
|---|---|
| File | Nome del file in A |
| Esito | Uno dei 4 livelli sotto |
| EXIF A / EXIF B | Data di scatto letta dai metadati |
| Percorso A / Percorso B | Percorsi completi dei due file |

I 4 esiti possibili:
- **Identica (nome + dimensione + data EXIF)**: presente anche in B con stessa data
- **Nome e dimensione uguali, data EXIF diversa/assente**: quasi certamente lo stesso file
- **Candidata (stesso nome, dimensione diversa)**: da verificare a occhio
- **Non presente nelle cartelle B**: file unico di A, da salvare se lo vuoi tenere

La barra di stato in basso resume il conteggio per esito.

## 8. Esportare il report CSV
Con **Esporta CSV** salvi la tabella in un file `.csv` (codifica UTF-8 con BOM,
compatibile con Excel). Le colonne sono:
`exif_nas, exif_pcloud, file, level, level_label, nas_path, pcloud_path, size_bytes`
(i nomi colonna restano quelli storici per compatibilita' con i report gia' esportati).

Il report e' il file che poi usi per la copia selettiva (paragrafo successivo).

## 9. Copiare i file non presenti in B
**Recupera foto da CSV...** legge un report esportato in precedenza e copia dalle
cartelle A nella cartella di destinazione che scegli:
- di default copia solo i file **non presenti in B**, mantenendo la struttura
  delle sottocartelle
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
  richiesta esplicita, **copiare** file da A verso la destinazione scelta

## 12. Limiti noti
- Il confronto si basa su nome + dimensione (+ EXIF): rinominare un file lo rende
  "non presente in B" o "candidato" anche se il contenuto e' identico
- File con EXIF mancante o corrotto vengono confrontati solo per nome e dimensione
- Formati foto supportati: jpg, jpeg, png, heic, heif, tif, tiff, bmp, gif, webp,
  cr2, nef, arw, dng, avif

## 13. Domande frequenti (FAQ)
**D: PhotoMatch cancella i file?**
R: No. Non cancella mai nulla, automaticamente o meno.

**D: Posso confrontare piu' cartelle insieme?**
R: Si, aggiungile tutte nella lista A (o in B).

**D: Una cartella non e' raggiungibile, cosa succede?**
R: Viene segnalata e saltata; il confronto procede con le cartelle disponibili.

**D: Due file con lo stesso nome in B?**
R: Viene scelto il migliore in base a dimensione ed EXIF; il percorso B mostrato
in tabella e' quello del match scelto.

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
