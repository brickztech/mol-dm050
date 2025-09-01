import re

img_extract_pattern = re.compile("\(attachment:\\/\\/(.*?)\)", re.MULTILINE | re.DOTALL)  # zed:disable-ligatures
python_code_exp = re.compile("```python\\s(.*?)```", re.MULTILINE | re.DOTALL)
