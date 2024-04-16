import asyncio
import os

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv()

app = FastAPI()

client = OpenAI(api_key=find_dotenv("OPENAI_API_KEY"))

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get("/")
async def get():
    with open(os.path.join(os.path.dirname(__file__), "templates", "test.html")) as fh:
        data = fh.read()
    return HTMLResponse(content=data, media_type="text/html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.websocket('/gpt')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()

            print('data:', data)

            stream = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": data}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    current_content = chunk.choices[0].delta.content

                    await websocket.send_text(current_content)

                    await asyncio.sleep(0.01)
            
            await websocket.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await websocket.close()
