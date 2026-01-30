import duckdb

def safe_numeric_expr(column_name: str) -> str:
    """
    Always cast metric to DOUBLE to avoid SUM(VARCHAR) errors.
    """
    return f'TRY_CAST({column_name} AS DOUBLE)'



def quote_identifier(identifier: str) -> str:
    return f'"{identifier}"'


def build_sql_query(intent: dict, table_name: str = "sales") -> str:
    # ---------- Guard ----------
    if intent.get("metric") is None:
        raise ValueError("No numeric metric available for aggregation.")

    aggregation = intent["aggregation"]
    group_by = intent.get("group_by", [])
    filters = intent.get("filters", {})
    # --------------------------------------------------
    # DEFENSIVE GUARD: remove logical time filters
    # --------------------------------------------------
    date_fields = intent.get("time_fields", [])

    if not date_fields:
        filters = {
            k: v for k, v in filters.items()
            if k not in ["year", "quarter", "month"]
        }
    # ---------- Metric ----------
    raw_metric = quote_identifier(intent["metric"])
    metric_expr = safe_numeric_expr(raw_metric)

    # ---------- SELECT ----------
    if aggregation == "sum":
        select_expr = f"SUM({metric_expr}) AS value"
    elif aggregation == "avg":
        select_expr = f"AVG({metric_expr}) AS value"
    elif aggregation == "count":
        select_expr = f"COUNT({raw_metric}) AS value"
    else:
        raise ValueError(f"Unsupported aggregation: {aggregation}")

    quoted_group_by = [quote_identifier(col) for col in group_by]

    select_clause = (
        ", ".join(quoted_group_by) + ", " + select_expr
        if quoted_group_by else select_expr
    )

    # ---------- WHERE ----------
    where_clauses = []

    date_fields = intent.get("time_fields") or []
    date_column = (
        quote_identifier(date_fields[0])
        if date_fields else None
    )

    for col, val in filters.items():
        if col in ["year", "quarter", "month"] and date_column:
            time_sql = resolve_time_filter(col, val, date_column)
            if time_sql:
                where_clauses.append(time_sql)
        else:
            where_clauses.append(f"{quote_identifier(col)} = '{val}'")

    for col in group_by:
        where_clauses.append(f"{quote_identifier(col)} IS NOT NULL")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # ---------- GROUP BY ----------
    group_by_sql = (
        "GROUP BY " + ", ".join(quoted_group_by)
        if quoted_group_by else ""
    )

    # ---------- HAVING ----------
    having_sql = ""
    if quoted_group_by and aggregation in ["sum", "avg"]:
        having_sql = f"HAVING SUM({metric_expr}) > 0"

    # ---------- ORDER / LIMIT ----------
    order_sql = ""
    limit_sql = ""

    if intent.get("order_by") == "value":
        order_sql = f"ORDER BY value {intent.get('order_direction', 'ASC')}"

    if intent.get("limit"):
        limit_sql = f"LIMIT {intent['limit']}"

    sql = f"""
    SELECT {select_clause}
    FROM {table_name}
    {where_sql}
    {group_by_sql}
    {having_sql}
    {order_sql}
    {limit_sql}
    """

    return sql.strip()


def execute_query(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql).fetchdf()

def resolve_time_filter(col, val, date_column):
    """
    Convert logical time filters (year, quarter, month)
    into SQL expressions using a real date column.
    """
    if col == "year":
        return f"EXTRACT(YEAR FROM {date_column}) = {val}"

    if col == "quarter":
        q = val.upper().replace("Q", "")
        return f"EXTRACT(QUARTER FROM {date_column}) = {q}"

    if col == "month":
        return f"EXTRACT(MONTH FROM {date_column}) = {val}"

    return None