import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrapeReviews

load_dotenv()

st.set_page_config(
    page_title="Myntra Review Scrapper",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Myntra Review Scrapper")

if "data" not in st.session_state:
    st.session_state["data"] = False
if "scraped_df" not in st.session_state:
    st.session_state["scraped_df"] = None
if SESSION_PRODUCT_KEY not in st.session_state:
    st.session_state[SESSION_PRODUCT_KEY] = None


def form_input():
    product = st.text_input("Search Products")
    st.session_state[SESSION_PRODUCT_KEY] = product
    no_of_products = st.number_input("No of products to search",
                                     step=1,
                                     min_value=1)

    if st.button("Scrape Reviews"):
        if not product:
            st.error("Please enter a product name to search.")
            return

        st.session_state[SESSION_PRODUCT_KEY] = product
        scrapper = ScrapeReviews(
            product_name=product,
            no_of_products=int(no_of_products)
        )

        scrapped_data = scrapper.get_review_data()
        if scrapped_data is not None:
            st.session_state["data"] = True
            st.session_state["scraped_df"] = scrapped_data

            mongo_url = os.getenv("MONGO_DB_URL")
            if mongo_url:
                try:
                    mongoio = MongoIO()
                    mongoio.store_reviews(product_name=product,
                                          reviews=scrapped_data)
                    st.success("✅ Stored Data into MongoDB")
                except Exception as e:
                    st.warning(f"⚠️ Could not store reviews in MongoDB: {e}")
            else:
                st.info("ℹ️ MongoDB not configured. Skipping storage.")

        st.dataframe(scrapped_data)


if __name__ == "__main__":
    data = form_input()
