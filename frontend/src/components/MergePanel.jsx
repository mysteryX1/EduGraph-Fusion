import React, { useState, useEffect } from 'react';
import { mergeGraphs, getMergeDecisions } from '../api';

export default function MergePanel() {
  const [loading, setLoading] = useState(false);
  const [decisions, setDecisions] = useState([]);
  const [message, setMessage] = useState(null);
  const [localDecisions, setLocalDecisions] = useState([]);

  useEffect(() => {
    loadDecisions();
  }, []);

  const loadDecisions = async () => {
    try {
      const result = await getMergeDecisions();
      if (result.success) {
        setDecisions(result.data.decisions || []);
      }
    } catch (error) {
      console.error('Failed to load decisions:', error);
    }
  };

  const handleMerge = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const result = await mergeGraphs(localDecisions);
      if (result.success) {
        setMessage({
          type: 'success',
          text: `合并成功: ${result.data.merged_count} 个节点, 移除 ${result.data.removed_duplicates} 个重复项`,
        });
        setLocalDecisions([]);
        loadDecisions();
      } else {
        setMessage({ type: 'error', text: '合并失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setLoading(false);
    }
  };

  const toggleDecision = (decisionId) => {
    setLocalDecisions((prev) => {
      if (prev.includes(decisionId)) {
        return prev.filter((d) => d !== decisionId);
      } else {
        return [...prev, decisionId];
      }
    });
  };

  return (
    <div className="merge-panel">
      <div className="section-title">图谱合并</div>

      {decisions.length === 0 ? (
        <div
          style={{
            padding: '20px',
            textAlign: 'center',
            color: '#999',
            fontSize: '13px',
          }}
        >
          <p>暂无合并建议</p>
          <p style={{ marginTop: '8px', fontSize: '12px' }}>
            在多个教材的知识图谱中检测到重复或相似节点时，将显示合并建议。
          </p>
        </div>
      ) : (
        <>
          <div className="divider"></div>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '12px' }}>
            共检测到 {decisions.length} 个可能的合并点
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
            {decisions.map((decision, idx) => (
              <div
                key={idx}
                style={{
                  padding: '10px',
                  background: '#fff',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  borderColor: localDecisions.includes(idx) ? '#1890ff' : '#e0e0e0',
                  backgroundColor: localDecisions.includes(idx) ? '#e6f7ff' : '#fff',
                }}
                onClick={() => toggleDecision(idx)}
              >
                <div style={{ fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>
                  ✓ {decision.source_node} → {decision.target_node}
                </div>
                <div style={{ fontSize: '11px', color: '#999' }}>
                  相似度: {(decision.similarity * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>

          {localDecisions.length > 0 && (
            <button
              className={`btn btn-primary btn-full-width ${loading ? 'loading' : ''}`}
              onClick={handleMerge}
              disabled={loading}
            >
              {loading && <span className="loading-spinner"></span>}
              {loading ? '合并中...' : `确认合并 (${localDecisions.length})`}
            </button>
          )}
        </>
      )}

      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginTop: '12px' }}>
          <span className="alert-message">{message.text}</span>
        </div>
      )}

      <div className="divider" style={{ marginTop: '20px' }}></div>
      <div style={{ fontSize: '11px', color: '#999', lineHeight: '1.6' }}>
        <p>
          图谱合并可以：
        </p>
        <ul style={{ marginLeft: '16px', marginTop: '6px' }}>
          <li>消除知识重复</li>
          <li>统一概念表示</li>
          <li>增强图谱一致性</li>
        </ul>
      </div>
    </div>
  );
}
