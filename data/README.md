# 数据目录

将三国演义 TXT 文件放置在此目录下：

```
data/
└── 三国演义.txt
```

## 文件格式要求

- **编码**: UTF-8
- **格式**: 纯文本，章节分隔不限
- **大小**: 建议 1MB 以内（完整三国演义约 700KB）

## 示例获取

可以从以下来源获取三国演义 TXT：
- 古腾堡计划（Project Gutenberg）
- 维基文库
- 其他公版资源

## 处理流程

运行解析脚本后，会自动生成：

```
data/
├── 三国演义.txt          # 源文件（不提交到 git）
├── entities.json         # 提取的实体列表
└── relationships.json    # 提取的关系数据
```

以及 Neo4j 导入文件：

```
backend/neo4j/
├── romance_schema.cypher  # 图谱 schema
└── romance_seed.cypher    # 种子数据
```
