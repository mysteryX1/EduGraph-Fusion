import React, { useState } from 'react';
import { uploadFile, parseTextbook } from '../api';

export default function UploadPanel({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [parseLoading, setParseLoading] = useState(false);
  const [selectedTextbookId, setSelectedTextbookId] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: '请选择文件' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await uploadFile(file);
      if (result.success) {
        setMessage({
          type: 'success',
          text: `文件 "${file.name}" 上传成功`,
        });
        setFile(null);
        setSelectedTextbookId(result.data.textbook_id);
        onUploadSuccess(result.data);
      } else {
        setMessage({ type: 'error', text: '上传失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleParse = async () => {
    if (!selectedTextbookId) {
      setMessage({ type: 'error', text: '请先上传文件' });
      return;
    }

    setParseLoading(true);
    setMessage(null);

    try {
      const result = await parseTextbook(selectedTextbookId);
      if (result.success) {
        setMessage({
          type: 'success',
          text: `解析完成: ${result.data.chapter_count} 章, ${result.data.total_words} 字`,
        });
      } else {
        setMessage({ type: 'error', text: '解析失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setParseLoading(false);
    }
  };

  return (
    <div className="upload-panel">
      <div className="section-title">文件上传</div>

      <div className="form-group">
        <label>选择文件 (PDF/Markdown/Text)</label>
        <div className="file-input-wrapper">
          <input
            type="file"
            className="file-input"
            id="file-upload"
            onChange={handleFileChange}
            accept=".pdf,.md,.markdown,.txt"
            disabled={loading}
          />
          <label htmlFor="file-upload" className="file-input-label">
            {file ? file.name : '点击选择文件或拖拽'}
          </label>
        </div>
      </div>

      <button
        className={`btn btn-primary btn-full-width ${loading ? 'loading' : ''}`}
        onClick={handleUpload}
        disabled={loading || !file}
      >
        {loading && <span className="loading-spinner"></span>}
        {loading ? '上传中...' : '上传'}
      </button>

      {selectedTextbookId && (
        <>
          <div className="divider"></div>
          <div className="section-title">文件解析</div>
          <p style={{ fontSize: '12px', color: '#666', marginBottom: '12px' }}>
            ID: {selectedTextbookId.slice(0, 20)}...
          </p>

          <button
            className={`btn btn-primary btn-full-width ${parseLoading ? 'loading' : ''}`}
            onClick={handleParse}
            disabled={parseLoading}
          >
            {parseLoading && <span className="loading-spinner"></span>}
            {parseLoading ? '解析中...' : '开始解析'}
          </button>
        </>
      )}

      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginTop: '12px' }}>
          <span className="alert-message">{message.text}</span>
        </div>
      )}

      <div className="divider" style={{ marginTop: '20px' }}></div>
      <div style={{ fontSize: '12px', color: '#999', lineHeight: '1.6' }}>
        <p>支持的格式:</p>
        <ul style={{ marginLeft: '16px', marginTop: '8px' }}>
          <li>PDF (.pdf) - 最大 100MB</li>
          <li>Markdown (.md)</li>
          <li>纯文本 (.txt)</li>
        </ul>
      </div>
    </div>
  );
}
