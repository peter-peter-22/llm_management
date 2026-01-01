import sqlite3
from datetime import datetime

# Create in-memory database
conn = sqlite3.connect(':memory:')


def initialize():
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
                   CREATE TABLE projects
                   (
                       id          INTEGER PRIMARY KEY AUTOINCREMENT,
                       title       TEXT,
                       description TEXT,
                       created_at  TIMESTAMP
                   )
                   """)

    # Insert data
    projects = [
        (
            'AI-image-generator-v3',
            "An AI powered image generator that builds and edits images from user prompts.",
            datetime(2018, 1, 1).timestamp()
        ),
        (
            'Company dashboard',
            "A website to oversee and manage company related data.",
            datetime(2019, 1, 1).timestamp()
        ),
        (
            'AI company agent',
            "An AI agent for doing research based on internal company data.",
            datetime(2020, 1, 1).timestamp()
        ),
        (
            'Ball game',
            "A platformer game with a ball.",
            datetime(2021, 1, 1).timestamp()
        ),
        (
            'Company messenger application',
            "A website for internal discussions of the a company.",
            datetime(2022, 1, 1).timestamp()
        ),
        (
            'AI visual translator',
            "An AI powered OCR and translator for images.",
            datetime(2023, 1, 1).timestamp()
        ),
        (
            'Ball game 2',
            "The second episode of the ball game series. Same ball, different levels.",
            datetime(2024, 1, 1).timestamp()
        ),
    ]
    cursor.executemany("INSERT INTO projects (title,description,created_at) VALUES (?, ?, ?)", projects)
    conn.commit()
