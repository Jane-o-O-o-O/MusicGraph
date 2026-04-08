# 数据库设计与 Neo4j 设置

## 1. 选型结论

当前阶段只使用 `Neo4j`，不引入 `MySQL`。

原因：

- 当前需求是图谱展示与搜索
- 主查询是邻居扩展、路径查询、实体关系展示
- 使用单一图数据库可以降低建模和同步复杂度

后续如果需要后台管理、数据治理、批量导入审计，再考虑增加 MySQL。

## 2. 本地部署方式

推荐优先使用 Docker 启动 Neo4j。

## 3. Docker 启动示例

```powershell
docker run `
  --name musicgraph-neo4j `
  -p 7474:7474 `
  -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/musicgraph123 `
  -e NEO4J_dbms_memory_pagecache_size=512M `
  -e NEO4J_dbms_memory_heap_initial__size=512M `
  -e NEO4J_dbms_memory_heap_max__size=1G `
  -v neo4j_data:/data `
  neo4j:5
```

启动后：

- Web UI: `http://localhost:7474`
- Bolt: `bolt://localhost:7687`
- 用户名：`neo4j`
- 密码：`musicgraph123`

## 4. 数据模型

### 节点标签

- `Person`
- `Band`
- `Work`
- `Album`
- `Genre`

### 通用节点属性

每个节点建议统一保留：

- `id`: 全局唯一 ID
- `name`: 主名称
- `type`: 节点类型
- `aliases`: 别名数组
- `summary`: 简介
- `source`: 数据来源
- `popularity`: 热度，可选
- `updated_at`: 更新时间

### 专属属性

#### Person

- `roles`
- `country`
- `birth_date`

#### Band

- `country`
- `formed_year`

#### Work

- `release_date`
- `language`
- `duration_seconds`

#### Album

- `release_date`
- `album_type`

#### Genre

- `description`

## 5. 关系模型

### 关系类型

- `PERFORMED`
- `COMPOSED`
- `WROTE_LYRICS_FOR`
- `MEMBER_OF`
- `IN_ALBUM`
- `HAS_GENRE`

### 通用关系属性

- `source`
- `confidence`
- `start_date`
- `end_date`
- `role_detail`

第一阶段如果数据量不大，关系属性可以先只保留：

- `source`
- `confidence`

## 6. 索引与约束

```cypher
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
```

如果使用 Neo4j 全文搜索，再增加：

```cypher
CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
FOR (n:Person|Band|Work|Album|Genre)
ON EACH [n.name, n.summary];
```

说明：

- Neo4j 5 对数组字段的全文索引支持需要按实际版本确认
- 第一版建议先搜索 `name` 和 `summary`
- `aliases` 可以在应用层做补充匹配，或在导入时拼接为字符串字段

## 7. 示例数据

```cypher
CREATE (jay:Person {
  id: 'person_jay_chou',
  name: '周杰伦',
  type: 'Person',
  aliases: ['Jay Chou'],
  roles: ['Singer', 'Composer'],
  country: 'CN'
});

CREATE (fang:Person {
  id: 'person_fang_wenshan',
  name: '方文山',
  type: 'Person',
  aliases: [],
  roles: ['Lyricist'],
  country: 'CN'
});

CREATE (song:Work {
  id: 'work_qinghuaci',
  name: '青花瓷',
  type: 'Work',
  language: 'zh',
  release_date: date('2007-11-02')
});

CREATE (album:Album {
  id: 'album_womihenmang',
  name: '我很忙',
  type: 'Album',
  release_date: date('2007-11-02')
});

CREATE (genre:Genre {
  id: 'genre_pop',
  name: 'Pop',
  type: 'Genre'
});

CREATE (jay)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(song);
CREATE (jay)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(song);
CREATE (fang)-[:WROTE_LYRICS_FOR {source: 'seed', confidence: 1.0}]->(song);
CREATE (song)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(album);
CREATE (song)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(genre);
```

## 8. 查询示例

### 按关键词搜索

```cypher
CALL db.index.fulltext.queryNodes('entity_fulltext', $query)
YIELD node, score
RETURN node, score
ORDER BY score DESC
LIMIT 20;
```

### 查询节点 1 跳子图

```cypher
MATCH (n {id: $id})-[r]-(m)
RETURN n, r, m
LIMIT 100;
```

### 查询 2 跳子图

```cypher
MATCH p=(n {id: $id})-[*1..2]-(m)
RETURN p
LIMIT 100;
```

### 查询两个实体最短路径

```cypher
MATCH (a {id: $from}), (b {id: $to})
MATCH p = shortestPath((a)-[*..6]-(b))
RETURN p;
```

## 9. 数据导入建议

第一版建议先用 `CSV + Cypher` 导入少量样例数据，不要一上来接复杂采集系统。

建议导入顺序：

1. 导入节点
2. 导入关系
3. 创建索引
4. 验证搜索和路径查询

## 10. 数据库边界

当前数据库只承担：

- 图存储
- 图查询
- 搜索索引

当前数据库不承担：

- 用户系统
- 审计日志
- 复杂 ETL
- 文本向量检索

这样范围最清楚，也最适合尽快完成第一版。
