import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Iterator
import base64
from numpy.f2py.crackfortran import endifs
from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputRefusal, \
    ResponseOutputText
from openai.types.responses.response import Response

from api.dto import HistoryMessage
from langutils.context import ExecutionContext
from langutils.llm_tools import llm_tools_list_descriptor, ToolsHandler


def extract_text_content(content: List[ResponseOutputMessage | ResponseOutputRefusal]) -> str:
    response = ""
    for part in content:
        response += part.text
    return response

def get_response(delta: Dict[str, str], created: int = None, id: str = None):
    created = created or int(datetime.now().timestamp())
    id = id or str(uuid.uuid4())
    return dict(id=str(id), model='', created=int(created), choices=[dict(index=0, delta=delta)])


def build_explanation_question(query: str):
    return [
        {"role": "system", "content": LangUtils.system_instruction_for_explanation},
        {"role": "user", "content": LangUtils.prompt_prefix_for_explanation + query}
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
        {"role": "user", "content": LangUtils.prompt_prefix_for_query + query}
    ]


class LangUtils:
    python_code_exp = re.compile("```python\\s(.*?)```", re.MULTILINE | re.DOTALL)
    img_extract_example = re.compile("\(attachment://(.*)\)", re.MULTILINE | re.DOTALL)


    client = OpenAI(
    )

    unknown_context_response = "I can not process this from the given context."

    # these will be set only by the main program
    prompt_prefix_for_query = ""
    system_instruction_for_query = ""
    system_instruction_for_explanation = ""
    prompt_prefix_for_explanation = ""

    def __init__(self, _context: ExecutionContext):
        self.context = _context
        self.tools_handler = ToolsHandler(_context)

    def extract_python_code(self, text: str):
        match = self.python_code_exp.search(text)
        if match and LangUtils.python_code_exp.groups == 1:
            return match.group(1)
        return None

    def get_response(self, messages: list) -> Response:
        return self.client.responses.create(
            model="gpt-4.1",
            input=messages,
            tools=llm_tools_list_descriptor,
        )

    def call_chat(self, messages: list) -> Iterator[str]:
        raw_response = self.get_response(messages)
        new_function_calls = False
        for response in raw_response.output:
            if type(response) == ResponseFunctionToolCall:
                print(f"call_function {response.name}, arguments {response.arguments}")
                result = self.tools_handler.call_function(response.name, json.loads(response.arguments))
                messages.append(response)
                messages.append({
                    "type": "function_call_output",
                    "call_id": response.call_id,
                    "output": str(result)
                })
                new_function_calls = True
            elif type(response) == ResponseOutputMessage:
                return self.extract_stream_content(response.content)
            else:
                # Handle other types of responses
                raise ValueError("Unknown response type")
        if new_function_calls:
            # If there are new function calls, call the chat again with the updated messages
            return self.call_chat(messages)
        raise ValueError("Unknown state")

    def extract_stream_content(self, content: List[ResponseOutputText]) -> Iterator[str]:
        text_to_yield = ""
        for part in content:
            if part.type != "output_text":
                raise ValueError(f"Unexpected content type: {part.type}")
            text_to_yield += part.text

            if not "(" in text_to_yield:
                yield text_to_yield
                text_to_yield = ""
            elif ")" in text_to_yield:
                p_start = 0
                try:
                    while p_start < len(text_to_yield):
                        p_start = text_to_yield.index("(", p_start)
                        try:
                            p_end = text_to_yield.index(")", p_start + 1)
                            match = self.img_extract_example.search(text_to_yield, p_start)
                            if match and len(match.groups())==1:
                                img_name = match.group(1)
                                img_data = self.tools_handler.img_cache.get_image(img_name)
                                if img_data:
                                    # <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...">

                                    img_base64 = base64.b64encode(img_data.img_buffer.getvalue()).decode("utf-8")
                                    text_to_yield = text_to_yield[:p_start] + "<img src=\"data:image/png;base64,"+img_base64+"\">" + text_to_yield[p_end+ 1:]
                                    yield text_to_yield
                                else:
                                    yield f'<img src="/assets/unknown.png" alt="Unknown image: {img_name}">'
                                text_to_yield = ""
                            else:
                                p_start += 1
                        except ValueError:
                            pass
                except ValueError:
                    pass
        yield text_to_yield
    def process_response(self, in_response: str, console_out: bool = False) -> str:
        print("response:", in_response)
        code = self.extract_python_code(in_response)
        if code:
            print("python_code:", code)
            # Execute the code in the context
            return self.context.execute(code, console_out)
        else:
            print("no code")
            return in_response
