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

    const nodes = (graphData.nodes || []).map((node) => ({
      id: node.id,
      name: node.name,
      value: node.value || 30,
      category: node.category || '默认',
      symbolSize: Math.max(20, Math.min(80, (node.value || 30) / 2)),
      itemStyle: {
        color: getNodeColor(node),
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: {
        show: true,
        formatter: node.name,
        fontSize: 12,
        fontWeight: 'bold',
        color: '#fff',
        position: 'top',
      },
      ...node,
    }));

    const links = (graphData.links || []).map((link) => ({
      ...link,
      lineStyle: {
        width: (link.value || 1) / 5,
        color: 'rgba(0, 0, 0, 0.2)',
      },
    }));

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
            return `<strong>${params.data.name}</strong><br/>
                   分类: ${params.data.category}<br/>
                   频率: ${params.data.value}`;
          } else {
            return `关联强度: ${params.data.value}`;
          }
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff',
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
