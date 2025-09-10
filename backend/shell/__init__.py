from abc import ABC, abstractmethod
from dataclasses import dataclass

from blockz.LLMBlockz import History, RecStrDict


@dataclass
class Element:
    def getcontent(self) -> str:
        raise NotImplementedError()


@dataclass
class TextElement(Element):
    """Carrier of literal texts. Anything that can possibly be found in an LLM reply will make it here: Markdown, links etc. so be prepared"""

    _content: str

    def __repr__(self) -> str:
        return f"TextElement(_content={self._content})"

    def getcontent(self) -> str:
        return self._content


@dataclass
class GraphicsElement(Element):
    """Carrier of a graphics element encoded as a legal string. For now this is PNG over base64"""

    _content: str
    _id: str

    def __repr__(self) -> str:
        return f"GraphicsElement(_content={self._content}, _id={self._id})"

    def getcontent(self) -> str:
        return self._content


@dataclass
class TableElement(Element):
    """Carrier of a table"""

    _content: list[dict[str, str]]
    _id: str

    def __repr__(self) -> str:
        return f"""TableElement(_content={self._content}, _id={self._id})"""

    def getcontent(self) -> list[dict[str, str]]:
        return self._content


class ShellWrapper(ABC):
    @abstractmethod
    def request(self, history: list[RecStrDict], req: str) -> tuple[list[Element], History]:
        """
        Processes the request using the LLM and tools, updating the history.
        Returns a tuple of Result and updated History.
        """
