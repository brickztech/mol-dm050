import logging
import os
from datetime import datetime

import pandas as pd
import psycopg
import tabulate

from langutils.context import ExecutionContext

from .open_ai import LangUtils

pd.options.display.max_columns = None


class RedmineContext(ExecutionContext):
    def __init__(self, variables: dict[str, object], domain_description: str):
        self.domain_description = """The database contains the results of time logging for various projects by the project members.

        The table 'projects' contains data describing the projects.
        Every row in the table 'projects' corresponds to a single project and every project has one row.
        Every row in the table 'projects' has an integer-valued field called 'id'. The value of this field is the unique identifier of the project described by the current row. This field is the primary key of the table.
        Every row in the table 'projects' has a string-valued field called 'name'. The value of this field is the name of the project described by the current row.
        Every row in the table 'projects' has an integer-valued field called 'parent_id'. The value of this field is the identifier of the parent project of the project described by the current row, or NULL if there is no parent project. Projects form a tree and a project that is the parent project of some other project can itself have a parent project, to an arbitrary depth.

        The table 'users' contains data describing the individual users who can access the system and log times. In addition it can store groups and technical users.
        Every row in the table 'users' corresponds to a single user and every user has one row.
        Every row in the table 'users' has an integer-valued field called 'id'. The value of this field is the unique identifier of the user described by the current row. This field is the primary key of the table.
        Every row in the table 'users' has a string-valued field called 'firstname'. The value of this field is the first name of the user described by the current row.
        Every row in the table 'users' has a string-valued field called 'lastname'. The value of this field is the last name of the user described by the current row.
        Every row in the table 'users' has a boolean-valued field called 'admin'. The value of this field is 'true' if the user is an administrator and 'false' otherwise.
        Every row in the table 'users' has an integer-valued field called 'status'. The value of this field shows whether the user in question is active or inactive. For active users this field has the value '1' and for inactive users it has the value '3'. Other values are possible, but not for regular users.
        Every row in the table 'users' has a string-valued field called 'type'. The value of this field is 'User' for regular users and something different otherwise.

        The table 'members' contains association data between projects and users. Whenever a user is a member of a project, this table will contain a row referencing both the user and the project by their respective 'id' values.
        Every row in the table 'members' has an integer-valued field called 'id'. The value of this field is the unique identifier of the association between an user and a project. This field is the primary key of the table.
        Every row in the table 'members' has an integer-valued field called 'user_id'. The value of this field is the unique identifier of the user being associated to a project by the current row. This field is a foreign key into the 'users' table.
        Every row in the table 'members' has an integer-valued field called 'project_id'. The value of this field is the unique identifier of the project being associated with an user by the current row. This field is a foreign key into the 'projects' table.

        The table 'time_entries' contains entries for times worked by a certain user on a certain project. Every time entry has its own separate row.
        Every row in the table 'time_entries' has an integer-valued field called 'id'. The value of this field is the unique identifier of the time entry. This field is the primary key of the table.
        Every row in the table 'time_entries' has an integer-valued field called 'project_id'. The value of this field is the unique identifier of the project on which the time entered in the current row was spent. This is a foreign key into the 'projects' table.
        Every row in the table 'time_entries' has an integer-valued field called 'user_id'. The value of this field is the unique identifier of the user who spent the time logged in the current row. This is a foreign key into the 'users' table.
        Every row in the table 'time_entries' has a floating point-valued field called 'hours'. The value of this field is the number of hours - possibly fractional - being logged.
        Every row in the table 'time_entries' has a date-valued field called 'spent_on', having the format YYYY-MM-DD. The value of this field is the date on which the time being logged was spent."""

        self.variables = variables

        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(f'{current_dir}/issues.csv'):
            raise FileNotFoundError("File 'issues.csv' does not exist.")

        issues = pd.read_csv(f'{current_dir}/issues.csv')
        users = pd.read_csv(f'{current_dir}/users.csv')
        users['last_login_on'] = pd.to_datetime(users['last_login_on'])
        users['created_on'] = pd.to_datetime(users['created_on'])
        users['updated_on'] = pd.to_datetime(users['updated_on'])

        # feladatok = pd.read_csv('redmine/issues.csv')
        # feladatok['due_date'] = pd.to_datetime(feladatok['due_date'])
        # feladatok['start_date'] = pd.to_datetime(feladatok['start_date'])
        # feladatok['created_on'] = pd.to_datetime(feladatok['created_on'])
        # feladatok['updated_on'] = pd.to_datetime(feladatok['updated_on'])

        projects = pd.read_csv(f'{current_dir}/projects.csv')
        projects['created_on'] = pd.to_datetime(projects['created_on'])
        projects['updated_on'] = pd.to_datetime(projects['updated_on'])

        members = pd.read_csv(f'{current_dir}/members.csv')

        time_entries = pd.read_csv(f'{current_dir}/time_entries.csv')
        time_entries['spent_on'] = pd.to_datetime(time_entries['spent_on'])
        time_entries['created_on'] = pd.to_datetime(time_entries['created_on'])
        time_entries['updated_on'] = pd.to_datetime(time_entries['updated_on'])

        # time_entries.set_index('spent_on', inplace=True)
        # self.variables['risks'] = risks_df
        self.variables['users'] = users
        self.variables['issues'] = issues
        # self.variables['feladatok'] = feladatok
        # self.variables['risk_list'] = risk_list_df
        self.variables['projects'] = projects
        self.variables['members'] = members
        self.variables['time_entries'] = time_entries

        today = datetime.now()
        self.variables['today'] = today
        first_day_last_year = datetime(today.year - 1, 1, 1)
        self.variables['first_day_last_year'] = first_day_last_year
        first_day_last_month = datetime(today.year, today.month - 1 if today.month > 1 else 12, 1)
        self.variables['first_day_of_last_month'] = first_day_last_month

    def get_domain_description(self) -> str:
        return self.domain_description

    def execute_query(self, query: str) -> list[dict[str, str]]:
        """
        Executes the given SQL query and returns the result as a list of dictionaries.
        Each dictionary represents a row with field names as keys.
        """
        if not query.strip():
            return []
        try:
            exec("import pandas as pd\n" + query, self.variables)
            result = self.variables.get("result_table", None)
            if result is None:
                print("No result_table found in the executed query.")
                return []
            else:
                return result.to_dict(orient='records')  # type: ignore
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def execute(self, code: str, console_out: bool = True) -> str | None:
        # self.test_code()
        exec("import pandas as pd\n" + code, self.variables)
        result = self.variables.get("result_table", None)
        if result is not None and not isinstance(result, pd.DataFrame):
            return str(result)
        if isinstance(result, pd.DataFrame):
            if not result.empty:
                headers: list[str] = list(result.columns)
                # tabulate expects a mapping type; convert DataFrame to a dict of columns
                result_dict = result.to_dict(orient='list')  # type: ignore
                result_text = tabulate(result_dict, headers=headers)  # type: ignore
                if console_out:
                    print("Result:\n")
                    # result_html = result.to_html()
                    print(result_text)
                    # print("Result html:\n", result_html)
                return result_text
            else:
                if console_out:
                    print("No result.")
                return None
        else:
            if console_out:
                print("result:" + str(result))
            return result

    def inspect_tables_structure(self, table_name: str | None = None) -> str:
        var_keys = self.variables.keys()
        description = ""
        for key in var_keys:
            variable: object = self.variables[key]
            if isinstance(variable, pd.DataFrame):
                description += f"\nDataframe {key} has the following columns: "
                cols: list[str] = list(variable.columns)
                for col in cols:
                    if variable[col].dtype != "object":  # type: ignore
                        description += f" {col} type is {str(variable.dtype)},"  # type: ignore
                    else:
                        description += f" {col},"
        return description

    def validate(self):
        for key, value in self.variables.items():
            logging.info(f'Validating {key}')
            if isinstance(value, pd.DataFrame):
                if not self.validate_dataframe(value):
                    logging.info(f"Validation failed for {key} DataFrame.")
                    return False
            else:
                logging.info(f"Variable {key} is not a DataFrame.")
        return True

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> bool:
        # Check if the DataFrame is empty
        if df.empty:
            logging.warning("DataFrame is empty.")
            return False

        # Check for NaN values
        # if df.isnull().values.any():
        #    print("DataFrame contains NaN values.")
        #    return False

        # Check for duplicate rows
        if df.duplicated().any():  # type: ignore
            logging.warning("DataFrame contains duplicate rows.")
            return False

        # Check for non-numeric values in numeric columns
        number_fields_df: pd.DataFrame = df.select_dtypes(include=['number'])  # type: ignore
        fields: list[str] = list(number_fields_df.columns)
        for col in fields:
            if not pd.api.types.is_numeric_dtype(df[col]):  # type: ignore
                logging.warning(f"Column {col} contains non-numeric values.")
                return False

        return True


def init_context() -> RedmineContext:
    context = RedmineContext(dict(), "")
    LangUtils.system_instruction_for_query = f"""
        You are a programmer working on reporting tasks.
        The reports all come from a database realized as a collection of pandas dataframes.
        {context.get_domain_description()}
        When you need information about all the available tables in the database use the "get_tables" function.
        When you need information about a particular table in the database use the "describe_table" function.
        This function will return the table structure and the connections to other tables.
        When this function return "unknown" text it means that the table is not known, it is not in the database.
        If you don't have information about a particular table, don't try to guess or generate something. Return back a response which says that you don't know that object.
        When you are asked to execute a query, you have to use the "execute_query" function.
        "execute_query" function takes panda queries as text input and executes them on the database. The query has to save the output to "result_table" variable. The result will be returned as tab separated table.
        Consider that the user interface is in Hungarian and it is a HTML interface. Format the output to HTML or keep the original formatting received by the tools if it is in HTML format.
        If you are returning images returned it in the following format: (attachment://<name of the picture>)
    """

    LangUtils.prompt_prefix_for_query = """
        The question is the following:
    """
    context.validate()

    return context


class RedmineSQLContext(RedmineContext):

    def open_connection(self) -> psycopg.Connection:
        con = psycopg.connect(
            host=os.getenv('PGHOST', 'localhost'),
            port=os.getenv('PGPORT', '5432'),
            dbname=os.getenv('PGDATABASE', 'redmine'),
            user=os.getenv('PGUSER', 'postgres'),
            password=os.getenv('PGPASSWORD', 'password'),
        )
        con.autocommit = True
        return con

    def execute_query(self, query: str) -> list[dict]:
        conn = self.open_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)  # pyright: ignore[reportArgumentType]
            result = cursor.fetchall()
            description = cursor.description
            if description is None:
                return []
            columns = [desc[0] for desc in description]
            result = [dict(zip(columns, row)) for row in result]
            return result
        finally:
            cursor.close()
            conn.close()


def init_sql_context() -> RedmineSQLContext:
    context = RedmineSQLContext(dict(), "")
    LangUtils.system_instruction_for_query = f"""
        You are a programmer working on reporting tasks.
        The reports all come from a postgreSQL database.
        {context.get_domain_description()}
        When you need information about all the available tables in the database use the "get_tables" function.
        When you need information about a particular table in the database use the "describe_table" function.
        This function will return the table structure and the connections to other tables.
        When this function returns "unknown" text, it means that the table is not known, it is not in the database.
        If you don't have information about a particular table, don't try to guess or generate something. Return back a response which says that you don't know that object.
        When you are asked to execute a query, you have to use the "execute_query" function.
        "execute_query" function takes postgres SQL queries as text input and executes them on the database. The result will be returned as tab separated table.
        Consider that the user interface is in Hungarian and it is a HTML interface. Format the output to HTML or keep the original formatting received by the tools if it is in HTML format.
        If you are returning images returned it in the following format: (attachment://<name of the picture>)
    """

    LangUtils.prompt_prefix_for_query = """
        The question is the following:
    """
    context.validate()

    return context


# removed hints
# When you are indexing columns never use the table name for prefix. For example instead of felhasznalok.firstname use firstname or instead of 'projektek.name' user name.
