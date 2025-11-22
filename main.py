"""
TeBook - система для створення презентацій з чернеток

Запуск сервера:
    uvicorn tebook.main:app --reload --port 8000

Або через FastAPI CLI:
    fastapi dev tebook/main.py
"""

from tebook.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)