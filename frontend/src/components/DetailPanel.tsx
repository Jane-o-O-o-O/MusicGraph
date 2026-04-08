import type { EntityDetails } from "../types/graph";

interface DetailPanelProps {
  entity: EntityDetails | null;
  errorMessage: string | null;
}

function formatMetaValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.join(", ");
  }
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  return String(value);
}

export function DetailPanel({ entity, errorMessage }: DetailPanelProps) {
  return (
    <aside className="panel panel-right">
      <div className="panel-header">
        <p className="eyebrow">Detail</p>
        <h2>{entity?.name ?? "No entity selected"}</h2>
        <p className="panel-copy">
          {entity?.summary ?? "Click a search result or graph node to inspect the entity."}
        </p>
      </div>

      {errorMessage ? <div className="status-card error">{errorMessage}</div> : null}

      {entity ? (
        <>
          <div className="detail-grid">
            <div className="detail-item">
              <span>ID</span>
              <strong>{entity.id}</strong>
            </div>
            <div className="detail-item">
              <span>Type</span>
              <strong>{entity.type}</strong>
            </div>
            <div className="detail-item">
              <span>Aliases</span>
              <strong>{entity.aliases.length > 0 ? entity.aliases.join(", ") : "-"}</strong>
            </div>
          </div>

          <section className="stack">
            <div className="section-title">
              <h3>Metadata</h3>
              <span>{Object.keys(entity.meta).length}</span>
            </div>
            <div className="meta-list">
              {Object.entries(entity.meta).length === 0 ? (
                <p className="placeholder">No extra metadata.</p>
              ) : (
                Object.entries(entity.meta).map(([key, value]) => (
                  <div className="meta-row" key={key}>
                    <span>{key}</span>
                    <strong>{formatMetaValue(value)}</strong>
                  </div>
                ))
              )}
            </div>
          </section>
        </>
      ) : (
        <div className="status-card">Load an entity to populate this panel.</div>
      )}
    </aside>
  );
}
