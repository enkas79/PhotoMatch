# PhotoMatch

Confronta le foto di **due insiemi di cartelle qualsiasi** (A vs B) e ti dice quali
file di A sono gia' presenti in B: **non cancella e non sposta mai nulla
automaticamente**.

Caso d'uso tipico: le cartelle A sono il **cestino del NAS** (foto "da buttare") e
le cartelle B il **backup su pCloud** — così prima di svuotare il cestino sai quali
foto perderesti davvero. Ma funziona con qualsiasi cartella: locale, di rete, USB.

## Cosa fa
- Confronta ogni file di A con B per **nome**, **dimensione** e **data EXIF**
  (opzionale)
- Puoi aggiungere **piu' cartelle per lato**, scansionate in modo ricorsivo; le
  cartelle sovrapposte non producono doppioni
- Mostra i risultati in una **tabella con 4 esiti** ed esporta tutto in **CSV**
- Recupero selettivo: copia da A in una cartella di destinazione (da un report CSV)
  solo i file **non presenti in B**, senza sovrascrivere nulla
- Tutto **in locale**: l'unica rete usata e' il controllo aggiornamenti su GitHub

## Come funziona
Per ogni file di A ottieni uno di questi esiti:

| Esito | Significato |
|---|---|
| Identica | nome + dimensione + data EXIF uguali: gia' presente in B |
| Nome e dimensione uguali | stesso file, EXIF diversa o assente |
| Candidata | stesso nome, dimensione diversa: da verificare a occhio |
| Non presente in B | file unico di A, da salvare se lo vuoi tenere |

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
2. Aggiungi una o piu' cartelle **A** e una o piu' cartelle **B**
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

**EN**: PhotoMatch compares the files of any two sets of folders (A vs B) by name,
size and EXIF date, lists the matches in a table exportable to CSV and never deletes
anything automatically. Typical use: NAS recycle bin vs pCloud backup. Full guide
(Italian): [docs/GUIDA.md](docs/GUIDA.md). Run from source with `python -m photomatch`.
