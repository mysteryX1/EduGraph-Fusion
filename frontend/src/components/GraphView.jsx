import React, { useEffect, useMemo, useRef, useState } from 'react';
import * as echarts from 'echarts';
import { getKnowledgeGraph } from '../api';

const PALETTE = ['#93c5fd', '#86efac', '#fcd34d', '#fca5a5', '#c4b5fd', '#67e8f9', '#fdba74', '#a7f3d0'];
const RELATION_COLORS = {
  contains: '#2563eb',
  prerequisite: '#dc2626',
  parallel: '#059669',
  related: '#7c3aed',
};
const NOISE_NAMES = new Set(['目录', '参考文献', '习题', '复习题', '本章小结', '思考题', '附录', '二维码', '图', '表']);

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const normalizeLinks = (data) => data?.links || data?.edges || [];
const getLinkSource = (link) => link.source ?? link.source_id;
const getLinkTarget = (link) => link.target ?? link.target_id;
const clean = (value) => String(value || '').trim();
const stem = (value) => clean(value).replace(/\.[^.]+$/, '');

const selectedCandidates = (textbook) =>
  new Set(
    [
      textbook?.id,
      textbook?.textbook_id,
      textbook?.title,
      textbook?.filename,
      stem(textbook?.filename),
      stem(textbook?.title),
    ]
      .filter(Boolean)
      .map((value) => clean(value).toLowerCase())
  );

const nodeSources = (node) => {
  const sources = [];
  [node.source_textbook, node.textbook_id, node.source, node.filename, node.textbook_title].forEach((value) => {
    if (value) sources.push(value);
  });

  if (Array.isArray(node.sources)) {
    node.sources.forEach((source) => {
      if (typeof source === 'string') {
        sources.push(source);
      } else if (source) {
        [source.textbook_id, source.source_textbook, source.filename, source.title, source.textbook_title].forEach((value) => {
          if (value) sources.push(value);
        });
      }
    });
  }

  return sources.map((value) => clean(value).toLowerCase()).filter(Boolean);
};

const belongsToTextbook = (node, textbook) => {
  if (!textbook) return true;

  const candidates = selectedCandidates(textbook);
  const sources = nodeSources(node);
  return sources.some((source) => candidates.has(source) || candidates.has(stem(source).toLowerCase()));
};

const isNoiseNode = (node) => {
  const name = clean(node.name || node.label);
  const compact = name.replace(/\s+/g, '');

  if (!compact || compact.length < 2) return true;
  if (/^[\d\s.,，。:：;；、\-—_/\\()[\]（）]+$/.test(compact)) return true;
  if (NOISE_NAMES.has(compact)) return true;
  if (/^(第?[一二三四五六七八九十百千万\d]+[章节篇部])$/.test(compact)) return true;
  if (/^(图|表)\s*[\d一二三四五六七八九十.-]+$/.test(compact)) return true;
  if (/(参考文献|复习题|思考题|本章小结|二维码|附录|目录)/.test(compact)) return true;

  return false;
};

const filterGraph = (graphData, selectedTextbook) => {
  const rawNodes = Array.isArray(graphData?.nodes) ? graphData.nodes : [];
  const rawLinks = normalizeLinks(graphData).filter((link) => getLinkSource(link) && getLinkTarget(link));

  const nodes = rawNodes.filter((node) => belongsToTextbook(node, selectedTextbook)).filter((node) => !isNoiseNode(node));
  const nodeIds = new Set(nodes.map((node) => String(node.id)));
  const links = rawLinks.filter((link) => nodeIds.has(String(getLinkSource(link))) && nodeIds.has(String(getLinkTarget(link))));

  return { nodes, links };
};

export default function GraphView({ selectedTextbook, onNodeClick }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const filteredGraph = useMemo(() => filterGraph(graphData, selectedTextbook), [graphData, selectedTextbook]);

  useEffect(() => {
    let cancelled = false;

    const loadGraph = async () => {
      setLoading(true);
      setError('');

      try {
        const result = await getKnowledgeGraph();
        if (!cancelled) {
          if (result.success) {
            setGraphData(result.data || { nodes: [], links: [] });
          } else {
            setError(result.error || '知识图谱加载失败');
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || '知识图谱加载失败');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadGraph();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    onNodeClick?.(null);
  }, [selectedTextbook]);

  useEffect(() => {
    if (!graphData || !chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const rawNodes = filteredGraph.nodes;
    const rawLinks = filteredGraph.links;
    const degreeMap = new Map();
    const sourceColorMap = new Map();

    rawNodes.forEach((node) => {
      degreeMap.set(String(node.id), 0);
      const source = node.source_textbook || node.textbook_id || node.source || 'default';
      if (!sourceColorMap.has(source)) {
        sourceColorMap.set(source, PALETTE[sourceColorMap.size % PALETTE.length]);
      }
    });

    rawLinks.forEach((link) => {
      const source = String(getLinkSource(link));
      const target = String(getLinkTarget(link));
      degreeMap.set(source, (degreeMap.get(source) || 0) + 1);
      degreeMap.set(target, (degreeMap.get(target) || 0) + 1);
    });

    const nodes = rawNodes.map((node) => {
      const frequency = Number(node.frequency ?? node.value ?? node.weight ?? 1);
      const degree = degreeMap.get(String(node.id)) || 0;
      const importance = degree * 2 + Math.log(frequency + 1);
      const symbolSize = clamp(24 + importance * 4, 24, 90);
      const isCore = symbolSize >= 54;
      const source = node.source_textbook || node.textbook_id || node.source || 'default';
      const name = node.name || node.label || String(node.id);

      return {
        ...node,
        id: String(node.id),
        name,
        value: importance,
        raw_frequency: frequency,
        frequency,
        degree,
        symbolSize,
        draggable: true,
        itemStyle: {
          color: sourceColorMap.get(source) || PALETTE[0],
          borderColor: isCore ? '#111827' : '#ffffff',
          borderWidth: isCore ? 2.5 : 1.5,
          shadowColor: 'rgba(15, 23, 42, 0.22)',
          shadowBlur: isCore ? 10 : 4,
        },
        label: {
          show: true,
          formatter: ({ data }) => (data.name.length > 12 ? `${data.name.slice(0, 12)}...` : data.name),
          position: isCore ? 'inside' : 'right',
          distance: 5,
          fontSize: isCore ? 12 : 10,
          fontWeight: isCore ? 700 : 500,
          color: '#111827',
          textBorderColor: '#ffffff',
          textBorderWidth: 2,
          overflow: 'truncate',
        },
      };
    });

    const links = rawLinks.map((link) => {
      const relationType = link.relation_type || link.type || link.relation || 'related';
      const strength = Number(link.value ?? link.weight ?? link.confidence ?? 1);
      const width = clamp(1 + Math.log(strength + 1), 1, 5);

      return {
        ...link,
        source: String(getLinkSource(link)),
        target: String(getLinkTarget(link)),
        value: strength,
        lineStyle: {
          width,
          color: RELATION_COLORS[relationType] || '#64748b',
          opacity: clamp(0.28 + width * 0.09, 0.32, 0.78),
          curveness: 0.12,
        },
      };
    });

    const titleSuffix = selectedTextbook ? ` - ${selectedTextbook.title || selectedTextbook.filename || selectedTextbook.id}` : '';
    const option = {
      backgroundColor: '#f8fafc',
      title: {
        text: `知识图谱${titleSuffix}`,
        left: 'center',
        top: 10,
        textStyle: { color: '#111827', fontSize: 16, fontWeight: 'bold' },
      },
      tooltip: {
        trigger: 'item',
        confine: true,
        formatter: (params) => {
          if (params.dataType === 'node') {
            const data = params.data;
            return `<strong>${data.name}</strong><br/>
              类型：${data.category || data.type || '未分类'}<br/>
              频次：${data.frequency || 0}<br/>
              连接数：${data.degree || 0}<br/>
              章节：${data.chapter || '未知'}<br/>
              页码：${data.page || data.pages || '-'}<br/>
              来源：${data.source_textbook || data.textbook_id || data.source || '未知'}`;
          }

          const relationType = params.data.relation_type || params.data.type || 'related';
          return `关系：${relationType}<br/>强度：${params.data.value || 1}`;
        },
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        borderColor: '#334155',
        textStyle: { color: '#fff', fontSize: 12 },
      },
      animationDuration: 900,
      animationEasing: 'cubicOut',
      series: [
        {
          type: 'graph',
          layout: 'force',
          roam: true,
          draggable: true,
          focusNodeAdjacency: true,
          layoutAnimation: true,
          scaleLimit: { min: 0.35, max: 4 },
          force: { repulsion: 620, gravity: 0.045, edgeLength: [70, 210], friction: 0.45 },
          nodes,
          links,
          lineStyle: { color: '#94a3b8', opacity: 0.45, width: 1.2 },
          emphasis: {
            focus: 'adjacency',
            label: { show: true, color: '#111827', textBorderColor: '#ffffff', textBorderWidth: 3 },
            lineStyle: { width: 4, opacity: 0.9 },
          },
        },
      ],
    };

    chartInstance.current.setOption(option, true);

    chartInstance.current.off('click');
    chartInstance.current.on('click', (params) => {
      if (params.dataType === 'node') {
        onNodeClick?.(params.data);
      }
    });

    const handleResize = () => chartInstance.current?.resize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [filteredGraph, graphData, onNodeClick, selectedTextbook]);

  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, []);

  if (loading) {
    return (
      <div className="graph-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div>
          <div className="loading-spinner"></div>
          <p style={{ marginTop: 12, color: '#666' }}>加载知识图谱中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="graph-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="alert alert-error">{error}</div>
      </div>
    );
  }

  if (graphData && filteredGraph.nodes.length === 0) {
    return (
      <div className="graph-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#64748b', fontSize: 14 }}>当前教材暂无知识图谱，请先解析并构建图谱</div>
      </div>
    );
  }

  return <div ref={chartRef} className="graph-container" style={{ width: '100%', height: '100%' }} />;
}
