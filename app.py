import streamlit as st
import pandas as pd

st.set_page_config(page_title="Horror Generator", layout="centered")

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv("horror_data.csv")

# Clean numeric columns
df["Runtime"] = pd.to_numeric(df["Runtime"], errors="coerce")
df["Vote Avg"] = pd.to_numeric(df["Vote Avg"], errors="coerce")
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

st.title("🎬 Horror Movie Generator")

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
        "Select Genres",
        genre_list,
        default=[]
    )
else:
    genres_selected = []

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
# SEARCH BAR (MOVED TO LAST)
# ----------------------------
query = st.text_input("Search title, director, or overview")

# ----------------------------
# FILTER DATA
# ----------------------------
filtered = df.copy()

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

# Search filter (APPLIED LAST logically)
if query:
    filtered = filtered[
        filtered["Title"].fillna("").str.contains(query, case=False, na=False) |
        filtered["Director"].fillna("").str.contains(query, case=False, na=False) |
        filtered["Overview"].fillna("").str.contains(query, case=False, na=False)
    ]

st.write(f"🎥 {len(filtered)} movies match your filters")

# ----------------------------
# RANDOM PICK
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
