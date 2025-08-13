import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from tabulate import tabulate
from pandas import DataFrame

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)


def read_ddl(name: str):
    content = ""
    with open(f'redmine/{name}_ddl.sql', 'r') as file:
        for line in file:
            content += line.strip()
    return content


def inspect_tables_structure(table_name: str = None) -> str:
    if table_name:
        return read_ddl(table_name)
    else:
        return read_ddl("issues") + "\n" + read_ddl("projects") + "\n" + read_ddl(
            "users") + "\n" + read_ddl("time_entries")



class ExecutionContext:
    def __init__(self, variables: dict, domain_description: str = None):
        self.variables = variables
        self.domain_description = domain_description
    def get_domain_description(self) -> str:
        return self.domain_description
    def test_code(self):
        users = self.variables["users"]
        issues = self.variables["issues"]
        # user7_id = users[users['login'] == 'user7']['id'].iloc[0]
        # result_table = issues[issues['assigned_to_id'] == user7_id]

        user_id = users[users['login'] == 'user6']['id'].iloc[0]
        issues_user6 = issues[issues['assigned_to_id'] == user_id]
        (issues_user6['created_on'].dt.date.value_counts().sort_index().reset_index().
         rename(columns={'index': 'date', 'created_on': 'issue_count'}).to_csv(sep='\\t', index=False))
        result_table = issues_user6[['id', 'subject', 'created_on']]
        result_table['created_on'] = result_table['created_on'].dt.date
        result_table = result_table.groupby('created_on').agg({'id': 'count'}).rename(
            columns={'id': 'issue_count'}).reset_index().rename(columns={'created_on': 'date'})

    def execute(self, code: str, console_out: bool = True) -> str:
        # self.test_code()
        exec("import pandas as pd\n" + code, self.variables)
        result: DataFrame | None = self.variables.get("result_table", None)
        if isinstance(result, pd.DataFrame):

            if not result.empty:
                if console_out:
                    print("Result:\n")
                    result_html = result.to_html()
                    #print(tabulate(result, headers=result.columns))
                    print("Result html:\n", result_html)
                return result_html
            else:
                if console_out:
                    print("No result.")
                return None
        elif isinstance(result, DataFrameGroupBy):
            if console_out:
                print(result)
            return result
        else:
            if console_out:
                print("result:" + str(result))
            return result

    def inspect_tables_structure(self, table_name: str = None) -> str:
        var_keys = self.variables.keys()
        description = ""
        for key in var_keys:
            if isinstance(self.variables[key], pd.DataFrame):
                description += f"\nDataframe {key} has the following columns: "
                cols = list(self.variables[key].columns)
                for col in cols:
                    if self.variables[key][col].dtype != "object":
                        description += f" {col} type is {self.variables[key][col].dtype},"
                    else:
                        description += f" {col},"
        return description

    def validate(self):
        for key, value in self.variables.items():
            print('Validating', key)
            if isinstance(value, pd.DataFrame):
                if not self.validate_dataframe(value):
                    print(f"Validation failed for {key} DataFrame.")
                    return False
            else:
                print(f"Variable {key} is not a DataFrame.")
        return True

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> bool:
        # Check if the DataFrame is empty
        if df.empty:
            print("DataFrame is empty.")
            return False

        # Check for NaN values
        # if df.isnull().values.any():
        #    print("DataFrame contains NaN values.")
        #    return False

        # Check for duplicate rows
        if df.duplicated().any():
            print("DataFrame contains duplicate rows.")
            return False

        # Check for non-numeric values in numeric columns
        for col in df.select_dtypes(include=['number']).columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"Column {col} contains non-numeric values.")
                return False

        return True
