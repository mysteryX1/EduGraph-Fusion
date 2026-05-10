import React, { useState } from 'react';
import { submitFeedback } from '../api';

export default function FeedbackPanel() {
  const [feedbackType, setFeedbackType] = useState('bug');
  const [content, setContent] = useState('');
  const [relatedNode, setRelatedNode] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!content.trim()) {
      setMessage({ type: 'error', text: '请输入反馈内容' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // 后端期望 instruction 字段
      const feedbackData = {
        instruction: content.trim(),
      };

      const result = await submitFeedback(feedbackData);
      if (result.success) {
        setMessage({
          type: 'success',
          text: '反馈已提交，感谢您的意见！',
        });
        setContent('');
        setRelatedNode('');
        setFeedbackType('bug');
      } else {
        setMessage({
          type: 'error',
          text: result.error || '提交失败，请稍后重试',
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: '提交失败：' + (error.message || '未知错误'),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feedback-panel">
      <div className="section-title">用户反馈</div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>反馈类型</label>
          <select
            value={feedbackType}
            onChange={(e) => setFeedbackType(e.target.value)}
            disabled={loading}
          >
            <option value="bug">缺陷报告</option>
            <option value="suggestion">建议改进</option>
            <option value="question">问题咨询</option>
            <option value="other">其他</option>
          </select>
        </div>

        <div className="form-group">
          <label>反馈内容</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="请详细描述您的反馈..."
            disabled={loading}
            rows="5"
          />
        </div>

        <div className="form-group">
          <label>相关知识点 (可选)</label>
          <input
            type="text"
            value={relatedNode}
            onChange={(e) => setRelatedNode(e.target.value)}
            placeholder="例如: 函数, 导数等"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className={`btn btn-primary btn-full-width ${loading ? 'loading' : ''}`}
          disabled={loading}
        >
          {loading && <span className="loading-spinner"></span>}
          {loading ? '提交中...' : '提交反馈'}
        </button>
      </form>

      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginTop: '12px' }}>
          <span className="alert-message">{message.text}</span>
        </div>
      )}

      <div className="divider" style={{ marginTop: '20px' }}></div>
      <div style={{ fontSize: '11px', color: '#999', lineHeight: '1.6' }}>
        <p>您的反馈帮助我们：</p>
        <ul style={{ marginLeft: '16px', marginTop: '6px' }}>
          <li>改进系统功能</li>
          <li>修复已发现的问题</li>
          <li>优化用户体验</li>
          <li>建立更完整的知识库</li>
        </ul>
      </div>
    </div>
  );
}
