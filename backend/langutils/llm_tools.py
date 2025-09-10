import io
import json
import os
import uuid
from datetime import datetime
from itertools import groupby

from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from rapidfuzz import fuzz

from langutils.context import ExecutionContext
from t2sqltools.tools import ImgData, T2SQLTools

from . import COLORS, GRID_COLOR, MAX_VALUES_X_AXIS


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
    def default(self, o: object):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class ToolsHandler(T2SQLTools):
    def __init__(self, context: ExecutionContext):
        self.context = context
        self.img_cache = ImgCache()
        # load the similar cache from a file or database if needed
        similarity_query = os.getenv("SIMILARITY_QUERY", "")
        if similarity_query:
            result_dict = context.execute_query(similarity_query)
            similars = [(str(rec.get("value")), str(rec.get("col_name")), str(rec.get("table"))) for rec in result_dict]
            self.similars_cache = similars
        else:
            self.similars_cache: list[tuple[str, str, str]] = []

    def similar(self, ref: str, limit: int = 0) -> list[tuple[str, str, str, float]]:
        """
        Returns the topN (default 10) most similar (value, table, field) tuples to the given ref
        from all soft-searchable columns in all tables.
        Has to work based on some preloaded data of a database. The fields of the preloaded database has to come from a configuration.
        """
        ratios = [(rec[0], rec[1], rec[2], fuzz.ratio(ref, rec[0])) for rec in self.similars_cache]
        ratios.sort(key=lambda x: x[3], reverse=True)
        filtered_ratios = [x for x in ratios if x[3] > limit]
        return filtered_ratios

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
        chart_data = self.data(sql)
        if not chart_data:
            raise ValueError("No data returned from the SQL query.")

        labels = [row[labelfield] for row in chart_data]
        values = [row[valuefield] for row in chart_data]
        bar_colors = self._build_color_list_scale(values)

        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=bar_colors)
        img_name = f"{uuid.uuid4()}"
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.savefig("pie.png", format='png')
        self.img_cache.add_image(img_name, img_buffer)

        return img_name

    def set_axis_lables(self, x_values: list[list[str]]):
        x_values_merged = []
        for x in x_values:
            x_values_merged.extend(x)
        x_values_merged = list(set(x_values_merged))
        x_values_merged.sort()

        scale = len(x_values_merged) // MAX_VALUES_X_AXIS

        if len(x_values_merged) > MAX_VALUES_X_AXIS:
            plt.xticks(
                ticks=[i for i in range(len(x_values_merged)) if i % scale == 0],
                labels=[str(x_values_merged[i]) for i in range(len(x_values_merged)) if i % scale == 0],
                rotation=45,
                ha='right',
            )
        else:
            plt.xticks(rotation=45, ha='right')

    def linechart(self, sql: str, xfield: str, ylabel: str, name: str, value: str) -> str:
        """
        Executes the SQL and generates a line chart.

        xfield: column for x-axis labels, ylabel: y-axis label, linelist: list of columns for values of x-axis.
        Returns a string (e.g., image path or base64).
        """
        data_series_names, data_series_values, x_values = self._build_chart_data(sql, xfield, name, value)

        bar_colors = self._build_static_color_list(data_series_names)

        plt.figure(figsize=(8, 5))  # type: ignore
        for i, y in enumerate(data_series_values):
            plt.plot(x_values[i], y, marker='o', label=data_series_names[i], color=bar_colors[i])

        self.set_axis_lables(x_values)

        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(axis='y', color=GRID_COLOR)
        plt.tight_layout()

        img_name = f"{uuid.uuid4()}"
        img_buffer = io.BytesIO()
        plt.savefig("line.png", format='png')
        plt.savefig(img_buffer, format='png')

        self.img_cache.add_image(img_name, img_buffer)

        return img_name

    def _build_chart_data(
        self, sql: str, xfield: str, line_name: str, line_value: str
    ) -> tuple[list[str], list[list[str]], list[list[str]]]:
        """sql: the SQL query to execute
        xfield: the column name to use for x-axis values
        line_name : the column name to group by for different lines
        line_value: the column name to use for y-axis values
        returns a tuple with the following elements:
        - list with the name of data series of different data_series_values
        - list of lists with the data_series_values for each data series, the upper level list has the same size as the name list above
        - list of lists with the x_values for each data series. The length of this list is equal with number of series.
        """

        chart_data = self.data(sql)
        if not chart_data:
            raise ValueError("No data returned from the SQL query.")

        chart_data.sort(key=lambda x: x[line_name])

        data_series_values: list[list[str]] = []
        data_series_names: list[str] = []
        x_values: list[list[str]] = []
        # grouped contains data for each line_name with the key.
        for key, group in groupby(chart_data, key=lambda x: x[line_name]):
            group = list(group)
            values = [row[line_value] for row in group]
            x_labels = [row[xfield] for row in group]
            data_series_values.append(values)
            x_values.append(x_labels)
            data_series_names.append(key)
            # Display the shape of data_series_values
            print(f"Shape of data_series_values: ({len(data_series_values)}, {len(data_series_values[0]) if data_series_values else 0})")
        return data_series_names, data_series_values, x_values

    def _build_color_list_scale(
        self, values_scale: list[str] | list[float], invert_order: bool = False
    ) -> list[tuple[float, float, float, float]]:
        flat_y_values_float = [float(y) for y in values_scale]
        norm = Normalize(min(flat_y_values_float), max(flat_y_values_float))
        from matplotlib.colors import ListedColormap

        color_list = COLORS[::-1] if invert_order else COLORS
        if len(values_scale) < len(COLORS):
            color_list = color_list[: len(values_scale)]

        cmap = ListedColormap(color_list)
        bar_colors = [cmap(norm(y)) for y in flat_y_values_float]
        return bar_colors

    def _build_static_color_list(self, category_list: list[int] | list[str]) -> list[tuple[float, float, float, float]]:
        category_list.sort()
        values = [float(i) for i in range(0, len(category_list))]
        return self._build_color_list_scale(values, True)

    def barchart(self, sql: str, xfield: str, ylabel: str, name: str, value: str) -> str:
        """
        Executes the SQL and generates a bar chart.
        xfield: column for x-axis, ylabel: y-axis label, barlist: columns for bars.
        Returns a string (e.g., image path or base64).
        """
        data_series_names, data_series_values, x_labels = self._build_chart_data(sql, xfield, name, value)

        if len(data_series_names) == 1:
            bar_colors = self._build_color_list_scale(data_series_values[0])
        else:
            bar_colors = self._build_static_color_list(data_series_names)

        # Merge all x_labels into a set to ensure uniqueness
        x_labels_set = set()
        for labels in x_labels:
            x_labels_set.update(labels)

        # create a complete dataset for all the values. Fill the missing values in certain series with 0
        x_labels_set = sorted(x_labels_set)
        y_values_for_x_labels = []
        for labels, values in zip(x_labels, data_series_values):
            label_value_map: dict[str, str] = dict(zip(labels, values))
            y_values = [label_value_map.get(label, 0) for label in x_labels_set]  # type: ignore
            y_values_for_x_labels.append(y_values)

        # Group the bars around the labels (grouped bar chart)
        import numpy as np

        num_series = len(y_values_for_x_labels)
        num_labels = len(x_labels_set)
        x = np.arange(num_labels)
        width = 0.8 / num_series if num_series > 0 else 0.8  # total width for all bars at one x-tick

        plt.figure(figsize=(10, 5))
        for i, y in enumerate(y_values_for_x_labels):
            plt.bar(x + i * width, y, width=width, label=data_series_names[i], color=bar_colors[i], edgecolor='grey')

        plt.xticks(x + width * (num_series - 1) / 2, x_labels_set, rotation=45, ha='right')

        # plt.figure(figsize=(10, 5))
        # for i, y in enumerate(y_values_for_x_labels):
        #     plt.bar(x_labels_set, y, label=data_series_names[i], color=bar_colors[i], edgecolor='grey')

        # self.set_axis_lables(x_labels)

        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(axis='y', color=GRID_COLOR)
        plt.tight_layout()

        img_name = f"{uuid.uuid4()}"
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.savefig("bar2.png", format='png')
        self.img_cache.add_image(img_name, img_buffer)

        return img_name

    def _generate_chart(self, chart_type: str, x_axis: list, y_axis: list[float], y_axis_label: str, title: str):
        norm = Normalize(min(y_axis), max(y_axis))
        from matplotlib.colors import ListedColormap

        cmap = ListedColormap(COLORS)
        bar_colors = [cmap(norm(y)) for y in y_axis]

        if chart_type == "line":
            plt.plot(x_axis, y_axis, marker='o', linestyle='-', label=y_axis_label, color=bar_colors)
        elif chart_type == "bar":
            plt.bar(x_axis, y_axis, label=y_axis_label, color=bar_colors)
            # plt.bar(x_axis, y_axis, label=y_axis_label, color=colors)
        elif chart_type == "pie":
            plt.pie(y_axis, labels=x_axis, autopct='%1.1f%%', colors=bar_colors)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
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

    def call_function(self, name: str, args: dict[str, object]) -> str:
        raise NotImplementedError("call_function has to be implemented in the subclass")
