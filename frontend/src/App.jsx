import React, { useState, useEffect } from 'react';
import UploadPanel from './components/UploadPanel';
import GraphView from './components/GraphView';
import MergePanel from './components/MergePanel';
import RagPanel from './components/RagPanel';
import FeedbackPanel from './components/FeedbackPanel';
import ReportPanel from './components/ReportPanel';
import { getTextbooks, getStats } from './api';

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

  const handleUploadSuccess = (data) => {
    setSelectedTextbook(data);
    loadData();
  };

  const handleNodeClick = (nodeData) => {
    setSelectedNode({
      name: nodeData.name,
      definition: nodeData.definition || nodeData.description || '暂无定义',
      chapter: nodeData.chapter || '未知',
      page: nodeData.page || nodeData.pages || '-',
      source_textbook: nodeData.source_textbook || nodeData.source || '未知',
      frequency: nodeData.frequency || nodeData.value || 0,
      sources: nodeData.sources || [],
      degree: nodeData.degree || 0,
      category: nodeData.category || '其他',
    });
  };

  return (
    <div className="app-container">
      {/* 左侧：教材管理 */}
      <div className="sidebar">
        <h2 style={{ fontSize: '16px', marginBottom: '16px', color: '#333' }}>
          📚 教材管理
        </h2>

        {stats && (
          <div className="stats" style={{ marginBottom: '16px' }}>
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
          <div style={{ fontSize: '12px', color: '#999', padding: '20px 0', textAlign: 'center' }}>
            暂无教材
          </div>
        ) : (
          <div className="textbook-list">
            {textbooks.map((tb) => (
              <div
                key={tb.id}
                className={`textbook-item ${selectedTextbook?.textbook_id === tb.id ? 'active' : ''}`}
                onClick={() => setSelectedTextbook(tb)}
              >
                <div className="textbook-item-name">{tb.title}</div>
                <div className="textbook-item-info">
                  <span>{tb.chapter_count} 章</span>
                  <span>{(tb.total_words / 1000).toFixed(0)}K 字</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 中间和右侧 */}
      <div className="main-content">
        <div className="header">
          <h1>🧠 EduGraph Fusion - 教材知识底座</h1>
        </div>

        <div className="content-wrapper">
          {/* 知识图谱 */}
          <div className="graph-container">
            <GraphView onNodeClick={handleNodeClick} />
          </div>

          {/* 右侧功能面板 */}
          <div className="right-panel">
            <div className="tabs">
              <button
                className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
                onClick={() => setActiveTab('upload')}
              >
                上传
              </button>
              <button
                className={`tab-btn ${activeTab === 'merge' ? 'active' : ''}`}
                onClick={() => setActiveTab('merge')}
              >
                合并
              </button>
              <button
                className={`tab-btn ${activeTab === 'rag' ? 'active' : ''}`}
                onClick={() => setActiveTab('rag')}
              >
                检索
              </button>
              <button
                className={`tab-btn ${activeTab === 'feedback' ? 'active' : ''}`}
                onClick={() => setActiveTab('feedback')}
              >
                反馈
              </button>
              <button
                className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
                onClick={() => setActiveTab('report')}
              >
                报告
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'upload' && <UploadPanel onUploadSuccess={handleUploadSuccess} />}
              {activeTab === 'merge' && <MergePanel />}
              {activeTab === 'rag' && <RagPanel />}
              {activeTab === 'feedback' && <FeedbackPanel />}
              {activeTab === 'report' && <ReportPanel />}

              {/* 节点详情 */}
              {selectedNode && (
                <>
                  <div className="divider" style={{ marginTop: '20px' }}></div>
                  <div className="section-title">节点详情</div>
                  <div className="node-details">
                    <div className="node-details-title">{selectedNode.name}</div>

                    <div className="node-details-item">
                      <div className="node-details-label">定义</div>
                      <div className="node-details-value">{selectedNode.definition}</div>
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
                      <div className="node-details-label">来源教材</div>
                      <div className="node-details-value">{selectedNode.source_textbook}</div>
                    </div>

                    <div className="node-details-item">
                      <div className="node-details-label">出现频率</div>
                      <div className="node-details-value">{selectedNode.frequency} 次</div>
                    </div>
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
