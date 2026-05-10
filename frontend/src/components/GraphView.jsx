import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';
import { getKnowledgeGraph } from '../api';

const TEXTBOOK_COLORS = {
  textbook_demo001: '#FF6B6B',
  textbook_demo002: '#4ECDC4',
  textbook_demo003: '#45B7D1',
  textbook_demo004: '#FFA07A',
  textbook_demo005: '#98D8C8',
};

export default function GraphView({ onNodeClick }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadGraph = async () => {
      setLoading(true);
      try {
        const result = await getKnowledgeGraph();
        if (result.success) {
          setGraphData(result.data);
        }
      } catch (error) {
        console.error('Failed to load graph:', error);
      } finally {
        setLoading(false);
      }
    };

    loadGraph();
  }, []);

  useEffect(() => {
    if (!graphData || !chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const getNodeColor = (node) => {
      return TEXTBOOK_COLORS[node.source_textbook] || '#1890ff';
    };

    // 计算节点度数（连接数）以动态调整大小
    const calculateNodeDegree = (nodeId) => {
      return (graphData.links || []).filter(
        (link) => link.source === nodeId || link.target === nodeId
      ).length;
    };

    const nodes = (graphData.nodes || []).map((node) => {
      const frequency = node.frequency || node.value || 10;
      const degree = calculateNodeDegree(node.id);
      // 节点大小基于 frequency 和 degree 动态计算，范围 25-100
      const baseSize = Math.max(25, Math.min(100, frequency / 2 + degree * 5));
      const labelSize = Math.max(10, Math.min(14, frequency / 20));

      // 节点标签只显示前 10 个字符
      const shortName = node.name.length > 10 ? node.name.slice(0, 10) + '...' : node.name;

      return {
        id: node.id,
        name: node.name,
        value: frequency,
        category: node.category || '默认',
        degree,
        symbolSize: baseSize,
        itemStyle: {
          color: getNodeColor(node),
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: true,
          formatter: shortName,
          fontSize: labelSize,
          fontWeight: 'bold',
          color: '#fff',
          position: 'inside',
          overflow: 'truncate',
        },
        ...node,
      };
    });

    const links = (graphData.links || []).map((link) => {
      // 关系类型颜色映射
      const relationTypeColors = {
        prerequisite: '#FF6B6B',  // 前置关系 - 红色
        contains: '#4ECDC4',      // 包含关系 - 绿色
        parallel: '#95E1D3',      // 平行关系 - 浅绿
        related: '#FFA07A',       // 相关关系 - 橙色
      };
      const relationType = link.relation_type || link.type || 'related';
      const relationColor = relationTypeColors[relationType] || 'rgba(0, 0, 0, 0.2)';

      return {
        ...link,
        lineStyle: {
          width: Math.max(1, (link.value || 1) / 5),
          color: relationColor,
          opacity: 0.6,
        },
      };
    });

    const option = {
      title: {
        text: '知识图谱',
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold',
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          if (params.dataType === 'node') {
            const data = params.data;
            return `<strong>${data.name}</strong><br/>
                   分类: ${data.category || '未分类'}<br/>
                   频率: ${data.frequency || data.value || 0}<br/>
                   连接数: ${data.degree || 0}<br/>
                   来源: ${data.source_textbook || '未知'}`;
          } else {
            const relationType = params.data.relation_type || params.data.type || 'related';
            return `关系类型: ${relationType}<br/>强度: ${params.data.value || 1}`;
          }
        },
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        borderColor: '#333',
        textStyle: {
          color: '#fff',
          fontSize: 12,
        },
      },
      animationDuration: 800,
      animationEasing: 'cubicOut',
      series: [
        {
          type: 'graph',
          layout: 'force',
          roam: true,
          draggable: true,
          focusNodeAdjacency: true,
          scaleLimit: {
            min: 0.5,
            max: 3,
          },
          force: {
            repulsion: 100,
            gravity: 0.1,
            edgeLength: 150,
            friction: 0.6,
          },
          nodes: nodes,
          links: links,
          lineStyle: {
            curveness: 0.3,
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 3,
              color: '#1890ff',
            },
          },
        },
      ],
    };

    chartInstance.current.setOption(option);

    const handleClick = (params) => {
      if (params.dataType === 'node' && onNodeClick) {
        onNodeClick(params.data);
      }
    };

    chartInstance.current.off('click', handleClick);
    chartInstance.current.on('click', handleClick);

    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [graphData, onNodeClick]);

  if (loading) {
    return (
      <div className="graph-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div>
          <div className="loading-spinner"></div>
          <p style={{ marginTop: '12px', color: '#666' }}>加载知识图谱中...</p>
        </div>
      </div>
    );
  }

  return <div ref={chartRef} className="graph-container" style={{ width: '100%', height: '100%' }} />;
}
