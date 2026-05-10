#!/bin/bash
# EduGraph Fusion API curl 测试命令
# 使用方式: bash CURL_TESTS.sh
# 注意: 需要 API 服务器运行在 http://localhost:8000

BASE_URL="http://localhost:8000"

echo "================================"
echo "EduGraph Fusion API 测试套件"
echo "================================"
echo ""
echo "确保已启动 API 服务器: python -m backend.main"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试计数
TOTAL=0
SUCCESS=0
FAILED=0

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4

    TOTAL=$((TOTAL + 1))
    echo -e "${BLUE}[测试 $TOTAL]${NC} $name"
    echo "  方法: $method"
    echo "  端点: $endpoint"

    if [ -n "$data" ]; then
        echo "  数据: $data"
        response=$(curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json")
    fi

    # 检查响应中是否包含 "success" 或 "error"
    if echo "$response" | grep -q '"status"'; then
        echo -e "  结果: ${GREEN}✓ 成功${NC}"
        SUCCESS=$((SUCCESS + 1))
        # 显示响应的前 200 字符
        echo "  响应: $(echo "$response" | head -c 200)..."
    else
        echo -e "  结果: ${YELLOW}⚠ 需要检查${NC}"
        FAILED=$((FAILED + 1))
        echo "  响应: $(echo "$response" | head -c 200)..."
    fi
    echo ""
}

# ==================== RAG 测试 ====================
echo -e "${YELLOW}=== RAG 模块测试 ===${NC}"
echo ""

test_endpoint \
    "1. 建立 RAG 索引" \
    "POST" \
    "/api/rag/index"

test_endpoint \
    "2. 获取 RAG 状态" \
    "GET" \
    "/api/rag/status"

test_endpoint \
    "3. 查询知识库 - 函数" \
    "POST" \
    "/api/rag/query" \
    '{"question":"什么是函数？","top_k":5}'

test_endpoint \
    "4. 查询知识库 - 不存在的内容" \
    "POST" \
    "/api/rag/query" \
    '{"question":"火星上有什么？","top_k":5}'

# ==================== 反馈测试 ====================
echo -e "${YELLOW}=== 反馈模块测试 ===${NC}"
echo ""

test_endpoint \
    "5. 反馈: 保留 函数概念" \
    "POST" \
    "/api/feedback" \
    '{"instruction":"保留 函数概念"}'

test_endpoint \
    "6. 反馈: 删除 冗余内容" \
    "POST" \
    "/api/feedback" \
    '{"instruction":"删除 冗余内容"}'

test_endpoint \
    "7. 反馈: 拆分 函数概念 和 高级函数" \
    "POST" \
    "/api/feedback" \
    '{"instruction":"拆分 函数概念 和 高级函数"}'

test_endpoint \
    "8. 反馈: 合并 基本函数 和 函数概念" \
    "POST" \
    "/api/feedback" \
    '{"instruction":"合并 基本函数 和 函数概念"}'

test_endpoint \
    "9. 获取反馈摘要" \
    "GET" \
    "/api/feedback/summary"

# ==================== 报告测试 ====================
echo -e "${YELLOW}=== 报告生成模块测试 ===${NC}"
echo ""

test_endpoint \
    "10. 生成整合报告" \
    "POST" \
    "/api/report/generate"

test_endpoint \
    "11. 获取最新报告" \
    "GET" \
    "/api/report/latest"

test_endpoint \
    "12. 获取报告摘要" \
    "GET" \
    "/api/report/summary"

# ==================== 测试总结 ====================
echo ""
echo -e "${YELLOW}==================================${NC}"
echo -e "${YELLOW}测试总结${NC}"
echo -e "${YELLOW}==================================${NC}"
echo "总测试数: $TOTAL"
echo -e "成功: ${GREEN}$SUCCESS${NC}"
echo -e "需检查: ${YELLOW}$FAILED${NC}"
echo ""

# 检查生成的文件
if [ -f "report/整合报告.md" ]; then
    echo -e "${GREEN}✓ 报告文件已生成: report/整合报告.md${NC}"
else
    echo -e "${YELLOW}⚠ 报告文件未找到${NC}"
fi

# 检查数据文件
echo ""
echo "数据文件状态:"
if [ -f "backend/data/metadata/textbook_001_chapters.json" ]; then
    echo -e "  ${GREEN}✓${NC} metadata/textbook_001_chapters.json"
else
    echo -e "  ${YELLOW}⚠${NC} metadata/textbook_001_chapters.json"
fi

if [ -f "backend/data/processed/merged_kg.json" ]; then
    echo -e "  ${GREEN}✓${NC} processed/merged_kg.json"
else
    echo -e "  ${YELLOW}⚠${NC} processed/merged_kg.json"
fi

if [ -f "backend/data/processed/merge_decisions.json" ]; then
    echo -e "  ${GREEN}✓${NC} processed/merge_decisions.json"
else
    echo -e "  ${YELLOW}⚠${NC} processed/merge_decisions.json"
fi

echo ""
echo -e "${GREEN}测试完成！${NC}"
