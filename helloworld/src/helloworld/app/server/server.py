from fastapi_offline import FastAPIOffline
import uvicorn

app = FastAPIOffline()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def run_server(port:int=9500):
    uvicorn.run(app=app, host="0.0.0.0", port=port)