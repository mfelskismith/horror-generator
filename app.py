import streamlit as st
import pandas as pd

st.set_page_config(page_title="Horror Generator", layout="centered")

# ----------------------------
# LOAD DATA (Streamlit Cloud safe path)
# ----------------------------
df = pd.read_csv("horror_data.csv")

# Clean numeric columns
df["Runtime"] = pd.to_numeric(df["Runtime"], errors="coerce")
df["Vote Avg"] = pd.to_numeric(df["Vote Avg"], errors="coerce")

st.title("🎬 Horror Movie Generator")

# ----------------------------
# BUILD COUNTRY LIST
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

# Multi-select countries
countries_selected = st.multiselect(
    "Select Countries",
    country_list,
    default=[]
)

# Runtime filter
min_runtime = st.slider("Minimum runtime (minutes)", 0, 200, 70)

# Optional rating filter
min_rating = st.slider("Minimum rating", 0.0, 10.0, 0.0)

# ----------------------------
# FILTER DATA
# ----------------------------
filtered = df.copy()

if countries_selected:
    filtered = filtered[
        filtered["Country"].astype(str).apply(
            lambda x: any(c in x for c in countries_selected)
        )
    ]

filtered = filtered[filtered["Runtime"] >= min_runtime]
filtered = filtered[filtered["Vote Avg"] >= min_rating]

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
        st.write(f"**Rating:** {row['Vote Avg']}")

        st.write(row["Overview"])

        if pd.notna(row["Poster"]):
            st.image(row["Poster"])

        st.markdown(f"[🔗 Letterboxd Link]({row['Letterboxd URL']})")
