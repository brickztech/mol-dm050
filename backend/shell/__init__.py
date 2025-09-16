import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

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


class ImgData:
    def __init__(self, img_name: str, img_buffer: io.BytesIO):
        self.img_name: str = img_name
        self.create_dt: datetime = datetime.now()
        self.img_buffer = img_buffer


class T2SQLTools(ABC):
    @abstractmethod
    def similar(self, ref: str) -> list[tuple[str, str, str]]:
        """
        Returns the topN (default 10) most similar (value, table, field) tuples to the given ref
        from all soft-searchable columns in all tables.
        """

    @abstractmethod
    def data(self, sql: str) -> list[dict[str, str]]:
        """
        Executes the given SQL and returns the result as a list of dicts (field: value).
        """

    @abstractmethod
    def piechart(self, sql: str, labelfield: str, valuefield: str) -> str:
        """
        Executes the SQL and generates a pie chart from the result.
        labelfield: column name for labels, valuefield: column name for values.
        Returns a string (e.g., image path or base64).
        """

    @abstractmethod
    def linechart(self, sql: str, xfield: str, ylabel: str, name: str, value: str) -> str:
        """
        Executes the SQL and generates a line chart.
        xfield: column for x-axis, ylabel: y-axis label, name: the name of the line field, value: the name of the value field.
        xflelf, name and value parameters has to be used to extract values from the SQL result.
        Returns a string (e.g., image path or base64).
        """

    @abstractmethod
    def barchart(self, sql: str, xfield: str, ylabel: str, name: str, value: str) -> str:
        """
        Executes the SQL and generates a bar chart.
        xfield: column for x-axis, ylabel: y-axis label, name: the name of the bar field, value: the name of the value field.
        xflelf, name and value parameters has to be used to extract values from the SQL result.
        Returns a string (e.g., image path or base64).
        """

    @abstractmethod
    def call_function(self, name: str, args: dict[str, object]) -> str:
        """
        Calls a predefined function by name with the given arguments.
        Returns the result as a string.
        """

    @abstractmethod
    def get_image(self, name: str) -> ImgData | None:
        """
        Retrieves an image by name.
        Returns the image data as a string (e.g., base64).
        """
