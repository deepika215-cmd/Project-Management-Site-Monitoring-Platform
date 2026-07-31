from fastapi import FastAPI

app = FastAPI()

@app.get("/test-db")
def test_db():
    return {"database": "SQLite connected successfully"}