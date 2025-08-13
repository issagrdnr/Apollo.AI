# Historical AI (web-ready)

A small historical assistant that **grows over time**.

- **Year → events**: Ask "1066" and it stores/finds a representative item for that year (from Wikipedia).
- **Event → exact date**: Ask "Battle of Hastings" and it fetches an exact date from Wikidata (down to the day if known) and stores it.

Shared logic lives in `core.py`. Both the terminal app (`historical_ai.py`) and the web app (`app.py`) use it.

## Terminal Quick Start
```bash
pip install -r requirements.txt
python historical_ai.py
```
Try:
- `1066`
- `When was the Battle of Hastings?`
- `When did Apollo 11 land?`
- `When did the Titanic sink?`

Extras:
- `list 10` — recent learned entries
- `stats` — totals + year coverage
- `quit` — exit

## Web Quick Start
```bash
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000/

## Files
- `core.py` – shared logic (Wikidata/Wikipedia, parsing, storing)
- `database.py` – SQLite helpers
- `historical_ai.py` – terminal interface
- `app.py` – Flask web interface
- `requirements.txt` – dependencies
- `README.md` – this guide

## Notes
- Database: `history.db` (created in the same folder).
- Each terminal run auto-learns 5 random years (edit in `historical_ai.py`).
- To reset, delete `history.db`.
- Dates from Wikidata sometimes have month/day unknown; you'll get best-available precision.

Generated: 2025-08-13T17:22:04.625712
