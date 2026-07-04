from selenium import webdriver
from selenium.webdriver.common.by import By
from src.exception import CustomException
from bs4 import BeautifulSoup as bs
import pandas as pd
import os, sys
import time
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
import re
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


class ScrapeReviews:
    def __init__(self,
                 product_name:str,
                 no_of_products:int):
        options = Options()
        # Enable headless mode for cloud deployment
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-web-resources")
        options.add_argument("--disable-images")  # Don't load images to save bandwidth
        # Make the browser less detectable as automation
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        # Start a new Chrome browser session
        try:
            self.driver = webdriver.Chrome(options=options)
        except WebDriverException as e:
            raise CustomException(e, sys)
        # Try to further mask automation
        try:
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                },
            )
        except Exception:
            pass

        self.product_name = product_name
        self.no_of_products = no_of_products

    def scrape_product_urls(self, product_name):
        try:
            # Use Myntra search endpoint
            encoded_query = quote(product_name)
            search_url = f"https://www.myntra.com/search?q={encoded_query}"
            self.driver.get(search_url)

            # Wait for search results to load and scroll to load more items
            product_urls = []
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-base, ul.results-base, div.product-grid"))
                )
            except TimeoutException:
                # fallback to parsing whatever is available
                pass

            # Scroll a few times to let dynamic content load
            for _ in range(6):
                try:
                    self.driver.execute_script("window.scrollBy(0, 1500);")
                    time.sleep(1.2)
                except Exception:
                    break

            page_html = bs(self.driver.page_source, "html.parser")
            # First try extracting product URLs from JSON-LD structured data
            import json
            json_urls = []
            for script in page_html.find_all("script", {"type": "application/ld+json"}):
                try:
                    txt = script.string or script.get_text()
                    payload = json.loads(txt)
                except Exception:
                    continue
                # Look for ItemList structures
                if isinstance(payload, dict) and payload.get("@type") == "ItemList":
                    for item in payload.get("itemListElement", []):
                        if isinstance(item, dict):
                            url = item.get("url") or (item.get("item") or {}).get("@id")
                            if url:
                                # normalize to path
                                if url.startswith("http"):
                                    json_urls.append(urlparse(url).path)
                                else:
                                    json_urls.append(url)

            # If we found JSON-LD URLs, use them first
            if json_urls:
                product_urls = json_urls
            else:
                product_urls = []

            # Try common Myntra selectors in order of preference
            selectors = [
                "a.desktop-searchLink",
                "a.product-base",
                "li.product-base a",
                "ul.results-base a",
                "a[href*='/']",
            ]

            for sel in selectors:
                links = page_html.select(sel)
                for a in links:
                    href = a.get("href")
                    if href and href.startswith("/"):
                        product_urls.append(href)

            # deduplicate while preserving order
            seen = set()
            unique_urls = []
            for u in product_urls:
                if u not in seen:
                    seen.add(u)
                    unique_urls.append(u)

            # Filter likely product pages: require any path segment to contain digits
            filtered = []
            for u in unique_urls:
                path = urlparse(u).path if u.startswith('http') or u.startswith('/') else urlparse(u).path
                segments = [seg for seg in path.split('/') if seg]
                if any(any(ch.isdigit() for ch in seg) for seg in segments):
                    filtered.append(u)

            return filtered

        except Exception as e:
            raise CustomException(e, sys)

    def extract_reviews(self, product_link):
        try:
            productLink = "https://www.myntra.com" + product_link
            self.driver.get(productLink)

            # Wait for page to load key elements
            try:
                WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.TAG_NAME, "title"))
                )
            except TimeoutException:
                pass

            prodRes_html = bs(self.driver.page_source, "html.parser")

            title_tag = prodRes_html.find("title")
            self.product_title = title_tag.text.strip() if title_tag else ""

            overallRating = prodRes_html.find(
                "div", {"class": "index-overallRating"}
            )
            if overallRating:
                inner = overallRating.find("div")
                self.product_rating_value = inner.text.strip() if inner else ""
            else:
                self.product_rating_value = ""

            price_tag = prodRes_html.find("span", {"class": "pdp-price"})
            self.product_price = price_tag.text.strip() if price_tag else ""

            # Look for review page link using multiple fallbacks
            product_reviews = None
            # Common anchor classes or href patterns
            candidates = prodRes_html.select("a.detailed-reviews-allReviews, a[href*='product-reviews'], a[href*='reviews']")
            if candidates:
                product_reviews = candidates[0]

            # If not found, try to locate by text
            if not product_reviews:
                for a in prodRes_html.find_all("a", href=True):
                    href = a["href"]
                    if "review" in href or "reviews" in href:
                        product_reviews = a
                        break

            if not product_reviews:
                return None

            return product_reviews
        except Exception as e:
            raise CustomException(e, sys)
        
    def scroll_to_load_reviews(self):
        # Change the window size to load more data
        self.driver.set_window_size(1920, 1080)  # Example window size, adjust as needed

        # Get the initial height of the page
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Scroll in smaller increments, waiting between scrolls
        while True:
            # Scroll down by a small amount
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(3)  # Adjust this delay if needed
            
            # Calculate the new height after scrolling
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Break the loop if no new content is loaded after scrolling
            if new_height == last_height:
                break
            
            # Update the last height for the next iteration
            last_height = new_height



    def extract_products(self, product_reviews: list):
        try:
            # product_reviews can be a bs4 Tag; get href safely
            t2 = product_reviews.get("href") if hasattr(product_reviews, 'get') else None
            if not t2:
                return pd.DataFrame()

            Review_link = "https://www.myntra.com" + t2
            self.driver.get(Review_link)
            
            self.scroll_to_load_reviews()
            
            review_page = self.driver.page_source

            review_html = bs(review_page, "html.parser")
            review = review_html.findAll(
                "div", {"class": "detailed-reviews-userReviewsContainer"}
            )

            for i in review:
                user_rating = i.findAll(
                    "div", {"class": "user-review-main user-review-showRating"}
                )
                user_comment = i.findAll(
                    "div", {"class": "user-review-reviewTextWrapper"}
                )
                user_name = i.findAll("div", {"class": "user-review-left"})

            reviews = []
            for i in range(len(user_rating)):
                try:
                    rating = (
                        user_rating[i]
                        .find("span", class_="user-review-starRating")
                        .get_text()
                        .strip()
                    )
                except:
                    rating = "No rating Given"
                try:
                    comment = user_comment[i].text
                except:
                    comment = "No comment Given"
                try:
                    name = user_name[i].find("span").text
                except:
                    name = "No Name given"
                try:
                    date = user_name[i].find_all("span")[1].text
                except:
                    date = "No Date given"

                mydict = {
                    "Product Name": self.product_title,
                    "Over_All_Rating": self.product_rating_value,
                    "Price": self.product_price,
                    "Date": date,
                    "Rating": rating,
                    "Name": name,
                    "Comment": comment,
                }
                reviews.append(mydict)

            review_data = pd.DataFrame(
                reviews,
                columns=[
                    "Product Name",
                    "Over_All_Rating",
                    "Price",
                    "Date",
                    "Rating",
                    "Name",
                    "Comment",
                ],
            )

            return review_data

        except Exception as e:
            raise CustomException(e, sys)
        
    
    def skip_products(self, search_string, no_of_products, skip_index):
        product_urls: list = self.scrape_product_urls(search_string, no_of_products + 1)

        product_urls.pop(skip_index)

    def get_review_data(self) -> pd.DataFrame:
        try:
            # search_string = self.request.form["content"].replace(" ", "-")
            # no_of_products = int(self.request.form["prod_no"])

            product_urls = self.scrape_product_urls(product_name=self.product_name)

            

            product_details = []

            # Iterate over available product URLs and collect reviews until
            # we've gathered the requested number or run out of URLs.
            for product_url in product_urls:
                if len(product_details) >= self.no_of_products:
                    break

                review = self.extract_reviews(product_url)

                if review:
                    product_detail = self.extract_products(review)
                    if product_detail is not None and not product_detail.empty:
                        product_details.append(product_detail)

            # Ensure the webdriver is closed
            try:
                self.driver.quit()
            except Exception:
                pass

            if not product_details:
                # Return empty DataFrame if nothing was scraped
                return pd.DataFrame()

            data = pd.concat(product_details, axis=0, ignore_index=True)
            data.to_csv("data.csv", index=False)
            return data
            
            
                
            # columns = data.columns

            # values = [[data.loc[i, col] for col in data.columns ] for i in range(len(data)) ]
            
            # return columns, values
        
    

        except Exception as e:
            raise CustomException(e, sys)
