from src.scrapper.scrape import ScrapeReviews

s = ScrapeReviews('shoes', 1)
urls = s.scrape_product_urls('shoes')
print('URL_COUNT', len(urls))
print(urls[:10])
with open('scripts/search_shoes.html', 'w', encoding='utf-8') as f:
    f.write(s.driver.page_source)
    print('WROTE search_shoes.html')
if len(urls) > 0:
    u = urls[0]
    print('CHECK_PRODUCT', u)
    r = s.extract_reviews(u)
    print('REVIEW_TAG', bool(r))
    if r and hasattr(r, 'get'):
        print('REVIEW_HREF', r.get('href'))

try:
    s.driver.quit()
except Exception:
    pass
