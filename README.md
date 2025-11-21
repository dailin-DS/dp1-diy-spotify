Here is the complete Markdown content. You can copy the code block below and paste it directly into your `README.md` file.

````markdown
# Cloud-Native DIY Spotify 🎵 ☁️

A full-stack, event-driven music streaming application built on AWS. This project demonstrates a serverless ingestion pipeline, containerized backend services, and a managed relational database to create a scalable Spotify clone.

### 📺 [Watch the Demo Video](https://youtu.be/hJJ_HMDzN2w)

---

## 🏗️ Architecture

The system uses a decoupled architecture to handle music uploads and streaming separately.

```mermaid
flowchart TD
    User((User / Browser))
    Admin((Admin / You))

    subgraph AWS_Cloud [AWS Cloud Infrastructure]
        direction TB
        
        subgraph S3_Bucket [S3 Bucket]
            Frontend[index.html]
            Media[Song Files .mp3 / .jpg / .json]
        end
        
        subgraph Compute [Compute Layer]
            EC2[EC2 Instance: FastAPI Container]
            Lambda[Lambda Function: Ingestor]
        end

        subgraph Database [Data Layer]
            RDS[(RDS MySQL)]
        end
        
        %% Relationships
        User -- "1. Visits Website" --> Frontend
        Frontend -- "2. Request Song Data" --> EC2
        EC2 -- "3. Query Metadata" --> RDS
        
        Admin -- "4. Uploads Songs" --> Media
        Media -- "5. Triggers Event" --> Lambda
        Lambda -- "6. Inserts Metadata" --> RDS
    end

    %% Styling
    style S3_Bucket fill:#ff9900,stroke:#232f3e,color:white
    style EC2 fill:#ff9900,stroke:#232f3e,color:white
    style Lambda fill:#ff9900,stroke:#232f3e,color:white
    style RDS fill:#3355da,stroke:#232f3e,color:white
````

### Tech Stack

  * **Frontend:** Static HTML/JS/Bootstrap hosted on **Amazon S3**.
  * **Backend API:** **FastAPI** (Python) running in **Docker** on **Amazon EC2**.
  * **Database:** **Amazon RDS** (MySQL) for structured metadata.
  * **Ingestion:** **AWS Lambda** & **Chalice** for serverless event processing.
  * **CI/CD:** GitHub Actions for automated container builds.

-----

## 🚀 Deployment Guide

Follow these steps to deploy your own version of this project.

### Prerequisites

  * An AWS Account.
  * Docker installed locally.
  * Python 3.10+ installed.
  * `pip` packages: `chalice`, `mysql-connector-python`.

### Step 1: Database Setup (RDS)

1.  Create a **MySQL** database instance in Amazon RDS (Free Tier is sufficient).
2.  Ensure your Security Group allows traffic on port `3306` from your IP and your future EC2 instance.
3.  Connect to the database and run the following SQL to create the schema:

<!-- end list -->

```sql
CREATE DATABASE music_db;
USE music_db;

CREATE TABLE genres (
    genreid INT PRIMARY KEY,
    genre VARCHAR(20)
);

CREATE TABLE songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50),
    album VARCHAR(30),
    artist VARCHAR(30),
    genre INT,
    year INT,
    file VARCHAR(200),
    image VARCHAR(150)
);

-- Seed Genres
INSERT INTO genres VALUES (1, 'Rock'), (2, 'Indie'), (3, 'Pop'), (4, 'Hiphop'), (5, 'Jazz'), (6, 'Country'), (7, 'Classical'), (8, 'Other');
```

### Step 2: S3 Bucket Setup

1.  Create an S3 bucket (e.g., `my-spotify-app`).
2.  Enable **Static Website Hosting** in the bucket properties.
3.  Update the Bucket Policy to allow public read access (for streaming MP3s/images):
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
            }
        ]
    }
    ```

### Step 3: Deploy the Backend API

The API serves the song metadata to the frontend.

1.  **Edit `app/main.py`:** Update the `DBHOST`, `DBUSER`, and `DB` variables to match your RDS settings.
2.  **Build & Run with Docker:**
    You can run this locally or on an EC2 instance.
    ```bash
    docker build -t spotify-api .
    docker run -d -p 80:80 -e DBPASS='your_db_password' spotify-api
    ```
3.  **Note:** If deploying on EC2, ensure the instance's Security Group allows inbound HTTP traffic on port 80.

### Step 4: Deploy the Ingestor (Lambda)

This function automatically adds songs to the database when files are uploaded to S3.

1.  Navigate to the `ingestor/` directory.
2.  Update `.chalice/config.json` with your database credentials:
    ```json
    {
      "version": "2.0",
      "app_name": "ingestor",
      "stages": {
        "dev": {
          "environment_variables": {
            "DBHOST": "your-rds-endpoint.amazonaws.com",
            "DBUSER": "admin",
            "DBPASS": "your_db_password",
            "DB": "music_db"
          }
        }
      }
    }
    ```
3.  Deploy using Chalice:
    ```bash
    chalice deploy
    ```

### Step 5: Connect the Frontend

1.  Open `frontend/index.html`.
2.  Find the `url` variable in the script section and update it to your API's address:
    ```javascript
    // Example: EC2 Public IP
    url = "[http://12.34.56.78/songs](http://12.34.56.78/songs)";
    ```
3.  Upload `index.html` to the root of your S3 bucket.

-----

## 🎧 Usage

To add music to your library, you do **not** need to touch the database manually.

1.  Prepare a song bundle with three files sharing the same prefix (e.g., `song1.mp3`, `song1.jpg`, `song1.json`).
2.  The `.json` metadata file must follow this format:
    ```json
    {
      "title": "Song Title",
      "album": "Album Name",
      "artist": "Artist Name",
      "genre": 1,
      "year": 2024
    }
    ```
3.  **Upload these 3 files to your S3 bucket.**
4.  The Lambda function will trigger automatically, parse the JSON, and insert the record into RDS.
5.  Refresh your website to see the new track\!

<!-- end list -->

```
```