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
