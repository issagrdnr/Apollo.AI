# historical_ai.py
from database import DB, ensure_schema
from core import answer_question
import random, datetime

def auto_grow(db: DB, n: int = 5):
    current_year = datetime.datetime.now().year
    tried = 0
    learned = 0
    while learned < n and tried < n*5:
        y = random.randint(1, current_year)
        resp = answer_question(db, str(y))
        if resp.get("saved"):
            print(f"[Auto-Learn] {y} → saved")
            learned += 1
        tried += 1

def main():
    db = DB()
    ensure_schema(db)
    print("\n[Auto-growth] Learning random years...")
    auto_grow(db, 5)
    print("\nHi! Ask me about a year or an event (type 'list', 'stats', or 'quit')")
    while True:
        q = input("\n> ").strip()
        if q.lower() in ("quit","exit","q"): break
        if q.lower().startswith("list"):
            try: limit = int(q.split()[-1])
            except: limit = 10
            rows = db.recent(limit)
            if not rows: print("No entries yet.")
            else:
                for y,d,e,t in rows:
                    print(f"- {t} | {y or ''} | {d}: {e}")
            continue
        if q.lower().startswith("stats"):
            total, bounds = db.stats()
            print(f"Total stored events: {total}")
            print(f"Year range covered: {bounds[0]}–{bounds[1]}")
            continue
        resp = answer_question(db, q)
        print(resp["answer"])

if __name__ == "__main__":
    main()
