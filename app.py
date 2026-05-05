import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Horror Generator", layout="centered")

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv("horror_data.csv")

# Clean numeric columns
df["Runtime"] = pd.to_numeric(df["Runtime"], errors="coerce")
df["Vote Avg"] = pd.to_numeric(df["Vote Avg"], errors="coerce")
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Vote Count"] = pd.to_numeric(df["Vote Count"], errors="coerce")

# ----------------------------
# TITLE
# ----------------------------
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown(
        """
        <div style="text-align:center; font-size:32px; font-weight:700; line-height:1.2;">
            💀 Random Horror<br>
            Movie Generator 🎬
        </div>
        """,
        unsafe_allow_html=True
    )

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
# SEARCH BAR
# ----------------------------
query = st.text_input("Search title, director, or overview")

# ----------------------------
# FILTER DATA BASE
# ----------------------------
filtered = df.copy()

if countries_selected:
    filtered = filtered[
        filtered["Country"]
        .fillna("")
        .astype(str)
        .apply(lambda x: any(c in x for c in countries_selected))
    ]

filtered = filtered[
    (filtered["Year"] >= year_range[0]) &
    (filtered["Year"] <= year_range[1])
]

filtered = filtered[filtered["Runtime"] >= min_runtime]
filtered = filtered[filtered["Vote Avg"] >= min_rating]

if genres_selected and "Genres" in df.columns:
    filtered = filtered[
        filtered["Genres"]
        .fillna("")
        .astype(str)
        .apply(lambda x: any(g in x for g in genres_selected))
    ]

# ----------------------------
# SEARCH FUNCTION
# ----------------------------
def word_match(text, query):
    if pd.isna(text) or not query:
        return False

    text = str(text).lower()
    query = query.lower().strip()

    terms = query.split()

    return all(
        re.search(rf"\b{re.escape(term)}\b", text)
        for term in terms
    )

if query:
    title_match = filtered["Title"].apply(lambda x: word_match(x, query))
    director_match = filtered["Director"].apply(lambda x: word_match(x, query))
    overview_match = filtered["Overview"].apply(lambda x: word_match(x, query))

    filtered = filtered[
        title_match |
        (director_match & ~title_match) |
        (overview_match & ~title_match & ~director_match)
    ]

# ----------------------------
# OUTPUT COUNT
# ----------------------------
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

        # NEW: vote count added here
        if pd.notna(row["Vote Count"]):
            st.write(f"**Votes:** {int(row['Vote Count'])}")
        else:
            st.write("**Votes:** N/A")

        st.write(row["Overview"])

        if pd.notna(row["Poster"]):
            st.image(row["Poster"])

        st.markdown(f"[🔗 Letterboxd Link]({row['Letterboxd URL']})")
