CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (n:Person) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT band_id_unique IF NOT EXISTS
FOR (n:Band) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT work_id_unique IF NOT EXISTS
FOR (n:Work) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT album_id_unique IF NOT EXISTS
FOR (n:Album) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT genre_id_unique IF NOT EXISTS
FOR (n:Genre) REQUIRE n.id IS UNIQUE;

CREATE INDEX person_name_index IF NOT EXISTS
FOR (n:Person) ON (n.name);

CREATE INDEX band_name_index IF NOT EXISTS
FOR (n:Band) ON (n.name);

CREATE INDEX work_name_index IF NOT EXISTS
FOR (n:Work) ON (n.name);

CREATE INDEX album_name_index IF NOT EXISTS
FOR (n:Album) ON (n.name);

CREATE INDEX genre_name_index IF NOT EXISTS
FOR (n:Genre) ON (n.name);

CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
FOR (n:Person|Band|Work|Album|Genre)
ON EACH [n.name, n.summary, n.aliases];

CALL db.awaitIndexes(300);
