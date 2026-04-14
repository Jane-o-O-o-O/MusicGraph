# MusicGraph - 三国演义知识图谱模式

## 1. 目标

MusicGraph 现在支持两种模式：

1. **音乐知识图谱** - 音乐、歌手、专辑、流派关系
2. **三国演义知识图谱** - 人物、地点、事件、官职关系

## 2. 三国演义实体模型

### 节点标签

- `Person` - 人物（刘备、关羽、张飞、曹操...）
- `Location` - 地点（荆州、益州、赤壁、官渡...）
- `Event` - 事件（赤壁之战、官渡之战、三顾茅庐...）
- `Title` - 官职/封号（丞相、大将军、都督...）

### 通用节点属性

每个节点统一保留：

- `id`: 全局唯一 ID（格式：`{type}_{name}`）
- `name`: 主名称
- `type`: 节点类型
- `summary`: 简介
- `popularity`: 出现频率（仅 Person）

### 关系模型

#### 自动提取的关系（基于共现）

- `(:Person)-[:ASSOCIATED_WITH]->(:Person)` - 人物共现关系
- `(:Person)-[:LOCATED_AT]->(:Location)` - 人物所在地点

#### 可手动扩展的关系

- `(:Person)-[:SWEAR_BROTHER_WITH]->(:Person)` - 结义关系
- `(:Person)-[:SERVE_UNDER]->(:Person)` - 效忠关系
- `(:Person)-[:FATHER_OF]->(:Person)` - 父子关系
- `(:Person)-[:FOUGHT_AT]->(:Event)` - 参战关系
- `(:Person)-[:APPOINTED_AS]->(:Title)` - 官职关系
- `(:Person)-[:ALLIED_WITH]->(:Person)` - 同盟关系
- `(:Person)-[:ENEMY_OF]->(:Person)` - 敌对关系

## 3. 三国演义模式使用方式

### 3.1 准备数据

将三国演义 TXT 文件放置到 `data/三国演义.txt`

### 3.2 运行解析脚本

```bash
python scripts/build_romance_graph.py
```

脚本会自动：
1. 使用 spaCy 中文模型进行分词和实体识别
2. 基于预定义的 60+ 人物别名映射表做实体消歧
3. 基于共现窗口提取人物关系
4. 生成 Neo4j Cypher 导入脚本

### 3.3 导入 Neo4j

```bash
# 启动 Neo4j
docker compose up -d

# 导入 schema
python backend/scripts/init_neo4j.py --schema-only

# 导入种子数据
python backend/scripts/init_neo4j.py --seed-only
```

### 3.4 启动服务

```bash
cd backend
uvicorn app.main:app --reload
```

## 4. 实体别名消歧

三国演义中人物有大量别名，系统已内置别名映射表：

### 示例

| 标准名 | 别名 |
|--------|------|
| 刘备 | 刘玄德、玄德、刘皇叔、汉中王 |
| 关羽 | 关云长、云长、关公、美髯公 |
| 诸葛亮 | 孔明、诸葛孔明、卧龙、诸葛丞相 |
| 曹操 | 曹孟德、孟德、曹丞相、魏王 |

完整映射表见 `data/romance_entities.json`

## 5. 提取策略

### 实体识别

1. **精确匹配**：基于预定义的实体名单和别名映射表（优先级高）
2. **NLP 补充**：使用 spaCy 中文模型 `zh_core_web_md` 做 NER

### 关系提取

1. **共现关系**：两个人物在 200 字符窗口内同时出现 → `ASSOCIATED_WITH`
2. **地点关系**：人物和地点在同一段落出现 → `LOCATED_AT`

### 置信度

- 共现关系：`0.5`
- 地点关系：`0.6`
- 手动标注关系：`1.0`

## 6. 扩展建议

### 第二批可以做的改进

1. **人工标注关系**：基于文本内容标注具体关系类型（结义、效忠、敌对等）
2. **事件参与关系**：提取人物参与的具体事件
3. **时间线**：按章节顺序构建人物关系变化时间线
4. **对话分析**：基于对话内容分析人物关系亲密度
5. **战场分析**：基于战斗场景分析对阵关系

### 可视化增强

1. **势力颜色编码**：蜀汉（红）、曹魏（蓝）、东吴（绿）
2. **关系强度**：根据共现频率调整边的粗细
3. **时间轴**：按章节展示关系演化

## 7. 当前局限

1. **别名映射表不完整**：只包含 60+ 核心人物，次要人物未覆盖
2. **关系类型单一**：目前只有共现关系，缺少具体语义关系
3. **实体消歧困难**：相同称呼可能指代不同人（如"将军"）
4. **无时间维度**：未记录关系的时间变化

## 8. 快速开始

```bash
# 1. 放置三国演义 TXT
# data/三国演义.txt

# 2. 运行解析脚本
python scripts/build_romance_graph.py

# 3. 启动 Neo4j
docker compose up -d

# 4. 导入数据
python backend/scripts/init_neo4j.py

# 5. 启动后端
cd backend && uvicorn app.main:app --reload

# 6. 访问前端
# http://localhost:5173
```
