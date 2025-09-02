import base64
import json
from typing import Iterator, List

from openai import OpenAI
from openai.types.responses import (
    ResponseFunctionToolCall,
    ResponseOutputMessage,
    ResponseOutputRefusal,
)
from openai.types.responses.response import Response
from openai.types.responses.response_output_message import Content

from api.dto import HistoryMessage
from langutils import img_extract_pattern, python_code_exp
from langutils.context import ExecutionContext
from langutils.llm_tools import llm_tools_list_descriptor
from shell.llm import LLM
from shell.tools import T2SQLTools


def extract_text_content(content: List[ResponseOutputMessage | ResponseOutputRefusal]) -> str:
    response = ""
    for part in content:
        if type(part) == ResponseOutputMessage and part.type == "output_text":
            response += part.content
    return response


# def get_response(delta: Dict[str, str], created: int = None, id: str = None):
#     created = created or int(datetime.now().timestamp())
#     id = id or str(uuid.uuid4())
#     return dict(id=str(id), model='', created=int(created), choices=[dict(index=0, delta=delta)])


def build_explanation_question(query: str):
    return [
        {"role": "system", "content": LangUtils.system_instruction_for_explanation},
        {"role": "user", "content": LangUtils.prompt_prefix_for_explanation + query},
    ]


def build_query_with_history(query: str, history: list[HistoryMessage]):
    history_list = [{"role": "system", "content": LangUtils.system_instruction_for_query}]
    for item in history:
        history_list.append({"role": str(item.role), "content": item.content})
    history_list.append({"role": "user", "content": LangUtils.prompt_prefix_for_query + query})
    return history_list


def build_query(query: str):
    print("Building query")
    print("System instruction:", LangUtils.system_instruction_for_query)
    print("Query:", LangUtils.prompt_prefix_for_query + query)
    return [
        {"role": "system", "content": LangUtils.system_instruction_for_query},
        {"role": "user", "content": LangUtils.prompt_prefix_for_query + query},
    ]


def fill_in_img_attachments(text: str, tools_handler: T2SQLTools) -> str:

    p_start = text.index("(")
    p_end = text.index(")")
    if p_start == -1 or p_end == -1:
        return text

    matches = img_extract_pattern.finditer(text)
    matches = list(matches)
    parsed = ""
    last_group_end = 0
    for match in matches:
        img_name = match.group(1)
        img_data = tools_handler.get_image(img_name)
        if img_data:
            parsed += text[last_group_end : match.start(0)]
            img_base64 = base64.b64encode(img_data.img_buffer.getvalue()).decode("utf-8")
            parsed += "<img src=\"data:image/png;base64," + img_base64 + "\">"
            last_group_end = match.end(0)
        else:
            parsed += text[last_group_end : match.end(0)]
            last_group_end = match.end(0)
    parsed += text[last_group_end:]
    return parsed


class LangUtils(LLM):

    unknown_context_response = "I can not process this from the given context."
    # these will be set only by the main program
    prompt_prefix_for_query = ""
    system_instruction_for_query = ""
    system_instruction_for_explanation = ""
    prompt_prefix_for_explanation = ""

    def __init__(self, _context: ExecutionContext):
        super().__init__()
        self.context = _context
        self.client = OpenAI()

    def extract_python_code(self, text: str):
        match = python_code_exp.search(text)
        if match and python_code_exp.groups == 1:
            return match.group(1)
        return None

    def get_response(self, messages: list[str]) -> Response:
        return self.client.responses.create(
            model="gpt-4.1",
            input=messages,
            tools=llm_tools_list_descriptor,
        )

    def call_chat(self, messages: list, tools_handler: T2SQLTools | None) -> Iterator[str]:
        raw_response = self.get_response(messages)
        new_function_calls = False
        for response in raw_response.output:
            if type(response) == ResponseFunctionToolCall:
                print(f"call_function {response.name}, arguments {response.arguments}")
                args = json.loads(response.arguments)
                if not tools_handler:
                    raise ValueError("Tools handler is not provided")
                result = tools_handler.call_function(response.name, args)
                messages.append(response)
                messages.append({"type": "function_call_output", "call_id": response.call_id, "output": str(result)})
                new_function_calls = True
            elif type(response) == ResponseOutputMessage:
                return self.extract_stream_content(response.content, tools_handler)
            else:
                # Handle other types of responses
                raise ValueError("Unknown response type")
        if new_function_calls:
            # If there are new function calls, call the chat again with the updated messages
            return self.call_chat(messages, tools_handler)
        raise ValueError("Unknown state")

    def extract_stream_content(self, content: list[Content], tools_handler: T2SQLTools | None) -> Iterator[str]:
        text_to_yield = ""
        for part in content:
            if part.type != "output_text":
                raise ValueError(f"Unexpected content type: {part.type}")
            text_to_yield += part.text
            if not "(" in text_to_yield:
                yield text_to_yield
                text_to_yield = ""
            elif ")" in text_to_yield and tools_handler is not None:
                yield fill_in_img_attachments(text_to_yield, tools_handler)
                text_to_yield = ""

        yield text_to_yield

    # def process_response(self, in_response: str, console_out: bool = False) -> str:
    #     print("response:", in_response)
    #     code = self.extract_python_code(in_response)
    #     if code:
    #         print("python_code:", code)
    #         # Execute the code in the context
    #         return self.context.execute(code, console_out)
    #     else:
    #         print("no code")
    #         return in_response
