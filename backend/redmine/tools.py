import json
from datetime import datetime

from langutils.context import ExecutionContext
from openai.types.responses import FunctionToolParam
from redmine.llm_tools import DateTimeEncoder, ToolsHandler

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


class RedmineToolsHandler(ToolsHandler):
    def __init__(self, context: ExecutionContext):
        super().__init__(context)

    def call_function(self, name: str, args: dict[str, object]) -> str:
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
            table_name = str(args.get("table"))
            if table_name:
                return self.context.inspect_tables_structure(table_name)
            else:
                raise ValueError("Table parameter is required for describe_table function.")
        elif name == "execute_query":
            query = args.get("query")  # type: ignore
            if query is None:
                raise ValueError("Query parameter is required for execute_query function.")
            result: list[dict[str, str]] = self.data(str(query))
            return json.dumps(result, indent=2, cls=DateTimeEncoder)
        elif name == "generate_chart":
            x_axis_input = args.get("x_axis")
            y_axis_input = args.get("y_axis")
            if not isinstance(x_axis_input, list) or not isinstance(y_axis_input, list):
                raise ValueError("x_axis and y_axis must be arrays.")
            if x_axis_input is None or y_axis_input is None:
                raise ValueError("x_axis or y_axis values are not found")

            try:
                y_axis: list[float] = [float(i) for i in y_axis_input]
                title = str(args.get("title", ""))
                chart_type = str(args.get("chart_type", "line"))
                y_axis_label = str(args.get("y_axis_label", ""))
                chart_name = self._generate_chart(chart_type, x_axis_input, y_axis, y_axis_label, title)
                return f"(attachment://{chart_name})"
            except Exception as e:
                print(f"Error generating chart: {e}")
                raise ValueError("x_axis and y_axis must be valid JSON arrays of numbers.")

        else:
            raise ValueError(f"Unknown function name: {name}")
