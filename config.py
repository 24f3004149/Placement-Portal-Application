import os

class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URL = 'sqlite:///placement.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
