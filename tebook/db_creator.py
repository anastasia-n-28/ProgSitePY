"""Скрипт для створення бази даних"""
from tebook.models import Base
from tebook.dal import engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("База даних створена успішно!")