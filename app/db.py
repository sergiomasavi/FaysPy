from sqlalchemy import create_engine, Column, Integer, Float, \
    String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

engine = create_engine('sqlite:///app/databases/fays-web-dev.db', connect_args={'check_same_thread':False})
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
