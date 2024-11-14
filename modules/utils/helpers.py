from config import DatabaseUri
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DatabaseUri)  # Замените на ваш URI подключения

Session = sessionmaker(bind=engine)

def get_session():
    return Session()