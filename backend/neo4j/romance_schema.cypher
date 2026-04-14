// 三国演义知识图谱 Schema

// PERSON ID 唯一约束
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (n:PERSON) REQUIRE n.id IS UNIQUE;

// LOCATION ID 唯一约束
CREATE CONSTRAINT location_id_unique IF NOT EXISTS
FOR (n:LOCATION) REQUIRE n.id IS UNIQUE;

// EVENT ID 唯一约束
CREATE CONSTRAINT event_id_unique IF NOT EXISTS
FOR (n:EVENT) REQUIRE n.id IS UNIQUE;

// TITLE ID 唯一约束
CREATE CONSTRAINT title_id_unique IF NOT EXISTS
FOR (n:TITLE) REQUIRE n.id IS UNIQUE;


// 名称索引
CREATE INDEX person_name_index IF NOT EXISTS
FOR (n:PERSON) ON (n.name);

CREATE INDEX location_name_index IF NOT EXISTS
FOR (n:LOCATION) ON (n.name);

CREATE INDEX event_name_index IF NOT EXISTS
FOR (n:EVENT) ON (n.name);

CREATE INDEX title_name_index IF NOT EXISTS
FOR (n:TITLE) ON (n.name);


// 全文搜索索引
CREATE FULLTEXT INDEX romance_entity_fulltext IF NOT EXISTS
FOR (n:Person|Location|Event|Title)
ON EACH [n.name, n.summary];
