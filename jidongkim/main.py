import asyncio
from datetime import datetime
import json
import os

from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values
from sqlalchemy.orm import Session

from db.db import engine, get_db_session
from db.models.BaseModel import Base
from db.models import AuthModels, ChattingModels
from routes.auth_routes import decode_access_token, get_current_user
import routes
from routes.chatting_routes import add_chat
import routes.chatting_routes

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

key = os.environ.get("OPENAI_API_KEY")
print("KEY", key)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://223.130.140.186:5173",
    "http://223.130.128.222:30002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.chatting_routes)
app.include_router(routes.room_routes)
app.include_router(routes.auth_routes)


@app.get("/")
async def get():
    with open(os.path.join(os.path.dirname(__file__), "templates", "test.html")) as fh:
        data = fh.read()
    return HTMLResponse(content=data, media_type="text/html")


@app.websocket("/infer")
async def websocket_endpoint(
    websocket: WebSocket, db: Session = Depends(get_db_session)
):
    await websocket.accept()
    while True and websocket.client_state == WebSocketState.CONNECTED:
        if websocket.client_state != WebSocketState.CONNECTED:
            break

        data = await websocket.receive_text()

        print("data:", data)

        # msg, token, room_id
        data = json.loads(data)

        # email, room_id, exp
        decoded_token = decode_access_token(data["token"])

        db_token = (
            db.query(AuthModels.ChatToken)
            .filter(AuthModels.ChatToken.token == data["token"])
            .first()
        )

        if not decoded_token or not db_token:
            await websocket.send_text("Invalid token")
            await websocket.close()
            break

        if decoded_token["exp"] < datetime.utcnow().timestamp():
            await websocket.send_text("Token expired")
            await websocket.close()
            break

        room_info = (
            db.query(ChattingModels.ChattingRoomModel)
            .filter(ChattingModels.ChattingRoomModel.id == data["room_id"])
            .first()
        )

        if not room_info:
            await websocket.send_text("Room not found")
            await websocket.close()
            break

        user = (
            db.query(AuthModels.User)
            .filter(AuthModels.User.email == decoded_token["email"])
            .first()
        )

        if room_info.owner_id != user.id:
            await websocket.send_text("Not owner of the room")
            await websocket.close()
            break

        print("decoded_token:", decoded_token)

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": data["msg"]}],
            stream=True,
        )

        infer_text = ""

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                current_content = chunk.choices[0].delta.content
                infer_text += current_content

                await websocket.send_text(current_content)

                await asyncio.sleep(0.01)

            else:
                await websocket.close()

        print("str:", infer_text)

        add_chat(
            room_id=data["room_id"],
            question=data["msg"],
            answer=infer_text,
            db=db,
            user=user,
        )
