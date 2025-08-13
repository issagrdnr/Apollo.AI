# app.py
from flask import Flask, request, render_template_string
from database import DB, ensure_schema
from core import answer_question

app = Flask(__name__)
db = DB()
ensure_schema(db)

PAGE = """
<!doctype html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Historical AI</title>
<style>
body{font-family:system-ui,Arial,sans-serif;margin:2rem;}
.card{max-width:800px;margin:auto;padding:1rem 1.5rem;border:1px solid #ddd;border-radius:12px;box-shadow:0 1px 6px rgba(0,0,0,.06);}
.input{width:100%;padding:.8rem;font-size:1rem;border:1px solid #bbb;border-radius:8px;}
button{padding:.6rem 1rem;font-size:1rem;border-radius:8px;border:1px solid #333;background:#f8f8f8;cursor:pointer;}
.muted{color:#666;font-size:.9rem;}
.answer{margin-top:1rem;white-space:pre-wrap;}
</style>
</head><body>
<div class="card">
  <h1>Historical AI</h1>
  <p class="muted">Ask about a <b>year</b> (e.g., 1066) or an <b>event</b> (e.g., Battle of Hastings). It will answer down to the exact day when known and learn as it goes.</p>
  <form method="POST">
    <input class="input" name="q" placeholder="e.g., When was Apollo 11? or 1914" value="{{q or ''}}" />
    <div style="margin-top:.8rem;"><button type="submit">Ask</button></div>
  </form>
  {% if answer %}
  <div class="answer"><h3>Answer</h3><div>{{ answer }}</div></div>
  {% endif %}
  {% if extra %}
  <div class="muted">Saved: {{ extra.saved }} | Type: {{ extra.type }}</div>
  {% endif %}
</div>
</body></html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    q = ""
    answer = ""
    extra = None
    if request.method == "POST":
        q = request.form.get("q","").strip()
        if q:
            resp = answer_question(db, q)
            answer = resp.get("answer","")
            extra = {"saved": resp.get("saved"), "type": resp.get("type")}
    return render_template_string(PAGE, q=q, answer=answer, extra=extra)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
