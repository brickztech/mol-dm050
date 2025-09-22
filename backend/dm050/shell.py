import ast
import logging
from datetime import date

import blockz.LLMBlockz as lb
from shell import T2SQLTools

from . import shellutils as su

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

############################################################

full_tooldict: lb.ToolDict = su.complete_tool_dict

semantic_stage_system_instruction = f"""
You are an assistant whose task is to figure out the data domains referenced in user questions. The questions are ultimately aimed at a database containing
data about the financial environment of an oil and gas company. Determine the data domain from the following rules only:
- MOL, OMV and Orlen (sometimes PKN) imply stocks.
- Brent or Dated Brent, Azeri Light, CPC or CPC Blend, Urals (CIF Med Urals, CIF NWE Urals and DAP India Urals) imply crude quotations.
- CEGH or CEGH/VTP and TTF imply natural gas quotations
- propane, propane-butane and butane imply lpg quotations
- benzene, ethylene, propylene, butadiene, polyethylene, polypropylene, ldpe and hdpe imply petchem quotations
- gasoline, diesel, naphta, jet (or jet fuel or kerosene), gasoil, fuel oil, vgo and butadiene-naphta imply spreads
- IEA Brent or IEA Med Urals imply iea margins
- company names in 'MOL Group', MOL, SN, Slovnaft, 'MOL+SN', 'MOL and Slovnaft, MPC, MOL Petrokémia, SPC and 'INA Rijeka' (sometimes just INA) imply company margins
- polymer margin implies company margins
If the user question or statement seems to refer to or clarify previous chat exchanges, consider recent chat history as well.
Beyond this, do not use other information for determining the data domains.
Respond with a list of the names of the appropriate data domains only ('stocks', 'crude quotations', 'natural gas quotations', 'lpg quotations', 'petchem quotations', 'spreads', 'iea margins' and 'company margins') or with an empty list if no data domain seems to apply.
"""

eval_systeminstr_dict = {
    "stocks": """
Use the 'stocks' table of the database to access daily closing stock prices of regionally important oil and gas companies.
The 'stocks' table has four columns: 'stdate', 'stname', 'stcurrency' and 'stvalue'. Do not use other column names.
The date for the current stock quote is stored in the 'stdate' field.
The name of the stock is stored in the 'stname' field. Valid stock names are MOL, OMV (sometimes ÖMV) and Orlen (also sometimes called PKN). In the column only the 'MOL', 'OMV' and 'Orlen' values are allowed.
Assume that there is at most a single row per date and stock name. Be prepared for rows missing for certain dates, such as weekends.
The currency in which the stock value is given can be found in the 'stcurrency' column. This column can now contain 'USD', 'EUR' and 'PLN'. The currency is a function of the stock, so the same stock cannot figure with two different currencies.
The value of the stock is stored in the 'stvalue' column.
""",
    "crude quotations": """
Use the 'quotations' table to access crude oil quotations and calculate crude prices.
The 'quotations' table has three columns, 'qdate', 'qname' and 'qprice'. Do not use other column names.
The date of the quotation or price is stored in the 'qdate' column.
The name of the product to which the quotation refers is stored in the 'qname' column. For crudes this column can contain the following values:
- For Dated Brent or simply Brent:
    - IF the user specified USD/tons or just tons as unit of measure -> qname = 'dated brent tons'.
    - IF the user specified USD/barrels or USD/bbl or just barrels, or did not specify any unit of measure -> qname = 'dated brent'.
- For Azeri or Azeri Light -> qname = "cif azeri light".
- For CPC or CPC Blend or Caspian -> qname = "cif med cpc".
- For Urals:
    - IF Med or Mediterranean is specified -> qname = "cif med urals"
    - IF NWE or NorthWest Europe is specified -> qname = "cif nwe urals"
    - IF India is specified -> qname = "dap india urals"
    - ELSE if none of these is specified -> ask for clarification.
Always assume that other values, not shown here, might exist in the 'qname' column.
The quotation value is stored in the 'qprice' column.
    - IF the current crude is Dated Brent in USD/tons -> 'qprice' contains the absolute price of Brent crude in USD/tons
    - IF the current crude is Dated Brent in USD/barrels -> 'qprice' contains the absolute price of Brent crude in USD/barrels
    - ELSE for all others -> 'qprice' contains the difference between the price of the crude and the price of Brent crude in USD/barrels.
Assume that at most a single row exists for any combination of 'qdate' and 'qname' values. Be prepared for the possibility that certain qdate+qname combinations do not have a corresponding row.
""",
    "natural gas quotations": """
Use the 'quotations' table to access natural gas quotations/prices.
The 'quotations' table has three columns, 'qdate', 'qname' and 'qprice'. Do not use other column names.
The date of the quotation or price is stored in the 'qdate' column.
The name of the product to which the quotation refers is stored in the 'qname' column. For natural gases this column can contain the following values:
- For Central European Gas Hub or CEGH (or CEGH/VTP) -> qname = "cegh vtp da"
- For Title Tansfer Facility or TTF:
    - IF 'day-ahead' is specified -> qname = "ttf day-ahead"
    - IF 'month-ahead' is specified -> qname = "ttf month-ahead"
    - ELSE if neither is specified -> ask for clarification.
Always assume that other values, not shown here, might exist in the 'qname' column.
The quotation value, which is the same as the price, is stored in the 'qprice' column, and is expressed expressed in EUR/MWh.
Assume that at most a single row exists for any combination of 'qdate' and 'qname' values. Be prepared for the possibility that certain qdate+qname combinations do not have a corresponding row.
""",
    "lpg quotations": """
Use the 'quotations' table to access lpg (Liquid petrol gas) quotations/prices.
The 'quotations' table has three columns, 'qdate', 'qname' and 'qprice'. Do not use other column names.
The date of the quotation or price is stored in the 'qdate' column.
The name of the product to which the quotation refers is stored in the 'qname' column. For lpg products this column can contain the following values:
- For propane -> qname = "propane"
- For butane -> qname = "butane"
- For propane-butane -> qname = "propane-butane"
Always assume that other values, not shown here, might exist in the 'qname' column.
The quotation value, which is the same as the price, is stored in the 'qprice' column, and is expressed in USD/tons.
Assume that at most a single row exists for any combination of 'qdate' and 'qname' values. Be prepared for the possibility that certain qdate+qname combinations do not have a corresponding row.
""",
    "petchem quotations": """
Use the 'quotations' table to access petrochemical quotations/prices.
The 'quotations' table has three columns, 'qdate', 'qname' and 'qprice'. Do not use other column names.
The date of the quotation or price is stored in the 'qdate' column.
The name of the petrochemical product to which the quotation refers is stored in the 'qname' column. For petrochemcial products this column can contain the following values:
- For benzene:
    - IF spot or spot trading is specified -> qname = 'benzene spot'
    - IF 'c' or 'contracted' is specified -> qname = 'benzene c'
    - ELSE if neither is specified or something else is specified -> ask for clarification.
- For propylene:
    - IF spot or spot trading is specified -> qname = 'propylene spot'
    - IF 'c' or 'contracted' is specified -> qname = 'propylene c'
    - ELSE if neither is specified or something else is specified -> ask for clarification.
- For ethylene:
    - IF spot or spot trading is specified -> qname = 'ethylene spot'
    - IF 'c' or 'contracted' is specified -> qname = 'ethylene c'
    - ELSE -> ask for clarification.
- For butadiene:
    - IF 'c' or contracted is specified, or if nothing is specified -> qname = 'butadiene c'
    - IF spot or spot trading is specified -> inform the user that there's no data available for butadiene spot
    - ELSE if something else is specified -> ask for clarification.
- For polypropylene -> qname = 'polypropylene'
- For polyethylene:
    - IF high-density or hd or hdpe is specified -> qname = 'hdpe'
    - IF low-density or ld or ldpe is specified -> qname = 'ldpe'
    - ELSE if neither is specified or something else is specified -> ask for clarification.
Always assume that other values, not shown here, might exist in the 'qname' column.
The quotation value, which is the same as the price, is stored in the 'qprice' column, and is expressed in EUR/tons.
Assume that at most a single row exists for any combination of 'qdate' and 'qname' values. Be prepared for the possibility that certain qdate+qname combinations do not have a corresponding row.
""",
    "spreads": """
Use the 'spreads' table to access crack spreads of various petrochemical products.
The 'spreads' table has four columns: 'spdate', 'spname', 'spuom' and 'spvalue'. Do not use other column names.
The date of the crack spread is stored in the 'spdate' column.
The name of the product for which the crack spread is given in the current row is stored in the 'spname' column. This column can have the following values:
- For diesel -> spname = 'diesel'.
- For fuel oil:
    - IF 0.5 or 0.5% is specified -> spname = 'fuel oil 0.5'
    - IF 1 or 1.0 or 1.0% is specified -> spname = 'fuel oil 1.0'
    - IF 3.5 or 3.5% is specified -> spname = 'fuel oil 3.5'
    - ELSE -> ask for clarification.
- For gasoil or gas oil -> spname = 'gasoil'
- For gasoline -> spname = 'gasoline'
- For jet or jet fuel or kerosene -> spname = 'jet'
- For naphta -> spname = 'naphta'
- For vgo or vacuum gas oil:
    - IF 'hs' or high sulphur is specified -> spname = 'vgo hs'
    - IF 'ls' or low sulphur is specified -> spname = 'vgo ls'
    - ELSE -> ask for clarification.
- for butadiene-naphta -> spname = 'but-naph'
Always assume that the spname field may be NULL.
- For butadiene-naphta spread, the unit of measure is always EUR/tons.
- For vgo, the unit of measure is always USD/tons.
- For diesel, fuel oil, gasoil, gasoline, jet and naphta:
    - IF USD/barrel or USD/bbl is specified -> spuom = 'BBL' and the unit of measurement is USD/barrel
    - IF USD/ton is specified -> spuom = 'T' and the unit of measurement is USD/t
    - IF something else is specified -> ask for clarification
    - ELSE if nothing is specified -> use USD/ton, spuom = 'T', and mention this fact to the user.
The actual crack spread value is stored in the 'spvalue' column.
Assume that at most a single row exists for any combination of 'spdate', 'spname' and 'spuom' values, Be prepared for the possibility that certain spdate+spname+spuom combinations do not have a corresponding row.
""",
    "iea margins": """
Use the 'margins' table to access margins according to IEA standards.
The 'margins' table has three columns: 'mdate', 'mname' and 'mvalue'. Do not use other column names.
The date of the margin is stored in the 'mdate' column.
The name of the IEA margin is stored in the 'mname' column. This column can have the following values:
- For IEA Med Urals margin -> mname = 'iea med urals'
- For IEA Brent margin -> mname = 'iea brent'.
Always assume that other values, not shown here, might exist in the 'mname' column.
The value of the margin in question, expressed in EUR/ton, is stored in the 'mvalue' column.
Assume that at most a single row exists for any combination of 'mdate' and 'mname' values. Be prepared for the possibility that certain mdate+mname combinations do not have a corresponding row.
""",
    "company margins": """
Use the 'margins' table to access refinery or petrochemical margins for different member companies or groupings of member companies.
The 'margins' table has four columns: 'mdate', 'mname', 'mcompany' and 'mvalue'. Do not use other column names.
These margins are determined wrt a company or company grouping.
The date of the margin is stored in the 'mdate' column.
The name of the margin type is stored in the 'mname' column. This column can have the following values:
- For refinery or 'ref' margins:
    - IF 'without Urals' is specified or nothing is specified -> mname = 'c-ref'
    - IF 'with Urals' or 'old' is specified -> mname = 'c-ref-old'
    - ELSE if something else is specified -> ask for clarification.
- For petrochemical or 'petchem' margins:
    - IF 'old' or 'without CO2' is specified -> mname = 'pechem-old'
    - IF 'new' or 'with CO2' is specified or nothing is specified -> mname = 'petchem'
    - ELSE if something else is specified -> ask for clarification.
Always assume that other values, not shown here, might exist in the 'mname' column.
The name of the company or company group to which the margins refer to is stored in the 'mcompany' column. This column can have the following values:
- For MOL Group or 'the group' -> mcompany = 'MOL Group'
- For MOL -> mcompany = 'MOL'
- For SN or Slovnaft -> mcompany = 'SN'
- For MOL and SN or MOL and Slovnaft -> mcompany = 'MOL+SN'
- For MPC (standing for MOL Petrokémia) -> mcompany = 'MPC'
- For SPC (standing for Slovnaft Petrokémia) -> mcompany = 'SPC'
- For INA or INA Rijeka -> mcompany = 'INA Rijeka'.
The value of the margin is stored in the 'mvalue' column, and it is always expressed in EUR/tons.
Always assume that other values, not shown here, might exist in the 'mcompany' column.
Assume that at most a single row exists for any combination of 'mdate', 'mname' and 'mcompany' values. Be prepared for the possibility that certain mdate+mname+mcompany combinations do not have a corresponding row.
SPECIAL RULES:
- IF MOL, SN/Slovnaft, MOL+SN or INA margins are requested, treat it as a refinery margin. Asking for petrochemical/petchem margin for these companies is an error from the part of the user.
- IF MPC or SPC margins are requested, treat it as a petrochemical margin. Asking for refinery margins for these companies is an error from the part of the user.
- IF MOL Group margin is requested, ask for clarification about which margin is meant.
- IF 'polymer margin' is requested:
    - IF no company is named, treat is as a request for MOL Group petrochemical margin
    - ELSE treat it as a request for petrochemical margin.
""",
}

evaluation_stage_system_instruction_template = """
You are an assistant helping users extract and analyze data from a database of financial data (quotations, stock
values, margins and spreads) of an integrated oil and gas company. Your task is to compose a reply to the user by interpreting the question and making use
of a number of tools at your disposal (querying the database, requesting diagram construction, compositing the final answer).

You can return a sequence of explanatory texts, tables and line charts. Prefer explanatory text first, then try tables, then line charts unless the user requested otherwise.

Request data from the database via the get_data tool at the aggregation level the user actually needs - if they want monthly averages, request monthly averages in SQL, don't request daily data. Apply maximum aggregation consistent with the question. Push all filtering, grouping, and computation to the database rather than post-processing results.

Compose your SQL queries in the latest MS SQL Server T-SQL (Transact-SQL) dialect.

When calling tools, be aware of the field aliasing requirements.

When using get_data for final results, construct SQL queries that return the actual data needed for your response (tables, charts, analysis). Include proper field aliases for chart labels and ensure date ordering for time series.

Add aliases for all tables used and qualify all fields everywhere in the query with the proper table alias.

{subdomain_description}

Interpret terms like 'last year', 'last month' as referring to the last calendar year and last calendar month.
Incomplete dates like 'the second quarter' (meaning the second quarter-year), 'third week', 'January' etc. refer to dates or date ranges within the current year.

Always respond with JSON:
{{
    "items": "list of elements"
}}
where the elements are themselves JSON objects in the following format:
{{
    "type": "text" | "graphics" | "table",
    "text": "generated text (commentary, explanations, ambiguity resolutions)" | null,
    "graphics": "identifier of the graphics as returned by the line_chart tool" | null,
    "table": "identifier of the table as returned by the create_table tool" | null
}}
(* CRITICAL: The "table" field must contain ONLY the identifier string returned by create_table tool, never a manually constructed table object.
If you need tabular output, call create_table with the appropriate SQL and use its returned identifier. *)
Do not include anything else in the answer but the aforementioned JSON object.
Make sure line breaks in text are represented as backslash+'n' and quotes (both single and double) are escaped with a preceding backslash.
Include explanatory text elements that describe data choices, ambiguity resolutions, and key findings.
The elements in this list should come in the order they are to be displayed going from top downwards. The ordering should conform to what is logical for reading order: first explanations, then data/visualization (if required), then analysis (again if it is required).

Today's date is {todays_date}
"""


def request(llm: lb.LLM, tools: T2SQLTools, history: list[lb.RecStrDict], req: str) -> tuple[list[su.Element], list[lb.RecStrDict]]:
    logger.debug(f"request() called with req='{req}'.")
    lbhistory: lb.History = lb.deserialized_History(history)
    basequery: lb.Query = lb.Query.empty().with_history(lbhistory)
    triagequery: lb.Query = (
        basequery.with_systeminstr(semantic_stage_system_instruction)
        # .with_user(f"What is the data domain of the following request: {req}")
        .with_user(req)
    )

    triagereply: lb.TextReply = llm.answer(triagequery, temperature=0.0)
    logger.debug(f"Triage returned '{triagereply.text()}'.")
    try:
        parsed: list[str] = ast.literal_eval(triagereply.text())
        if not isinstance(parsed, list):
            raise su.ShellError(f"Result '{triagereply.text()}' parses to something else than a Python list-of-strings.")
        if not all(isinstance(item, str) for item in parsed):
            raise su.ShellError(f"Not all items in '{parsed}' are strings.")
        parsedset = set(parsed)
        if 'petchem quotations' in parsedset and 'company margins' in parsedset:
            parsedset.discard('petchem quotations')
        if len(parsedset) != 1:
            sorryanswer = """I am sorry but I am unable to evaluate your request. Reframing the question might help in some cases."""
            return [su.TextElement(sorryanswer)], lb.serialized_History(lbhistory + [lb.UserEntry(req), lb.AssistantEntry(sorryanswer)])
        dom: str = list(parsedset)[0]
        logger.debug(f"Data domain determined to be '{dom}'")
        if dom not in eval_systeminstr_dict:
            raise su.ShellError(f"Domain {dom} is not a valid data domain.")
    except (ValueError, SyntaxError):
        raise su.ShellError(f"Result '{triagereply.text()}' is not parseable as a Python list-of-strings")

    eval_systeminstr = evaluation_stage_system_instruction_template.format(
        subdomain_description=eval_systeminstr_dict[dom], todays_date=date.today().isoformat()
    )
    evaluatorquery: lb.Query = basequery.with_systeminstr(eval_systeminstr).with_tools(full_tooldict).with_user(req)

    evaluator_cycle_count: int = 1
    repcount: int = 1
    while repcount <= evaluator_cycle_count:
        logger.debug(f"Evaluator pass attempt #{repcount} out of {evaluator_cycle_count}")
        resources: dict[str, su.Element] = dict()
        evaluatorreply: lb.TextReply = llm.answer(
            evaluatorquery,
            temperature=0.25,
            toolfunction=lambda name, params: su.toolfunction(tools, resources, name, params),
            cycle_limit=5,
        )
        logger.debug(f"Evaluated to '{evaluatorreply.text()}'.")
        try:
            answer: list[su.Element] = su.unparse_answer(resources, evaluatorreply.text())
            logger.debug(f"Successfully finished evaluation pass with unparsed answer={answer}'")
            return answer, lb.serialized_History(evaluatorquery.history() + [lb.AssistantEntry(su.textify_elementlist(answer))])
        except su.WrongAnswer as e:
            logger.debug(f"WrongAnswer exception received from evaluation pass: '{e}'")
            repcount += 1

    raise su.ShellError(f"No final answer to '{request}' after {evaluator_cycle_count} attempts.")
