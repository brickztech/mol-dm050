import time
from typing import Final

from fastapi import APIRouter, FastAPI
from starlette.responses import FileResponse, JSONResponse, StreamingResponse
from starlette.staticfiles import StaticFiles

from api.dto import AuthenticationRequest, AuthenticationResponse, ChatRequest
from langutils import LangUtils, build_query, build_explanation_question, build_query_with_history
from redmine.context import init_context

router = APIRouter()
app = FastAPI()
app.include_router(router)

lang_utils = LangUtils(init_context())

# Mount dist files
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

users: Final = [
    {'id': 1, 'code': 'asdasd', 'name': 'Brickztech', 'email': 'user@brickztech.com', 'password': 'Secret2025!'},
    {'id': 2, 'code': 'asdasdasd', 'name': 'EGIS', 'email': 'user@egis.com', 'password': 'BrickzText2Sql25'}
]

websocket_clients = set()

@app.get('/api/chat_rq')
def chat_rq(
    query: str
) -> str:
    response_iter = lang_utils.call_chat(build_query(query))
    response = ""
    for part in response_iter:
        response += part

    if not response == LangUtils.unknown_context_response:
        return lang_utils.process_response(response, True)
    else:
        print("Context explanation call...")
        return lang_utils.process_response(response, True)

@app.post('/api/authenticate', response_model=AuthenticationResponse)
def authenticate(
    request: AuthenticationRequest
):
    for user in users:
        if user['email'] == request.email:
            if user['password'] == request.password:
                res = AuthenticationResponse(code=user['code'], name=user['name'], email=user['email'])
                return JSONResponse(status_code=200, content=res.model_dump())
            else:
                return JSONResponse(status_code=400, content='Unathorized')
    return JSONResponse(status_code=404, content='Not found')

def generate_numbers():
    for i in range(1, 11):
        yield f"{i}\n"
        time.sleep(1)  # simulate streaming delay

@app.post("/api/chat_rq_stream", response_class=StreamingResponse)
def chat_rq_stream(
request: ChatRequest
    ) -> StreamingResponse:
    response_iter = lang_utils.call_chat(build_query_with_history(request.query, request.history))
    return StreamingResponse(response_iter, media_type="text/plain")

# static content serving
@app.get("/")
async def serve_root():
    for client in websocket_clients:
        await client.send_text("Welcome to the FastAPI STOMP WebSocket server!")
    return FileResponse("dist/index.html")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("dist/index.html")

