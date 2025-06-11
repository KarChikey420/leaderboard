from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
import sqlite3
from auth import hash_password, verify_password, create_access_token
from model import UserCreate, Token, TokenData, Answer
from jose import jwt, JWTError
from datetime import timedelta
from passlib.context import CryptContext

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "a3a33c4742e8fdbd31a9584994d6f3b693d6fbab848ad9e311026cdaac8fb0ee"
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/signup", response_model=Token)
def signup(user: UserCreate):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                    (user.username, hash_password(user.password)))
        cur.execute("INSERT INTO user_progress (username) VALUES (?)", (user.username,))
        conn.commit()
    except:
        raise HTTPException(status_code=400, detail="Username already taken")
    finally:
        conn.close()
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (form_data.username,))
    user = cur.fetchone()
    conn.close()
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid login")
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/question")
def get_question(username: str = Depends(get_current_user), section: str = "Python"):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT progress FROM user_progress WHERE username=? AND section=?", (username, section))
    progress_row = cur.fetchone()
    if progress_row is None:
        cur.execute("INSERT INTO user_progress (username, section, progress) VALUES (?, ?, ?)", (username, section, 0))
        conn.commit()
        current_q = 0
    else:
        current_q = progress_row["progress"]
    cur.execute("SELECT * FROM questions WHERE section=? ORDER BY id LIMIT 1 OFFSET ?", (section, current_q))
    question = cur.fetchone()
    conn.close()
    if not question:
        return JSONResponse(status_code=200, content={"message": f"{section} quiz completed!"})
    return {
        "id": question["id"],
        "question": question["question"],
        "options": [question["option1"], question["option2"], question["option3"], question["option4"]]
    }

@app.post("/submit")
def submit_answer(answer: Answer, username: str = Depends(get_current_user)):
    section = answer.section
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT progress FROM user_progress WHERE username=? AND section=?", (username, section))
    progress_row = cur.fetchone()

    if progress_row is None:
        cur.execute("INSERT INTO user_progress (username, section, progress) VALUES (?, ?, ?)", (username, section, 0))
        conn.commit()
        current_q = 0
    else:
        current_q = progress_row["progress"]

    cur.execute("SELECT * FROM questions WHERE section=? ORDER BY id LIMIT 1 OFFSET ?", (section, current_q))
    question = cur.fetchone()

    if not question or question["id"] != answer.question_id:
        raise HTTPException(status_code=400, detail="Invalid question")

    # Ensure the user score is initialized
    cur.execute("SELECT score FROM user_scores WHERE username=? AND section=?", (username, section))
    score_row = cur.fetchone()

    if score_row is None:
        cur.execute("INSERT INTO user_scores (username, section, score) VALUES (?, ?, ?)", (username, section, 0))

    # Increment score only if the answer is correct
    if answer.selected_option == question["answer"]:
        cur.execute("UPDATE user_scores SET score = score + 1 WHERE username=? AND section=?", (username, section))
    
    conn.commit()

    # Update user's progress
    cur.execute("UPDATE user_progress SET progress = progress + 1 WHERE username=? AND section=?", (username, section))
    conn.commit()

    # Retrieve updated score
    cur.execute("SELECT score FROM user_scores WHERE username=? AND section=?", (username, section))
    score_row = cur.fetchone()
    score = score_row["score"] if score_row else 0
    conn.close()

    return {"message": "Answer submitted", "score": score}
 
@app.get("/leaderboard")
def leaderboard(section: str = None):
    conn = get_db()
    cur = conn.cursor()

    if section:
        cur.execute("""
            SELECT username, score 
            FROM user_scores 
            WHERE section = ? 
            ORDER BY score DESC 
            LIMIT 10
        """, (section,))
        leaderboard = [{"username": row["username"], "score": row["score"]} for row in cur.fetchall()]
    else:
        cur.execute("""
            SELECT username, SUM(score) as total_score 
            FROM user_scores 
            GROUP BY username 
            ORDER BY total_score DESC 
            LIMIT 10
        """)
        leaderboard = [{"username": row["username"], "score": row["total_score"]} for row in cur.fetchall()]

    conn.close()
    return leaderboard
