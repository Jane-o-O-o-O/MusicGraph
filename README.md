# MusicGraph

MusicGraph 是一个面向音乐实体关系的 3D 图谱项目，目标是先完成两个核心能力：

- 音乐实体搜索
- 3D 图谱展示与关系展开

第一阶段不做 GraphRAG、不做复杂数据治理平台，先把 `Neo4j + 后端查询接口 + 前端 3D 图谱` 做成可用原型。

## 文档

- [架构方案](E:/MusicGraph/docs/architecture.md)
- [数据库设计与 Neo4j 设置](E:/MusicGraph/docs/database.md)
- [前后端方案](E:/MusicGraph/docs/frontend-backend.md)

## 推荐技术栈

- 数据库：`Neo4j`
- 后端：`Python + FastAPI`
- 前端：`React + TypeScript`
- 3D 可视化：`react-force-graph-3d`

## 第一阶段范围

- 支持 `Person`、`Band`、`Work`、`Album`、`Genre`
- 支持关键词搜索、节点详情、邻居展开、路径查询
- 支持 3D 交互：旋转、缩放、拖拽、点击展开

## 后续

代码初始化前，先以文档中的 schema、接口和目录方案为准。

## 当前代码结构

```text
MusicGraph/
  backend/
    app/
    requirements.txt
    .env.example
  frontend/
    src/
    package.json
  docs/
```

## 当前状态

当前仓库已经包含：

- `FastAPI` 后端骨架
- `Neo4j` 适配层
- `mock` 图数据模式
- `Neo4j schema / seed / reset` 脚本
- `Neo4j` 一键初始化脚本
- `docker-compose.yml`
- `React + TypeScript + Vite` 前端骨架
- `react-force-graph-3d` 3D 图谱页面

后端默认使用 mock 数据，因此即使还没启动 Neo4j，也能先联调页面和接口。

## 启动 Neo4j

在 `E:\MusicGraph` 下执行：

```powershell
docker compose up -d
```

默认地址：

- Neo4j Browser: `http://localhost:7474`
- Bolt: `bolt://localhost:7687`

默认账号：

- 用户名：`neo4j`
- 密码：`musicgraph123`

## 初始化 Neo4j Schema 和样例数据

在 `E:\MusicGraph\backend` 下执行：

```powershell
Copy-Item .env.example .env
python scripts\init_neo4j.py --reset
```

也可以只执行部分步骤：

```powershell
python scripts\init_neo4j.py --schema-only
python scripts\init_neo4j.py --seed-only
```

## 启动后端

在 `E:\MusicGraph\backend` 下执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

默认地址：

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

如果要切换到 Neo4j：

1. 修改 `backend\.env`
2. 将 `MUSICGRAPH_USE_MOCK_DATA=false`
3. 填好 `MUSICGRAPH_NEO4J_URI`、`MUSICGRAPH_NEO4J_USERNAME`、`MUSICGRAPH_NEO4J_PASSWORD`

## 启动前端

在 `E:\MusicGraph\frontend` 下执行：

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

默认地址：

- Web: `http://localhost:5173`

前端默认请求：

- `http://localhost:8000/api`

如果后端地址不同，可以在前端启动前设置：

```powershell
$env:VITE_API_BASE_URL="http://localhost:8000/api"
```

## 当前 API

- `GET /api/health`
- `GET /api/search?q=`
- `GET /api/entities/{id}`
- `GET /api/graph/{id}?depth=1`
- `GET /api/path?from=&to=`

## 示例 ID

可以先用这几个 mock 数据测试：

- `person_jay_chou`
- `person_fang_wenshan`
- `work_qinghuaci`
- `band_mayday`
- `person_ashin`
