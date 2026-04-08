import type { SearchItem } from "../types/graph";

interface SearchPanelProps {
  query: string;
  entityType: string;
  pathFrom: string;
  pathTo: string;
  loading: boolean;
  pathLoading: boolean;
  results: SearchItem[];
  onQueryChange: (value: string) => void;
  onEntityTypeChange: (value: string) => void;
  onPathFromChange: (value: string) => void;
  onPathToChange: (value: string) => void;
  onSearch: () => void;
  onSearchKeyDown: (value: string) => void;
  onSelect: (item: SearchItem) => void;
  onHighlightPath: () => void;
}

const ENTITY_TYPES = ["", "Person", "Band", "Work", "Album", "Genre"];

export function SearchPanel(props: SearchPanelProps) {
  const {
    query,
    entityType,
    pathFrom,
    pathTo,
    loading,
    pathLoading,
    results,
    onQueryChange,
    onEntityTypeChange,
    onPathFromChange,
    onPathToChange,
    onSearch,
    onSearchKeyDown,
    onSelect,
    onHighlightPath,
  } = props;

  return (
    <aside className="panel panel-left">
      <div className="panel-header">
        <p className="eyebrow">Search</p>
        <h1>MusicGraph</h1>
        <p className="panel-copy">
          Search artists, bands, works, and albums, then expand their local graph in 3D.
        </p>
      </div>

      <section className="stack">
        <label className="field-label" htmlFor="search-input">
          Keyword
        </label>
        <div className="search-row">
          <input
            id="search-input"
            className="text-input"
            placeholder="Jay Chou, 青花瓷, 五月天..."
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                onSearchKeyDown(query);
              }
            }}
          />
          <button className="primary-button" onClick={onSearch} disabled={loading}>
            {loading ? "Searching" : "Search"}
          </button>
        </div>

        <label className="field-label" htmlFor="entity-type">
          Entity type
        </label>
        <select
          id="entity-type"
          className="text-input"
          value={entityType}
          onChange={(event) => onEntityTypeChange(event.target.value)}
        >
          {ENTITY_TYPES.map((option) => (
            <option key={option || "all"} value={option}>
              {option || "All"}
            </option>
          ))}
        </select>
      </section>

      <section className="stack">
        <div className="section-title">
          <h2>Results</h2>
          <span>{results.length}</span>
        </div>
        <div className="result-list">
          {results.length === 0 ? (
            <p className="placeholder">Run a search to load entities.</p>
          ) : (
            results.map((item) => (
              <button
                key={item.id}
                className="result-card"
                onClick={() => onSelect(item)}
                type="button"
              >
                <span className={`type-pill type-${item.type.toLowerCase()}`}>{item.type}</span>
                <strong>{item.name}</strong>
                <small>{item.id}</small>
                <p>{item.summary ?? "No summary available."}</p>
              </button>
            ))
          )}
        </div>
      </section>

      <section className="stack">
        <div className="section-title">
          <h2>Path Tool</h2>
          <span>2 nodes</span>
        </div>
        <input
          className="text-input"
          placeholder="Source entity id"
          value={pathFrom}
          onChange={(event) => onPathFromChange(event.target.value)}
        />
        <input
          className="text-input"
          placeholder="Target entity id"
          value={pathTo}
          onChange={(event) => onPathToChange(event.target.value)}
        />
        <button className="secondary-button" onClick={onHighlightPath} disabled={pathLoading}>
          {pathLoading ? "Loading path" : "Highlight path"}
        </button>
      </section>
    </aside>
  );
}
