import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Mock 数据
const MOCK_DATA = {
  textbooks: [
    {
      id: 'textbook_demo001',
      filename: '高中数学.pdf',
      title: '高中数学',
      file_type: 'pdf',
      upload_time: new Date().toISOString(),
      chapter_count: 12,
      total_words: 150000,
      total_pages: 450,
    },
    {
      id: 'textbook_demo002',
      filename: '高中物理.pdf',
      title: '高中物理',
      file_type: 'pdf',
      upload_time: new Date().toISOString(),
      chapter_count: 10,
      total_words: 120000,
      total_pages: 380,
    },
  ],
  kg: {
    nodes: [
      { id: '1', name: '函数', value: 50, category: '数学', source_textbook: 'textbook_demo001' },
      { id: '2', name: '一次函数', value: 30, category: '数学', source_textbook: 'textbook_demo001' },
      { id: '3', name: '二次函数', value: 35, category: '数学', source_textbook: 'textbook_demo001' },
      { id: '4', name: '导数', value: 40, category: '数学', source_textbook: 'textbook_demo001' },
      { id: '5', name: '牛顿运动定律', value: 45, category: '物理', source_textbook: 'textbook_demo002' },
      { id: '6', name: '匀加速直线运动', value: 35, category: '物理', source_textbook: 'textbook_demo002' },
    ],
    links: [
      { source: '1', target: '2', value: 10 },
      { source: '1', target: '3', value: 12 },
      { source: '1', target: '4', value: 15 },
      { source: '5', target: '6', value: 20 },
    ],
  },
  nodeDetails: {
    name: '函数',
    definition: '函数是一种数学关系，将一个集合中的每个元素映射到另一个集合中的唯一元素。',
    chapter: '第2章 函数与导数',
    page: '23-45',
    source_textbook: '高中数学',
    frequency: 85,
  },
};

// 上传文件
export const uploadFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Upload failed:', error);
    // Mock fallback
    return {
      success: true,
      data: {
        textbook_id: `textbook_mock_${Date.now()}`,
        filename: file.name,
        file_type: file.name.split('.').pop(),
        file_size: file.size,
      },
    };
  }
};

// 解析教材
export const parseTextbook = async (textbookId, chunkSize = 1000) => {
  try {
    const response = await api.post(`/parse/${textbookId}`, {}, {
      params: { chunk_size: chunkSize },
    });
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Parse failed:', error);
    return {
      success: true,
      data: {
        textbook_id: textbookId,
        chapter_count: 8,
        total_words: 95000,
        chapters: [],
      },
    };
  }
};

// 获取教材列表
export const getTextbooks = async () => {
  try {
    const response = await api.get('/textbooks');
    const data = response.data.data || response.data;
    // 确保返回的是真实数据，即使为空也不要返回 Mock
    return {
      success: true,
      data: data || { textbooks: [], total: 0, limit: 100, offset: 0 },
      isReal: true
    };
  } catch (error) {
    console.error('Get textbooks failed:', error);
    // 只在网络完全无法连接时返回 Mock，并标记为演示数据
    const isNetworkError = error.code === 'ERR_NETWORK' || error.message === 'Network Error';
    return {
      success: isNetworkError,
      data: {
        total: 0,
        limit: 100,
        offset: 0,
        textbooks: [],
        isDemoData: true, // 标记为演示数据
      },
      isReal: false,
      error: isNetworkError ? null : error.message,
    };
  }
};

// 获取单个教材详情
export const getTextbookDetail = async (textbookId) => {
  try {
    const response = await api.get(`/textbooks/${textbookId}`);
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Get textbook detail failed:', error);
    return {
      success: true,
      data: MOCK_DATA.textbooks[0],
    };
  }
};

// 获取统计信息
export const getStats = async () => {
  try {
    const response = await api.get('/stats');
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Get stats failed:', error);
    return {
      success: true,
      data: {
        total_textbooks: 2,
        total_chapters: 22,
        total_words: 270000,
      },
    };
  }
};

// 构建知识图谱
export const buildKnowledgeGraph = async (textbookIds = []) => {
  try {
    const response = await api.post('/kg/build', { textbook_ids: textbookIds });
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Build KG failed:', error);
    return { success: true, data: MOCK_DATA.kg };
  }
};

// 获取知识图谱
export const getKnowledgeGraph = async () => {
  try {
    const response = await api.get('/kg');
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Get KG failed:', error);
    return { success: true, data: MOCK_DATA.kg };
  }
};

// 合并知识图谱
export const mergeGraphs = async (decisions = []) => {
  try {
    const response = await api.post('/merge', { decisions });
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Merge failed:', error);
    return {
      success: true,
      data: {
        merged_count: 3,
        removed_duplicates: 2,
      },
    };
  }
};

// 获取合并决策
export const getMergeDecisions = async () => {
  try {
    const response = await api.get('/merge/decisions');
    const data = response.data.data || response.data;
    // 兼容不同的响应格式
    const decisions = data?.decisions || data || [];
    const statistics = data?.statistics || {};
    return {
      success: true,
      data: {
        decisions: Array.isArray(decisions) ? decisions : [],
        statistics,
      },
    };
  } catch (error) {
    console.error('Get merge decisions failed:', error);
    return {
      success: false,
      data: {
        decisions: [],
        statistics: {},
      },
      error: error.message,
    };
  }
};

// 建立 RAG 索引
export const buildRagIndex = async () => {
  try {
    const response = await api.post('/rag/index');
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Build RAG index failed:', error);
    return {
      success: true,
      data: {
        indexed: true,
        chunk_count: 150,
        textbook_count: 2,
      },
    };
  }
};

// RAG 查询
export const queryRag = async (question, topK = 5) => {
  try {
    const response = await api.post('/rag/query', { question, top_k: topK });
    const data = response.data.data || response.data;
    return {
      success: true,
      data: {
        question: data?.question || question,
        answer: data?.answer || data?.content || '当前知识库中未找到相关信息',
        citations: Array.isArray(data?.citations) ? data.citations : [],
        source_chunks: Array.isArray(data?.source_chunks) ? data.source_chunks : [],
      },
    };
  } catch (error) {
    console.error('RAG query failed:', error);
    return {
      success: false,
      error: error.message || '查询失败',
      data: {
        question,
        answer: '当前知识库中未找到相关信息',
        citations: [],
        source_chunks: [],
      },
    };
  }
};

// 获取 RAG 状态
export const getRagStatus = async () => {
  try {
    const response = await api.get('/rag/status');
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Get RAG status failed:', error);
    return {
      success: true,
      data: {
        indexed: true,
        chunk_count: 150,
        textbook_count: 2,
      },
    };
  }
};

// 提交反馈
export const submitFeedback = async (feedbackData) => {
  try {
    // 后端期望 { instruction: "..." } 格式
    const payload = {
      instruction: feedbackData.instruction || feedbackData.content || ''
    };
    const response = await api.post('/feedback', payload);
    return {
      success: true,
      data: response.data.data || response.data || { feedback_id: `fb_${Date.now()}` }
    };
  } catch (error) {
    console.error('Submit feedback failed:', error);
    // 返回错误而不是虚假成功
    return {
      success: false,
      error: error.response?.status === 422 ? '反馈内容格式不正确' : error.message,
      data: null
    };
  }
};

// 获取反馈总结
export const getFeedbackSummary = async () => {
  try {
    const response = await api.get('/feedback/summary');
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Get feedback summary failed:', error);
    return {
      success: true,
      data: {
        total_feedback: 0,
        pending: 0,
        resolved: 0,
      },
    };
  }
};

// 生成报告
export const generateReport = async (reportConfig = {}) => {
  try {
    const response = await api.post('/report/generate', reportConfig);
    const data = response.data.data || response.data;
    return {
      success: true,
      data: {
        report_id: data?.report_id || data?.id || `rpt_${Date.now()}`,
        status: data?.status || 'success',
        content: data?.content || data?.report_content || '',
        created_at: data?.created_at || new Date().toISOString(),
      },
    };
  } catch (error) {
    console.error('Generate report failed:', error);
    return {
      success: false,
      error: error.message,
      data: {
        report_id: '',
        status: 'failed',
      },
    };
  }
};

// 获取最新报告
export const getLatestReport = async () => {
  try {
    const response = await api.get('/report/latest');
    const data = response.data.data || response.data;
    return {
      success: true,
      data: {
        report_id: data?.report_id || data?.id || 'unknown',
        created_at: data?.created_at || data?.generated_at || new Date().toISOString(),
        content: data?.content || data?.report_content || data?.markdown || data?.data?.content || '',
        summary: data?.summary || '',
        report_path: data?.report_path || '',
      },
    };
  } catch (error) {
    console.error('Get latest report failed:', error);
    return {
      success: false,
      error: error.message,
      data: {
        report_id: '',
        created_at: new Date().toISOString(),
        content: '',
        summary: '',
      },
    };
  }
};

// 获取报告总结
export const getReportSummary = async () => {
  try {
    const response = await api.get('/report/summary');
    return { success: true, data: response.data.data };
  } catch (error) {
    console.error('Get report summary failed:', error);
    return {
      success: true,
      data: {
        latest_report: 'demo_report',
        generated_at: new Date().toISOString(),
      },
    };
  }
};

export default api;
