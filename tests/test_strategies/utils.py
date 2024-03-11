def normalize_sql(query: str):
    return str(query).replace('\n', '').replace('  ', '').strip()
