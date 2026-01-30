import duckdb
import pandas as pd




def create_duckdb_connection(df: pd.DataFrame):
    con = duckdb.connect(database=":memory:")
    con.register("sales", df)
    return con

