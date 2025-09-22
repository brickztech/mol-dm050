import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Annotated, Any, Callable, Iterator, Tuple, TypeAlias, cast, final

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

incr = "  "
"""As there are many formatted printing functions, this value here acts as the unit indentation"""


def remove_comments(text: str) -> str:
    """
    Remove nested comments from text. Comments are delimited by (* and *).

    - Handles nested comments by counting open/close pairs
    - Ignores escaped comment starts: backlash then (*
    - Ignores unmatched closing *)
    - Collapses spaces around removed comments

    Args:
        text: Input string that may contain comments

    Returns:
        String with comments removed and spaces collapsed
    """
    result: list[str] = []
    i: int = 0

    while i < len(text):
        # Check for escaped comment start
        if i < len(text) - 2 and text[i : i + 3] == r'\(*':
            # Add the escaped sequence without the backslash
            result.append('(*')
            i += 3
            continue

        # Check for comment start
        if i < len(text) - 1 and text[i : i + 2] == '(*':
            # Record if there was a space before the comment
            space_before: bool = len(result) > 0 and result[-1] == ' '

            # Find the matching closing *)
            comment_depth: int = 1
            j: int = i + 2

            while j < len(text) - 1 and comment_depth > 0:
                # Check for escaped comment start inside comment
                if j < len(text) - 2 and text[j : j + 3] == r'\(*':
                    j += 3
                    continue

                # Check for nested comment start
                if text[j : j + 2] == '(*':
                    comment_depth += 1
                    j += 2
                # Check for comment end
                elif text[j : j + 2] == '*)':
                    comment_depth -= 1
                    j += 2
                else:
                    j += 1

            # If we found a matching close, skip the entire comment
            if comment_depth == 0:
                # Check if there's a space after the comment
                space_after: bool = j < len(text) and text[j] == ' '

                # Handle space collapsing
                if space_before and space_after:
                    # Remove the trailing space we added, will add one space
                    if result and result[-1] == ' ':
                        result.pop()
                    result.append(' ')
                    j += 1  # Skip the space after comment
                elif space_before or space_after:
                    # Keep one space if there was one on either side
                    if not (result and result[-1] == ' '):
                        result.append(' ')
                    if space_after:
                        j += 1  # Skip the space after comment

                i = j
            else:
                # Unmatched comment start, treat as regular text
                result.append(text[i])
                i += 1
        else:
            # Regular character
            result.append(text[i])
            i += 1

    return ''.join(result)


RecStrDictValue: TypeAlias = 'str | RecStrDict | list[RecStrDictValue]'
RecStrDict: TypeAlias = Mapping[str, RecStrDictValue]
"""Recursive immutable dicts from string to either string or another recursive dictionary. Common type for LLM communications"""


def as_string(v: RecStrDictValue) -> str:
    assert isinstance(v, str)
    return v


def as_dictstrstr(v: RecStrDictValue) -> Mapping[str, str]:
    assert isinstance(v, dict) and all(isinstance(k, str) and isinstance(val, str) for k, val in v.items())
    return cast(Mapping[str, str], v)


def as_recstrdict(v: RecStrDictValue) -> RecStrDict:
    assert isinstance(v, dict)
    return v


class Entry:
    """The (abstract) base type of LLM-independent history entries"""



@dataclass
class UserEntry(Entry):
    """An entry made by the user"""

    content: Annotated[str, "The text the user typed in and the shell sent to the LLM"]  # This will need extension to multimodal input

    def __repr__(self) -> str:
        return f"UserEntry(content={self.content})"


@dataclass
class AssistantEntry(Entry):
    """Entry made in reply by the LLM"""

    content: Annotated[str, "The text the LLM sent back as a response."]

    def __repr__(self) -> str:
        return f"AssistantEntry(content={self.content})"


@dataclass
class RawEntry(Entry):
    """Kludge to quickly accommodate unexpected situations. This entry contains the actual message in a model-dependent format.
    Out-of sequence system instruction fragments, custom roles etc. can be quickly accomodated by this entry, but it is extremely dangerous,
    as it is not model-independent.
    """

    content: Annotated[RecStrDict, "Raw JSON, no guarantees."]

    def __repr__(self) -> str:
        return f"RawEntry(content={repr(self.content)})"


ToolFunction: TypeAlias = Callable[[str, Mapping[str, str]], str]


@dataclass
class SingleToolCall:
    """A single tool call that is the component of a message from the LLM that could possibly ask for multiple tool calls in parallel"""

    call_id: Annotated[str, "The identifier of this call."]
    name: Annotated[str, "The name of the tool being called."]
    paramvalues: Annotated[Mapping[str, str], "The parameter values in a string-to-string dictionary."]

    def __repr__(self) -> str:
        return f"""SingleToolCall(call_id={self.call_id},name={self.name},paramvalues={self.paramvalues})"""


def print_SingleToolCall(indent: str, stcall: SingleToolCall) -> None:
    """Prints a SingleToolCall object on multiple lines, originally indented by indent"""
    match stcall:
        case SingleToolCall(call_id=call_id, name=name, paramvalues=paramvalues):
            print(indent, f"Id: {call_id}", sep="")
            print(indent, f"Function name: {name}", sep="")
            for pname, pvalue in paramvalues.items():
                print(indent + incr, f"{pname} = {pvalue}", sep="")
        case _:
            raise TypeError("Invalid type received in print_SingleToolCall")


def serialize_SingleToolCall(stcall: SingleToolCall) -> RecStrDict:
    match stcall:
        case SingleToolCall(call_id=call_id, name=name, paramvalues=paramvalues):
            # this is where I learned that dict is *invariant* in both type arguments - I expected it to be covariant in the value type, for I'm
            # implicitly thinking in immutable structures
            return {'call_id': call_id, 'name': name, 'paramvalues': paramvalues}
        case _:
            raise TypeError("Invalid type received in serialize_SingleToolCall")


def deserialize_SingleToolCall(stc: RecStrDict) -> SingleToolCall:
    if "call_id" not in stc:
        raise TypeError(f"Field 'call_id' missing from serialized SingleToolCall {stc}")
    elif "name" not in stc:
        raise TypeError(f"Field 'name' missing from serialized SingleToolCall {stc}")
    elif "paramvalues" not in stc:
        raise TypeError(f"Field 'paramvalues' missing from serialized SingleToolCall {stc}")
    else:
        return SingleToolCall(as_string(stc["call_id"]), as_string(stc["name"]), as_dictstrstr(stc["paramvalues"]))


@dataclass
class ToolCallsEntry(Entry):
    """A message sent by the LLM in which one or more tool calls are present."""

    calls: Annotated[list[SingleToolCall], "The list of calls made. Contains at least one element."]


@dataclass
class ToolResultEntry(Entry):
    """Entry created by the shell in order to report the result of a single tool call to the LLM.
    Even if multiple tool calls were issued in one message by the LLM, we assume they have to be replied to individually. OpenAI decreed this.
    """

    call_id: Annotated[str, "The identifier of the particular call for which this is a reply"]
    name: Annotated[str, "The name of the tool that was called."]
    result: Annotated[
        str, "The result in string format. This can be a simple string value like '20250801' or the string representation of a JSON object"
    ]

    def __repr__(self) -> str:
        return f"ToolResultEntry(call_id={self.call_id},name={self.name},result={self.result})"


def _evaluate_singletoolcall(toolfunction: ToolFunction, singletoolcall: SingleToolCall) -> ToolResultEntry:
    """Passes the name and parameters of the call to toolfunction and returns the result"""
    match singletoolcall:
        case SingleToolCall(call_id=call_id, name=name, paramvalues=paramvalues):
            return ToolResultEntry(call_id, name, toolfunction(name, paramvalues))
        case _:
            raise TypeError("ToolCallsReply.evaluate_single_call received a singletoolcall value that is not of SingleToolCall type")


def print_Entry(indent: str, entry: Entry) -> None:
    """Prints the Entry with a general indent of 'indent'"""
    match entry:
        case UserEntry(content=content):
            print(indent, "User: ", content, sep="")
        case AssistantEntry(content=content):
            print(indent, "Assistant: ", content, sep="")
        case RawEntry(content=content):
            print(json.dumps(dict(content)))
        case ToolCallsEntry(calls=calls):
            print(indent, "Assistant:", sep="")
            for stcall in calls:
                print_SingleToolCall(indent + incr, stcall)
        case ToolResultEntry(call_id=call_id, name=name, result=result):
            print(indent, "Tool:", sep="")
            print(indent + incr, f"Id: {call_id}", sep="")
            print(indent + incr, f"Function name: {name}", sep="")
            print(indent + incr, f"Result: {result}", sep="")
        case _:
            raise TypeError("Invalid type received in print_Entry")


History = list[Entry]


def print_History(indent: str, history: History) -> None:
    for entry in history:
        print_Entry(indent, entry)


def serialized_History(history: History) -> list[RecStrDict]:
    """Outputs a form of the history that can be further serialized as it is pure JSON"""
    retval: list[RecStrDict] = []
    for entry in history:
        match entry:
            case UserEntry(content=content):
                retval.append({"user": content})
            case AssistantEntry(content=content):
                retval.append({"assistant": content})
            case ToolCallsEntry(calls=calls):
                retval.append({"calls": [serialize_SingleToolCall(stcall) for stcall in calls]})
            case ToolResultEntry(call_id=call_id, name=name, result=result):
                retval.append({"tool": {"call_id": call_id, "name": name, "result": result}})
            case RawEntry(content=content):
                retval.append({"raw": f"{json.dumps(dict(content))}"})
            case _:
                raise TypeError("Invalid type received in serialize_Entry_list")
    return retval


def deserialized_History(dictlist: list[RecStrDict]) -> History:
    """Reverts the effect of serialized_History.
    Error handling is minimal, you are supposed to only feed this function with outputs of serialized_History.
    """
    retval: list[Entry] = []
    for d in dictlist:
        if len(d) != 1:
            raise ValueError("Dictionary not of correct form for deserialize_History")
        elif "user" in d:
            retval.append(UserEntry(as_string(d["user"])))
        elif "assistant" in d:
            retval.append(AssistantEntry(as_string(d["assistant"])))
        elif "calls" in d:
            dictlist_v = d["calls"]
            retval.append(ToolCallsEntry([deserialize_SingleToolCall(as_recstrdict(stc)) for stc in dictlist_v]))
        elif "tool" in d:
            dict_v = as_recstrdict(d["tool"])
            retval.append(ToolResultEntry(as_string(dict_v["call_id"]), as_string(dict_v["name"]), as_string(dict_v["result"])))
        elif "raw" in d:
            dict_v = as_recstrdict(d["raw"])
            retval.append(RawEntry(dict_v))
        else:
            raise ValueError("Dictionary in history passed to deserialize_History contains unrecognizable entry")
    return retval


def is_tool_Entry(entry: Entry) -> bool:
    """Decides if an entry is dealing with tool calls. This function is then used to trim the history e.g. in .newquery() of some descendants of Reply.
    Does not consider RawEntry as a tool entry even if that's a major possible use for raw entries. If you are using raw entries, you should write your
    own filter functions anyway.
    """
    match entry:
        case ToolCallsEntry() | ToolResultEntry():
            return True
        case UserEntry() | AssistantEntry() | RawEntry():
            return False
        case _:
            raise TypeError("is_tool_Entry received a parameter of the wrong (non-Entry) types")


##################################################################################


class LLMBlockzException(Exception):
    """The mother of all exceptions thrown because something went wrong with the logic of this library."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


###################################################################################


@dataclass
class Parameter:
    """Description of a single parameter used in tool descriptions"""

    name: Annotated[str, "Parameter name"]
    typ: Annotated[str, "Parameter type. Don't be creative - string,integer,float,boolean should be enough"]
    description: Annotated[str, "Description of the meaning of this value"]
    must: Annotated[bool, "Whether this parameter is mandatory (True) or optional (False)"]

    def __repr__(self) -> str:
        return f"Parameter(name={self.name},typ={self.typ},description={self.description},must={self.must})"


def param(name: str, typ: str, description: str) -> Parameter:
    """Utility generating mandatory Parameter values"""
    return Parameter(name, typ, description, True)


def optional(name: str, typ: str, description: str) -> Parameter:
    """ "Utility generating optional Parameter values"""
    return Parameter(name, typ, description, False)


def print_Parameter(indent: str, parameter: Parameter) -> None:
    """Prints a parameter with an initial indent of 'indent'"""
    match parameter:
        case Parameter(name=name, typ=typ, description=description, must=must):
            if must:
                print(indent, f"Mandatory {name} : {typ} -- {description}", sep="")
            else:
                print(indent, f"Optional  {name} : {typ} -- {description}", sep="")
        case _:
            raise TypeError("Invalid type received in print_Parameter")


@dataclass
class ToolDescription:
    """Full description of a single tool"""

    description: Annotated[str, "Description of what does the tool do."]
    paramdecls: Annotated[list[Parameter], "List of parameter descriptions."]

    def __repr__(self) -> str:
        return f"ToolDescription(description={self.description},paramdecls={self.paramdecls})"


def print_ToolDescription(indent: str, tooldescription: ToolDescription) -> None:
    """Description of a single tool"""
    match tooldescription:
        case ToolDescription(description=description, paramdecls=paramdecls):
            print(indent, f"{description}", sep="")
            for param in paramdecls:
                print_Parameter(indent + incr, param)
        case _:
            raise TypeError("Invalid type received in print_Tooldescription")


def tool(description: str, paramdecls: list[Parameter]) -> ToolDescription:
    """Utility function to create a tool description from elements"""
    return ToolDescription(description, paramdecls)


def _valid_call_against_descr(paramlist: list[Parameter], paramvaluedict: Mapping[str, str]) -> bool:
    """Utility to check whether all mandatory parameters are present in an actual parameter list"""
    for formal_param in paramlist:
        if formal_param.must and formal_param.name not in paramvaluedict:
            return False
    return True


ToolDict = Mapping[str, ToolDescription]


def valid_tools_against_calls(tooldict: ToolDict, calllist: list[SingleToolCall]) -> bool:
    """Utility to decide if a list of single calls are all valid wrt a tool dictionary."""
    for toolcall in calllist:
        if toolcall.name not in tooldict or not _valid_call_against_descr(tooldict[toolcall.name].paramdecls, toolcall.paramvalues):
            return False
    return True


############################################################################################


@dataclass
class Query:
    """ "Class of objects that are/can be sent to the LLM.
    The basic usage is to build a Query by whatever means, then build new Query'es from it using the various with_*() member functions.
    Be careful with these functions, because some of them replace values and others append to history, and this difference is not reflected
    in the naming convention.
    """

    _history: Annotated[
        History, "List of entries forming the discussion history we want to show the LLM, without the initial system instruction."
    ]
    _systeminstr: Annotated[str, "The system instruction for this query"]
    _tools: Annotated[ToolDict, "Tool dictionary to be transferred to the LLM - this is what it can choose from."]

    @staticmethod
    def empty() -> 'Query':
        """Return an empty Query to be used as the starting block in a builder pattern"""
        return Query([], "", dict())

    def with_user(self, content: str) -> 'Query':
        """APPENDS an user entry to the history"""
        return replace(self, _history=self._history + [UserEntry(content)])

    def with_assistant(self, content: str) -> 'Query':
        """APPENDS an user entry to the history"""
        return replace(self, _history=self._history + [AssistantEntry(content)])

    def with_toolcalls(self, calls: list[SingleToolCall]) -> 'Query':
        """APPENDS a toolcalls message to the history"""
        return replace(self, _history=self._history + [ToolCallsEntry(calls)])

    def with_toolreply(self, call_id: str, name: str, result: str) -> 'Query':
        """APPENDS a toolreply message to the history"""
        return replace(self, _history=self._history + [ToolResultEntry(call_id, name, result)])

    def with_raw(self, content: RecStrDict) -> 'Query':
        """APPENDS a raw message to the history."""
        return replace(self, _history=self._history + [RawEntry(content)])

    def with_history(self, history: History) -> 'Query':
        """REPLACES self._history with the parameter."""
        return replace(self, _history=history)

    def with_systeminstr(self, systeminstr: str) -> 'Query':
        """REPLACES the system instruction with the parameter"""
        return replace(self, _systeminstr=remove_comments(systeminstr))

    def with_tools(self, tools: ToolDict) -> 'Query':
        """REPLACES the tools declaration with the parameter"""
        return replace(self, _tools=tools)

    def history(self) -> History:
        return self._history

    def tools(self) -> ToolDict:
        return self._tools

    def systeminstr(self) -> str:
        return self._systeminstr

    def replify(self) -> 'RootReply':
        """Artifact to make the code cleaner, by creating a fake Reply that can be turned into a Query by adding user input to it."""
        return RootReply(self)

    def streamreplify(self) -> 'StreamingRootReply':
        return StreamingRootReply(self)

    def last_message(self) -> str:
        """Returns the last message of the chat history stored in the query if it is a user message
        Returns a string in any case; meant to be used in logging only.
        """
        if len(self._history) == 0:
            return "<EMPTY CHAT HISTORY>"
        lastentry: Entry = self._history[-1]
        match lastentry:
            case UserEntry(content=content):
                return content
            case _:
                return "<LAST ENTRY IS NOT AN USER ENTRY>"

    def __repr__(self) -> str:
        return f"""Query(_history={self._history},
systeminstr={self._systeminstr},
tools={self._tools})"""


def print_Query(indent: str, query: Query) -> None:
    """Prints a query with initial indent 'indent'."""
    match query:
        case Query(_history=history, _systeminstr=systeminstr, _tools=tools):
            print(indent, "Tools:", sep="")
            for name, descr in tools.items():
                print(indent + incr, f"Tool name: {name}", sep="")
                print_ToolDescription(indent + 2 * incr, descr)
            print(indent, f"System instruction: {systeminstr}", sep="")
            print(indent, "History:", sep="")
            print_History(indent + incr, history)
        case _:
            raise TypeError("print_Query_common received invalid type")


###################################################################


@dataclass
class Reply:
    """The base class of Replies as received from the LLM. Meant to be treated as abstract."""

    lastquery: Annotated[Query, "The query that led to this reply."]


@dataclass
class NonStreamingReply(Reply):
    """Convenience class to group those Reply'es that can be printed out.
    These are the classes we receive from non-streaming calls.
    """



@dataclass
class RootReply(NonStreamingReply):
    """Helper class meant to simplify code.
    RootReply is one of the subclasses of Reply that sport a .newquery() member function. This means that a RootReply can be supplied
    as a reply to a cycle in which the last reply is turned into the next Query by supplying a user input. The usage is as follows: one creates
    an empty Query, adds tools and system instruction via the appropriate with_*() functions, then turns it into a RootReply with Query.replify().
    Then the main cycle can start with requesting user input, creating a query from the current reply, creating a reply from the query via one of the
    LLM.answer() or LLM.streamanswer() functions, printing the reply text and going back to the start where user input is asked, except that the second
    and subsequent passes will use an actual reply and not the RootReply. If you aren't allowed to use RootReply, your cycles will be much uglier.
    """

    def newquery(self, userinput: str, *historyfilters: Callable[[History], History]) -> Query:
        """Creates a query from the original query of the RootReply by filtering its history (doing nothing if historyfilter is not set),
        then adding an user entry and returning the new Query.
        """
        newhistory: History = self.lastquery.history()
        for historyfilter in historyfilters:
            newhistory = historyfilter(newhistory)
        return self.lastquery.with_history(newhistory).with_user(userinput)


def drop_toolexchanges(history: History) -> History:
    """Removes the entries related to tool invocation and tool call results from the end of history"""
    return [entry for entry in history if not is_tool_Entry(entry)]


def apply_history_filters(history: History, *historyfilters: Callable[[History], History]) -> History:
    retval = history
    for historyfilter in historyfilters:
        retval = historyfilter(retval)
    return retval


@dataclass
class TextReply(NonStreamingReply):
    """Plain, final reply with text content."""

    _text: Annotated[str, "The text received from the LLM."]

    def text(self) -> str:
        return self._text

    def history(self) -> History:
        return self.lastquery.history() + [AssistantEntry(self.text())]

    def newquery(self, userinput: str, *historyfilters: Callable[[History], History]) -> Query:
        """Creates a new query from the last plain reply by filtering the history and adding an user input.
        By default the tool-related entries (toolcalls and toolresult) are removed from the end of the history,
        but you can change this behavior by supplying a different historyfilter.
        .newquery() can be called any number of times, possibly with different userinput and/or historyfilter parameters, and it will always return
        a fresh Query that picks up evaluation history from where the previous call (leading to the creation of this StreamingTextReply) left it off.
        """
        if historyfilters == ():
            historyfilters = (drop_toolexchanges,)
        logger.debug(
            f"TextReply.newquery called with userinput={userinput} and historyfilters={[func.__qualname__ for func in historyfilters]}"
        )
        newhistory: History = apply_history_filters(self.history(), *historyfilters)
        return self.lastquery.with_history(newhistory).with_user(userinput)


@dataclass
class ToolCallsReply(NonStreamingReply):
    """Reply from the LLM carrying one or more tool calls"""

    calls: Annotated[list[SingleToolCall], "The list of single tool calls sent with this message."]

    def history(self) -> History:
        return self.lastquery.history() + [ToolCallsEntry(self.calls)]

    def evaluate(self, toolfunction: ToolFunction) -> Query:
        """Creates a new Query from the original one that led to this reply by evaluating all the calls and appending the corresponding
        tool result entries to the history. The Query thus built is immediately ready to be sent back to the LLM.
        .evaluate() can be called any number of times, perhaps with different toolfunctions, and it will return Query'es that continue
        the history that led to the creation of this ToolCallsReply. In other words multiple calls of .evaluate() will branch the history of
        evaluation.
        """
        logger.debug(f"ToolCallsReply.evaluate called with toolfunction={toolfunction.__qualname__}")
        toolresultentries: list[Entry] = [_evaluate_singletoolcall(toolfunction, singletoolcall) for singletoolcall in self.calls]
        return self.lastquery.with_history(self.history() + toolresultentries)


def print_NonStreamingReply(indent: str, nonstreamingreply: NonStreamingReply) -> None:
    """Prints a non-streaming reply after an initial indent. (Streaming replies have state, so it is hard to tell what to print about them.)"""
    match nonstreamingreply:
        case TextReply(lastquery=lastquery, text=text):
            print(indent, "<TextReply>", sep="")
            print_Query(indent + incr, lastquery)
            print(indent + incr, f"Text: {text}", sep="")
        case ToolCallsReply(lastquery=lastquery, calls=calls):
            print(indent, "<ToolCallsReply>", sep="")
            print_Query(indent + incr, lastquery)
            print(indent + incr, "Current calls:", sep="")
            for singletoolcall in calls:
                print_SingleToolCall(indent + incr, singletoolcall)
        case _:
            raise TypeError("print_NonStreamingReply received a value with the wrong type")


@dataclass
class StreamingReply(Reply):
    """Base class for replies received from streaming completion requests"""



@dataclass
class StreamingRootReply(StreamingReply):
    def newquery(self, userinput: str, *historyfilters: Callable[[History], History]) -> Query:
        """Creates a query from the original query of the RootReply by filtering its history (doing nothing if historyfilter is not set),
        then adding an user entry and returning the new Query.
        """
        logger.debug(
            f"StreamingRootReply.newquery called with userinput={userinput} and historyfilters={[func.__qualname__ for func in historyfilters]}"
        )
        newhistory: History = apply_history_filters(self.lastquery.history(), *historyfilters)
        return self.lastquery.with_history(newhistory).with_user(userinput)


class StreamingTextReply(StreamingReply):
    """Final, plain reply received from a streaming completion request"""

    def __init__(self, lastquery: Query, rootstream: Iterator[str]) -> None:
        super().__init__(lastquery)
        self._rootstream: Annotated[Iterator[str], "The stream of tokens-as-strings that resulted from the call"] = rootstream
        self._textlist: Annotated[list[str], "The list of tokens read from _rootstream so far."] = []
        self._done: Annotated[bool, "Whether the _rootstream has ended (True) or not (False)"] = False

    @staticmethod
    def of_text(query: Query, text: str) -> 'StreamingTextReply':
        """Creates a StreamingTextReply from a text."""
        retval: StreamingTextReply = StreamingTextReply(query, iter(()))
        retval._done = True
        parts: list[str] = text.split(' ')
        retval._textlist = [part + ' ' for part in parts[:-1]] + [parts[-1]] if parts else []
        return retval

    def _progress_to(self, mark: int) -> None:
        """Internal utility forcing the reading of _rootstream up to 'mark' tokens.
        All the different streams we provide through .stream() read the _textlist, not directly the _rootstream, and they invoke _progress_to
        before reading to make sure their next token is in _textlist or that the stream has ended.
        """
        logger.debug(f"StreamingTextReply._progress_to progressing to mark={mark}")
        while not self._done and len(self._textlist) <= mark:
            try:
                nextchunk: str = next(self._rootstream)
                self._textlist.append(nextchunk)
            except StopIteration:
                self._done = True
                break

    def stream(self) -> Iterator[str]:
        """Creates and returns a new stream of tokens-as-strings. These streams are independent of each other, all go through the whole
        output of _rootstream, no matter in what order they are called.
        There was no explicit call for this behavior, but it turns out that implementing both .stream() and .text() can be done in the most
        economic way if we have the possibility of an unlimited number of truly independent streams (and .text() simply uses one of them).
        """
        mark: int = 0
        while True:
            if mark < len(self._textlist):
                yield self._textlist[mark]
                mark += 1
            else:
                if self._done:
                    break
                self._progress_to(mark)
                if mark < len(self._textlist):
                    continue
                else:
                    break

    def text(self) -> str:
        """Returns the text returned with this reply in one chunk.
        .text() can be called any number of times, and it will always return the same text, which is, however, not physically the same string as before.
        """
        if not self._done:
            for chunk in self._rootstream:
                self._textlist.append(chunk)
            self._done = True
        return "".join(self._textlist)

    def history(self) -> History:
        return self.lastquery.history() + [AssistantEntry(self.text())]

    def newquery(self, userinput: str, *historyfilters: Callable[[History], History]) -> Query:
        """Creates a Query from the original query that led to this Reply, by filtering history, adding the last reply by the assistant and the
        new user input.
        .newquery() can be called any number of times, possibly with different userinput and/or historyfilter parameters, and it will always return
        a fresh Query that picks up evaluation history from where the previous call (leading to the creation of this StreamingTextReply) left it off.
        """
        if historyfilters == ():
            historyfilters = (drop_toolexchanges,)
        logger.debug(
            f"StreamingTextReply.newquery called with userinput={userinput} and historyfilters={[func.__qualname__ for func in historyfilters]}"
        )
        newhistory: History = apply_history_filters(self.history(), *historyfilters)
        return self.lastquery.with_history(newhistory).with_user(userinput)


class StreamingToolCallsReply(StreamingReply):
    """The type of objects representing tool calls received from a streaming completions request.
    This is returned immediately upon realizing that tool calls are being transmitted from the LLM in a streaming manner,
    without waiting for the chunks making up the tool calls to come to an end, such that the user can be informed immediately
    about the reason for the delay.
    """

    def __init__(self, lastquery: Query, callsbuilder: Callable[[], list[SingleToolCall]]) -> None:
        super().__init__(lastquery)
        self._callsbuilder: Annotated[Callable[[], list[SingleToolCall]], "The closure that builds the call list."] = callsbuilder
        self._calls: list[SingleToolCall] | None = None

    def _get_calls(self) -> list[SingleToolCall]:
        if self._calls is None:
            self._calls = self._callsbuilder()
        return self._calls

    @staticmethod
    def of_calls(query: Query, calls: list[SingleToolCall]) -> 'StreamingToolCallsReply':
        """Builds a StreamingToolCallsReply from a list of single calls."""
        logger.debug(f"StreamingToolCallsReply.of_calls called with calls={calls}")
        return StreamingToolCallsReply(query, lambda: calls)

    def history(self) -> History:
        return self.lastquery.history() + [ToolCallsEntry(self._get_calls())]

    def evaluate(self, toolfunction: ToolFunction) -> Query:
        """Reads the rest of the chunks if not done so earlier, then evaluates the tool calls via the toolfunction and builds the Query
        that can be sent back immediately to the LLM.
        .evaluate() can be called multiple times, possibly with different toolfunctions, and it will create a Query that continues work
        from the call that led to the creation of this StreamingToolCallsReply. In other words, evaluate can be called multiple times to branch the
        history of evaluation.
        """
        logger.debug(f"StreamingToolCallsReply.evaluate called with toolfunction={toolfunction.__qualname__}")
        toolresultentries: list[Entry] = [_evaluate_singletoolcall(toolfunction, singletoolcall) for singletoolcall in self._get_calls()]
        logger.debug(f"calls={self._get_calls()}")
        return self.lastquery.with_history(self.history() + toolresultentries)


def manual_toolfunction(name: str, params: Mapping[str, str]) -> str:
    """Utility toolfunction meant for debugging. It simply asks for the result of the tool call."""
    return input(f"Evaluate the tool \"{name}\" called on {params}: ")


def sentinel_toolfunction(name: str, params: Mapping[str, str]) -> str:
    """Utility toolfunction meant to serve as a meaningful default. It raises an exception if called."""
    raise LLMBlockzException("No toolfunction provided")


##################################################################################


class LLM(ABC):
    """The root class of all LLMs, meant to be an abstract base class."""

    @abstractmethod
    def step(self, query: Query, temperature: float | None, model: str | None, **kwargs: Any) -> NonStreamingReply:
        """.step() will have the LLM evaluate a Query and return the answer immediately in a non-streaming manner. Tool calls may be returned."""

    @abstractmethod
    def streamstep(self, query: Query, temperature: float | None, model: str | None, **kwargs: Any) -> StreamingReply:
        """streamstep() will have the LLM evaluate a Query and reply in a streaming manner. Tool calls may be returned."""

    def answer(
        self,
        query: Query,
        temperature: float | None = None,
        model: str | None = None,
        toolfunction: ToolFunction | None = None,
        cycle_limit: int | None = None,
        **kwargs: Any,
    ) -> TextReply:
        """.answer() will keep calling .step() and iterate through the replies until a final, plain answer is received.
        In other words, it will deal with the tool calls on its own terms, evaluating them via the toolfunction received, so that you don't have to.
        cycle_limit limits the number of turns for which the LLM is accepted to request tool calls. Since LLMs are known to go into infinite loops
        of tool calls, this rather crude mechanism is thought as satisfactory to stop this behavior.
        """
        if temperature is None:
            raise ValueError("LLM.answer() called with temperature=None")
        if model is None:
            raise ValueError("LLM.answer() called with model=None")
        if toolfunction is None:
            raise ValueError("LLM.answer() called with toolfunction=None")
        if cycle_limit is None:
            raise ValueError("LLM.answer() called with cycle_limit=None")
        iterations: int = 0
        while True:
            reply: NonStreamingReply = self.step(query, temperature=temperature, model=model, **kwargs)
            match reply:
                case TextReply():
                    return reply
                case ToolCallsReply():
                    iterations += 1
                    if iterations > cycle_limit:
                        raise LLMBlockzException(f"Cycle limit of {cycle_limit} exceeded")
                    query = reply.evaluate(toolfunction)
                    continue
                case _:
                    raise TypeError("Wrong type in LLM.answer")

    def streamanswer(
        self,
        query: Query,
        temperature: float | None = None,
        model: str | None = None,
        toolfunction: ToolFunction | None = None,
        cycle_limit: int | None = None,
        **kwargs: Any,
    ) -> StreamingTextReply:
        """.streamanswer() will keep calling .streamstep() and iterate through the replies until a final, plain answer is received.
        In other words, it will deal with the tool calls on its own terms, evaluating them via the toolfunction received, so that you don't have to.
        cycle_limit limits the number of turns for which the LLM is accepted to request tool calls. Since LLMs are known to go into infinite loops
        of tool calls, this rather crude mechanism is thought as satisfactory to stop this behavior.
        """
        if temperature is None:
            raise ValueError("LLM.streamanswer() called with temperature=None")
        if model is None:
            raise ValueError("LLM.streamanswer() called with model=None")
        if toolfunction is None:
            raise ValueError("LLM.streamanswer() called with toolfunction=None")
        if cycle_limit is None:
            raise ValueError("LLM.streamanswer() called with cycle_limit=None")
        iterations: int = 0
        while True:
            reply: StreamingReply = self.streamstep(query, temperature=temperature, model=model, **kwargs)
            match reply:
                case StreamingTextReply():
                    return reply
                case StreamingToolCallsReply():
                    iterations += 1
                    if iterations > cycle_limit:
                        raise LLMBlockzException(f"Cycle limit of {cycle_limit} exceeded")
                    query = reply.evaluate(toolfunction)
                    continue
                case _:
                    raise TypeError("Wrong type in LLM.streamanswer")


#    @abstractmethod
#    def tokencount(self,target: Query | History | str) -> int:
#        pass


class ManualLLM(LLM):
    """Supporting class helping with debugging. It asks the user at every turn what should it return to the caller. It can be passed on to any
    application that expects an LLM, it can issue tool calls, reply in either streaming or non-streaming manner etc.
    """

    _next_call_id: Annotated[int, "Global running number used to generate unique call ids"] = 0

    @classmethod
    def _force(cls, prompt: str, explanation: str, alternatives: list[str]) -> str:
        while True:
            response = input(prompt)
            if alternatives != [] and response.lower() not in alternatives:
                print(explanation)
                continue
            else:
                return response

    def _step(self, query: Query, stream: bool) -> Reply:
        while True:
            responsetype: str = self._force(
                "What kind of reply do you want to create?\n\t1 => (Streaming)TextReply\n\t2 => (Streaming)ToolCallsReply\n",
                "Only 1 and 2 are acceptable answers (streaming or not is decided by the parameter).",
                ["1", "2"],
            )
            if responsetype == '1':  # TextReply
                text: str = input("Please enter textual reply or '/' to return to the reply type choice: ")
                if text.strip() == "/":
                    continue
                if stream:
                    return StreamingTextReply.of_text(query, text)
                else:
                    return TextReply(query, text)
            else:  # responsetype == '2': ToolCallsReply
                calls: list[SingleToolCall] = []
                toolname: str = input("Enter the name of the first tool to be called or '/' to return to the reply type choice: ").strip()
                if toolname == "/":
                    continue
                argname: str = ""
                while True:
                    if toolname == "." or toolname == '/':
                        break
                    args: dict[str, str] = dict()
                    argname = input(
                        "Enter name of first argument, '.' to finish the list of arguments or '/' to return to the reply type choice: "
                    ).strip()
                    while True:
                        if argname == "." or argname.strip() == '/':
                            break
                        if argname in args:
                            print(f"Argument '{argname}' already set, entry ignored.")
                        else:
                            argvalue: str = input(f"Enter value for argument '{argname}': ")
                            args[argname] = argvalue
                        argname = input(
                            "Enter name of next argument, '.' to finish the list of arguments or '/' to return to the reply type choice: "
                        ).strip()
                    if argname == '/':
                        break
                    calls.append(SingleToolCall(str(ManualLLM._next_call_id), toolname, args))
                    ManualLLM._next_call_id += 1
                    toolname = input(
                        "Enter the name of the next tool to be called, '.' to finish or '/' to return to the reply type choice: "
                    ).strip()
                if argname == '/' or toolname.strip() == '/':
                    continue
                if stream:
                    return StreamingToolCallsReply.of_calls(query, calls)
                else:
                    return ToolCallsReply(query, calls)

    def step(self, query: Query, temperature: float | None = None, model: str | None = None, **kwargs: Any) -> NonStreamingReply:
        print(f"ManualLLM.step invoked with temperature = {temperature}, model = {model}, **kwargs = {kwargs} and query =")
        print_Query(incr, query)
        retval = self._step(query, False)
        assert isinstance(retval, NonStreamingReply)
        return retval

    def streamstep(self, query: Query, temperature: float | None = None, model: str | None = None, **kwargs: Any) -> StreamingReply:
        print(f"ManualLLM.streamstep invoked with temperature = {temperature}, model = {model}, **kwargs = {kwargs} and query =")
        print_Query(incr, query)
        retval = self._step(query, True)
        assert isinstance(retval, StreamingReply)
        return retval

    def answer(
        self,
        query: Query,
        temperature: float | None = None,
        model: str | None = None,
        toolfunction: ToolFunction | None = None,
        cycle_limit: int | None = None,
        **kwargs: Any,
    ) -> TextReply:
        print(
            f"ManualLLM.answer() invoked with temperature = {temperature}, model = {model}, toolfunction = {toolfunction.__qualname__ if toolfunction else None}, cycle_limit = {cycle_limit} and **kwargs = {kwargs}"
        )
        iterations: int = 0
        while True:
            reply: NonStreamingReply = self.step(query, temperature=temperature, model=model, **kwargs)
            match reply:
                case TextReply():
                    return reply
                case ToolCallsReply():
                    iterations += 1
                    leave: str = input("Iteration count = {iterations}, do you want to continue ([Y]/n)?").strip().lower()
                    if leave == 'n':
                        raise LLMBlockzException(f"Cycle limit of {cycle_limit} exceeded")
                    query = reply.evaluate(toolfunction if toolfunction else sentinel_toolfunction)
                    continue
                case _:
                    raise TypeError("Wrong type in LLM.answer")

    def streamanswer(
        self,
        query: Query,
        temperature: float | None = None,
        model: str | None = None,
        toolfunction: ToolFunction | None = None,
        cycle_limit: int | None = None,
        **kwargs: Any,
    ) -> StreamingTextReply:
        print(
            f"ManualLLM.stramanswer() invoked with temperature = {temperature}, model = {model}, toolfunction = {toolfunction.__qualname__ if toolfunction else None}, cycle_limit = {cycle_limit} and **kwargs = {kwargs}"
        )
        iterations: int = 0
        while True:
            reply: StreamingReply = self.streamstep(query, temperature=temperature, model=model, **kwargs)
            match reply:
                case StreamingTextReply():
                    return reply
                case StreamingToolCallsReply():
                    iterations += 1
                    leave: str = input("Iteration count = {iterations}, do you want to continue ([Y]/n)?").strip().lower()
                    if leave == 'n':
                        raise LLMBlockzException(f"Cycle limit of {cycle_limit} exceeded")
                    query = reply.evaluate(toolfunction if toolfunction else sentinel_toolfunction)
                    continue
                case _:
                    raise TypeError("Wrong type in LLM.streamanswer")


#################################################################################


class Embedding(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def embedding_of(self, text: str) -> list[float]:
        pass


# Much to be done here is.
#   t. master Yoda

##################################################################################


@final
class OpenAILikeLLM(LLM):
    @staticmethod
    def _get_service_name(client: Any) -> str:
        """Returns the service name behind the raw client"""
        if not getattr(client, "base_url", None):
            raise LLMBlockzException("Alleged client has no 'base_url' attribute in OpenAILLM._get_service_name")
        base_url = str(client.base_url).lower()
        if "openai.azure.com" in base_url:
            return "azure"
        elif "api.openai.com" in base_url:
            return "openai"
        elif ":11434" in base_url or "ollama" in base_url:
            return "ollama"
        elif ":8000" in base_url or "vllm" in base_url:
            return "vllm"
        else:
            return "unknown"

    def __init__(self, client: Any, default_model: str, default_temperature: float = 0.7) -> None:
        super().__init__()
        logger.debug(
            f"OpenAILikeLLM constructor called with client.base_url={client.base_url}, default_model={default_model} and default_temperature={default_temperature}"
        )
        self._client: Annotated[Any, "An ollama client"] = client
        self._default_temperature: Annotated[float, "The temperature to be used if not explicitly supplied"] = default_temperature
        self._default_model: Annotated[str, "The model to be used if not explicitly supplied"] = default_model
        self._service_name: Annotated[str, "Service name: openai, azure, ollama, vllm or unknown"] = self._get_service_name(client)
        self._can_stream: Annotated[bool, "Whether the inner client supports streaming"] = self._service_name in ["openai", "azure"]
        logger.debug(
            f"OpenAILikeLLM instance created with service={self._service_name}, \
default_model={default_model},default_temperature={default_temperature}"
        )

    def _resolve_named_parameters(
        self, temperature: float | None, model: str | None, toolfunction: ToolFunction | None, cycle_limit: int | None
    ) -> Tuple[float, str, ToolFunction, int]:
        temperature = self._default_temperature if temperature is None else temperature
        model = self._default_model if model is None else model
        toolfunction = sentinel_toolfunction if toolfunction is None else toolfunction
        cycle_limit = 5 if cycle_limit is None else cycle_limit
        return temperature, model, toolfunction, cycle_limit

    def _format_param_properties(self, parameter: Parameter) -> RecStrDict:
        if parameter.description == "":
            return {"type": parameter.typ}
        else:
            return {"type": parameter.typ, "description": remove_comments(parameter.description)}

    def _format_tools_of(self, query: Query) -> list[RecStrDict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": toolname,
                    "description": remove_comments(tooldescr.description),
                    "parameters": {
                        **(
                            {
                                "type": "object",
                                "properties": {par.name: self._format_param_properties(par) for par in tooldescr.paramdecls},
                                "required": [as_string(par.name) for par in tooldescr.paramdecls if par.must],
                            }
                            if tooldescr.paramdecls
                            else {}
                        )  # Ollama chokes on empty "properties" for some reason.
                    },
                },
            }
            for toolname, tooldescr in query.tools().items()
        ]

    def _format_singletoolcall(self, singletoolcall: SingleToolCall) -> RecStrDict:
        match singletoolcall:
            case SingleToolCall(call_id=call_id, name=name, paramvalues=paramvalues):
                return {"id": call_id, "type": "function", "function": {"name": name, "arguments": json.dumps(dict(paramvalues))}}
            case _:
                raise TypeError("OpenAILLM._format_singletoolcall received a value 'singletoolcall' that is not of type SingleToolCall")

    def _format_entry(self, entry: Entry) -> RecStrDict:
        match entry:
            case UserEntry(content=content):
                return {"role": "user", "content": content}
            case AssistantEntry(content=content):
                return {"role": "assistant", "content": content}
            case ToolCallsEntry(calls=calls):
                return {"role": "assistant", "tool_calls": list(map(self._format_singletoolcall, calls))}
            case ToolResultEntry(call_id, name, result):
                return {"role": "tool", "name": name, "tool_call_id": call_id, "content": result}
            case RawEntry(content=content):
                return content
            case _:
                raise TypeError("OpenAILLM._format_entry received a value 'entry' that is not of type Entry")

    def _format_messages_of(self, query: Query) -> list[RecStrDict]:
        system_dict: list[RecStrDict] = [{"role": "system", "content": query.systeminstr()}]
        history_list: list[RecStrDict] = [self._format_entry(entry) for entry in query.history()]
        combined_list: list[RecStrDict] = system_dict + history_list
        retval: list[RecStrDict] = combined_list
        return retval

    def _step(self, query: Query, temperature: float, model: str, **kwargs: Any) -> str | list[SingleToolCall]:
        logger.debug(f"OpenAILikeLLM._step called with temperature={temperature}, model={model}, **kwargs={kwargs} and query={query}")
        tools: list[RecStrDict] = self._format_tools_of(query)
        response = self._client.chat.completions.create(
            model=model,
            messages=self._format_messages_of(query),
            temperature=temperature,
            stream=False,
            **{**({"tools": tools} if len(tools) > 0 else {}), **kwargs},
        ).choices[0]
        if (finish_reason := getattr(response, "finish_reason", None)) is None:
            raise LLMBlockzException("LLM did not return a finish_reason when non-streaming.")
        elif finish_reason == "stop":
            logger.debug("finish_reason=stop")
            if (message_end := getattr(response, "message", None)) is None:
                raise LLMBlockzException("Response does not have a 'message' field")
            content_end = getattr(message_end, "content", None)
            if content_end is None:
                raise LLMBlockzException("response.message.content is missing")
            if isinstance(content_end, str):
                logger.debug(f"String returned: {content_end}")
                return content_end
            else:
                raise LLMBlockzException("response.message.content contains a non-string value")
        elif finish_reason == "tool_calls":
            logger.debug("finish_reason=tool_calls")
            if (toolcalls_end := getattr(response.message, "tool_calls", None)) is None:
                raise LLMBlockzException("Response.message does not have a 'tool_calls' field, despite finish_reason='tool_calls'")
            calls: list[SingleToolCall] = []
            for toolcall in toolcalls_end:
                if (id_end := getattr(toolcall, "id", None)) is None:
                    raise LLMBlockzException("Tool call has no 'id' field")
                if (function_end := getattr(toolcall, "function", None)) is None:
                    raise LLMBlockzException("Tool call has no 'function' field")
                if (name_end := getattr(function_end, "name", None)) is None:
                    raise LLMBlockzException("Tool call 'function' attribute has no 'name' field")
                if (arguments_end := getattr(function_end, "arguments", None)) is None:
                    raise LLMBlockzException("Tool call 'function' attribute has no 'arguments' field")
                calls.append(SingleToolCall(id_end, name_end, json.loads(arguments_end)))
            logger.debug(f"Tool calls={calls}")
            if valid_tools_against_calls(query.tools(), calls):
                logger.debug("Validation successful.")
                return calls
            else:
                raise LLMBlockzException("LLM returned tool calls that do not match the tool declarations")
        else:
            raise LLMBlockzException("LLM returned response with finish_reason = {response.finish_reason}")

    def step(self, query: Query, temperature: float | None = None, model: str | None = None, **kwargs: Any) -> NonStreamingReply:
        temperature, model, _toolfunction, _cycle_limit = self._resolve_named_parameters(temperature, model, None, None)
        logger.debug(f"OpenAILikeLLM.step() called with temperature={temperature}, model={model}, extra arguments={kwargs}\nQuery={query}")
        essence: str | list[SingleToolCall] = self._step(query, temperature, model, **kwargs)
        if isinstance(essence, str):
            logger.debug(f"Final reply is about to be returned from OpenAILikeLLM.step(): {essence}")
            return TextReply(query, essence)
        else:  # isinstance(essence,list):
            logger.debug(f"Tool call reply is about to be returned from OpenAILikeLLM.step() with calls={essence}")
            return ToolCallsReply(query, essence)

    def _tokenstream_of(self, chunkstream: Iterator[Any], firstmessage: Any) -> Iterator[str]:
        """Stream of string fragments in the case of a plain reply.
        chunkstream is consumed completely."""
        nextmessage: Any = firstmessage
        logger.debug("OpenAILLM._tokenstream_of called")
        while True:
            try:
                if (
                    (delta_end := getattr(nextmessage, "delta", None)) is not None
                    and (content_end := getattr(delta_end, "content", None)) is not None
                    and isinstance(content_end, str)
                ):
                    logger.debug(f"OpenAILLM._tokenstream_of yields {content_end}")
                    yield content_end
                if (finish_reason := getattr(nextmessage, "finish_reason", None)) is None:
                    logger.debug("No finish_reason, retrieving next chunk.")
                    nextmessage = next(chunkstream).choices[0]
                elif finish_reason == 'stop':
                    logger.debug("finish_reason=stop")
                    break
                else:
                    raise LLMBlockzException(f"Raw stream yielded finish_reason = {finish_reason}")
            except StopIteration:
                raise LLMBlockzException(
                    "Raw stream came to an end in OpenAILLM._tokenstream_of without first seeing finish_reason = 'stop'"
                )
        logger.debug("Proper finish_reason received, emptying stream.")
        for _ in chunkstream:
            pass

    def _update_tool_call_item(self, toolcallfragment: Any, collection: dict[int, Any]) -> None:
        if (indexval := getattr(toolcallfragment, "index", None)) is None:
            raise LLMBlockzException(f"OpenAILLM._update_tool_call_item received fragment with no index")
        index: int = int(indexval)
        if index not in collection:
            collection[index] = {"argl": []}
        if (id_end := getattr(toolcallfragment, "id", None)) is not None:
            collection[index]["call_id"] = id_end
        if (function_end := getattr(toolcallfragment, "function", None)) is not None:
            if (name_end := getattr(function_end, "name", None)) is not None:
                collection[index]["name"] = name_end
            if (arguments_end := getattr(function_end, "arguments", None)) is not None:
                collection[index]["argl"].append(arguments_end)

    def _calls_of(self, query: Query, chunkstream: Iterator[Any], firstmessage: Any) -> list[SingleToolCall]:
        """Reads, assembles and returns a list of singletoolcalls. Completely consumes chunkstream in the process"""
        collection: dict[int, dict[str, Any]] = dict()
        nextmessage: Any = firstmessage
        while True:
            try:
                if (delta_end := getattr(nextmessage, "delta", None)) is not None and (
                    toolcalls_end := getattr(delta_end, "tool_calls", None)
                ) is not None:
                    for toolcallfragment in toolcalls_end:
                        self._update_tool_call_item(toolcallfragment, collection)
                if (finish_reason := getattr(nextmessage, "finish_reason", None)) is None:
                    nextmessage = next(chunkstream).choices[0]
                elif finish_reason == "tool_calls":
                    break
                else:
                    raise LLMBlockzException(f"Raw stream yielded finish_reason = {finish_reason}")
            except StopIteration:
                raise LLMBlockzException(
                    "Raw stream came to an end in OpenAILLM._toolcalls_of without first seeing finish_reason = 'tool_calls'"
                )
        for _ in chunkstream:
            pass
        calls: list[SingleToolCall] = []
        for call in collection.values():
            if "call_id" not in call or "name" not in call or "argl" not in call:
                raise LLMBlockzException(f"call in OpenAILLM._toolcalls_of is missing a required field")
            calls.append(SingleToolCall(call["call_id"], call["name"], json.loads("".join(call["argl"]))))
        if not valid_tools_against_calls(query.tools(), calls):
            raise LLMBlockzException("LLM returned tool calls that do not match the tool declarations")
        return calls

    def streamstep(self, query: Query, temperature: float | None = None, model: str | None = None, **kwargs: Any) -> StreamingReply:
        temperature, model, _toolfunction, _cycle_limit = self._resolve_named_parameters(temperature, model, None, None)
        logger.debug(
            f"OpenAILikeLLM.streamstep() called with temperature={temperature}, model={model}, extra arguments={kwargs}\nQuery={query}"
        )
        tools = self._format_tools_of(query)
        if self._can_stream:
            chunkstream = self._client.chat.completions.create(
                model=model,
                messages=self._format_messages_of(query),
                temperature=temperature,
                stream=True,
                **{**({"tools": tools} if len(tools) > 0 else {}), **kwargs},
            )
            while True:
                firstmessage: Any = next(chunkstream).choices[0]
                if (delta_end := getattr(firstmessage, "delta", None)) is None:
                    raise LLMBlockzException("Streamed message has no 'delta' field")
                if getattr(delta_end, "tool_calls", None) is not None:
                    return StreamingToolCallsReply(query, lambda: self._calls_of(query, chunkstream, firstmessage))
                if (content_end := getattr(delta_end, "content", None)) is not None and content_end != '':
                    return StreamingTextReply(query, self._tokenstream_of(chunkstream, firstmessage))
                if (finish_reason := getattr(delta_end, "finish_reason", None)) is None:
                    continue
                else:
                    raise LLMBlockzException(f"Message stream reached finish_reason = {finish_reason} without any content")
        else:
            essence: str | list[SingleToolCall] = self._step(query, temperature, model, **kwargs)
            if isinstance(essence, str):
                return StreamingTextReply.of_text(query, essence)
            else:  # isinstance(essence,list):
                return StreamingToolCallsReply.of_calls(query, essence)

    def answer(
        self,
        query: Query,
        temperature: float | None = None,
        model: str | None = None,
        toolfunction: ToolFunction | None = None,
        cycle_limit: int | None = None,
        **kwargs: Any,
    ) -> TextReply:
        """Overridden only to provide defaults."""
        temperature, model, toolfunction, cycle_limit = self._resolve_named_parameters(temperature, model, toolfunction, cycle_limit)
        logger.info(f"Calling model {model}, in normal mode, with query {query.last_message()}")
        logger.debug(f"Toolfunction={toolfunction.__qualname__}, cycle_limit={cycle_limit}")
        return super().answer(query, temperature, model, toolfunction, cycle_limit, **kwargs)

    def streamanswer(
        self,
        query: Query,
        temperature: float | None = None,
        model: str | None = None,
        toolfunction: ToolFunction | None = None,
        cycle_limit: int | None = None,
        **kwargs: Any,
    ) -> StreamingTextReply:
        temperature, model, toolfunction, cycle_limit = self._resolve_named_parameters(temperature, model, toolfunction, cycle_limit)
        logger.info(f"Calling model {model}, in streaming mode, with query {query.last_message()}")
        logger.debug(f"ToolFunction={toolfunction.__qualname__}, cycle_limit={cycle_limit}")
        return super().streamanswer(query, temperature, model, toolfunction, cycle_limit, **kwargs)


# class OpenAIEmbedding(Embedding):
