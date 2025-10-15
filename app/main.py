import os
from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DBHOST = "database-1.c6zeoiy22gcj.us-east-1.rds.amazonaws.com"
DBUSER = "admin"
DBPASS = os.getenv("DBPASS")
DB = "esd4uq"

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            user=DBUSER,
            host=DBHOST,
            password=DBPASS,
            database=DB
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get('/genres')
def get_genres():
    query = "SELECT * FROM genres ORDER BY genreid;"
    db = None
    cur = None
    try:
        db = get_db_connection()
        cur = db.cursor()
        cur.execute(query)
        headers = [x[0] for x in cur.description]
        results = cur.fetchall()
        json_data = []
        for result in results:
            json_data.append(dict(zip(headers, result)))
        return {"data": json_data}
    except Error as e:
        print("Error reading data from MySQL table", e)
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        if cur:
            cur.close()
        if db:
            db.close()

@app.get('/songs')
def get_songs():
    """
    Fetch all songs from the database, joining with the genres table to get the genre name.
    """
    query = """
        SELECT
            s.id,
            s.title,
            s.artist,
            s.album,
            s.year,
            s.file,
            s.image,
            g.genre
        FROM songs s
        JOIN genres g ON s.genre = g.genreid
    """
    db = None
    cur = None
    try:
        db = get_db_connection()
        cur = db.cursor()
        cur.execute(query)
        headers = [x[0] for x in cur.description]
        results = cur.fetchall()
        json_data = []
        for result in results:
            json_data.append(dict(zip(headers, result)))
        return json_data
    except Error as e:
        print("Error reading data from MySQL table", e)
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        if cur:
            cur.close()
        if db:
            db.close()