import re

img_extract_pattern = re.compile("\(attachment:\\/\\/(.*?)\)", re.MULTILINE | re.DOTALL)  # zed:disable-ligatures
python_code_exp = re.compile("```python\\s(.*?)```", re.MULTILINE | re.DOTALL)
COLORS = ['#f4ff24', '#ffdb1b', '#ff9e20', '#ff6a1f', '#ff001c']
GRID_COLOR = '#cccccc'
MAX_VALUES_X_AXIS = 20
