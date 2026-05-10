#!/bin/bash

# KG 和 Merge API 测试脚本
# 使用前请确保：
# 1. 运行过 generate_test_data.py 生成测试数据
# 2. FastAPI 服务已启动：python -m backend.main

API_URL="http://localhost:8000/api"

echo "=========================================="
echo "知识图谱与合并 API 测试"
echo "=========================================="
echo

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================
# 测试 1: 构建知识图谱
# ============================================================
echo -e "${BLUE}【测试 1】POST /api/kg/build - 构建知识图谱${NC}"
echo "请求："
echo "  POST $API_URL/kg/build"
echo "  Body: {}"
echo

curl -X POST "$API_URL/kg/build" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\n\n状态码: %{http_code}\n" 2>/dev/null | python -m json.tool

echo

sleep 1

# ============================================================
# 测试 2: 获取知识图谱
# ============================================================
echo -e "${BLUE}【测试 2】GET /api/kg - 获取知识图谱${NC}"
echo "请求："
echo "  GET $API_URL/kg"
echo

curl "$API_URL/kg" \
  -w "\n\n状态码: %{http_code}\n" 2>/dev/null | python -m json.tool | head -100

echo
echo "... (省略部分输出)"
echo

sleep 1

# ============================================================
# 测试 3: 合并知识图谱
# ============================================================
echo -e "${BLUE}【测试 3】POST /api/merge - 合并知识图谱${NC}"
echo "请求："
echo "  POST $API_URL/merge"
echo "  Body: {}"
echo

curl -X POST "$API_URL/merge" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\n\n状态码: %{http_code}\n" 2>/dev/null | python -m json.tool

echo

sleep 1

# ============================================================
# 测试 4: 获取合并决策
# ============================================================
echo -e "${BLUE}【测试 4】GET /api/merge/decisions - 获取合并决策${NC}"
echo "请求："
echo "  GET $API_URL/merge/decisions"
echo

curl "$API_URL/merge/decisions" \
  -w "\n\n状态码: %{http_code}\n" 2>/dev/null | python -m json.tool | head -100

echo
echo "... (省略部分输出)"
echo

echo -e "${GREEN}=========================================="
echo "所有测试完成！"
echo "==========================================${NC}"
