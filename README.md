# PhotoMatch

Confronta le foto presenti nel cestino del NAS (Ugreen) con quelle gia' salvate su
pCloud, in base a nome file, dimensione e data di scatto EXIF. Le corrispondenze
vengono elencate in una tabella ed esportabili in CSV: **nessuna cancellazione
automatica**.

EN: Compares photos in the NAS recycle bin against the pCloud photo library by file
name, size and EXIF shooting date. Results are listed in a table and exportable to
CSV; nothing is ever deleted automatically.

## Indice / Contents
- [Guida completa (IT)](docs/GUIDA.md) — install, multi-cartella, esiti, CSV, FAQ
- [Quick start](#quick-start)
- [Installazione](#installazione)
- [Test e build](#test-e-build)

## Quick start
```
pip install -r requirements.txt
python -m photomatch
```
Aggiungi una o piu' cartelle NAS e pCloud, poi premi **Confronta**.
La guida in-app si apre con **F1** (menu Aiuto > Guida).

## Installazione
Scarica l'installer dalla pagina [Releases](https://github.com/enkas79/PhotoMatch/releases):
`PhotoMatch-<ver>-setup.exe` (Windows), `PhotoMatch-<ver>.dmg` (macOS),
`photomatch_<ver>_amd64.deb` (Debian/Ubuntu). Gli installer sono generati
automaticamente dalla CI quando `version.txt` cambia su `main`.

## Test e build
```
pytest tests/                    # test (logica core + UI se PyQt6 disponibile)
python -m PyInstaller build.spec # build desktop (dist/PhotoMatch[.exe])
```

## Licenza
MIT (c) Enrico Martini
