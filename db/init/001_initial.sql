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
    winery TEXT
);

CREATE TABLE IF NOT EXISTS embeddings (
    source_id BIGINT PRIMARY KEY REFERENCES wines(source_id),

    embedding VECTOR(768),
    embedding_model TEXT,
    embedding_template_version TEXT,
    content_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS embeddings_vector_idx
ON embeddings
USING hnsw (embedding vector_cosine_ops);
