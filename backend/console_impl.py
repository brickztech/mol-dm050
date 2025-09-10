from typing import Tuple

from dotenv import load_dotenv
from openai.types.responses.response_input_param import ResponseInputParam
from typing_extensions import cast

from blockz.LLMBlockz import History
from langutils.llm_tools import ToolsHandler
from redmine.context import init_sql_context
from redmine.open_ai import LangUtils, build_query
from shell import Element, ShellWrapper, TextElement

print("=" * 10)


class MolShellWrapper(ShellWrapper):
    def __init__(self):
        self.context = init_sql_context()
        self.tools = ToolsHandler(self.context)
        self.llm = LangUtils(self.context)

    def request(self, history: list[dict[str, str]], req: str) -> Tuple[list[Element], History]:
        message_list: ResponseInputParam = cast(ResponseInputParam, build_query(req))
        response_iterator = self.llm.call_chat(message_list, None)

        response: list[Element] = []
        _text_content = ""
        for part in response_iterator:
            response.append(TextElement(part))
            _text_content += part
        return response, []


if __name__ == "__main__":
    load_dotenv()
    shell = MolShellWrapper()
    while True:
        user_input = input("Ask me >>> ")
        if user_input == "exit":
            break
        try:
            result, new_history = shell.request([], user_input)
            for item in result:
                print(item.getcontent(), end="", flush=True)
        except Exception as e:
            print("Error execute", e)
