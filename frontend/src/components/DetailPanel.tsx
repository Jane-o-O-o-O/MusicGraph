import type { EntityDetails } from "../types/graph";

interface DetailPanelProps {
  entity: EntityDetails | null;
  errorMessage: string | null;
  visible: boolean;
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

export function DetailPanel({ entity, errorMessage, visible }: DetailPanelProps) {
  return (
    <aside className={`panel panel-right ${visible ? "is-visible" : "is-hidden"}`}>
      <div className="panel-header">
        <p className="eyebrow">Entity Detail</p>
        <h2>{entity?.name ?? "\u7b49\u5f85\u9009\u62e9\u5b9e\u4f53"}</h2>
        <p className="panel-copy">
          {entity?.summary ?? "\u70b9\u51fb\u641c\u7d22\u7ed3\u679c\u6216\u56fe\u4e2d\u8282\u70b9\uff0c\u8fd9\u91cc\u4f1a\u5c55\u793a\u5b9e\u4f53\u6982\u89c8\u4e0e\u9644\u52a0\u5c5e\u6027\u3002"}
        </p>
      </div>

      {errorMessage ? <div className="status-card error">{errorMessage}</div> : null}

      {entity ? (
        <>
          <div className="detail-grid">
            <div className="detail-item detail-item-strong">
              <span>ID</span>
              <strong>{entity.id}</strong>
            </div>
            <div className="detail-item">
              <span>{"\u7c7b\u578b"}</span>
              <strong>{entity.type}</strong>
            </div>
            <div className="detail-item detail-item-wide">
              <span>{"\u522b\u540d"}</span>
              <strong>{entity.aliases.length > 0 ? entity.aliases.join(" / ") : "-"}</strong>
            </div>
          </div>

          <section className="stack glass-block glass-block-soft">
            <div className="section-title">
              <h3>{"\u6269\u5c55\u5c5e\u6027"}</h3>
              <span>{Object.keys(entity.meta).length}</span>
            </div>
            <div className="meta-list">
              {Object.entries(entity.meta).length === 0 ? (
                <p className="placeholder">{"\u5f53\u524d\u5b9e\u4f53\u6ca1\u6709\u989d\u5916\u5143\u6570\u636e\u3002"}</p>
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

          <div className="status-card status-card-muted">
            {"\u53ef\u4ee5\u7ee7\u7eed\u70b9\u51fb\u56fe\u4e2d\u7684\u76f8\u90bb\u8282\u70b9\uff0c\u56f4\u7ed5\u5f53\u524d\u5b9e\u4f53\u9010\u5c42\u6269\u5c55\u4e00\u8df3\u90bb\u5c45\uff0c\u9010\u6b65\u6784\u5efa\u4f60\u81ea\u5df1\u7684\u97f3\u4e50\u5b50\u56fe\u3002"}
          </div>
        </>
      ) : (
        <div className="status-card status-card-muted">{"\u5de6\u4fa7\u5feb\u901f\u5f00\u59cb\u533a\u5df2\u7ecf\u63d0\u4f9b\u4e86\u51e0\u4e2a\u6837\u4f8b\u5165\u53e3\uff0c\u53ef\u76f4\u63a5\u4f53\u9a8c\u56fe\u8c31\u5c55\u5f00\u3002"}</div>
      )}
    </aside>
  );
}
