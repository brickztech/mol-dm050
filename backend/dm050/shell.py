import json
import os
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any

import blockz.LLMBlockz as lb
from shell import Element, GraphicsElement, TableElement, TextElement
from t2sqltools import T2SQLTools


def safe_json_parse(text: str) -> Any:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


class WrongAnswer(Exception):
    "Raised when the reply has some issues, like wrong toolfunction name"


class ShellError(Exception):
    "Raised when the shell feels like giving up"


def textify_elementlist(elist: list[Element]) -> str:
    outelems: list[str] = []
    for elem in elist:
        match elem:
            case TextElement(_content=content):
                outelems.append(content)
            case GraphicsElement(_id=identifier):
                outelems.append(f"Diagram {identifier}")
            case TableElement(_id=identifier):
                outelems.append(f"Table {identifier}")
    return " ".join(outelems)


############################################################

basic_tooldict: lb.ToolDict = {
    "similar": lb.tool(
        """Find a list of values from the database that are sufficiently similar to the supplied reference value.
Each entry in the return value is a triplet of strings, the first element being the actual value that is deemed similar enough to the given reference
value, the second string being the name of the table in the database where this value is found and the third string is the name of the field within
that table where the value was found.""",
        [
            lb.param(
                name="reference",
                typ="string",
                description="The reference value to which we look for approximately matching/similar results",
            )
        ],
    ),
    "get_data": lb.tool(
        """Execute SQL queries against the database. For data analysis tasks, use analytical
        queries with aggregation (SELECT DISTINCT, GROUP BY, COUNT, MIN/MAX) that return
        small result sets. For data retrieval tasks, construct queries that return the
        actual data needed for final answers or visualizations.""",
        [
            lb.param(
                "sql",
                "string",
                """SQL query using MS SQL Server dialect. For checking data availability
                    and dimensions, use aggregation and DISTINCT to examine structure efficiently.
                    For final data retrieval, construct queries that return the specific
                    data needed for tables, charts, or analysis.""",
            )
        ],
    ),
}

full_tooldict = basic_tooldict | {
    "create_table": lb.tool(
        """Create a table with the results of the SQL query and return an identifier to it,
which is to be included in the final answer""",
        [lb.param(name="sql", typ="string", description="The SQL query whose result is to be displayed")],
    ),
    "line_chart": lb.tool(
        """Execute the provided SQL query and render the results as a line chart with multiple series.
The SQL query must return data in a format where each row represents one data point for one series, with separate columns for the x-axis value,
series identifier, and y-axis value. Time series data is particularly well-suited for this visualization.
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

prefix = """
with stocks as (select distinct
        stock_dt as stdate,
        case stock_element_sid
            when 1 then 'MOL'
            when 2 then 'OMV'
            when 3 then 'Orlen'
        end as stname,
        stock_value as stvalue,
        case stock_element_sid
            when 1 then 'USD'
            when 2 then 'EUR'
            when 3 then 'PLN'
        end as stcurrency
    from  [prod_dm050_ds_valuechain_extenv].[t050_04_stock]
),
quotations as (select distinct
        q.quotation_dt as qdate,
        q.dn_quotation_type_id as qtype,
        q.dn_currency_id as qcurrency,
        q.quote_price as qprice,
        q.dn_uom as quom,
        e.rate_type_id as qratetype,
        e.stock_quote_id as stockquoteid
    from [prod_dm050_ds_valuechain_extenv].[t050_01_quotation] q
    join [prod_dm050_ds_valuechain_extenv].[t050_53_quotation_element] e
        on e.quotation_element_sid = q.quotation_element_sid
    where q.dn_quotation_cat_id in ('crude-brent-diff','crude-oil')
),
spreads as (select distinct
        spread_dt as spdate,
        dn_spread_type_id as sptype,
        spread_value as spvalue,
        dn_currency_id as spcurrency,
        dn_uom as spuom
    from [prod_dm050_ds_valuechain_extenv].[t050_02_spread]
    where dn_spread_cat_id like 'crack%' or dn_spread_cat_id = 'wow-bde-nph'
),
calendar as (select
        day_date_id,
        year,
        month_of_year,
        monthname_of_year,
        quarter_of_year,
        year_quarter,
        year_half
    from [prod_dm050_ds_valuechain_extenv].[t050_99_calendar]
)
"""


def basic_toolfunction(tools: T2SQLTools, name: str, params: dict[str, str]) -> str:
    match name:
        case "similar":
            hits: str = str(tools.similar(params["reference"]))
            return hits
        case "get_data":
            res: str = str(tools.data(prefix + params["sql"]))
            return res
        case _:
            raise WrongAnswer(f"Unknown tool {name} called with parameters {params}.")


def extended_toolfunction(tools: T2SQLTools, resources: dict[str, Element], name: str, params: dict[str, str]) -> str:
    match name:
        case "create_table":
            contents: list[dict[str, str]] = tools.data(prefix + params["sql"])
            identifier = uuid.uuid4().hex
            resources[identifier] = TableElement(contents, identifier)
            return f'{{"status":"success","identifier":"{identifier}"}}'
        case "line_chart":
            graph: str = tools.linechart(
                prefix + params["sql"], params["xfield"], params["ylabel"], params["labelfield"], params["valuefield"]
            )
            identifier = uuid.uuid4().hex
            resources[identifier] = GraphicsElement(graph, identifier)
            return f'{{"status":"success","identifier":"{identifier}"}}'
        case _:
            return basic_toolfunction(tools, name, params)


domain_description_path = os.getenv("DOMAIN_DESCRIPTION", "")
domain_description = open(domain_description_path).read()

analysis_stage_system_instruction = f"""You are an assistant performing part of the task of extracting and analyzing data from a database of financial data
(quotations, stock values, margins and spreads) of an integrated oil and gas company. Your specific task is to take the raw question of the user, and
reformulate it in a more rigorous way, or report if this is not possible.

{domain_description}

REFORMULATION REQUIREMENTS:
1. Convert user input into complete grammatical sentences (users often type cryptic fragments like 'Brent how much?')

2. Explicitly specify the data sub-domain (quotation, stock price, margin, or spread). Example: 'Med Urals' becomes 'CIF MED Urals quotation'

3. Handle the unspecified dimensions like currency, unit of measurement etc. as described by the appropriate database field; currencies, units of measurement etc.

4. Verify data coverage adequacy by querying the database for date ranges and scope. Refuse requests that fall significantly outside available data periods
(soft criterion - minor gaps acceptable). For SQL use the MS SQL Server dialect.

5. Preserve and, if needed, amplify any hint as to the format the user expects the answer in (general description, tabulated result, diagram, what kind of
diagram etc.)

DATABASE ANALYSIS APPROACH:
When checking for ambiguous dimensions (currencies, units, date ranges), use ANALYTICAL queries that examine data characteristics, not data retrieval queries.

When using get_data for analysis, focus on ANALYTICAL PATTERNS:
- SELECT DISTINCT qcurrency FROM quotations WHERE qtype LIKE '%brent%'
- SELECT COUNT(*) FROM stocks WHERE stname = 'MOL' GROUP BY stcurrency
- SELECT MIN(qdate), MAX(qdate) FROM quotations WHERE qtype = 'cif-med-urals'
Goal: Understand data structure and identify ambiguities with small result sets.

ANALYTICAL QUERY PATTERNS:
- Check available currencies: SELECT DISTINCT qcurrency FROM quotations WHERE qtype LIKE '%brent%'
- Check units of measure: SELECT DISTINCT quom FROM quotations WHERE qtype = 'cif-med-urals'
- Check date coverage: SELECT MIN(qdate), MAX(qdate) FROM quotations WHERE qtype = 'cif-azeri-light'
- Count variations: SELECT qcurrency, COUNT(*) FROM quotations WHERE qtype LIKE '%urals%' GROUP BY qcurrency

AVOID THESE PATTERNS:
- SELECT * FROM quotations WHERE qtype = 'dtd-brent' (returns full dataset)
- SELECT qdate, qprice FROM quotations (retrieves actual values)
- Any query without DISTINCT, GROUP BY, COUNT, MIN/MAX when checking dimensions

PURPOSE: Identify ambiguity and data availability, not retrieve final results.
Your analytical queries should typically return fewer than 20 rows.
Use aggregation to understand data structure efficiently.

RESPONSE CATEGORIES:
1. VALID REQUEST: Can be answered using available petrochemical/refinery financial database
2. INVALID WITH REASON: Asks for unavailable data or outside domain scope
3. INVALID UNCLEAR: Ambiguous, nonsensical, or incomprehensible

Always respond with JSON:
{{
  "status": "valid" | "invalid_reason" | "invalid_unclear",
  "reformulated_request": "clearer version of the request" | null,
  "reason": "explanation why request cannot be fulfilled or follow-up question" | null
}}

EXAMPLES:
Valid: "polyethylene prices over time" → reformulate per above principles
Invalid reason: "EUR/USD exchange rate" → "Currency exchange rates not in petrochemical database"
Invalid unclear: "blue elephant flies backwards" → incomprehensible request

Today's date is {date.today().isoformat()}
"""

execution_stage_system_instruction = f"""You are an assistant helping users extract and analyze data from a database of financial data (quotations, stock
values, margins and spreads) of an integrated oil and gas company. Your task is to compose a reply to the user by interpreting the question and making use
of a number of tools at your disposal (querying the database, requesting diagram construction, compositing the final answer).
Compose your SQL queries in the latest MS SQL Server dialect. Be aware of the field aliasing requirements, since a number of tools expect field names to
also fulfill the role of labels on diagrams.

When using get_data for final results, construct queries that return the actual data
needed for your response (tables, charts, analysis). Include proper field aliases
for chart labels and ensure date ordering for time series.

{domain_description}

AMBIGUITY TRANSPARENCY:
When the reformulated request indicates that ambiguities were resolved (multiple currencies, units, logistic parities, etc.), always include explanatory text that informs the user about:

1. What alternatives were available
2. Which option was chosen and why
3. How the user can request other options

EXPLANATION PATTERNS:
- Single option available: "Only USD/barrel prices are available in the database, so I used those."
- Multiple options with USD preference: "Prices are available in both USD and EUR. I used USD prices as requested, but you can ask for EUR prices as well."
- Multiple options without clear preference: "I found prices in three currencies (USD, EUR, PLN). I used USD prices by default - let me know if you'd prefer a different currency."
- Multiple logistic parities: "Urals quotations are available for three regions (CIF MED, CIF NWE, DAP India). I'm showing all three for comparison."

Always include this transparency information as a text element in your response, typically at the beginning to provide context for the data that follows.

DIMENSION HANDLING:
If the reformulated request includes specific currency/unit specifications (like "in USD" or "USD/barrel"),
assume these have been validated and resolved by a previous phase of semantic analysis.
Do not re-check for multiple currencies/units - proceed directly with the specified values.

Always respond with a JSON list with elements in the following format:
{{
    "type": "text" | "graphics" | "table",
    "text": "generated text (commentary, explanations, ambiguity resolutions)" | null,
    "graphics": "identifier of the graphics as returned by the line_chart tool" | null,
    "table": "identifier of the table as returned by the create_table tool" | null
}}

Include explanatory text elements that describe data choices, ambiguity resolutions, and key findings.
The elements should be ordered for logical flow: explanations first, then data/visualizations, then analysis.

The elements in this list should come in the order they are to be displayed going from top downwards.

Today's date is {date.today().isoformat()}
"""


@dataclass
class Intermediate:  # this should probably start a pydantic class tree, I'll return to it when I have the time
    pass


@dataclass(repr=False)
class ValidRequest(Intermediate):
    request: Annotated[str, "The reformulated request"]

    def __repr__(self) -> str:
        return f"ValidRequest(request={self.request})"


@dataclass(repr=False)
class InvalidWithReason(Intermediate):
    reason: Annotated[str, "Reason reformulating did not work"]

    def __repr__(self) -> str:
        return f"InvalidWithReason(reason={self.reason})"


@dataclass
class InvalidUnclear(Intermediate):
    reason: Annotated[str, "Optional reason"]

    def __repr__(self) -> str:
        return f"InvalidUnclear(reason={self.reason})"


def parse_intermediate_result(text: str) -> Intermediate:
    jsonresult: dict[str, str] = safe_json_parse(text)
    if not jsonresult:
        raise WrongAnswer(f"Intermediate text {text} is not JSON-parseable.")
    if "status" not in jsonresult:
        raise WrongAnswer(f"Intermediate result {jsonresult} has no 'status' field.")
    status = jsonresult["status"]
    if not isinstance(status, str):
        raise WrongAnswer(f"Field 'status' in {jsonresult} is not a string.")
    elif status == "valid":
        if "reformulated_request" not in jsonresult:
            raise WrongAnswer(f"Intermediate result {jsonresult} has no 'reformulated_request' field")
        elif not isinstance(jsonresult["reformulated_request"], str):
            raise WrongAnswer(f"Field 'reformulated_request' in {jsonresult} is not a string.")
        else:
            return ValidRequest(jsonresult["reformulated_request"])
    elif status == "invalid_reason":
        if "reason" not in jsonresult:
            raise WrongAnswer(f"Intermediate result {jsonresult} has no 'reason' field.")
        elif not isinstance(jsonresult["reason"], str):
            raise WrongAnswer(f"Field 'reason' in {jsonresult} is not a string.")
        else:
            return InvalidWithReason(jsonresult["reason"])
    elif status == "invalid_unclear":
        return InvalidUnclear(jsonresult.get("reason", ""))
    else:
        raise WrongAnswer(f"Unexpected value of 'status' field in {jsonresult}.")


def unparse_answer(resources: dict[str, Element], evaluatorresult: Any) -> list[Element]:
    if evaluatorresult is None or not isinstance(evaluatorresult, list):
        raise WrongAnswer("Not parseable as JSON or not a JSON list")
    retval: list[Element] = []
    for rawelem in evaluatorresult:
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
                    raise WrongAnswer(f"Type is 'graphics' but no 'graphics' field is present in {rawelem}")
                if rawelem["graphics"] not in resources:
                    raise WrongAnswer(f"Graphics field is present in {rawelem} but does not point to anything in resources.")
                if not isinstance(resources[rawelem["graphics"]], GraphicsElement):
                    raise WrongAnswer(f"Graphics field in {rawelem} points to a resource that is not a GraphicsElement")
                else:
                    retval.append(resources[rawelem["graphics"]])
            case "table":
                if "table" not in rawelem:
                    raise WrongAnswer(f"Type is 'table' but no 'table' field is present in {rawelem}")
                elif rawelem["table"] not in resources:
                    raise WrongAnswer(f"Table field is present in {rawelem} but does not point to anything in resources.")
                elif not isinstance(resources[rawelem["table"]], TableElement):
                    raise WrongAnswer("Table field in {rawelem} points to a resource that is not a TableElement")
                else:
                    retval.append(resources[rawelem["table"]])
            case _:
                raise WrongAnswer(f"Unexpected value of 'type' field in {rawelem}")
    return retval


def request(llm: lb.LLM, tools: T2SQLTools, history: list[lb.RecStrDict], req: str) -> tuple[list[Element], list[lb.RecStrDict]]:
    lbhistory: lb.History = lb.deserialized_History(history)
    semanticquery: lb.Query = (
        lb.Query.empty()
        .with_systeminstr(analysis_stage_system_instruction)
        .with_tools(basic_tooldict)
        .with_history(lbhistory)
        .with_user(req)
    )
    intermediate_cycle_count: int = 5
    repcount: int
    repcount = intermediate_cycle_count
    while repcount > 0:
        semanticreply: lb.TextReply = llm.answer(
            semanticquery, temperature=0.1, toolfunction=lambda name, params: basic_toolfunction(tools, name, params)
        )
        print(f"Evaluated to {semanticreply.text}")
        repcount -= 1
        try:
            intermediate: Intermediate = parse_intermediate_result(semanticreply.text)
        except WrongAnswer as e:
            continue
        match intermediate:
            case InvalidUnclear(reason=reason):
                msg = "Sorry, but I cannot understand this request at all. " + reason
                return [TextElement(msg)], lb.serialized_History(semanticreply.originalquery.history + [lb.AssistantEntry(msg)])
            case InvalidWithReason(reason=reason):
                return [TextElement(reason)], lb.serialized_History(semanticreply.originalquery.history + [lb.AssistantEntry(reason)])
            case ValidRequest(request=request):
                break

    if repcount == 0:
        raise ShellError(f"No intermediate result after {intermediate_cycle_count} attempts")

    evaluatorquery: lb.Query = (
        lb.Query.empty()
        .with_systeminstr(execution_stage_system_instruction)
        .with_tools(full_tooldict)
        .with_history(lbhistory)
        .with_user(request)
    )
    evaluator_cycle_count = 5
    repcount = evaluator_cycle_count
    while True:
        resources: dict[str, Element] = dict()
        evaluatorreply: lb.TextReply = llm.answer(
            evaluatorquery, temperature=0.25, toolfunction=lambda name, params: extended_toolfunction(tools, resources, name, params)
        )
        evaluatorresult = safe_json_parse(evaluatorreply.text)
        try:
            answer = unparse_answer(resources, evaluatorresult)
            return answer, lb.serialized_History(semanticreply.originalquery.history + [lb.AssistantEntry(textify_elementlist(answer))])
        except WrongAnswer as e:
            repcount -= 1
            if repcount == 0:
                break  # else continue

    raise ShellError(f"No final answer to {request} after {evaluator_cycle_count} attempts.")
