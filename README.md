# PhotoMatch

Confronta le foto presenti nel cestino del NAS (Ugreen) con quelle già salvate su pCloud,
in base a nome file, dimensione e data di scatto EXIF. Le corrispondenze vengono
elencate in una tabella ed esportabili in CSV: nessuna cancellazione automatica.

IT:Avvia con `python -m photomatch`. Scegli la cartella del cestino NAS e la cartella
foto di pCloud, poi premi "Confronta". Esito per file: identica (nome+dimensione+EXIF),
nome e dimensione uguali, stesso nome con dimensione diversa, oppure non presente su pCloud.

EN: Compares photos in the NAS recycle bin against the pCloud photo library by file name,
size and EXIF shooting date. Results are listed in a table and exportable to CSV;
nothing is ever deleted automatically. Run with `python -m photomatch`.

![screenshot](assets/screenshot.png)

## Requisiti / Requirements

- Python 3.11+
- `pip install -r requirements.txt`

## Test

```
pytest tests/
```

## Licenza

MIT (c) Enrico Martini
