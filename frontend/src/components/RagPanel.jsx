import React, { useEffect, useMemo, useState } from 'react';
import { buildRagIndex, getRagStatus, queryRag } from '../api';

const normalizeStatus = (data) => ({
  indexed: Boolean(data?.indexed),
  chunk_count: Number(data?.chunk_count || 0),
  textbook_count: Number(data?.textbook_count || 0),
});

const normalizeResult = (data, fallbackQuestion) => ({
  question: data?.question || fallbackQuestion,
  answer: data?.answer || '未找到相关答案',
  citations: Array.isArray(data?.citations) ? data.citations : [],
  source_chunks: Array.isArray(data?.source_chunks) ? data.source_chunks : [],
});

const valueAt = (obj, keys) => {
  for (const key of keys) {
    const value = key.split('.').reduce((current, part) => current?.[part], obj);
    if (value !== undefined && value !== null && value !== '') return value;
  }
  return null;
};

const formatCitation = (citation, index) => {
  if (typeof citation === 'string') {
    return citation;
  }

  const title = valueAt(citation, [
    'textbook_title',
    'textbook_name',
    'filename',
    'source_textbook',
    'metadata.title',
    'metadata.filename',
    'metadata.source_textbook',
  ]);
  const chapter = valueAt(citation, ['chapter', 'metadata.chapter', 'section', 'metadata.section']);
  const page = valueAt(citation, ['page', 'pages', 'metadata.page', 'metadata.pages']);
  const score = valueAt(citation, ['score', 'similarity', 'metadata.score']);

  const parts = [];
  if (title) parts.push(String(title));
  if (chapter) parts.push(String(chapter));
  if (page) parts.push(`p.${page}`);
  if (score !== null) {
    const numericScore = Number(score);
    parts.push(`score ${Number.isFinite(numericScore) ? numericScore.toFixed(2) : score}`);
  }

  return `来源 ${index + 1}：${parts.length > 0 ? parts.join(' / ') : '来源信息不完整'}`;
};

const buildCitationList = (result) => {
  const raw = result.citations.length > 0 ? result.citations : result.source_chunks;
  const seen = new Set();

  return raw
    .map((item, index) => formatCitation(item, index))
    .filter((text) => text && !/\[object Object\]|undefined/.test(text))
    .filter((text) => {
      if (seen.has(text)) return false;
      seen.add(text);
      return true;
    });
};

export default function RagPanel() {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [indexLoading, setIndexLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);

  const citations = useMemo(() => (result ? buildCitationList(result) : []), [result]);

  useEffect(() => {
    let cancelled = false;

    const loadStatus = async () => {
      try {
        const response = await getRagStatus();
        if (!cancelled && response.success) {
          setStatus(normalizeStatus(response.data));
        }
      } catch {
        if (!cancelled) setStatus(normalizeStatus(null));
      }
    };

    loadStatus();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleBuildIndex = async () => {
    setIndexLoading(true);
    setMessage(null);
    setResult(null);

    try {
      const response = await buildRagIndex();
      if (!response.success) throw new Error(response.error || '索引构建失败');

      const nextStatus = normalizeStatus({ ...response.data, indexed: true });
      setStatus(nextStatus);
      setMessage({
        type: 'success',
        text: `索引构建完成：${nextStatus.chunk_count} 个文本块，${nextStatus.textbook_count} 本教材`,
      });
    } catch (error) {
      setMessage({ type: 'error', text: error.message || '索引构建失败' });
    } finally {
      setIndexLoading(false);
    }
  };

  const handleQuery = async (event) => {
    event.preventDefault();
    const cleanQuestion = question.trim();

    if (!cleanQuestion) {
      setMessage({ type: 'error', text: '请输入问题' });
      return;
    }

    if (!status?.indexed) {
      setMessage({ type: 'error', text: '请先构建 RAG 索引' });
      return;
    }

    setLoading(true);
    setMessage(null);
    setResult(null);

    try {
      const response = await queryRag(cleanQuestion, topK);
      if (!response.success) throw new Error(response.error || '检索失败');
      setResult(normalizeResult(response.data, cleanQuestion));
    } catch (error) {
      setMessage({ type: 'error', text: error.message || '检索失败，请稍后重试' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-panel">
      <div className="section-title">知识检索</div>

      <div className="stats" style={{ marginBottom: 12 }}>
        <div className="stat-card">
          <div className="stat-label">索引状态</div>
          <div className="stat-value" style={{ fontSize: 16 }}>
            {status?.indexed ? '已建立' : '未建立'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">文本块</div>
          <div className="stat-value">{status?.chunk_count || 0}</div>
        </div>
      </div>

      <button
        type="button"
        className={`btn btn-primary btn-full-width ${indexLoading ? 'loading' : ''}`}
        onClick={handleBuildIndex}
        disabled={indexLoading || loading}
      >
        {indexLoading && <span className="loading-spinner"></span>}
        {indexLoading ? '构建中...' : '构建索引'}
      </button>

      <form onSubmit={handleQuery} style={{ marginTop: 14 }}>
        <div className="form-group">
          <label>输入问题</label>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="例如：什么是函数？"
            disabled={loading || indexLoading}
            rows="4"
          />
        </div>

        <div className="form-group">
          <label>返回结果数 Top-K</label>
          <input
            type="number"
            min="1"
            max="20"
            value={topK}
            onChange={(event) => setTopK(Math.max(1, Number.parseInt(event.target.value, 10) || 5))}
            disabled={loading || indexLoading}
          />
        </div>

        <button
          type="submit"
          className={`btn btn-primary btn-full-width ${loading ? 'loading' : ''}`}
          disabled={loading || indexLoading || !question.trim()}
        >
          {loading && <span className="loading-spinner"></span>}
          {loading ? '检索中...' : '搜索'}
        </button>
      </form>

      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginTop: 12 }}>
          <span className="alert-message">{message.text}</span>
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16, background: '#fff', padding: 12, borderRadius: 4, border: '1px solid #e0e0e0' }}>
          <div className="section-title" style={{ marginTop: 0 }}>
            检索结果
          </div>

          <div className="form-group">
            <label style={{ color: '#666', fontWeight: 'normal' }}>问题</label>
            <div style={{ fontSize: 13, color: '#333', padding: 8, background: '#f5f5f5', borderRadius: 3 }}>
              {result.question}
            </div>
          </div>

          <div className="form-group">
            <label style={{ color: '#666', fontWeight: 'normal' }}>答案</label>
            <div
              style={{
                fontSize: 13,
                color: '#333',
                lineHeight: 1.6,
                padding: 8,
                background: '#f5f5f5',
                borderRadius: 3,
                maxHeight: 220,
                overflowY: 'auto',
                whiteSpace: 'pre-wrap',
              }}
            >
              {result.answer}
            </div>
          </div>

          <div className="form-group">
            <label style={{ color: '#666', fontWeight: 'normal' }}>引用来源</label>
            {citations.length > 0 ? (
              <div style={{ fontSize: 12 }}>
                {citations.map((citation) => (
                  <div
                    key={citation}
                    style={{
                      padding: '6px 8px',
                      background: '#f5f5f5',
                      borderRadius: 3,
                      marginBottom: 4,
                      color: '#555',
                    }}
                  >
                    {citation}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ fontSize: 12, color: '#888' }}>暂无引用来源</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
