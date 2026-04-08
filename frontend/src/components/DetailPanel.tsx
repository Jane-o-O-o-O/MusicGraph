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
        <p className="eyebrow">Entity Detail</p>
        <h2>{entity?.name ?? "等待选择实体"}</h2>
        <p className="panel-copy">
          {entity?.summary ?? "点击搜索结果或图中节点，这里会展示实体概览与附加属性。"}
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
              <span>类型</span>
              <strong>{entity.type}</strong>
            </div>
            <div className="detail-item detail-item-wide">
              <span>别名</span>
              <strong>{entity.aliases.length > 0 ? entity.aliases.join(" / ") : "-"}</strong>
            </div>
          </div>

          <section className="stack glass-block glass-block-soft">
            <div className="section-title">
              <h3>扩展属性</h3>
              <span>{Object.keys(entity.meta).length}</span>
            </div>
            <div className="meta-list">
              {Object.entries(entity.meta).length === 0 ? (
                <p className="placeholder">当前实体没有额外元数据。</p>
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
            可以继续点击图中的相邻节点，围绕当前实体逐层扩展一跳邻居，逐步构建你自己的音乐子图。
          </div>
        </>
      ) : (
        <div className="status-card status-card-muted">左侧快速开始区已经提供了几个样例入口，可直接体验图谱展开。</div>
      )}
    </aside>
  );
}
