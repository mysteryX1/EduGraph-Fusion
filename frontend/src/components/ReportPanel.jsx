import React, { useEffect, useState } from 'react';
import { generateReport, getLatestReport, getReportSummary } from '../api';

const normalizeReport = (data) => ({
  report_id: data?.report_id || data?.id || 'latest',
  created_at: data?.created_at || data?.generated_at || new Date().toISOString(),
  content: data?.content || '',
  summary: data?.summary || '',
  report_path: data?.report_path || '',
});

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
      if (result.success) setReportSummary(result.data);
    } catch (error) {
      console.error('Failed to load report summary:', error);
    }
  };

  const loadLatestReport = async () => {
    const latest = await getLatestReport();
    if (!latest.success) {
      throw new Error(latest.error || '读取报告正文失败');
    }

    const normalized = normalizeReport(latest.data);
    if (!normalized.content) {
      throw new Error('报告已生成，但未读取到正文');
    }

    setReportData(normalized);
    return normalized;
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

      if (!result.success) {
        throw new Error(result.error || '报告生成失败');
      }

      const latest = await loadLatestReport();
      setMessage({
        type: 'success',
        text: `报告生成成功：${latest.report_id}`,
      });
      loadReportSummary();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.message || '报告生成失败',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewLatest = async () => {
    setLoading(true);
    setMessage(null);

    try {
      await loadLatestReport();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.message || '加载报告失败',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-panel">
      <div className="section-title">综合报告</div>

      <div style={{ marginBottom: 16 }}>
        <button className={`btn btn-primary btn-full-width ${loading ? 'loading' : ''}`} onClick={handleGenerateReport} disabled={loading}>
          {loading && <span className="loading-spinner"></span>}
          {loading ? '生成中...' : '生成新报告'}
        </button>
      </div>

      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginTop: 12, marginBottom: 12 }}>
          <span className="alert-message">{message.text}</span>
        </div>
      )}

      {reportSummary && (
        <>
          <div className="divider"></div>
          <div className="section-title">最新报告</div>

          <div className="stat-card" style={{ marginBottom: 12 }}>
            <div className="stat-label">报告 ID</div>
            <div style={{ fontSize: 12, color: '#666', wordBreak: 'break-all', marginTop: 4 }}>
              {reportSummary.latest_report || '暂无'}
            </div>
          </div>

          <div className="stat-card" style={{ marginBottom: 12 }}>
            <div className="stat-label">生成时间</div>
            <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
              {reportSummary.generated_at ? new Date(reportSummary.generated_at).toLocaleString('zh-CN') : '暂无'}
            </div>
          </div>

          <button className="btn btn-secondary btn-full-width" onClick={handleViewLatest} disabled={loading}>
            查看详情
          </button>
        </>
      )}

      {reportData && (
        <>
          <div className="divider"></div>
          <div className="section-title">报告正文</div>
          <div
            style={{
              padding: 12,
              background: '#f5f5f5',
              borderRadius: 4,
              maxHeight: 360,
              overflowY: 'auto',
              fontSize: 12,
              lineHeight: 1.6,
              color: '#333',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {reportData.content}
          </div>
        </>
      )}

      <div className="divider" style={{ marginTop: 20 }}></div>
      <div style={{ fontSize: 11, color: '#999', lineHeight: 1.6 }}>
        报告包含知识图谱统计、教材信息汇总、系统建议和质量指标。
      </div>
    </div>
  );
}
