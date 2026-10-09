from decimal import Decimal

import pandas as pd
import hashlib
import math

def make_region(row):
    if pd.isna(row["region_1"]) or row["province"] == row["region_1"]:
        return row["province"]
    return f"{row['province']}, {row['region_1']}"

# Version 1
def make_embedding_text_v1(row):
    return f"""
        Title: {row['title']}
        Country: {row['country']}
        Region: {row['region']}
        Variety: {row['variety']}
        Winery: {row['winery']}
        Designation: {row['designation']}
        Description: {row['description']}
        """.strip()

def make_final_df(df):
    # Make new region column (concatenation of region_1 + province)
    df["region"] = df.apply(make_region, axis=1)
    # Format data into input text
    df["embedding_text"] = df.apply(make_embedding_text_v1, axis=1)
    # Select columns
    df = df[['source_id', 'title', 'description', 'region', 'country', 'designation', 'points', 'price', 'variety', 'winery', "embedding_text"]]
    return df
        
def make_content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def make_embedding_df(
        batch_df,
        embeddings,
        embedding_model,
        embedding_template_version,
    ):
        embedding_df = pd.DataFrame({
            "source_id": batch_df["source_id"].values,
            "embedding": list(embeddings),
            "embedding_model": embedding_model,
            "embedding_template_version": embedding_template_version,
            "content_hash": batch_df["embedding_text"].apply(
                make_content_hash
            ).values,
        })

        return embedding_df

def clean_value(value):
    if value is None:
        return None

    if isinstance(value, Decimal):
        if not value.is_finite():
            return None
        return float(value)

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value