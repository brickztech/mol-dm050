import logging

import pandas as pd
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy
from tabulate import tabulate

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)


def read_ddl(name: str):
    content = ""
    with open(f'redmine/{name}_ddl.sql', 'r') as file:
        for line in file:
            content += line.strip()
    return content


def inspect_tables_structure(table_name: str | None = None) -> str:
    if table_name:
        return read_ddl(table_name)
    else:
        return read_ddl("issues") + "\n" + read_ddl("projects") + "\n" + read_ddl("users") + "\n" + read_ddl("time_entries")


class ExecutionContext:
    def __init__(self, variables: dict[str, object], domain_description: str):
        self.variables = variables
        self.domain_description = domain_description

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
        if result is not None and not isinstance(result, pd.DataFrame) and not isinstance(result, DataFrameGroupBy):
            return str(result)
        if isinstance(result, pd.DataFrame):
            if not result.empty:
                headers: list[str] = list(result.columns)
                # tabulate expects a mapping type; convert DataFrame to a dict of columns
                result_dict = result.to_dict(orient='list')  # type: ignore
                result_text = tabulate(result_dict, headers=headers)
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
        elif isinstance(result, DataFrameGroupBy):
            if console_out:
                print(result)  # type: ignore
            return result.obj.to_html()  # type: ignore
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
        number_fields_df: DataFrame = df.select_dtypes(include=['number'])  # type: ignore
        fields: list[str] = list(number_fields_df.columns)
        for col in fields:
            if not pd.api.types.is_numeric_dtype(df[col]):  # type: ignore
                logging.warning(f"Column {col} contains non-numeric values.")
                return False

        return True
