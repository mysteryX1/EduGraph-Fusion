import React, { useState, useEffect } from 'react';
import { generateReport, getLatestReport, getReportSummary } from '../api';

export default function ReportPanel() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [reportSummary, setReportSummary] = useState(null);

  useEffect(() => {
    loadReportSummary();
  }, []);

  const loadReportSummary = async () => {
    try {
      const result = await getReportSummary();
      if (result.success) {
        setReportSummary(result.data);
      }
    } catch (error) {
      console.error('Failed to load report summary:', error);
    }
  };

  const handleGenerateReport = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const result = await generateReport({
        include_statistics: true,
        include_graph_analysis: true,
        include_recommendations: true,
      });

      if (result.success) {
        setMessage({
          type: 'success',
          text: '报告生成成功！报告 ID: ' + result.data.report_id,
        });
        loadReportSummary();
      } else {
        setMessage({ type: 'error', text: '报告生成失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleViewLatest = async () => {
    setLoading(true);
    try {
      const result = await getLatestReport();
      if (result.success) {
        setReportData(result.data);
      } else {
        setMessage({ type: 'error', text: '加载报告失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-panel">
      <div className="section-title">综合报告</div>

      <div style={{ marginBottom: '16px' }}>
        <button
          className={`btn btn-primary btn-full-width ${loading ? 'loading' : ''}`}
          onClick={handleGenerateReport}
          disabled={loading}
        >
          {loading && <span className="loading-spinner"></span>}
          {loading ? '生成中...' : '生成新报告'}
        </button>
      </div>

      {reportSummary && (
        <>
          <div className="divider"></div>
          <div className="section-title">最新报告</div>

          <div className="stat-card" style={{ marginBottom: '12px' }}>
            <div className="stat-label">报告 ID</div>
            <div style={{ fontSize: '12px', color: '#666', wordBreak: 'break-all', marginTop: '4px' }}>
              {reportSummary.latest_report}
            </div>
          </div>

          <div className="stat-card" style={{ marginBottom: '12px' }}>
            <div className="stat-label">生成时间</div>
            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              {reportSummary.generated_at
                ? new Date(reportSummary.generated_at).toLocaleString('zh-CN')
                : '暂无'}
            </div>
          </div>

          <button
            className="btn btn-secondary btn-full-width"
            onClick={handleViewLatest}
            disabled={loading || !reportSummary.latest_report}
          >
            查看详情
          </button>
        </>
      )}

      {reportData && (
        <>
          <div className="divider"></div>
          <div className="section-title">报告内容</div>

          <div
            style={{
              padding: '12px',
              background: '#f5f5f5',
              borderRadius: '4px',
              maxHeight: '300px',
              overflowY: 'auto',
              fontSize: '12px',
              lineHeight: '1.6',
              color: '#666',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {reportData.content || '(空)'}
          </div>
        </>
      )}

      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginTop: '12px' }}>
          <span className="alert-message">{message.text}</span>
        </div>
      )}

      <div className="divider" style={{ marginTop: '20px' }}></div>
      <div style={{ fontSize: '11px', color: '#999', lineHeight: '1.6' }}>
        <p>报告包括：</p>
        <ul style={{ marginLeft: '16px', marginTop: '6px' }}>
          <li>知识图谱统计分析</li>
          <li>教材信息汇总</li>
          <li>系统建议</li>
          <li>质量指标评分</li>
        </ul>
      </div>
    </div>
  );
}
