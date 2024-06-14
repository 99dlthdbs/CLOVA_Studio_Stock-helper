import asyncio
from datetime import datetime
import json
import os
import requests

from fastapi import FastAPI, Request, WebSocket, Depends, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

llm_server_url = os.environ.get("LLM_SERVER")
llm_server_port = os.environ.get("LLM_SERVER_PORT")

print(llm_server_url, llm_server_port)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
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

# public path
app.mount("/assets", StaticFiles(directory="./dist/assets"), name="assets")


@app.get("/{rest_of_path:path}", response_class=HTMLResponse)
async def web():
    return FileResponse("./dist/index.html", media_type="text/html")


@app.websocket("/infer")
async def websocket_endpoint(
    websocket: WebSocket, db: Session = Depends(get_db_session)
):
    try:
        await websocket.accept()
        while True and websocket.client_state == WebSocketState.CONNECTED:
            if (
                websocket.client_state != WebSocketState.CONNECTED
                or websocket.application_state != WebSocketState.CONNECTED
            ):
                break

            data = await websocket.receive_text()

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

            msgs = []

            for item in room_info.chats:
                msgs.append(
                    {
                        "role": "user",
                        "content": item.question,
                    }
                )
                msgs.append(
                    {
                        "role": "assistant",
                        "content": item.answer,
                    }
                )

            msgs.append(
                {
                    "role": "user",
                    "content": data["msg"],
                }
            )

            r = requests.Session()

            stream = r.post(
                f"{llm_server_url}:{llm_server_port}/stock/chat",
                json=msgs,
                stream=True,
            )

            infer_text = ""

            toggle_read_rag = False
            toggle_read_card_data = False

            rag_data = ""
            card_data = []
            card_data_str = ""

            commands = ""
            send_text = ""

            for line in stream.iter_lines():
                if line:
                    text = line.decode("utf-8")
                    parsing_text = commands + text

                    print(text)
                    print(len(text), text[:5])

                    while len(parsing_text) > 0:
                        if "$#$#$" in parsing_text:
                            pos = parsing_text.find("$#$#$")
                            before = parsing_text[:pos]
                            after = parsing_text[pos + 5 :]
                            if toggle_read_rag:
                                toggle_read_rag = False
                                rag_data += before
                                parsing_text = after
                            else:
                                toggle_read_rag = True
                                rag_data += after
                                parsing_text = parsing_text.replace("$#$#$" + after, "")
                            continue

                        elif "#$#$#" in parsing_text:
                            pos = parsing_text.find("#$#$#")
                            before = parsing_text[:pos]
                            after = parsing_text[pos + 5 :]
                            if toggle_read_card_data:
                                toggle_read_card_data = False
                                card_data_str += before
                                await websocket.send_text(
                                    "#$#$#" + card_data_str + "#$#$#"
                                )
                                await asyncio.sleep(0.01)
                                card_data.append(card_data_str)
                                parsing_text = after
                            else:
                                toggle_read_card_data = True
                                card_data_str = ""
                                parsing_text = after
                            continue

                        elif toggle_read_rag:
                            rag_data += parsing_text
                            parsing_text = ""
                            continue

                        elif toggle_read_card_data:
                            card_data_str += parsing_text
                            parsing_text = ""
                            continue

                        else:
                            infer_text += parsing_text
                            await websocket.send_text(parsing_text)
                            await asyncio.sleep(0.01)
                            parsing_text = ""

            if infer_text == "Internal Server Error":
                pass
            else:
                add_chat(
                    room_id=data["room_id"],
                    question=data["msg"],
                    answer=infer_text,
                    db=db,
                    user=user,
                    card_data=card_data,
                    rag_data=rag_data,
                )

            print("CLODE WEBSOCKET")
            await websocket.close()
    except WebSocketDisconnect:
        print("ERROR DISCONNECTED")
        if (
            websocket.client_state == WebSocketState.CONNECTED
            and websocket.application_state == WebSocketState.CONNECTED
        ):
            await websocket.close()
