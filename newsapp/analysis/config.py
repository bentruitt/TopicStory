ARTICLE_URL_REGEXPS = [
  ('bbc.com', r'[0-9]{8,8}'),
  ('bloomberg.com', r'[0-9]{4,4}-[0-9]{1,2}-[0-9]{1,2}'),
  ('cnn.com', r'/[0-9]{4,4}/[0-9]{1,2}/[0-9]{1,2}/'),
  ('forbes.com', r'/[0-9]{4,4}/[0-9]{1,2}/[0-9]{1,2}/'),
  ('foxnews.com', r'/[0-9]{4,4}/[0-9]{1,2}/[0-9]{1,2}/'),
  ('huffingtonpost.com', r'[0-9a-f]{24,24}$'),
  ('nbcnews.com', r'n[0-9]{6,6}$'),
  ('nytimes.com', r'/[0-9]{4,4}/[0-9]{1,2}/[0-9]{1,2}/'),
  ('reuters.com', r'/article/'),
  ('theguardian.com', r'(?<!/live)(?<!/video)/2016/[a-z]{3,3}/[0-9]{1,2}'), # this one was annoying to get rid of videos/lives
  ('time.com', r'/[0-9]{7,7}'),
  ('usatoday.com', r'/story/'),
]
