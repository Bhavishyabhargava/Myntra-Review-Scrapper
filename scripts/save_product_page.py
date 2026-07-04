from src.scrapper.scrape import ScrapeReviews

s = ScrapeReviews('shoes', 1)
urls = s.scrape_product_urls('shoes')
if not urls:
    print('no urls')
else:
    u = urls[0]
    print('saving', u)
    s.driver.get('https://www.myntra.com' + u)
    with open('scripts/product_page.html', 'w', encoding='utf-8') as f:
        f.write(s.driver.page_source)
    print('saved product_page.html')
    try:
        s.driver.quit()
    except Exception:
        pass
