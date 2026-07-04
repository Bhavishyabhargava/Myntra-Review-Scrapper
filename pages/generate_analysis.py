import pandas as pd
import streamlit as st
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.data_report.generate_data_report import DashboardGenerator

try:
    mongo_con = MongoIO()
except Exception:
    mongo_con = None


def inject_style():
    st.markdown(
        """
        <style>
        .block-container {
            padding: 2rem 2rem 2rem 2rem;
            max-width: 1400px;
        }

        html, body, [data-testid='stAppViewContainer'] {
            background: radial-gradient(circle at 10% 10%, rgba(66, 150, 255, 0.16), transparent 22%),
                        radial-gradient(circle at 90% 10%, rgba(161, 59, 255, 0.1), transparent 18%),
                        radial-gradient(circle at 50% 90%, rgba(58, 247, 255, 0.08), transparent 20%),
                        #0e1320;
            color: #e8eef8;
        }

        .main .block-container {
            background: rgba(12, 17, 27, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 32px;
            box-shadow: 0 40px 120px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(18px);
        }

        .stButton>button, .stDownloadButton>button {
            border-radius: 18px;
            border: none;
            padding: 0.95rem 1.65rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            transition: transform 220ms ease, box-shadow 220ms ease, background 220ms ease;
            background: linear-gradient(135deg, rgba(71, 176, 255, 0.95), rgba(129, 96, 255, 0.95));
            color: #fff;
            box-shadow: 0 16px 35px rgba(27, 79, 255, 0.18);
        }

        .stButton>button:hover, .stDownloadButton>button:hover {
            transform: translateY(-1px) scale(1.01);
            box-shadow: 0 20px 45px rgba(27, 79, 255, 0.24);
        }

        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            background: rgba(20, 26, 36, 0.92) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 20px !important;
            color: #eef2ff !important;
            padding: 1rem 1.2rem !important;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02);
            transition: border-color 220ms ease, box-shadow 220ms ease;
        }

        .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
            border-color: rgba(90, 180, 255, 0.72) !important;
            box-shadow: 0 0 0 6px rgba(64, 188, 255, 0.14) !important;
        }

        .stTextInput label, .stNumberInput label, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #d4ddff;
        }

        .stDataFrame, .css-1lcbmhc.e1fqkh3o3 {
            border-radius: 28px !important;
            overflow: hidden !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            background: rgba(13, 18, 27, 0.88) !important;
            box-shadow: 0 28px 75px rgba(0, 0, 0, 0.18);
        }

        [data-testid='stSidebar'] > div {
            background: rgba(14, 19, 29, 0.92) !important;
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 1.4rem 1.3rem 1.8rem;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.008);
        }

        .section-card {
            background: rgba(18, 25, 39, 0.84);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 28px;
            padding: 1.8rem;
            margin-bottom: 1.75rem;
            box-shadow: 0 38px 82px rgba(0, 0, 0, 0.18);
            backdrop-filter: blur(16px);
        }

        .panel-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.75rem 1rem;
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
            color: #d8e2ff;
            font-weight: 600;
            margin-bottom: 1.25rem;
        }

        .hero-title {
            font-size: clamp(2.3rem, 3vw, 3.6rem);
            line-height: 1.02;
            letter-spacing: -0.04em;
            margin-bottom: 0.75rem;
            color: #f4f7ff;
        }

        .hero-subtitle {
            max-width: 760px;
            color: #c8d2ff;
            font-size: 1.02rem;
            line-height: 1.8;
            margin-bottom: 1.8rem;
        }

        .metric-card {
            background: rgba(24, 32, 47, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 24px;
            padding: 1.4rem 1.6rem;
            min-height: 140px;
            transition: transform 220ms ease, box-shadow 220ms ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.18);
        }

        .metric-card h4 {
            margin: 0;
            font-size: 0.92rem;
            color: #9bb2ff;
            font-weight: 600;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }

        .metric-card p {
            margin: 0.75rem 0 0;
            font-size: 2rem;
            color: #fff;
            font-weight: 700;
        }

        .empty-state-card {
            background: rgba(21, 28, 40, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 28px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 28px 70px rgba(0, 0, 0, 0.18);
        }

        .empty-state-card h2 {
            margin-bottom: 1rem;
            color: #f4f7ff;
            font-size: 2rem;
        }

        .empty-state-card p {
            margin: 0 auto;
            max-width: 720px;
            color: #c7d0ff;
            font-size: 1rem;
            line-height: 1.8;
        }

        .error-card {
            background: rgba(148, 33, 255, 0.08);
            border: 1px solid rgba(161, 59, 255, 0.25);
            border-radius: 26px;
            padding: 1.75rem;
            color: #f7f6ff;
        }

        .error-card h3 {
            margin: 0 0 0.5rem;
            color: #ffdfe8;
        }

        .error-card p {
            margin: 0;
            color: #ebd0dd;
        }

        @media (max-width: 900px) {
            .hero-title { font-size: 2.2rem; }
            .hero-subtitle { font-size: 1rem; }
            .block-container { padding-left: 1.25rem; padding-right: 1.25rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_analysis_page(review_data: pd.DataFrame):
    if review_data is not None and not review_data.empty:
        st.markdown(
            """
            <div class='section-card'>
                <div class='panel-pill'>Review intelligence</div>
                <div class='hero-title'>Generate product insights from Myntra review data.</div>
                <div class='hero-subtitle'>Use the analysis page to explore your scraped reviews, generate smart trends, and surface product-level patterns.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(review_data, use_container_width=True, height=460)
        if st.button("Generate Analysis"):
            dashboard = DashboardGenerator(review_data)

            dashboard.display_general_info()
            dashboard.display_product_sections()
    else:
        st.warning("No review data available for analysis.")


# Page state
has_data = st.session_state.get("data", False)
product_key = st.session_state.get(SESSION_PRODUCT_KEY, None)

inject_style()

if has_data and product_key:
    session_data = st.session_state.get("scraped_df", None)
    if session_data is not None and not session_data.empty:
        create_analysis_page(session_data)
    elif mongo_con is None:
        st.markdown(
            """
            <div class='error-card'>
                <h3>MongoDB Not Configured</h3>
                <p>Set <code>MONGO_DB_URL</code> in your <code>.env</code> file to enable review analysis from the cloud.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        try:
            data = mongo_con.get_reviews(product_name=product_key)
            create_analysis_page(data)
        except Exception as e:
            st.markdown(
                """
                <div class='error-card'>
                    <h3>Unable to load review history</h3>
                    <p>There was an issue fetching review data: {}</p>
                </div>
                """.format(str(e)),
                unsafe_allow_html=True,
            )
else:
    st.markdown(
        """
        <div class='empty-state-card'>
            <h2>No analysis data available yet</h2>
            <p>Visit the main scraping page and run a search to populate review data. Once reviews are available, this page can generate intelligent analysis and product insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.markdown(
            """
            <div class='section-card'>
                <div style='font-size:1rem; font-weight:700; color:#f1f5ff; margin-bottom:1rem;'>Analysis Guide</div>
                <div style='font-size:0.95rem; color:#c8d2ff; line-height:1.8;'>Run a scrape in the home page first, then return here to generate visual review insights and product summary sections.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

