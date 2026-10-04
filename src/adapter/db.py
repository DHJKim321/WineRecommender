import logging

logger = logging.getLogger(__name__)

class PostgresAdapter:
    
    def __init__(self, db_url):
        self.db_url = db_url
        logger.info(f"Set database url to {db_url}")
        
    def create_staging_table(self, conn):
        logger.info("Creating staging table")
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
                    winery TEXT,
        
                    embedding VECTOR(768)
                ) ON COMMIT DROP;
                """
            )

    def copy_into_staging_table(self, conn, df, embeddings):
        logger.info("Copying into staging table")
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
                    winery,
                    embedding
                )
                FROM STDIN
            """) as copy:

                for row, embedding in zip(
                    df.itertuples(index=False),
                    embeddings
                ):
                    vector = "[" + ",".join(map(str, embedding)) + "]"
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
                        vector,
                    ))
                    
    def upsert_into_table(self, conn):
        # Upsert from staging table
        logger.info("Upserting from staging table")
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
                    winery,
                    embedding
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
                    winery,
                    embedding
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
                    winery = EXCLUDED.winery,
                    embedding = EXCLUDED.embedding;
            """)
