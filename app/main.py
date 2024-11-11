from fastapi import FastAPI

app = FastAPI()

# Test route
@app.get('/')
async def helloworld():
    return {"message": "Hello World!"}