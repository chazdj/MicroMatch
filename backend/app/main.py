from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "MicroMatch API is running!"}