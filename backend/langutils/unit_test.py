import unittest
from io import BytesIO

from langutils.llm_tools import ToolsHandler
from redmine.context import init_sql_context

from .open_ai import fill_in_img_attachments


class TestMathUtils(unittest.TestCase):
    def setUp(self):
        context = init_sql_context()
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


if __name__ == '__main__':
    unittest.main()
