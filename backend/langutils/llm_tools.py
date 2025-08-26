import io
import json
import uuid
from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from openai.types.responses import FunctionToolParam

from langutils.context import ExecutionContext
from shell.tools import ImgData, T2SQLTools

llm_tools_list_descriptor: list[FunctionToolParam] = [
    {
        "type": "function",
        "name": "get_current_date",
        "description": "Get the current date.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_name_day",
        "description": "Returns the name day of the current date.",
        "parameters": {
            "type": "object",
            "properties": {"date": {"type": "string", "description": "The month and day in %m.%d format."}},
            "required": ["date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_tables",
        "description": "The list of all the available tables in the database.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "describe_table",
        "description": "Describes a table from the database.",
        "parameters": {
            "type": "object",
            "properties": {"table": {"type": "string", "description": "The name of the table."}},
            "required": ["table"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "execute_query",
        "description": "Takes panda queries as text input and executes them on the database. The result will be returned as an HTML table.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The query to be executed on the database."}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "generate_chart",
        "description": "Generates a chart based on the provided x-axis, y-axis and chart type. The chart can be a line, bar or pie chart which has to be specified in chart_type parameter. The function returns the name of the chart. For the user the chart has to be presented in the following format: (attachment://<name of the chart>).",
        "parameters": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": ["line", "bar", "pie"],
                    "description": "The type of chart to generate.",
                },
                "x_axis": {"type": "array", "items": {"type": "string"}, "description": "The array of x-axis data."},
                "y_axis": {"type": "array", "items": {"type": "number"}, "description": "The array of y-axis data."},
                "y_axis_label": {"type": "string", "description": "The label for the y-axis."},
                "title": {"type": "string", "description": "The title of the chart."},
            },
            "required": ["chart_type", "x_axis", "y_axis", "y_axis_label", "title"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


class ImgCache:
    def __init__(self):
        self.cache: list[ImgData] = list()

    def flush_old_images(self):
        now = datetime.now()
        self.cache = [img for img in self.cache if (now - img.create_dt).total_seconds() < 60 * 5]

    def add_image(self, img_name: str, img_buffer: io.BytesIO) -> ImgData:
        self.flush_old_images()
        img_data = ImgData(img_name, img_buffer)
        self.cache.append(img_data)
        return img_data

    def get_image(self, img_name: str) -> ImgData | None:
        for img in self.cache:
            if img.img_name == img_name:
                return img
        return None


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class ToolsHandler(T2SQLTools):
    def __init__(self, context: ExecutionContext):
        self.context = context
        self.img_cache = ImgCache()
        # load the similar cache from a file or database if needed
        self.similars_cache: list[tuple[str, str, str]] = []

    def similar(self, ref: str) -> list[tuple[str, str, str]]:
        """
        Returns the topN (default 10) most similar (value, table, field) tuples to the given ref
        from all soft-searchable columns in all tables.
        Has to work based on some preloaded data of a database. The fields of the preloaded database has to come from a configuration.
        """
        return [rec for rec in self.similars_cache if rec[0].find(ref) > -1]

    def data(self, sql: str) -> list[dict[str, str]]:
        """
        Executes the given SQL and returns the result as a list of dicts (field: value).
        """
        return self.context.execute_query(sql)

    def piechart(self, sql: str, labelfield: str, valuefield: str) -> str:
        """
        Executes the SQL and generates a pie chart from the result.
        labelfield: column name for labels, valuefield: column name for values.
        Returns a string (e.g., image path or base64).
        """
        raise NotImplementedError("piechart method is not implemented.")

    def linechart(self, sql: str, xfield: str, ylabel: str, linelist: list[str]) -> str:
        """
        Executes the SQL and generates a line chart.
        xfield: column for x-axis, ylabel: y-axis label, linelist: columns for lines.
        Returns a string (e.g., image path or base64).
        """
        chart_data = self.data(sql)
        if not chart_data:
            raise ValueError("No data returned from the SQL query.")

        raise NotImplementedError("linechart method is not implemented.")

    def barchart(self, sql: str, xfield: str, ylabel: str, barlist: list[str]) -> str:

        raise NotImplementedError("linechart method is not implemented.")

    def _generate_chart(self, chart_type: str, x_axis: list[float], y_axis: list[float], y_axis_label: str, title: str):
        norm = Normalize(min(y_axis), max(y_axis))
        from matplotlib.colors import ListedColormap

        colors = ['#ff001c', '#ff6a1f', '#ff9e20', '#ffdb1b', '#f4ff24']
        cmap = ListedColormap(colors)
        bar_colors = [cmap(norm(y)) for y in y_axis]

        if chart_type == "line":
            plt.plot(x_axis, y_axis, marker='o', linestyle='-', label=y_axis_label, color=bar_colors)
        elif chart_type == "bar":
            plt.bar(x_axis, y_axis, label=y_axis_label, color=bar_colors)
            # plt.bar(x_axis, y_axis, label=y_axis_label, color=colors)
        # Add labels and title
        # mpl.xlabel('X-axis')
        plt.ylabel(y_axis_label)

        if len(x_axis) > 10:
            x = range(len(x_axis))
            plt.xticks(ticks=x[::3], labels=[str(i) for i in x_axis[::3]], rotation=45)
        else:
            plt.xticks(rotation=45)
        plt.title(title)
        # Add a legend
        plt.legend()

        img_name = f"{uuid.uuid4()}"

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        self.img_cache.add_image(img_name, img_buffer)
        return img_name

    def get_image(self, name: str) -> ImgData | None:
        return self.img_cache.get_image(name)

    def call_function(self, name: str, args: dict[str, str]) -> str:
        if name == "get_current_date":
            return datetime.now().strftime("%Y-%m-%d")
        elif name == "get_tables":
            return self.context.inspect_tables_structure()
        elif name == "get_name_day":
            date_str = args.get("date")
            if date_str:
                return "Attila"
            else:
                raise ValueError("Date parameter is required for get_name_day function.")
        elif name == "describe_table":
            table_name = args.get("table")
            if table_name:
                return self.context.inspect_tables_structure(table_name)
            else:
                raise ValueError("Table parameter is required for describe_table function.")
        elif name == "execute_query":
            query: str | None = args.get("query")
            if query is None:
                raise ValueError("Query parameter is required for execute_query function.")
            result: list[dict] = self.data(query)

            return json.dumps(result, indent=2, cls=DateTimeEncoder)
        elif name == "generate_chart":
            x_axis_input = args.get("x_axis")
            y_axis_input = args.get("y_axis")
            if x_axis_input is None or y_axis_input is None:
                raise ValueError("x_axis or y_axis values are not found")

            try:
                x_axis: list[float] = [float(i) for i in json.loads(x_axis_input)]
                y_axis: list[float] = [float(i) for i in json.loads(y_axis_input)]
                title = args.get("title", "")
                chart_type = args.get("chart_type", "line")
                y_axis_label = args.get("y_axis_label", "")
                chart_name = self._generate_chart(chart_type, x_axis, y_axis, y_axis_label, title)
                return f"(attachment://{chart_name})"
            except:
                raise ValueError("x_axis and y_axis must be valid JSON arrays of numbers.")

        else:
            raise ValueError(f"Unknown function name: {name}")
