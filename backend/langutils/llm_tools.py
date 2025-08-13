import io
import uuid
from datetime import datetime

import matplotlib.pyplot as plt

from langutils import ExecutionContext

llm_tools_list_descriptor = [{
    "type": "function",
    "name": "get_current_date",
    "description": "Get the current date.",
    "parameters": {
        "type": "object",
        "properties": {
        },
        "additionalProperties": False
    },
    "strict": True
},
    {
        "type": "function",
        "name": "get_name_day",
        "description": "Returns the name day of the current date.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The month and day in %m.%d format."
                }
            },
            "required": [
                "date"
            ],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_tables",
        "description": "The list of all the available tables in the database.",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "describe_table",
        "description": "Describes a table from the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": "The name of the table."
                }
            },
            "required": [
                "table"
            ],
            "additionalProperties": False
        },
        "strict": True
    }, {
        "type": "function",
        "name": "execute_query",
        "description": "Takes panda queries as text input and executes them on the database. The result will be returned as an HTML table.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to be executed on the database."
                }
            },
            "required": [
                "query"
            ],
            "additionalProperties": False
        },
        "strict": True
    }, {
        "type": "function",
        "name": "generate_chart",
        "description": "Generates a chart based on the provided x-axis, y-axis and chart type. The chart can be a line, bar or pie chart which has to be specified in chart_type parameter."
                       "The function returns the name of the chart. For the user the chart has to be presented in the following format: (attachment://<name of the chart>).",
        "parameters": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": ["line", "bar", "pie"],
                    "description": "The type of chart to generate."
                },
                "x_axis": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The array of x-axis data."
                },
                "y_axis": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                    "description": "The array of y-axis data."
                },
                "y_axis_label": {
                    "type": "string",
                    "description": "The label for the y-axis."
                },
                "title": {
                    "type": "string",
                    "description": "The title of the chart."
                }
            },
            "additionalProperties": False
        },
        "required": [
            "x_axis",
            "y_axis",
            "title"
        ],
        "additionalProperties": False
    },
]


class ImgData:
    def __init__(self, img_name: str, img_buffer: io.BytesIO):
        self.img_name: str = img_name
        self.create_dt: datetime = datetime.now()
        self.img_buffer = img_buffer

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


class ToolsHandler:
    def __init__(self, context: ExecutionContext):
        self.context = context
        self.img_cache = ImgCache()

    def call_function(self, name: str, args: dict):
        if name == "get_current_date":
            return datetime.now()
        elif name == "get_tables":
            return self.context.inspect_tables_structure()
        elif name == "get_name_day":
            date_str = args.get("date")
            if date_str:
                date = datetime.strptime(date_str, "%m.%d")
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
            query = args.get("query")
            if query:
                return self.context.execute(query)
            else:
                raise ValueError("Query parameter is required for execute_query function.")
        elif name == "generate_chart":
            x_axis = args.get("x_axis")
            y_axis = args.get("y_axis")
            title = args.get("title")
            chart_type = args.get("chart_type")
            y_axis_label = args.get("y_axis_label")
            if x_axis and y_axis and title and chart_type and y_axis_label:
                # Create the line chart

                norm = plt.Normalize(min(y_axis), max(y_axis))
                from matplotlib.colors import ListedColormap
                colors = ['#ff001c', '#ff6a1f', '#ff9e20', '#ffdb1b', '#f4ff24']
                cmap = ListedColormap(colors)
                bar_colors = [cmap(norm(y)) for y in y_axis]
                #cmap = plt.cm.get_cmap('viridis')
                #bar_colors = [cmap(norm(y)) for y in y_axis]

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
            else:
                raise ValueError("x_axis, y_axis, and title parameters are required for generate_line_chart function.")
        else:
            raise ValueError(f"Unknown function name: {name}")







