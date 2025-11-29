import pandas as pd

from . import get_connection


def get_table_df(table_name: str) -> pd.DataFrame:
    """Return the full contents of a table as a DataFrame."""
    conn = get_connection()
    return pd.read_sql(f"SELECT * FROM {table_name}", conn)
