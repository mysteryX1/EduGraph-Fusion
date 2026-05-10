import React, { useEffect, useState } from 'react';
import UploadPanel from './components/UploadPanel';
import GraphView from './components/GraphView';
import MergePanel from './components/MergePanel';
import RagPanel from './components/RagPanel';
import FeedbackPanel from './components/FeedbackPanel';
import ReportPanel from './components/ReportPanel';
import { getStats, getTextbooks } from './api';

const getTextbookId = (textbook) => textbook?.id || textbook?.textbook_id || '';

const filterNodeSources = (sources, textbook) => {
  if (!Array.isArray(sources) || !textbook) return Array.isArray(sources) ? sources : [];

  const candidates = new Set(
    [textbook.id, textbook.textbook_id, textbook.title, textbook.filename, textbook.filename?.replace(/\.[^.]+$/, '')]
      .filter(Boolean)
      .map((value) => String(value).toLowerCase())
  );

  return sources.filter((source) => {
    const text = typeof source === 'string' ? source : source?.textbook_id || source?.filename || source?.title || source?.source_textbook;
    return text && candidates.has(String(text).toLowerCase());
  });
};

export default function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [selectedNode, setSelectedNode] = useState(null);
  const [textbooks, setTextbooks] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedTextbook, setSelectedTextbook] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const tbResult = await getTextbooks();
      if (tbResult.success) {
        setTextbooks(tbResult.data.textbooks || []);
      }

      const statsResult = await getStats();
      if (statsResult.success) {
        setStats(statsResult.data);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleSelectTextbook = (textbook) => {
    setSelectedTextbook(textbook);
    setSelectedNode(null);
  };

  const handleUploadSuccess = (data) => {
    setSelectedTextbook(data);
    setSelectedNode(null);
    loadData();
  };

  const handleNodeClick = (nodeData) => {
    if (!nodeData) {
      setSelectedNode(null);
      return;
    }

    const matchedSources = filterNodeSources(nodeData.sources, selectedTextbook);
    setSelectedNode({
      ...nodeData,
      name: nodeData.name || nodeData.label || '未命名知识点',
      definition: nodeData.definition || nodeData.description || '暂无定义',
      chapter: nodeData.chapter || nodeData.section || '未知',
      page: nodeData.page || nodeData.pages || '-',
      source_textbook:
        nodeData.source_textbook ||
        nodeData.textbook_id ||
        nodeData.source ||
        selectedTextbook?.title ||
        selectedTextbook?.filename ||
        '未知',
      frequency: nodeData.frequency || nodeData.raw_frequency || 0,
      sources: matchedSources,
      degree: nodeData.degree || 0,
      category: nodeData.category || nodeData.type || '其他',
    });
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <h2 style={{ fontSize: 16, marginBottom: 16, color: '#333' }}>教材管理</h2>

        {stats && (
          <div className="stats" style={{ marginBottom: 16 }}>
            <div className="stat-card">
              <div className="stat-label">教材数</div>
              <div className="stat-value">{stats.total_textbooks || 0}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">章节数</div>
              <div className="stat-value">{stats.total_chapters || 0}</div>
            </div>
          </div>
        )}

        <div className="section-title">已上传教材</div>
        {textbooks.length === 0 ? (
          <div style={{ fontSize: 12, color: '#999', padding: '20px 0', textAlign: 'center' }}>暂无教材</div>
        ) : (
          <div className="textbook-list">
            {textbooks.map((tb) => (
              <div
                key={getTextbookId(tb)}
                className={`textbook-item ${getTextbookId(selectedTextbook) === getTextbookId(tb) ? 'active' : ''}`}
                onClick={() => handleSelectTextbook(tb)}
              >
                <div className="textbook-item-name">{tb.title || tb.filename || getTextbookId(tb)}</div>
                <div className="textbook-item-info">
                  <span>{tb.chapter_count || 0} 章</span>
                  <span>{Math.round((tb.total_words || 0) / 1000)}K 字</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="main-content">
        <div className="header">
          <h1>EduGraph Fusion - 教材知识图谱</h1>
        </div>

        <div className="content-wrapper">
          <div className="graph-container">
            <GraphView selectedTextbook={selectedTextbook} onNodeClick={handleNodeClick} />
          </div>

          <div className="right-panel">
            <div className="tabs">
              <button className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}>
                上传
              </button>
              <button className={`tab-btn ${activeTab === 'merge' ? 'active' : ''}`} onClick={() => setActiveTab('merge')}>
                整合
              </button>
              <button className={`tab-btn ${activeTab === 'rag' ? 'active' : ''}`} onClick={() => setActiveTab('rag')}>
                检索
              </button>
              <button
                className={`tab-btn ${activeTab === 'feedback' ? 'active' : ''}`}
                onClick={() => setActiveTab('feedback')}
              >
                反馈
              </button>
              <button className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`} onClick={() => setActiveTab('report')}>
                报告
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'upload' && <UploadPanel onUploadSuccess={handleUploadSuccess} />}
              {activeTab === 'merge' && <MergePanel />}
              {activeTab === 'rag' && <RagPanel />}
              {activeTab === 'feedback' && <FeedbackPanel />}
              {activeTab === 'report' && <ReportPanel />}

              {selectedNode && (
                <>
                  <div className="divider" style={{ marginTop: 20 }}></div>
                  <div className="section-title">节点详情</div>
                  <div className="node-details">
                    <div className="node-details-title">{selectedNode.name}</div>

                    <div className="node-details-item">
                      <div className="node-details-label">定义/描述</div>
                      <div className="node-details-value">{selectedNode.definition}</div>
                    </div>

                    <div className="node-details-item">
                      <div className="node-details-label">当前教材来源</div>
                      <div className="node-details-value">{selectedNode.source_textbook}</div>
                    </div>

                    <div className="node-details-item">
                      <div className="node-details-label">章节</div>
                      <div className="node-details-value">{selectedNode.chapter}</div>
                    </div>

                    <div className="node-details-item">
                      <div className="node-details-label">页码</div>
                      <div className="node-details-value">{selectedNode.page}</div>
                    </div>

                    <div className="node-details-item">
                      <div className="node-details-label">分类 / 频次 / 连接数</div>
                      <div className="node-details-value">
                        {selectedNode.category} / {selectedNode.frequency} / {selectedNode.degree}
                      </div>
                    </div>

                    {selectedNode.sources?.length > 0 && (
                      <div className="node-details-item">
                        <div className="node-details-label">匹配来源</div>
                        <div className="node-details-value">{selectedNode.sources.map(String).join('，')}</div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
