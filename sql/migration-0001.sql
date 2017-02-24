ALTER TABLE visits
ADD COLUMN source_id INTEGER NOT NULL REFERENCES sources(id) DEFAULT 0;

UPDATE visits SET source_id =
    (SELECT id FROM sources
        WHERE visits.source = sources.base_url);

ALTER TABLE visits
DROP COLUMN source;

ALTER TABLE visits
RENAME COLUMN source_id TO source;
