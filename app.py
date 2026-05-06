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
        st.write(f"**Runtime:** {row['Runtime']} min")
        st.write(f"**Director:** {row['Director']}")
        st.write(f"**Country:** {row['Country']}")

        if "Genres" in df.columns:
            st.write(f"**Genres:** {row['Genres']}")

        st.write(f"**Rating:** {row['Vote Avg']}")

        if pd.notna(row["Vote Count"]):
            st.write(f"**Votes:** {int(row['Vote Count'])}")
        else:
            st.write("**Votes:** N/A")

        # ----------------------------
        # TIGHT CLICKABLE BLOCK (OVERVIEW + POSTER)
        # ----------------------------
        if link:
            st.markdown(
                f"""
                <style>
                .movie-card {{
                    margin: 0;
                    padding: 0;
                }}

                .movie-link {{
                    text-decoration: none;
                    color: inherit;
                    display: block;
                }}

                .movie-overview {{
                    margin: 0 0 6px 0;
                    line-height: 1.4;
                }}

                .poster-container {{
                    position: relative;
                    width: 100%;
                    margin: 0;
                }}

                .poster-img {{
                    width: 100%;
                    border-radius: 10px;
                    display: block;
                    margin: 0;
                    transition: transform 0.2s ease-in-out;
                }}

                .poster-container:hover .poster-img {{
                    transform: scale(1.01);
                }}

                .poster-overlay {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    border-radius: 10px;

                    background: rgba(0,0,0,0);
                    display: flex;
                    align-items: center;
                    justify-content: center;

                    opacity: 0;
                    transition: all 0.2s ease-in-out;
                }}

                .poster-container:hover .poster-overlay {{
                    background: rgba(0,0,0,0.35);
                    opacity: 1;
                }}

                .poster-label {{
                    font-size: 15px;
                    font-weight: 500;
                    color: white;
                    letter-spacing: 0.5px;
                }}
                </style>

                <div class="movie-card">
                    <a class="movie-link" href="{link}" target="_blank" rel="noopener noreferrer">

                        <div class="movie-overview">
                            {row['Overview']}
                        </div>

                        <div class="poster-container">
                            <img class="poster-img" src="{row['Poster']}">
                            <div class="poster-overlay">
                                <div class="poster-label">Open on Letterboxd</div>
                            </div>
                        </div>

                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.write(row["Overview"])
            st.image(row["Poster"], use_container_width=True)
