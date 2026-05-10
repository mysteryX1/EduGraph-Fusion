import React, { useState, useEffect } from 'react';
import { buildRagIndex, queryRag, getRagStatus } from '../api';

export default function RagPanel() {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [indexLoading, setIndexLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const res = await getRagStatus();
      if (res.success) {
        setStatus(res.data);
      }
    } catch (error) {
      console.error('Failed to check status:', error);
    }
  };

  const handleBuildIndex = async () => {
    setIndexLoading(true);
    setMessage(null);

    try {
      const res = await buildRagIndex();
      if (res.success) {
        setMessage({
          type: 'success',
          text: `索引构建完成: ${res.data.chunk_count} 个文本块, ${res.data.textbook_count} 本教材`,
        });
        setStatus(res.data);
      } else {
        setMessage({ type: 'error', text: '索引构建失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setIndexLoading(false);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
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
      const res = await queryRag(question, topK);
      if (res.success) {
        // 安全地处理响应数据
        const data = res.data || {};
        setResult({
          question: data.question || question,
          answer: data.answer || '当前知识库中未找到相关信息',
          citations: Array.isArray(data.citations) ? data.citations : [],
          source_chunks: Array.isArray(data.source_chunks) ? data.source_chunks : [],
        });
      } else {
        setMessage({
          type: 'error',
          text: res.error || '查询失败',
        });
      }
    } catch (error) {
      // 确保 catch 块不会导致白屏
      console.error('Query error:', error);
      setMessage({
        type: 'error',
        text: '查询出错：' + (error.message || '未知错误'),
      });
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-panel">
      <div className="section-title">知识检索</div>

      {!status?.indexed ? (
        <>
          <div className="alert alert-info">
            <span className="alert-message">需要先构建 RAG 索引以启用知识检索</span>
          </div>

          <button
            className={`btn btn-primary btn-full-width ${indexLoading ? 'loading' : ''}`}
            onClick={handleBuildIndex}
            disabled={indexLoading}
          >
            {indexLoading && <span className="loading-spinner"></span>}
            {indexLoading ? '构建中...' : '构建索引'}
          </button>
        </>
      ) : (
        <>
          <div className="stats">
            <div className="stat-card">
              <div className="stat-label">文本块</div>
              <div className="stat-value">{status?.chunk_count || 0}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">教材数</div>
              <div className="stat-value">{status?.textbook_count || 0}</div>
            </div>
          </div>

          <form onSubmit={handleQuery}>
            <div className="form-group">
              <label>输入问题</label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="例如: 什么是函数?"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>返回结果数 (Top-K)</label>
              <input
                type="number"
                value={topK}
                onChange={(e) => setTopK(Math.max(1, parseInt(e.target.value) || 5))}
                min="1"
                max="20"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className={`btn btn-primary btn-full-width ${loading ? 'loading' : ''}`}
              disabled={loading || !question.trim()}
            >
              {loading && <span className="loading-spinner"></span>}
              {loading ? '查询中...' : '搜索'}
            </button>
          </form>
        </>
      )}

      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginTop: '12px' }}>
          <span className="alert-message">{message.text}</span>
        </div>
      )}

      {result && (
        <div style={{ marginTop: '16px', background: '#fff', padding: '12px', borderRadius: '4px', border: '1px solid #e0e0e0' }}>
          <div className="section-title" style={{ marginTop: 0 }}>查询结果</div>

          <div className="form-group">
            <label style={{ color: '#666', fontWeight: 'normal' }}>问题</label>
            <div style={{ fontSize: '13px', color: '#333', padding: '8px', background: '#f5f5f5', borderRadius: '3px' }}>
              {result.question}
            </div>
          </div>

          <div className="form-group">
            <label style={{ color: '#666', fontWeight: 'normal' }}>回答</label>
            <div style={{ fontSize: '13px', color: '#333', lineHeight: '1.6', padding: '8px', background: '#f5f5f5', borderRadius: '3px', maxHeight: '200px', overflowY: 'auto' }}>
              {result.answer}
            </div>
          </div>

          {result.citations && result.citations.length > 0 && (
            <div className="form-group">
              <label style={{ color: '#666', fontWeight: 'normal' }}>引用来源</label>
              <div style={{ fontSize: '12px' }}>
                {result.citations.map((citation, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '6px 8px',
                      background: '#f5f5f5',
                      borderRadius: '3px',
                      marginBottom: '4px',
                      color: '#666',
                    }}
                  >
                    {citation}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
