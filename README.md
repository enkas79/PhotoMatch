# PhotoMatch

Confronta le foto presenti nel **cestino del NAS** (es. Ugreen) con quelle gia'
salvate su **pCloud** e ti dice quali sono gia' al sicuro: **non cancella mai
nulla automaticamente**.

## Cosa fa
- Confronta ogni foto del cestino con pCloud per **nome file**, **dimensione** e
  **data di scatto EXIF** (opzionale)
- Puoi aggiungere **piu' cartelle per lato** (NAS e pCloud), scansionate in modo
  ricorsivo; le cartelle sovrapposte non producono doppioni
- Mostra i risultati in una **tabella con 4 esiti** ed esporta tutto in **CSV**
- Recupero selettivo: copia fuori dal cestino solo le foto **uniche** (e
  volendo le "candidate") da un report CSV, senza sovrascrivere nulla
- Tutto **in locale**: l'unica rete usata e' il controllo aggiornamenti su GitHub

## Come funziona
Per ogni foto del cestino ottieni uno di questi esiti:

| Esito | Significato |
|---|---|
| Identica | nome + dimensione + data EXIF uguali: gia' su pCloud |
| Nome e dimensione uguali | stessa foto, EXIF diversa o assente |
| Candidata | stesso nome, dimensione diversa: da verificare a occhio |
| Non presente su pCloud | foto unica del cestino, da salvare se la vuoi tenere |

La guida completa e dettagliata e' in [docs/GUIDA.md](docs/GUIDA.md).

## Requisiti
- Windows 10/11, macOS 12+ oppure Linux (Debian/Ubuntu e derivate)
- Da sorgente: Python 3.11+ e `pip install -r requirements.txt`

## Installazione
Scarica l'installer dalla pagina [Releases](https://github.com/enkas79/PhotoMatch/releases):

- Windows: `PhotoMatch-<versione>-setup.exe`
- macOS: `PhotoMatch-<versione>.dmg`
- Linux: `photomatch_<versione>_amd64.deb`

Gli installer sono generati automaticamente dalla CI (workflow `Build Installers`)
quando `version.txt` cambia su `main`.

## Come si usa
1. Avvia l'app (installer oppure `python -m photomatch`)
2. Aggiungi una o piu' cartelle **Cestino NAS** e una o piu' cartelle **pCloud**
3. Premi **Confronta**, leggi la tabella, esporta il CSV se serve

La guida in-app si apre dal menu **Aiuto > Guida** o con **F1**.

## Sviluppo
```
pytest tests/                     # test (logica core + smoke UI se PyQt6 disponibile)
python -m PyInstaller build.spec  # build desktop locale (dist/PhotoMatch[.exe])
```
Per una nuova release basta aggiornare `version.txt` (deve restare allineato a
`photomatch.__version__`, controllato da `tests/test_version.py`): la CI compila
gli installer e crea la release `v<versione>` su GitHub.

## Licenza
MIT (c) Enrico Martini

---

**EN**: PhotoMatch compares photos in the NAS recycle bin against the pCloud
library by file name, size and EXIF date, lists matches in a table exportable to
CSV and never deletes anything automatically. Full guide (Italian):
[docs/GUIDA.md](docs/GUIDA.md). Run from source with `python -m photomatch`.
