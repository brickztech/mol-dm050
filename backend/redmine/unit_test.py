import unittest
from io import BytesIO

from dotenv.main import load_dotenv

from langutils.llm_tools import ToolsHandler
from redmine.open_ai import fill_in_img_attachments

from .context import init_context

load_dotenv()


class TestMolUtils(unittest.TestCase):
    def setUp(self):
        context = init_context()
        self.toolhandler = ToolsHandler(context)
        self.toolhandler.img_cache.add_image("12345", BytesIO(b"image data 1"))
        self.toolhandler.img_cache.add_image("234567", BytesIO(b"image data 2"))

    def test_img_extract(self):
        result = fill_in_img_attachments(
            "Here is an image (attachment://12345) and another one  (attachment://234567) end of text, this is not found (attachment://0000) neither this (attachment://) ) ( sdfsdfsdf",
            self.toolhandler,
        )
        self.assertIn(
            """Here is an image <img src="data:image/png;base64,aW1hZ2UgZGF0YSAx"> and another one  <img src="data:image/png;base64,aW1hZ2UgZGF0YSAy"> end of text, this is not found (attachment://0000) neither this (attachment://) ) ( sdfsdfsdf""",
            result,
        )

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
