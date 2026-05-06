import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Horror Generator", layout="centered")

# ----------------------------
# HORROR FONT ONLY
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik+Glitch&display=swap');
</style>
""", unsafe_allow_html=True)

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv("horror_data.csv")

df["Runtime"] = pd.to_numeric(df["Runtime"], errors="coerce")
df["Vote Avg"] = pd.to_numeric(df["Vote Avg"], errors="coerce")
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Vote Count"] = pd.to_numeric(df["Vote Count"], errors="coerce")

# Normalize country field
df["Country"] = (
    df["Country"]
    .fillna("")
    .astype(str)
    .str.replace("\u00a0", " ", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# ----------------------------
# TITLE
# ----------------------------
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown(
        """
        <style>
        .main-title {
            text-align: center;
            font-size: 44px;
            font-family: 'Rubik Glitch', cursive;
            line-height: 1.1;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .main-title {
                font-size: 30px;
                line-height: 1.15;
                margin-bottom: 20px;
            }
        }
        </style>

        <div class="main-title">
            💀 Random Horror<br>
            Movie Picker 📼
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------------------
# FILTER NOTE
# ----------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center; font-size:18px; color:gray;'>All Filters Optional</p>",
    unsafe_allow_html=True
)

# ----------------------------
# HORROR / THRILLER TOGGLE
# ----------------------------
include_non_horror_thrillers = st.toggle(
    'Include "Non-Horror" Thrillers',
    value=False
)

# ----------------------------
# COUNTRY FILTER
# ----------------------------
country_series = (
    df["Country"]
    .str.split(",")
    .explode()
    .str.replace("\u00a0", " ", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

country_list = sorted(country_series[country_series != ""].unique())

if "United States of America" in country_list:
    country_list.remove("United States of America")
    country_list.insert(0, "United States of America")

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
runtime_options = list(range(0, 200)) + ["200+"]

runtime_range = st.select_slider(
    "Runtime Range (minutes)",
    options=runtime_options,
    value=(80, "200+")
)

runtime_min = runtime_range[0]
runtime_max = runtime_range[1]

runtime_max_numeric = 200 if runtime_max == "200+" else runtime_max

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
# FILTER DATA
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

# Runtime filter with 200+ behavior
if runtime_max == "200+":
    filtered = filtered[
        filtered["Runtime"].isna() |
        (filtered["Runtime"] >= runtime_min)
    ]
else:
    filtered = filtered[
        filtered["Runtime"].isna() |
        (
            (filtered["Runtime"] >= runtime_min) &
            (filtered["Runtime"] <= runtime_max_numeric)
        )
    ]

filtered = filtered[filtered["Vote Avg"] >= min_rating]

# Horror-only filter
if not include_non_horror_thrillers and "Genres" in df.columns:
    filtered = filtered[
        filtered["Genres"]
        .fillna("")
        .astype(str)
        .str.lower()
        .apply(lambda x: "horror" in [g.strip() for g in x.split(",")])
    ]

# Secondary genre filter
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
# BUTTON STYLE
# ----------------------------
st.markdown("""
<style>
div.stButton > button {
    height: 75px;
    border-radius: 12px;
    background: linear-gradient(90deg, #ff0033, #8b0000);
    color: white;
    border: none;
    box-shadow: 0 0 12px rgba(255, 0, 51, 0.5);
    transition: all 0.25s ease-in-out;
}

div.stButton > button p,
div.stButton > button span {
    font-size: 28px !important;
    font-family: 'Rubik Glitch', cursive !important;
}

@media (max-width: 768px) {
    div.stButton > button p,
    div.stButton > button span {
        font-size: 20px !important;
    }
}

div.stButton > button:hover {
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)

clicked = st.button(
    "🎲 Pick Random Horror Movie 🎲",
    use_container_width=True
)

# ----------------------------
# RANDOM PICK
# ----------------------------
if clicked:
    if len(filtered) == 0:
        st.warning("No movies match your filters.")
    else:
        row = filtered.sample(1).iloc[0]

        link = None
        if pd.notna(row["tmdb_id"]):
            link = f"https://letterboxd.com/tmdb/{int(row['tmdb_id'])}/"

        st.subheader(row["Title"])

        st.write(f"**Year:** {row['Year']}")
        st.write(f"**Runtime:** {int(row['Runtime']) if pd.notna(row['Runtime']) else 'N/A'} min")
        st.write(f"**Director:** {row['Director']}")
        st.write(f"**Country:** {row['Country']}")

        if "Genres" in df.columns:
            st.write(f"**Genres:** {row['Genres']}")

        st.write(f"**Rating:** {row['Vote Avg']}")

        if pd.notna(row["Vote Count"]):
            st.write(f"**Votes:** {int(row['Vote Count'])}")
        else:
            st.write("**Votes:** N/A")

        st.markdown(
            f"""
            <div style="
                margin-bottom:6px;
                line-height:1.4;
            ">
                {row['Overview']}
            </div>
            """,
            unsafe_allow_html=True
        )

        if link:
            st.markdown(
                f"""
                <style>
                .poster-wrapper {{
                    display: flex;
                    justify-content: center;
                    margin: 0;
                    padding: 0;
                }}

                .poster-container {{
                    position: relative;
                    display: inline-block;
                    margin: 0;
                    padding: 0;
                    line-height: 0;
                    border-radius: 10px;
                    overflow: hidden;
                }}

                .poster-img {{
                    display: block;
                    max-width: 100%;
                    height: auto;
                    border-radius: 10px;
                }}

                .poster-overlay {{
                    position: absolute;
                    inset: 0;

                    display: flex;
                    align-items: center;
                    justify-content: center;

                    background: rgba(0,0,0,0);
                    opacity: 0;

                    transition: 0.2s ease-in-out;
                }}

                .poster-container:hover .poster-overlay {{
                    background: rgba(0,0,0,0.35);
                    opacity: 1;
                }}

                .poster-label {{
                    color: white;
                    font-size: 22px;
                    font-weight: 500;
                    letter-spacing: 0.3px;
                    text-shadow: 0 2px 6px rgba(0,0,0,0.7);
                }}

                @media (hover: none) {{
                    .poster-overlay {{
                        background: rgba(0,0,0,0.28);
                        opacity: 1;
                        align-items: flex-end;
                        padding-bottom: 18px;
                    }}

                    .poster-label {{
                        background: rgba(0,0,0,0.65);
                        padding: 8px 12px;
                        border-radius: 8px;
                        font-size: 16px;
                    }}
                }}
                </style>

                <div class="poster-wrapper">
                    <div class="poster-container">
                        <a href="{link}" target="_blank" rel="noopener noreferrer">
                            <img class="poster-img" src="{row['Poster']}">
                            <div class="poster-overlay">
                                <div class="poster-label">
                                    Open on Letterboxd ↗
                                </div>
                            </div>
                        </a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.image(row["Poster"], use_container_width=True)
