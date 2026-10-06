import sqlite3

from lession24.main import connection, cursor
from models import Movie, MovieCreate

def create_connection():
    """ Creates a connection to the SQlite database"""
    connection = sqlite3.connect("movies.db")
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies(
            id IS INTEGER PRIMARY KEY AUTOINCREMENTE,
            title TEXT NOT NULL,
            director TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

create_table()

def create_movie(movie: MovieCreate) ->int:
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO movies (title, director) VALUES (?,?)", (movie.title, movie.director))
    connection.commit()
    movie_id = cursor.lastrowid
    connection.close()
    return movie_id

def read_movies():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM movies")
    rows = cursor.fetchall()
    connection.close()
    movies = [Movie(id=row[0], title=[1], director=[2]) for row in rows]
    return movies

def read_movie(movie_id:int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM movies WHERE id=", (movie_id))
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    return Movie(id=row["id"], title=row["title"], director=row["director"])


























