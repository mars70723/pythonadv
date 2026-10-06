from pydantic import BaseModels

class MovieCreate(BaseModels):
    title:str
    director:str

class Movie(MovieCreate):
    id:int