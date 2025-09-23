import json
import logging
import re
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import blockz.LLMBlockz as lb
import sqlglot
from shell import T2SQLTools

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def safe_json_parse(text: str) -> Any:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


class WrongAnswer(Exception):
    "Raised when the reply has some issues, like wrong toolfunction name"

    msg: str

    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __repr__(self) -> str:
        return f"WrongAnswer(msg={self.msg})"


class ShellError(Exception):
    "Raised when the shell feels like giving up"


@dataclass
class Element:
    pass


@dataclass
class TextElement(Element):
    """Carrier of literal texts. Anything that can possibly be found in an LLM reply will make it here: Markdown, links etc. so be prepared"""

    _content: str

    def __repr__(self) -> str:
        return f"TextElement(_content={self._content})"

    def getcontent(self) -> str:
        return self._content


@dataclass
class GraphicsElement(Element):
    """Carrier of a graphics element encoded as a legal string. For now this is PNG over base64"""

    _content: str
    _id: str

    def __repr__(self) -> str:
        return f"GraphicsElement(_content={self._content}, _id={self._id})"

    def getcontent(self) -> str:
        return self._content


@dataclass
class TableElement(Element):
    """Carrier of a table"""

    _content: list[dict[str, Any]]
    _id: str

    def __repr__(self) -> str:
        return f"""TableElement(_content={self._content}, _id={self._id})"""

    def getcontent(self) -> list[dict[str, Any]]:
        return self._content


def textify_elementlist(elist: list[Element]) -> str:
    outelems: list[str] = []
    for elem in elist:
        match elem:
            case TextElement(_content=content):
                outelems.append(content)
            case GraphicsElement(_id=identifier):
                outelems.append(f"\nDiagram {identifier}\n")
            case TableElement(_id=identifier):
                outelems.append(f"\nTable {identifier}\n")
            case _:
                raise TypeError("Wrong type in Element list")
    return " ".join(outelems)


complete_tool_dict: lb.ToolDict = {
    #    "similar":
    #        lb.tool("""Find a list of values from the database that are sufficiently similar to the supplied reference value.
    # Each entry in the return value is a triplet of strings, the first element being the actual value that is deemed similar enough to the given reference
    # value, the second string being the name of the table in the database where this value is found and the third string is the name of the field within
    # that table where the value was found.""",
    #                       [lb.param(name="reference",typ="string",
    #                                 description="The reference value to which we look for approximately matching/similar results")
    #                       ]
    #                      ),
    "get_data": lb.tool(
        """Executes the SQL query received as parameter over the database and returns the result or an error message if something went wrong.""",
        [lb.param("sql", "string", """SQL query to be executed.""")],
    ),
    "create_table": lb.tool(
        """Creates a table with the results of the SQL query and returns an identifier to it, which is to be included in the final answer in order to identify this table. Make sure the elements of the selected list have proper aliases, since those aliases will become the column headings of the table.""",
        [lb.param(name="sql", typ="string", description="The SQL query whose result is to be displayed")],
    ),
    "line_chart": lb.tool(
        """Executes the provided SQL query and renders the results as a line chart with possibly multiple series.
The SQL query must return data in a format where each row represents one data point for one series, with separate columns for the x-axis value,
series identifier, and y-axis value.
Return an identifier to the generated image, to be included in the final reply""",
        [
            lb.param(
                name='sql',
                typ='string',
                description="""SQL query that returns the data for the line chart.
The query must include columns for: x-axis values (typically dates/timestamps), series labels (to distinguish different lines),
and numeric values for the y-axis.
Each row should represent one data point for one series. The query should be ordered appropriately for chronological data display.""",
            ),
            lb.param(
                name='xfield',
                typ='string',
                description="""Column name from the SQL result set that contains the x-axis values.
This field typically contains dates, timestamps, or sequential numeric values.
The field name will also be used as the label for the horizontal axis, so use descriptive aliases in your SQL (e.g., 'date', 'month', 'quarter')
rather than generic names.""",
            ),
            lb.param(
                name='ylabel',
                typ='string',
                description="""Label text to display for the y-axis (vertical axis). Should be descriptive of
what the values represent, including units when applicable (e.g., 'Price (USD)', 'Revenue ($M)', 'Count', 'Percentage').""",
            ),
            lb.param(
                name='labelfield',
                typ='string',
                description="""Column name from the SQL result set that contains the series identifiers.
Each unique value in this column will become a separate line on the chart.
Examples include company names, product categories, regions, or any categorical field that distinguishes different data series.""",
            ),
            lb.param(
                name='valuefield',
                typ='string',
                description="""Column name from the SQL result set that contains the numeric values
to plot on the y-axis. This should be a numeric field representing the metric being visualized (e.g., prices, counts, percentages, amounts).""",
            ),
        ],
    ),
}

import pathlib

current_file_path = pathlib.Path(__file__).resolve().parent
with open(current_file_path / "prefix.txt") as f:
    prefix = f.read()

with open(current_file_path / "imperative-dd.txt") as f:
    domain_description = f.read()


def validate_sql(sql: str, fields: list[str]) -> None:
    """Checks if the 'sql' param contains an sql command starting with 'select' and not ending in 'for update'
    Also checks if the fields in the 'fields' list appear in the string, or possibly as
    """
    sql = sql.replace('\\n', ' ')
    ast = sqlglot.parse_one(sql, dialect='tsql')
    if ast.key != 'select':
        raise ShellError(f"Command '{sql}' is not a query statement")
    if 'expressions' not in ast.args:
        raise ShellError(f"Parsing did not provide a selected expressions list")
    if 'locks' in ast.args:
        raise ShellError(f"Command '{sql}' tries to put a lock on the selected data")
    expressions = ast.args["expressions"]
    selectedlist = []
    for expr in expressions:
        match expr.key:
            case 'alias':
                selectedlist.append(expr.alias)
            case 'column':
                selectedlist.append(expr.this.this)
            case _:
                pass
    for field in fields:
        if field not in selectedlist:
            raise ShellError(f"Field {field} is not selected in the command '{sql}'")


#    lowersql: str = sql.lower()
#    return lowersql.startswith('select') and not lowersql.endswith('for update') and all(field in sql for field in fields) # imperfect, will do sqlparse


def toolfunction(tools: T2SQLTools, resources: dict[str, Element], name: str, params: Mapping[str, str]) -> str:
    logger.debug(f"Toolfunction called with name={name} and params={params}.")
    try:
        match name:
            case "create_table":
                validate_sql(params["sql"], [])
                logger.debug(f"Calling tools.data with sql='{prefix + params['sql']}'")
                contents: list[dict[str, Any]] = tools.data(prefix + params["sql"])
                logger.debug(f"tools.data returned {len(contents)} rows.")
                if len(contents) > 0 and len(contents) * len(contents[0]) > 5000:
                    logger.debug(f"Too much data in result set: {len(contents)} rows by {len(contents[0])} columns.")
                    return f"Too much data returned ({len(contents)} rows with {len(contents[0])} fields each), try something else."
                else:
                    identifier = str(uuid.uuid4())[-12:]
                    resources[identifier] = TableElement(contents, identifier)
                    return f'{{"status":"success","identifier":"{identifier}"}}'
            case "line_chart":
                validate_sql(params["sql"], [params["xfield"], params["labelfield"], params["valuefield"]])
                logger.debug(
                    f"Calling tools.linechart with sql={prefix+params['sql']}, xfield={params['xfield']}, ylabel={params['ylabel']}, labelfield={params['labelfield']}, valuefield={params['valuefield']}"
                )
                graph: str = tools.linechart(
                    prefix + params["sql"], params["xfield"], params["ylabel"], params["labelfield"], params["valuefield"]
                )
                identifier = str(uuid.uuid4())[-12:]
                resources[identifier] = GraphicsElement(graph, identifier)
                return f'{{"status":"success","identifier":"{identifier}"}}'
            case "similar":
                logger.debug(f"Calling tools.similar with ref={params['reference']}")
                hits: str = str(tools.similar(params["reference"]))
                return hits
            case "get_data":
                validate_sql(params["sql"], [])
                logger.debug(f"Calling tools.data with sql={params['sql']}")
                res: list[dict[str, Any]] = tools.data(prefix + params["sql"])
                if len(res) > 0 and len(res) * len(res[0]) > 500:
                    logger.debug(f"Too much data in result set: {len(res)} rows by {len(res[0])} columns.")
                    return f"Too much data returned ({len(res)} rows with {len(res[0])} fields each), try something else."
                else:
                    return str(res)
            case _:
                raise WrongAnswer(f"Unknown tool {name} called with parameters {params}.")
    except ShellError as e:
        raise WrongAnswer(str(e))


def extract_json_from_text(text: str) -> dict[Any, Any] | None:
    """
    Extract JSON from text that is either:
    1. An entirely serialized JSON object, or
    2. Text containing exactly one JSON in markdown code blocks (```json ... ```)

    Args:
        text (str): Input text to parse

    Returns:
        Optional[Dict[Any, Any]]: Parsed JSON object, or None if extraction fails
    """
    # Remove leading/trailing whitespace
    text = text.strip()

    # First, try to parse the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # If that fails, look for markdown JSON code blocks
    pattern = r'```json\s*\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    # Must have exactly one JSON block
    if len(matches) != 1:
        return None

    # Try to parse the single JSON block
    try:
        return json.loads(matches[0].strip())
    except json.JSONDecodeError:
        return None


def unparse_answer(resources: dict[str, Element], answerstring: str) -> list[Element]:
    logger.debug(f"unparse_answer called with answerstring='{answerstring}' and resources={resources}")
    if not (evaluatorresult := extract_json_from_text(answerstring)):
        raise WrongAnswer("Could not extract a JSON object from the answer string")
    if "items" not in evaluatorresult:
        raise WrongAnswer(f"'items' not a member of the result")
    if not isinstance(evaluatorresult["items"], list):
        raise WrongAnswer(f"Result {evaluatorresult['items']} is not a JSON list")
    retval: list[Element] = []
    for rawelem in evaluatorresult["items"]:
        logger.debug(f"Processing element {rawelem}.")
        if not isinstance(rawelem, dict):
            raise WrongAnswer("Element not a dictionary")
        if "type" not in rawelem:
            raise WrongAnswer("Field 'type' missing")
        match rawelem["type"]:
            case "text":
                if "text" not in rawelem or not isinstance(rawelem["text"], str):
                    raise WrongAnswer("Type is text but no 'text' field with string type avaliable")
                else:
                    retval.append(TextElement(rawelem["text"]))
            case "graphics":
                if "graphics" not in rawelem:
                    raise WrongAnswer(f"Type is 'graphics' but no 'graphics' field is present in '{rawelem}'")
                if rawelem["graphics"] not in resources:
                    raise WrongAnswer(f"Graphics field is present in {rawelem} but does not point to anything in resources.")
                if not isinstance(resources[rawelem["graphics"]], GraphicsElement):
                    raise WrongAnswer(f"Graphics field in {rawelem} points to a resource that is not a GraphicsElement")
                else:
                    retval.append(resources[rawelem["graphics"]])
            case "table":
                if "table" not in rawelem:
                    raise WrongAnswer(f"Type is 'table' but no 'table' field is present in '{rawelem}'")
                elif rawelem["table"] not in resources:
                    raise WrongAnswer(
                        f"Table field {rawelem['table']} is present in '{rawelem}' but does not point to anything in resources."
                    )
                elif not isinstance(resources[rawelem["table"]], TableElement):
                    raise WrongAnswer(f"Table field {rawelem['table']} in '{rawelem}' points to a resource that is not a TableElement")
                else:
                    retval.append(resources[rawelem["table"]])
            case _:
                raise WrongAnswer(f"Unexpected value of 'type' field in {rawelem}")
    return retval
