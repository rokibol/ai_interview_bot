import os
import sqlite3
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from livekit import api
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ডেটাবেজ সেটআপ (ইন্টারভিউয়ের ডাটা সেভ করার জন্য SQLite ব্যবহার করছি)
def init_db():
    conn = sqlite3.connect("interviews.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            score INTEGER,
            decision TEXT,
            client_feedback TEXT,
            customer_feedback TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
def read_root():
    # এটি আপনার রুট ডিরেক্টরির ফাইলগুলোকে সার্ভ করার পারমিশন দেবে
    app.mount("/static", StaticFiles(directory="."), name="static")

    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/get-token")
def get_token(username: str = "customer"):
    token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"))
    token.with_identity(username)
    token.with_name(username)
    token.with_grants(api.VideoGrants(room_join=True, room="interview-room"))
    return {"token": token.to_jwt()}

# নতুন ফিচার: Gemini যখন রেজাল্ট বের করবে, সে এই এপিআই-তে ডেটা পাঠাবে
@app.post("/save-result")
def save_result(data: dict = Body(...)):
    conn = sqlite3.connect("interviews.db")
    cursor = conn.cursor()

    print(data)

    cursor.execute("""
        INSERT INTO results (candidate_name, score, decision, client_feedback, customer_feedback)
        VALUES (?, ?, ?, ?, ?)
    """, (data['name'], data['score'], data['decision'], data['client_feedback'], data['customer_feedback']))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Interview data saved successfully!"}

# নতুন ফিচার: ক্লায়েন্ট ড্যাশবোর্ডে রেজাল্ট দেখার এপিআই
# server.py এর /view-results ফাংশনটি এটি দিয়ে রিপ্লেস করুন:

@app.get("/view-results")
def view_results():
    conn = sqlite3.connect("interviews.db")
    # এটি রো গুলোকে টুপল থেকে ডিকশনারি অবজেক্টে রূপান্তর করবে
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # পাইথন ডিকশনারি লিস্ট তৈরি করা
    results_list = []
    for row in rows:
        results_list.append({
            "id": row["id"],
            "candidate_name": row["candidate_name"],
            "score": row["score"],
            "decision": row["decision"],
            "client_feedback": row["client_feedback"],
            "customer_feedback": row["customer_feedback"]
        })
        
    return {"interviews": results_list}

@app.get("/dashboard", response_class=HTMLResponse)
def view_dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
