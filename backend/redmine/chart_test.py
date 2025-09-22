import unittest
from io import BytesIO

from dotenv.main import load_dotenv

from .context import init_context
from .llm_tools import ToolsHandler

load_dotenv()


class TestChartUtils(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        context = init_context()
        self.toolhandler = ToolsHandler(context)

    def setUp(self):
        self.toolhandler.img_cache.add_image("12345", BytesIO(b"image data 1"))
        self.toolhandler.img_cache.add_image("234567", BytesIO(b"image data 2"))

    def test_line_chart(self):

        pandas_query = """import pandas as pd
from pandas.tseries.offsets import MonthBegin
# Get project ids for 'Project1' and 'Project2'
filtered_projects = projects[projects['name'].isin(['Project1', 'Project2'])]\n
# Merge projects with time_entries
entries = pd.merge(time_entries, filtered_projects, left_on='project_id', right_on='id', suffixes=('', '_project'))
# Add month column\nentries['month'] = pd.to_datetime(entries['spent_on']) + MonthBegin(-1)
entries['month'] = entries['month'].dt.to_period('M').astype(str)
#Group by month and project_name, sum hours
result_table = entries.groupby(['month', 'name'])['hours'].sum().reset_index().rename(columns={'name': 'project_name'})"""

        name = self.toolhandler.linechart(pandas_query, "month", "Hours", "project_name", "hours")
        self.assertIsNotNone(self.toolhandler.get_image(name))

    def test_pie_chart(self):
        pandas_query = """import pandas as pd
from pandas.tseries.offsets import MonthBegin
filtered_projects = projects[projects['name'].isin(['Project1'])]\n
# Merge projects with time_entries
entries = pd.merge(time_entries, filtered_projects, left_on='project_id', right_on='id', suffixes=('', '_project'))
# Add month column\nentries['month'] = pd.to_datetime(entries['spent_on']) + MonthBegin(-1)
entries['month'] = entries['month'].dt.to_period('M').astype(str)
entries = entries[entries['month'] > '2024-01']
#Group by month and project_name, sum hours
result_table = entries.groupby(['month', 'name'])['hours'].sum().reset_index().rename(columns={'name': 'project_name'})"""

        name = self.toolhandler.piechart(pandas_query, "month", "hours")
        self.assertIsNotNone(self.toolhandler.get_image(name))

    def test_bar_chart(self):

        pandas_query = """import pandas as pd
from pandas.tseries.offsets import MonthBegin
# Get project ids for 'Project1' and 'Project2'
filtered_projects = projects[projects['name'].isin(['Project1', 'Project2'])]\n
# Merge projects with time_entries
entries = pd.merge(time_entries, filtered_projects, left_on='project_id', right_on='id', suffixes=('', '_project'))
# Add month column
entries['month'] = pd.to_datetime(entries['spent_on']) + MonthBegin(-1)
entries['month'] = entries['month'].dt.to_period('M').astype(str)
entries = entries[entries['month'] > '2022-01']
#Group by month and project_name, sum hours
result_table = entries.groupby(['month', 'name'])['hours'].sum().reset_index().rename(columns={'name': 'project_name'})"""

        name = self.toolhandler.barchart(pandas_query, "month", "Hours", "project_name", "hours")
        self.assertIsNotNone(self.toolhandler.get_image(name))

    def test_bar_chart_2(self):
        pandas_query = """result_table = time_entries.groupby(time_entries['spent_on'].dt.strftime('%Y-%m'))['hours'].sum().reset_index()
result_table['bar'] = 'All Projects'
result_table.columns = ['month', 'hours', 'bar']"""
        name = self.toolhandler.barchart(pandas_query, "month", "Hours", "bar", "hours")
        self.assertIsNotNone(self.toolhandler.get_image(name))

    def test_line_chart_2(self):
        pandas_query = """result_table = time_entries.groupby(time_entries['spent_on'].dt.strftime('%Y-%m'))['hours'].sum().reset_index()
result_table['bar'] = 'All Projects'
result_table.columns = ['month', 'hours', 'bar']"""
        name = self.toolhandler.linechart(pandas_query, "month", "Hours", "bar", "hours")
        self.assertIsNotNone(self.toolhandler.get_image(name))

    def test_similar(self):
        res = self.toolhandler.similar("project1", 80)
        self.assertGreater(len(res), 0)


if __name__ == '__main__':

    unittest.main()
