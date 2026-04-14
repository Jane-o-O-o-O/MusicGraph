import type { GraphRagResponse } from "../types/graph";

interface GraphRagDockProps {
  question: string;
  loading: boolean;
  result: GraphRagResponse | null;
  selectedEntityId: string | null;
  onQuestionChange: (value: string) => void;
  onSubmit: () => void;
}

export function GraphRagDock(props: GraphRagDockProps) {
  const { question, loading, result, selectedEntityId, onQuestionChange, onSubmit } = props;

  return (
    <div className="graphrag-dock-region">
      <section className="graphrag-dock">
        <div className="section-title graphrag-dock-header">
          <h2>GraphRAG 问答</h2>
          <span>{selectedEntityId ? "含当前焦点" : "全图检索"}</span>
        </div>

        {result ? (
          <div className="graphrag-dock-result">
            <div className="status-card">
              <strong>回答</strong>
              <p className="panel-note">{result.answer}</p>
            </div>
            <div className="status-card status-card-muted">
              <strong>命中实体</strong>
              <p className="panel-note">
                {result.matched_entities.length > 0
                  ? result.matched_entities.map((item) => item.name).join(" / ")
                  : "暂无"}
              </p>
            </div>
          </div>
        ) : (
          <p className="panel-note graphrag-dock-note">
            问答会基于图谱检索相关实体、关系和路径，并把相关子图并入当前视图。
          </p>
        )}

        <div className="graphrag-dock-controls">
          <input
            className="text-input graphrag-dock-input"
            placeholder="例如：刘备和诸葛亮有什么关系？"
            value={question}
            onChange={(event) => onQuestionChange(event.target.value)}
          />
          <button className="secondary-button graphrag-dock-button" onClick={onSubmit} disabled={loading}>
            {loading ? "问答生成中" : "提问"}
          </button>
        </div>
      </section>
    </div>
  );
}
