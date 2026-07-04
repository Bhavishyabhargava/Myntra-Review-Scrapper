import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrapeReviews

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Myntra Review Scrapper",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def inject_style():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
        }

        html, body, [data-testid='stAppViewContainer'] {
            background: radial-gradient(ellipse at top left, rgba(65, 140, 255, 0.18), transparent 30%),
                        radial-gradient(ellipse at bottom right, rgba(161, 43, 255, 0.12), transparent 24%),
                        #10151f;
            color: #e8eef8;
        }

        [data-testid='stHeader'] {
            background: transparent;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1500px;
        }

        .main .block-container {
            background: rgba(14, 18, 27, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 40px 120px rgba(0, 0, 0, 0.3);
            border-radius: 32px;
            backdrop-filter: blur(18px);
        }

        .stButton>button, .stDownloadButton>button {
            border-radius: 18px;
            border: none;
            padding: 0.95rem 1.6rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            transition: transform 220ms ease, box-shadow 220ms ease, background 220ms ease;
            box-shadow: 0 12px 30px rgba(0, 109, 255, 0.18);
            background: linear-gradient(135deg, rgba(64, 188, 255, 0.95), rgba(117, 92, 255, 0.95));
            color: #fff;
        }

        .stButton>button:hover, .stDownloadButton>button:hover {
            transform: translateY(-1px) scale(1.01);
            box-shadow: 0 18px 45px rgba(64, 188, 255, 0.24);
        }

        .stButton>button:focus-visible, .stDownloadButton>button:focus-visible {
            outline: 2px solid rgba(94, 206, 255, 0.75);
            outline-offset: 3px;
        }

        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            background: rgba(21, 27, 39, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            border-radius: 20px !important;
            color: #eef4ff !important;
            padding: 1rem 1.2rem !important;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.01);
            transition: border-color 220ms ease, box-shadow 220ms ease;
        }

        .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
            border-color: rgba(87, 172, 255, 0.8) !important;
            box-shadow: 0 0 0 6px rgba(64, 188, 255, 0.14) !important;
        }

        .stTextInput label, .stNumberInput label {
            color: #cfd9ff;
            font-weight: 600;
        }

        .stDataFrame, .css-1lcbmhc.e1fqkh3o3 {
            border-radius: 28px !important;
            overflow: hidden !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.22);
            background: rgba(12, 16, 24, 0.82) !important;
        }

        .stDataFrame div[data-testid='stMarkdownContainer'] {
            padding: 0 !important;
        }

        .css-1d391kg, .css-1g3ss8p {
            background: rgba(13, 18, 26, 0.92) !important;
        }

        [data-testid='stSidebar'] > div {
            background: rgba(13, 18, 26, 0.92) !important;
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 1.5rem 1.4rem 1.8rem;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.01);
        }

        .sidebar .stMarkdown h3, .sidebar .stMarkdown p {
            color: #d1dbff;
        }

        .sidebar .stInfo, .sidebar .stMarkdown, .sidebar .stText {
            color: #c3d1ff;
        }

        .section-card {
            background: rgba(17, 23, 34, 0.84);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 28px;
            padding: 1.8rem;
            margin-bottom: 1.75rem;
            box-shadow: 0 40px 80px rgba(0, 0, 0, 0.18);
            backdrop-filter: blur(18px);
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
            font-size: clamp(2.5rem, 3vw, 4rem);
            line-height: 1.02;
            letter-spacing: -0.04em;
            margin-bottom: 0.75rem;
            color: #f4f7ff;
        }

        .hero-subtitle {
            max-width: 780px;
            color: #c8d2ff;
            font-size: 1.06rem;
            line-height: 1.8;
            margin-bottom: 1.75rem;
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

        @media (max-width: 900px) {
            .hero-title { font-size: 2.4rem; }
            .hero-subtitle { font-size: 1rem; }
            .block-container { padding-left: 1.25rem; padding-right: 1.25rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class='section-card'>
            <div class='panel-pill'>Intelligent review intelligence</div>
            <div class='hero-title'>Myntra review scraping, reimagined for modern product intelligence.</div>
            <div class='hero-subtitle'>Enter a search query and retrieve rich review data from Myntra with a polished, premium experience designed for analysis and sharing.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def form_input():
    inject_style()
    render_header()

    with st.container():
        with st.expander("Start a new scraping session", expanded=True):
            with st.container():
                col1, col2 = st.columns([3, 1], gap='large')

                with col1:
                    product = st.text_input(
                        "Search products",
                        placeholder="e.g. denim jackets, sneakers, summer dresses",
                        key="product_input"
                    )

                with col2:
                    no_of_products = st.number_input(
                        "Products to search",
                        step=1,
                        min_value=1,
                        max_value=50,
                        value=5
                    )

                st.markdown("<div style='height: 18px'></div>", unsafe_allow_html=True)
                button_col, _ = st.columns([2, 1], gap='large')
                with button_col:
                    if st.button("Scrape Reviews", use_container_width=True):
                        if not product:
                            st.error("Please enter a product name.")
                            return

                        try:
                            with st.spinner("Scraping reviews and gathering insights..."):
                                st.session_state[SESSION_PRODUCT_KEY] = product
                                scrapper = ScrapeReviews(
                                    product_name=product,
                                    no_of_products=int(no_of_products)
                                )

                                scrapped_data = scrapper.get_review_data()

                                if scrapped_data is not None and not scrapped_data.empty:
                                    st.session_state["data"] = True
                                    st.session_state[SESSION_PRODUCT_KEY] = product
                                    st.session_state["scraped_df"] = scrapped_data

                                    mongo_url = os.getenv("MONGO_DB_URL")
                                    if mongo_url:
                                        try:
                                            from src.cloud_io import MongoIO
                                            mongoio = MongoIO()
                                            mongoio.store_reviews(product_name=product, reviews=scrapped_data)
                                            st.success("Data stored in MongoDB successfully.")
                                        except Exception as e:
                                            st.warning(f"Could not store in MongoDB: {str(e)}")
                                    else:
                                        st.info("MongoDB is not configured. Storage skipped.")

                                    st.success(f"Successfully scraped {len(scrapped_data)} reviews.")

                                    with st.container():
                                        st.markdown(
                                            """
                                            <div class='section-card'>
                                                <div style='display:flex; gap:1rem; flex-wrap:wrap;'>
                                                    <div class='metric-card'><h4>Products</h4><p>{products}</p></div>
                                                    <div class='metric-card'><h4>Reviews</h4><p>{reviews}</p></div>
                                                    <div class='metric-card'><h4>Source</h4><p>Myntra</p></div>
                                                </div>
                                            </div>
                                            """.format(products=no_of_products, reviews=len(scrapped_data)),
                                            unsafe_allow_html=True,
                                        )

                                    st.markdown(
                                        """
                                        <div class='section-card'>
                                            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;'>
                                                <div>
                                                    <div style='font-size:1rem; color:#9bb2ff; font-weight:600; letter-spacing:0.04em;'>Review Data</div>
                                                    <div style='font-size:1.75rem; font-weight:700; color:#f4f7ff;'>Scraped results</div>
                                                </div>
                                            </div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )

                                    st.dataframe(scrapped_data, use_container_width=True, height=420)

                                    csv = scrapped_data.to_csv(index=False)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv,
                                        file_name=f"{product}_reviews.csv",
                                        mime="text/csv"
                                    )
                                else:
                                    st.warning("No reviews found for the selected product.")

                        except Exception as e:
                            st.error(f"Error occurred: {str(e)}")
                            st.error(f"Details: {type(e).__name__}")

    with st.sidebar:
        st.markdown(
            """
            <div class='section-card' style='padding:1.4rem 1.3rem;'>
                <div style='font-size:1rem; font-weight:700; color:#f1f5ff; margin-bottom:1rem;'>About</div>
                <div style='font-size:0.95rem; color:#c8d2ff; line-height:1.8;'>This app scrapes product reviews from Myntra and presents them with a premium, futuristic interface. Download the CSV and continue your analysis with clarity.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class='section-card' style='padding:1.4rem 1.3rem;'>
                <div style='font-size:1rem; font-weight:700; color:#f1f5ff; margin-bottom:0.85rem;'>Configuration</div>
                <div style='font-size:0.95rem; color:#c8d2ff; line-height:1.75;'>
                    <div>• <strong>MongoDB</strong>: Set <code>MONGO_DB_URL</code> in <code>.env</code> to enable storage.</div>
                    <div>• <strong>Selenium</strong>: Runs headless for cloud deployment.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Initialize session state
if "data" not in st.session_state:
    st.session_state["data"] = False
if "scraped_df" not in st.session_state:
    st.session_state["scraped_df"] = None
if SESSION_PRODUCT_KEY not in st.session_state:
    st.session_state[SESSION_PRODUCT_KEY] = None


if __name__ == "__main__":
    form_input()
