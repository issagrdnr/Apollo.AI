# core.py
import re
from typing import Optional, Tuple, Dict, Any
import requests
from database import DB, ensure_schema

YEAR_REGEX = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
MONTHS = [None, "January","February","March","April","May","June","July","August","September","October","November","December"]

def extract_year(text: str) -> Optional[int]:
    m = YEAR_REGEX.search(text)
    return int(m.group(0)) if m else None

def format_wikidata_time(time_str: str) -> str:
    t = time_str.lstrip('+')
    date_part = t.split('T', 1)[0]
    y, m, d = [int(x) for x in date_part.split('-')]
    if m == 0:
        return f"{y}"
    if d == 0:
        return f"{MONTHS[m]} {y}"
    return f"{d} {MONTHS[m]} {y}"

def wikidata_search_event(query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"wbsearchentities","search":query,"language":"en","format":"json","type":"item","limit":str(limit)}
    headers = {"User-Agent":"HistoricalAI/1.0"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=12)
        res = r.json().get("search", [])
        if not res: return None
        return res[0]
    except Exception:
        return None

def wikidata_get_time_claim(qid: str) -> Optional[str]:
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"wbgetentities","ids":qid,"props":"claims","format":"json"}
    headers = {"User-Agent":"HistoricalAI/1.0"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=12)
        claims = r.json().get("entities", {}).get(qid, {}).get("claims", {})
        for pid in ("P585","P580","P571"):
            if pid in claims:
                dv = claims[pid][0].get("mainsnak", {}).get("datavalue", {})
                if dv.get("type") == "time":
                    return dv["value"]["time"]
        return None
    except Exception:
        return None

def event_to_exact_date(event_query: str):
    item = wikidata_search_event(event_query)
    if not item: return None
    qid = item.get("id")
    label = item.get("label") or event_query
    t = wikidata_get_time_claim(qid)
    if not t: return None
    return label, format_wikidata_time(t)

def wikipedia_year_snippet(year: int) -> Optional[str]:
    url = "https://en.wikipedia.org/w/api.php"
    params = {"action":"query","list":"search","srsearch":str(year),"format":"json","srlimit":5}
    headers = {"User-Agent":"HistoricalAI/1.0"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=12)
        hits = r.json().get("query", {}).get("search", [])
        if not hits: return None
        for h in hits:
            title = h.get("title","")
            if title.isdigit() and int(title) == year:
                return f"Events of {year} (Wikipedia year page)"
        return hits[0].get("title")
    except Exception:
        return None

def answer_question(db: DB, text: str):
    ensure_schema(db)
    text = text.strip()
    yr = extract_year(text)
    if yr:
        rows = db.get_events_by_year(yr)
        if rows:
            return {"type":"year","answer":"\n".join(f"{d}: {e}" for d,e in rows),"saved":False,"details":{"year":yr}}
        rep = wikipedia_year_snippet(yr)
        if rep:
            db.save_event(yr, str(yr), rep, "Wikipedia")
            return {"type":"year","answer":f"Learned: {yr} → {rep}","saved":True,"details":{"year":yr}}
        return {"type":"year","answer":"I couldn't find anything for that year.","saved":False,"details":{"year":yr}}
    ev = event_to_exact_date(text)
    if ev:
        title, date_str = ev
        ym = YEAR_REGEX.search(date_str)
        year_val = int(ym.group(0)) if ym else 0
        db.save_event(year_val, date_str, title, "Wikidata")
        return {"type":"event","answer":f"{title} happened on {date_str}.","saved":True,"details":{"event":title,"date":date_str,"year":year_val}}
    return {"type":"event","answer":"I couldn't find an exact date for that event.","saved":False,"details":{"query":text}}
