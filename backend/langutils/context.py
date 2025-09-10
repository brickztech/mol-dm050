import os
from abc import ABC, abstractmethod

import pandas as pd
import psycopg

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


class ExecutionContext(ABC):

    @abstractmethod
    def execute_query(self, query: str) -> list[dict[str, str]]:
        pass


class SQLContext(ExecutionContext):

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
