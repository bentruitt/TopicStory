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

-- tables below this line are used by NMF --
CREATE TABLE IF NOT EXISTS nmf_models (
    id SERIAL PRIMARY KEY,
    num_topics INTEGER,
    start_date DATE,
    end_date DATE
);
CREATE TABLE IF NOT EXISTS nmf_article_topics (
    nmf_model INTEGER REFERENCES nmf_models(id),
    article INTEGER REFERENCES articles(url),
    topic INTEGER,
    PRIMARY KEY(nmf_model,article)
);
CREATE TABLE IF NOT EXISTS nmf_topic_words (
    nmf_model INTEGER REFERENCES nmf_models(id),
    topic INTEGER,
    words VARCHAR[100],
    PRIMARY KEY(nmf_model,topic)
);
