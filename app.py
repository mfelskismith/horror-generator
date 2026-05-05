import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="Horror Generator", layout="centered")

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv("horror_data.csv")

# Clean numeric columns
df["Runtime"] = pd.to_numeric(df["Runtime"], errors="coerce")
df["Vote Avg"] = pd.to_numeric(df["Vote Avg"], errors="coerce")
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

# ----------------------------
# SEMANTIC MODEL (cached)
# ----------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ----------------------------
# BUILD SEARCH TEXT
# ----------------------------
df["search_text"] = (
    df["Title"].fillna("") + " " +
    df["Director"].fillna("") + " " +
    df["Overview"].fillna("") + " " +
    df.get("Genres", "").fillna("")
)

# ----------------------------
# PRECOMPUTE EMBEDDINGS (cached)
# ----------------------------
@st.cache_data
def compute_embeddings(texts):
    return model.encode(texts, show_progress_bar=True)

embeddings = compute_embeddings(df["search_text"].tolist())

# ----------------------------
# TITLE
# ----------------------------
st.markdown("# 🎬💀 Random Horror Movie Generator")

# ----------------------------
# COUNTRY FILTER
# ----------------------------
country_series = (
    df["Country"]
    .dropna()
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
)

country_list = sorted(country_series[country_series != ""].unique())

countries_selected = st.multiselect(
    "Select Countries",
    country_list,
    default=[]
)

# ----------------------------
# YEAR FILTER
# ----------------------------
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

year_range = st.slider(
    "Release Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# ----------------------------
# OTHER FILTERS
# ----------------------------
min_runtime = st.slider("Minimum runtime (minutes)", 0, 200, 70)
min_rating = st.slider("Minimum rating", 0.0, 10.0, 0.0)

# ----------------------------
# GENRE FILTER
# ----------------------------
if "Genres" in df.columns:
    genre_series = (
        df["Genres"]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
    )

    genre_list = sorted(genre_series[genre_series != ""].unique())

    genres_selected = st.multiselect(
        "Select Secondary Genres",
        genre_list,
        default=[]
    )
else:
    genres_selected = []

# ----------------------------
# SEARCH BAR (SEMANTIC)
# ----------------------------
query = st.text_input("Search movies (semantic search)")

# ----------------------------
# SEMANTIC RANKING
# ----------------------------
filtered = df.copy()

if query:
    query_vec = model.encode([query])[0]

    sims = np.dot(embeddings, query_vec) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
    )

    filtered["score"] = sims

    # keep top candidates for performance
    filtered = filtered.sort_values("score", ascending=False).head(500)

# ----------------------------
# APPLY FILTERS
# ----------------------------

# Country filter
if countries_selected:
    filtered = filtered[
        filtered["Country"]
        .fillna("")
        .astype(str)
        .apply(lambda x: any(c in x for c in countries_selected))
    ]

# Genre filter
if genres_selected and "Genres" in df.columns:
    filtered = filtered[
        filtered["Genres"]
        .fillna("")
        .astype(str)
        .apply(lambda x: any(g in x for g in genres_selected))
    ]

# Year filter
filtered = filtered[
    (filtered["Year"] >= year_range[0]) &
    (filtered["Year"] <= year_range[1])
]

# Runtime + rating filters
filtered = filtered[filtered["Runtime"] >= min_runtime]
filtered = filtered[filtered["Vote Avg"] >= min_rating]

# ----------------------------
# OUTPUT COUNT
# ----------------------------
st.write(f"🎥 {len(filtered)} movies match your filters")

# ----------------------------
# RANDOM PICK (FROM RANKED SET)
# ----------------------------
if st.button("🎲 Pick Random Horror Movie"):
    if len(filtered) == 0:
        st.warning("No movies match your filters.")
    else:
        row = filtered.sample(1).iloc[0]

        st.subheader(row["Title"])
        st.write(f"**Year:** {row['Year']}")
        st.write(f"**Runtime:** {row['Runtime']} min")
        st.write(f"**Director:** {row['Director']}")
        st.write(f"**Country:** {row['Country']}")

        if "Genres" in df.columns:
            st.write(f"**Genres:** {row['Genres']}")

        st.write(f"**Rating:** {row['Vote Avg']}")
        st.write(row["Overview"])

        if pd.notna(row["Poster"]):
            st.image(row["Poster"])

        st.markdown(f"[🔗 Letterboxd Link]({row['Letterboxd URL']})")
