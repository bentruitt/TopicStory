CREATE TABLE IF NOT EXISTS urls (
  id SERIAL PRIMARY KEY,
  url TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS robots (
  url INTEGER REFERENCES urls(id) PRIMARY KEY,
  allowed BOOLEAN
);
CREATE TABLE IF NOT EXISTS sources (
  id SERIAL PRIMARY KEY,
  name TEXT,
  base_url INTEGER REFERENCES urls(id) PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS visits (
  id SERIAL PRIMARY KEY,
  base_url INTEGER REFERENCES urls(id) NOT NULL,
  visit_url INTEGER REFERENCES urls(id) NOT NULL,
  visit_time TIMESTAMP
);
CREATE TABLE IF NOT EXISTS links (
  id SERIAL PRIMARY KEY,
  visit INTEGER REFERENCES visits(id),
  to_url INTEGER REFERENCES urls(id) NOT NULL
);
CREATE TABLE IF NOT EXISTS articles (
  url INTEGER REFERENCES urls(id) PRIMARY KEY,
  title TEXT,
  text TEXT,
  date DATE
);
CREATE TABLE article_labels (
  id SERIAL PRIMARY KEY,
  url INTEGER REFERENCES urls(id) UNIQUE NOT NULL,
  is_article BOOLEAN
);
CREATE TABLE cosine_similarities (
  article_1 INTEGER REFERENCES articles(url) NOT NULL,
  article_2 INTEGER REFERENCES articles(url) NOT NULL,
  similarity REAL,
  PRIMARY KEY(article_1,article_2),
  CHECK (article_2 > article_1)
);
