import pandas as pd

def make_region(row):
    if pd.isna(row["region_1"]) or row["province"] == row["region_1"]:
        return row["province"]
    return f"{row['province']}, {row['region_1']}"

def make_embedding_text(row):
    return f"""
        Title: {row['title']}
        Country: {row['country']}
        Region: {row['region']}
        Variety: {row['variety']}
        Winery: {row['winery']}
        Designation: {row['designation']}
        Description: {row['description']}
        """.strip()