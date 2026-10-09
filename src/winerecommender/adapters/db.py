import logging

logger = logging.getLogger(__name__)

class PostgresAdapter:
    
    def __init__(self, db_url):
        self.db_url = db_url
        logger.info(f"Set database url to {db_url}")
        
    def create_staging_tables(self, conn):
        logger.info("Creating staging tables")
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TEMP TABLE staging_wines (
                    source_id BIGINT PRIMARY KEY,
        
                    title TEXT,
                    description TEXT,
                    region TEXT,
                    country TEXT,
                    designation TEXT,
                    points INTEGER,
                    price NUMERIC,
                    variety TEXT,
                    winery TEXT
                );
                
                CREATE TEMP TABLE staging_embeddings (
                    source_id BIGINT PRIMARY KEY REFERENCES staging_wines(source_id),

                    embedding VECTOR(768),
                    embedding_model TEXT,
                    embedding_template_version INTEGER,
                    content_hash TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )

    def copy_into_wines_staging_table(self, conn, df):
        # logger.info("Copying into wine staging table")
        with conn.cursor() as cur:
            with cur.copy("""
                COPY staging_wines (
                    source_id,
                    title,
                    description,
                    region,
                    country,
                    designation,
                    points,
                    price,
                    variety,
                    winery
                )
                FROM STDIN;
            """) as copy:

                for row in df.itertuples(index=False):
                    copy.write_row((
                        row.source_id,
                        row.title,
                        row.description,
                        row.region,
                        row.country,
                        row.designation,
                        row.points,
                        row.price,
                        row.variety,
                        row.winery,
                    ))
                    
    def copy_into_embeddings_staging_table(self, conn, df):
        # logger.info("Copying into embeddings staging table")
        with conn.cursor() as cur:
            with cur.copy("""
                COPY staging_embeddings (
                    source_id,
                    embedding,
                    embedding_model,
                    embedding_template_version,
                    content_hash
                )
                FROM STDIN
            """) as copy:

                for row in df.itertuples(index=False):
                    vector = "[" + ",".join(map(str, row.embedding)) + "]"
                    copy.write_row((
                        row.source_id,
                        vector,
                        row.embedding_model,
                        row.embedding_template_version,
                        row.content_hash,
                    ))
                    
    def clear_staging_tables(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
                TRUNCATE TABLE staging_embeddings, staging_wines;
            """)
                    
    def upsert_into_wines_table(self, conn):
        # Upsert from staging table
        # logger.info("Upserting into wines from staging table")
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO wines (
                    source_id,
                    title,
                    description,
                    region,
                    country,
                    designation,
                    points,
                    price,
                    variety,
                    winery
                )
                SELECT
                    source_id,
                    title,
                    description,
                    region,
                    country,
                    designation,
                    points,
                    price,
                    variety,
                    winery
                FROM staging_wines

                ON CONFLICT (source_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    region = EXCLUDED.region,
                    country = EXCLUDED.country,
                    designation = EXCLUDED.designation,
                    points = EXCLUDED.points,
                    price = EXCLUDED.price,
                    variety = EXCLUDED.variety,
                    winery = EXCLUDED.winery
            """)
                    
    def upsert_into_embeddings_table(self, conn):
        # Upsert from staging table
        # logger.info("Upserting into embeddings from staging table")
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO embeddings (
                    source_id,
                    embedding,
                    embedding_model,
                    embedding_template_version,
                    content_hash
                )
                SELECT
                    source_id,
                    embedding,
                    embedding_model,
                    embedding_template_version,
                    content_hash
                FROM staging_embeddings

                ON CONFLICT (source_id)
                DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    embedding_model = EXCLUDED.embedding_model,
                    embedding_template_version = EXCLUDED.embedding_template_version,
                    content_hash = EXCLUDED.content_hash
            """)
            
    def get_top_candidates(self, conn, query_embedding, top_n):
        query_vector = "[" + ",".join(map(str, query_embedding)) + "]"
        with conn.cursor() as cur:
            cur.execute("""
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
                    e.embedding
                    e.embedding <=> %s::vector AS distance
                FROM wines AS w
                JOIN embeddings AS e
                    ON w.source_id = e.source_id
                ORDER BY e.embedding <=> %s::vector
                LIMIT %s
                """,
                (query_vector, query_vector, top_n),
            )
            return cur.fetchall()
