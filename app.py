import streamlit as st
import pandas as pd

df = pd.read_csv("/content/horror_data.csv")

df["Runtime"] = pd.to_numeric(df["Runtime"], errors="coerce")
df["Vote Avg"] = pd.to_numeric(df["Vote Avg"], errors="coerce")

st.title("🎬 Horror Movie Generator")

# ---- COUNTRY DROPDOWN ----
countries = (
    df["Country"]
    .dropna()
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
    .unique()
)

country = st.selectbox("Country", ["All"] + sorted(countries))

min_runtime = st.slider("Minimum runtime", 0, 200, 70)

filtered = df.copy()

if country != "All":
    filtered = filtered[
        filtered["Country"].astype(str).str.contains(country, case=False, na=False)
    ]

filtered = filtered[filtered["Runtime"] >= min_runtime]

st.write(f"{len(filtered)} movies available")

# ---- RANDOM PICK ----
if st.button("🎲 Random Horror Movie"):
    if len(filtered) == 0:
        st.warning("No matches")
    else:
        row = filtered.sample(1).iloc[0]

        st.subheader(row["Title"])
        st.write(f"{row['Year']} | {row['Runtime']} min")
        st.write(f"Director: {row['Director']}")
        st.write(f"Country: {row['Country']}")
        st.write(f"Rating: {row['Vote Avg']}")

        st.write(row["Overview"])

        if pd.notna(row["Poster"]):
            st.image(row["Poster"])

        st.markdown(f"[Letterboxd Link]({row['Letterboxd URL']})")
