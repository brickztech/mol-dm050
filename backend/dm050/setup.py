import json

from openai import OpenAI

from blockz.LLMBlockz import OpenAILikeLLM, RecStrDict
from langutils.context import SQLContext
from langutils.llm_tools import ToolsHandler
from shell import ShellWrapper

from . import shell as dm050
from . import shellutils as su


def init_dm050_context() -> SQLContext:
    return SQLContext()


class DM050Tools(ToolsHandler):
    def __init__(self, context):
        super().__init__(context)


class DM050Shell(ShellWrapper):
    def __init__(self):
        self.context = SQLContext()
        self.tools = DM050Tools(self.context)
        self.client = OpenAI()
        # llm = LangUtils(context)
        self.llm = OpenAILikeLLM(self.client, "gpt-4.1")

    def request(self, req: str, shell_history: str) -> tuple[list[su.Element], list[RecStrDict]]:
        if shell_history == "":
            history = []
        else:
            history = json.loads(shell_history)

        return dm050.request(self.llm, self.tools, history, req)
