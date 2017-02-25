CREATE TABLE IF NOT EXISTS urls (
  id SERIAL PRIMARY KEY,
  url TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS sources (
  id SERIAL PRIMARY KEY,
  base_url INTEGER REFERENCES urls(id) UNIQUE,
  name TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS crawls (
  id SERIAL PRIMARY KEY,
  source INTEGER REFERENCES sources(id) NOT NULL
);
CREATE TABLE IF NOT EXISTS visits (
  id SERIAL PRIMARY KEY,
  crawl INTEGER REFERENCES crawls(id) NOT NULL,
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
  date DATE,
  source INTEGER REFERENCES sources(id)
);

-- tables below this line not actively used --
----------------------------------------------
-- CREATE TABLE IF NOT EXISTS cosine_similarities (
--   article_1 INTEGER REFERENCES articles(url) NOT NULL,
--   article_2 INTEGER REFERENCES articles(url) NOT NULL,
--   similarity REAL,
--   PRIMARY KEY(article_1,article_2),
--   CHECK (article_2 > article_1)
-- );
-- 
-- -- 300-length vectors created from spacy
-- -- vectors for article headlines
-- CREATE TABLE IF NOT EXISTS spacy_title_vectors (
--     url INTEGER REFERENCES urls(id) PRIMARY KEY,
--     spacy_title_vector REAL[300]
-- );
-- -- vectors for article contents
-- CREATE TABLE IF NOT EXISTS spacy_text_vectors (
--     url INTEGER REFERENCES urls(id) PRIMARY KEY,
--     spacy_text_vector REAL[300]
-- );
