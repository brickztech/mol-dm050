from typing import Tuple

from dotenv import load_dotenv

from api.dto import HistoryMessage, Role
from langutils.llm_tools import ToolsHandler
from langutils.open_ai import LangUtils, build_query_with_history
from redmine.context import init_context
from shell.llm import LLM, History, Result, Shell, TextElement
from shell.tools import T2SQLTools

print("=" * 10)


class MolShell(Shell):
    def request(self, llm: LLM, tools: T2SQLTools, history: History, req: str) -> Tuple[Result, History]:
        """
        Processes the request using the LLM and tools, updating the history.
        Returns a tuple of Result and updated History.
        """

        history_list: list[HistoryMessage] = []
        for item in history:
            for key in item.keys():
                content = item[key]
                if isinstance(content, str):
                    history_item = HistoryMessage(role=Role(key), content=content)
                    history_list.append(history_item)
                else:
                    print("Unknown history item", item)

        response_iterator = llm.call_chat(build_query_with_history(req, history_list), tools)
        response: Result = []
        for part in response_iterator:
            response.append(TextElement(part))
            print(part, end="", flush=True)
        _new_history = history.copy()
        _new_history.append({"user": req})

        _text_content = ""
        for element in response:
            if isinstance(element, TextElement):
                _text_content += element.getcontent()
            else:
                print("Unknown element in response", element)

        _new_history.append({"assistant": _text_content})

        return response, _new_history


if __name__ == "__main__":
    load_dotenv()
    context = init_context()
    lang_utils = LangUtils(context)
    tools = ToolsHandler(context)
    history: History = []
    shell = MolShell()
    while True:
        user_input = input("Ask me >>> ")
        if user_input == "exit":
            break
        try:
            result, new_history = shell.request(lang_utils, tools, history, user_input)
            for item in result:
                print(item.getcontent(), end="", flush=True)
        except Exception as e:
            print("Error execute", e)
