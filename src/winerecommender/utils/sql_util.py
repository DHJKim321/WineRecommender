from winerecommender.models.attributes import WineQueryFilter


def build_sql_params(query_vector: str, top_n: int, filter_params: WineQueryFilter):
    conditions = []
    params: list[object] = [query_vector]
    text_fields = {
        "region": filter_params.region,
        "country": filter_params.country,
        "designation": filter_params.designation,
        "variety": filter_params.variety,
        "winery": filter_params.winery,
    }
    
    # For text fields
    for field, values in text_fields:
        if values:
            conditions.append(f"w.{field} ANY %s")
            params.append(values)
            
    # For numerical fields
    for field, bounds in (
        ("points", filter_params.points),
        ("price", filter_params.price)
    ):
        if bounds.min is not None:
            conditions.append(f"%s <= w.{field}")
            params.append(bounds.min)
            
        if bounds.max is not None:
            conditions.append(f"w.{field} <= %s")
            params.append(bounds.max)
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
        
    # Used to retrieve top N reviews
    params.append(top_n)
    sql = f"""
        SELECT
            w.source_id,
            w.title,
            w.description,
            w.region,
            w.country,
            w.designation,
            w.points,
            w.price,
            w.variety,
            w.winery,
            e.embedding,
            e.embedding <=> %s::vector AS distance
        FROM wines AS w
        JOIN embeddings AS e
            ON w.source_id = e.source_id
        {where_clause}
        ORDER BY distance ASC
        LIMIT %s
        """,
    return sql, params