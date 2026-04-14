import type { SearchItem } from "../types/graph";

interface SearchPanelProps {
  dataSourceLabel: string;
  query: string;
  entityType: string;
  loading: boolean;
  results: SearchItem[];
  selectedEntityId: string | null;
  sampleItems: SearchItem[];
  graphNodeCount: number;
  graphLinkCount: number;
  expandedCount: number;
  onQueryChange: (value: string) => void;
  onEntityTypeChange: (value: string) => void;
  onSearch: () => void;
  onSearchKeyDown: () => void;
  onSelect: (item: SearchItem) => void;
}

const ENTITY_TYPES = ["", "Person", "Location", "Event", "Title", "Band", "Work", "Album", "Genre"];

export function SearchPanel(props: SearchPanelProps) {
  const {
    dataSourceLabel,
    query,
    entityType,
    loading,
    results,
    selectedEntityId,
    sampleItems,
    graphNodeCount,
    graphLinkCount,
    expandedCount,
    onQueryChange,
    onEntityTypeChange,
    onSearch,
    onSearchKeyDown,
    onSelect,
  } = props;

  return (
    <aside className="panel panel-left">
      <div className="panel-header panel-hero">
        <p className="eyebrow">Knowledge Explorer</p>
        <h1>关系知识图谱</h1>
        <p className="panel-copy">
          搜索人物、地点、事件、作品等实体，在 3D 空间里逐层展开当前数据集的关系网络。
        </p>
      </div>

      <section className="stack glass-block">
        <div className="section-title">
          <h2>当前图谱</h2>
          <span>Live</span>
        </div>
        <div className="metric-grid">
          <div className="metric-card">
            <span>节点</span>
            <strong>{graphNodeCount}</strong>
          </div>
          <div className="metric-card">
            <span>关系</span>
            <strong>{graphLinkCount}</strong>
          </div>
          <div className="metric-card metric-card-wide">
            <span>已展开核心节点</span>
            <strong>{expandedCount}</strong>
          </div>
        </div>
      </section>

      <section className="stack glass-block">
        <div className="section-title">
          <h2>快速开始</h2>
          <span>{dataSourceLabel}</span>
        </div>
        <div className="sample-grid">
          {sampleItems.length === 0 ? (
            <p className="placeholder">当前后端还没有返回可用示例实体。</p>
          ) : (
            sampleItems.map((item) => (
              <button
                key={item.id}
                className={`sample-chip ${selectedEntityId === item.id ? "is-active" : ""}`}
                onClick={() => onSelect(item)}
                type="button"
              >
                <span>{item.name}</span>
                <small>{item.type}</small>
              </button>
            ))
          )}
        </div>
      </section>

      <section className="stack glass-block">
        <label className="field-label" htmlFor="search-input">
          搜索实体
        </label>
        <div className="search-row">
          <input
            id="search-input"
            className="text-input"
            placeholder="刘备、诸葛亮、赤壁之战、周杰伦..."
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                onSearchKeyDown();
              }
            }}
          />
          <button className="primary-button" onClick={onSearch} disabled={loading}>
            {loading ? "搜索中" : "搜索"}
          </button>
        </div>

        <label className="field-label" htmlFor="entity-type">
          实体类型
        </label>
        <select
          id="entity-type"
          className="text-input"
          value={entityType}
          onChange={(event) => onEntityTypeChange(event.target.value)}
        >
          {ENTITY_TYPES.map((option) => (
            <option key={option || "all"} value={option}>
              {option || "全部"}
            </option>
          ))}
        </select>
      </section>

      <section className="stack glass-block">
        <div className="section-title">
          <h2>搜索结果</h2>
          <span>{results.length}</span>
        </div>
        <div className="result-list">
          {results.length === 0 ? (
            <p className="placeholder">先输入关键词，或者直接点击上方示例实体。</p>
          ) : (
            results.map((item) => (
              <button
                key={item.id}
                className={`result-card ${selectedEntityId === item.id ? "is-active" : ""}`}
                onClick={() => onSelect(item)}
                type="button"
              >
                <span className={`type-pill type-${item.type.toLowerCase()}`}>{item.type}</span>
                <strong>{item.name}</strong>
                <small>{item.id}</small>
                <p>{item.summary ?? "暂无简介。"}</p>
              </button>
            ))
          )}
        </div>
      </section>
    </aside>
  );
}
