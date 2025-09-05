import io
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


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
    def call_function(self, name: str, args: dict[str, Any]) -> str:
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
