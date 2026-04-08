# 前后端方案

## 1. 技术选型

### 后端

- 语言：`Python`
- 框架：`FastAPI`
- 驱动：`neo4j`
- 数据校验：`Pydantic`

选择原因：

- 开发速度快
- 接口定义清晰
- 和 Neo4j 驱动结合简单
- 后续接脚本导入、数据清洗也顺手

### 前端

- 语言：`TypeScript`
- 框架：`React`
- 构建工具：`Vite`
- 3D 渲染：`react-force-graph-3d`
- UI：先用轻量自定义组件，不先上重型后台框架

选择原因：

- TypeScript 适合维护复杂图数据结构
- React 生态成熟
- `react-force-graph-3d` 足够支撑第一版 3D 图谱

## 2. 后端职责

后端不做复杂业务编排，只做一层“Neo4j 查询适配器”。

主要职责：

- 搜索实体
- 查询节点详情
- 查询邻居子图
- 查询两点路径
- 统一返回前端可直接消费的 JSON

## 3. 后端接口设计

### `GET /api/search`

参数：

- `q`: 搜索关键词
- `type`: 可选，按实体类型过滤
- `limit`: 默认 `20`

返回示例：

```json
{
  "items": [
    {
      "id": "person_jay_chou",
      "name": "周杰伦",
      "type": "Person",
      "summary": "Singer, Composer"
    }
  ]
}
```

### `GET /api/entities/{id}`

返回单个节点详情。

### `GET /api/graph/{id}`

参数：

- `depth`: 默认 `1`
- `limit`: 默认 `50`

返回示例：

```json
{
  "nodes": [
    {
      "id": "person_jay_chou",
      "label": "周杰伦",
      "type": "Person"
    },
    {
      "id": "work_qinghuaci",
      "label": "青花瓷",
      "type": "Work"
    }
  ],
  "links": [
    {
      "source": "person_jay_chou",
      "target": "work_qinghuaci",
      "type": "PERFORMED"
    }
  ]
}
```

### `GET /api/path`

参数：

- `from`
- `to`

返回两个实体之间的路径。

## 4. 前端职责

前端负责：

- 搜索输入
- 搜索结果列表
- 3D 图谱渲染
- 节点点击展开
- 节点详情展示
- 路径高亮

## 5. 页面结构

建议采用三栏布局：

- 左栏：搜索框、筛选器、搜索结果
- 中栏：3D 图谱
- 右栏：节点详情、关系列表

第一版页面不要过度复杂化，重点是图谱交互顺畅。

## 6. 图谱交互设计

### 节点

- 按 `type` 使用不同颜色
- 按连接数或热度调整大小
- 鼠标悬停显示名称
- 点击节点展开 1 跳邻居

### 边

- 不同关系类型使用不同颜色
- 悬停显示关系名
- 路径查询结果高亮显示

### 布局策略

- 初始只展示中心节点和 1 跳邻居
- 点击后再按需增量加载
- 节点数量达到阈值时限制再次展开

## 7. 推荐目录结构

```text
MusicGraph/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      services/
      main.py
    requirements.txt
  frontend/
    src/
      api/
      components/
      pages/
      types/
      hooks/
      App.tsx
      main.tsx
    package.json
  docs/
    architecture.md
    database.md
    frontend-backend.md
```

## 8. 前后端数据约定

### 节点结构

```json
{
  "id": "person_jay_chou",
  "label": "周杰伦",
  "type": "Person",
  "summary": "Singer, Composer",
  "meta": {
    "country": "CN"
  }
}
```

### 边结构

```json
{
  "id": "person_jay_chou__PERFORMED__work_qinghuaci",
  "source": "person_jay_chou",
  "target": "work_qinghuaci",
  "type": "PERFORMED",
  "meta": {
    "confidence": 1.0
  }
}
```

前端和后端都应围绕这个结构工作，避免字段混乱。

## 9. 开发顺序

### 第一步

- 启动 Neo4j
- 创建 schema 和索引
- 导入一批样例数据

### 第二步

- 写 `FastAPI` 搜索和图查询接口
- 用 Swagger 验证接口

### 第三步

- 初始化 React 项目
- 接入 `react-force-graph-3d`
- 对接搜索和子图接口

### 第四步

- 加详情面板
- 加路径查询
- 做交互细节优化

## 10. 最终结论

如果目标是尽快做出可用的 3D 音乐图谱，最优先的实现路径是：

- 后端用 `Python + FastAPI`
- 前端用 `React + TypeScript`
- 数据库用 `Neo4j`

这不是最重的方案，但对当前目标是最合适的方案。
