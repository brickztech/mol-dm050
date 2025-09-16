import json
import logging
import os
import time
from typing import TypedDict

from fastapi.applications import FastAPI
from loguru import logger
from starlette.responses import FileResponse, JSONResponse, StreamingResponse
from starlette.staticfiles import StaticFiles
from typing_extensions import Generator

from api.dto import AuthenticationRequest, AuthenticationResponse, ChatRequest
from blockz.LLMBlockz import RecStrDict
from dm050.setup import DM050Shell
from dm050.shellutils import GraphicsElement, TableElement, TextElement

# from shell.llm import History, TextElement


class InterceptHandler(logging.Handler):
    def emit(self, record):  # type: ignore
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller to get correct stack depth
        frame, depth = logging.currentframe(), 2
        while frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_loguru():
    # Remove existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

    # Configure loguru file logger
    sink: str = os.path.join(os.getenv('LOG_DIR', './log'), 'dm050.log')  # type: ignore
    logger.add(sink, rotation='10 MB', retention=5, enqueue=True, level=logging.DEBUG, backtrace=False, diagnose=False)

    # propagate to the root logger
    loggers = (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "asyncio",
        "starlette",
    )

    for logger_name in loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True

    logger.info('Logger {} configured', 'succesfully')


app = FastAPI()
configure_loguru()


# Mount dist files
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


class UserDict(TypedDict):
    id: int
    code: str
    name: str
    email: str
    password: str


users: list[UserDict] = [
    {'id': 1, 'code': 'asdasd', 'name': 'Brickztech', 'email': 'user@brickztech.com', 'password': 'Secret2025!'},
    {'id': 2, 'code': 'asdasdasd', 'name': 'EGIS', 'email': 'user@egis.com', 'password': 'BrickzText2Sql25'},
]


@app.post('/api/authenticate', response_model=AuthenticationResponse)
def authenticate(request: AuthenticationRequest):
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


def combine_response(response: Generator[str], history: list[RecStrDict]):
    for item in response:
        yield item
    yield "\n===========##}}\n"
    yield json.dumps(history)


def process_result(result) -> Generator[str]:
    for item in result:
        match item:
            case TextElement():
                # Process TextElement if needed
                yield item.getcontent()
            case GraphicsElement():
                yield "<img src=\"data:image/png;base64," + item.getcontent() + "\">"
            case TableElement():
                # Process TableElement if needed
                yield convert_table_to_html(item.getcontent())


def convert_table_to_html(table_data: list[dict[str, str]]) -> str:
    if not table_data:
        return "<table></table>"
    headers = table_data[0].keys()
    html = "<table><tr>"
    for header in headers:
        html += f"<th>{header}</th>"
    html += "</tr>"
    for row in table_data:
        html += "<tr>"
        for header in headers:
            html += f"<td>{row[header]}</td>"
        html += "</tr>"
    html += "</table>"
    return html


@app.post("/api/chat_rq_stream", response_class=StreamingResponse)
def chat_rq_stream(request: ChatRequest) -> StreamingResponse:
    shell = DM050Shell()
    result, new_history = shell.request(request.query, request.shell_history)

    result_gen = process_result(result)
    response = combine_response(result_gen, new_history)
    return StreamingResponse(response, media_type="text/plain")


# static content serving
@app.get("/")
def serve_root():
    return FileResponse("dist/index.html")


@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    return FileResponse("dist/index.html")
