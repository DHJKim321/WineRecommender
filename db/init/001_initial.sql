-- db/init/001_initial.sql

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS wines (
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
);

CREATE INDEX IF NOT EXISTS wines_embedding_idx
ON wines
USING hnsw (embedding vector_cosine_ops);
