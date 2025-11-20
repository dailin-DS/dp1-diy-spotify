import os
import json
import mysql.connector
import boto3
from chalice import Chalice

app = Chalice(app_name='ingestor')
app.debug = True

# --- CONFIGURATION (NO CHANGES NEEDED HERE) ---
S3_BUCKET = 'esd4uq-dp1-spotify'
s3 = boto3.client('s3')
baseurl='https://esd4uq-dp1-spotify.s3.us-east-1.amazonaws.com'
DBHOST = os.getenv('DBHOST')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DB = os.getenv('DB')
_SUPPORTED_EXTENSIONS = ('.json',)

# --- LAMBDA HANDLER FUNCTION (MAJOR CHANGES HERE) ---
@app.on_s3_event(bucket=S3_BUCKET, events=['s3:ObjectCreated:*'])
def s3_handler(event):
    # Initialize connection and cursor to None
    db_connection = None
    db_cursor = None

    try:
        if _is_json(event.key):
            # 1. Establish a NEW database connection for this specific invocation
            app.log.debug("Connecting to database...")
            db_connection = mysql.connector.connect(
                user=DBUSER, host=DBHOST, password=DBPASS, database=DB
            )
            db_cursor = db_connection.cursor()
            app.log.debug("Database connection successful.")

            # 2. Get and parse the S3 object
            response = s3.get_object(Bucket=S3_BUCKET, Key=event.key)
            text = response["Body"].read().decode()
            data = json.loads(text)

            # 3. Extract data and formulate URLs
            TITLE = data['title']
            ALBUM = data['album']
            ARTIST = data['artist']
            YEAR = data['year']
            GENRE = data['genre']
            
            identifier = event.key.split('.')[0]
            MP3 = f"{baseurl}/{identifier}.mp3"
            IMG = f"{baseurl}/{identifier}.jpg"

            app.log.debug(f"Received new song: {TITLE} by {ARTIST}")

            # 4. Insert the new song into the database
            add_song_query = (
                "INSERT INTO songs "
                "(title, album, artist, year, file, image, genre) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )
            song_values = (TITLE, ALBUM, ARTIST, YEAR, MP3, IMG, GENRE)
            
            db_cursor.execute(add_song_query, song_values)
            db_connection.commit()
            app.log.debug(f"Successfully inserted song '{TITLE}' into the database.")

    except mysql.connector.Error as err:
        app.log.error(f"Failed to insert song: {err}")
        if db_connection:
            db_connection.rollback()
    except Exception as e:
        app.log.error(f"An unexpected error occurred: {e}")
    finally:
        # 5. ALWAYS close the cursor and connection in the 'finally' block
        # This ensures they close even if an error happened.
        app.log.debug("Closing database connection.")
        if db_cursor:
            db_cursor.close()
        if db_connection:
            db_connection.close()

def _is_json(key):
  return key.endswith(_SUPPORTED_EXTENSIONS)
