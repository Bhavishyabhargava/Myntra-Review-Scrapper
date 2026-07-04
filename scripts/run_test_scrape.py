from src.scrapper.scrape import ScrapeReviews

s = ScrapeReviews('shoes', 1)
df = s.get_review_data()
print('DONE', type(df), getattr(df, 'shape', None))
if df is None or df.empty:
    print('EMPTY')
else:
    print(df.head().to_dict(orient='records'))
