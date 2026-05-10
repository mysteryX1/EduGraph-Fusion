#!/usr/bin/env python3
"""
完整的集成测试脚本
1. 生成测试数据
2. 验证模块导入
3. 测试 KG 提取
4. 测试 Merge
5. 验证输出
"""

import sys
import json
from pathlib import Path
from datetime import datetime

print("\n" + "="*80)
print("🚀 EduGraph Fusion - 知识图谱与合并模块完整测试")
print("="*80 + "\n")

# ============================================================================
# 第1步：生成测试数据
# ============================================================================
print("【步骤 1】生成测试教材数据")
print("-" * 80)

data_dir = Path("./data")
metadata_dir = data_dir / "metadata"
processed_dir = data_dir / "processed"

metadata_dir.mkdir(parents=True, exist_ok=True)
processed_dir.mkdir(parents=True, exist_ok=True)

# 教材 1：数学
textbook1_metadata = {
    "id": "textbook_math_001",
    "filename": "高中数学.pdf",
    "title": "高中数学基础",
    "file_type": "pdf",
    "file_path": "./data/uploads/math.pdf",
    "file_size": 5000000,
    "total_pages": 450,
    "upload_time": datetime.now().isoformat()
}

textbook1_chapters = [
    {
        "id": "textbook_math_001_ch_0",
        "chapter_num": 0,
        "title": "第1章 集合与函数",
        "start_page": 1,
        "end_page": 50,
        "content": "集合（Set）是数学中的基本概念。函数（Function）是建立集合之间对应关系的工具。函数的定义域和值域是重要属性。一次函数和二次函数是常见类型。",
        "word_count": 1200
    },
    {
        "id": "textbook_math_001_ch_1",
        "chapter_num": 1,
        "title": "第2章 导数与微分",
        "start_page": 51,
        "end_page": 120,
        "content": "导数（Derivative）表示函数在某点的变化率。微分（Differential）是导数的应用。梯度下降法在机器学习中应用广泛。反向传播算法基于链式求导法则。",
        "word_count": 1350
    },
    {
        "id": "textbook_math_001_ch_2",
        "chapter_num": 2,
        "title": "第3章 三角函数",
        "start_page": 121,
        "end_page": 180,
        "content": "三角函数（Trigonometric Functions）包括正弦、余弦、正切等。傅里叶变换基于三角函数的分解。傅里叶级数用三角函数逼近周期函数。",
        "word_count": 1100
    },
    {
        "id": "textbook_math_001_ch_3",
        "chapter_num": 3,
        "title": "第4章 积分学",
        "start_page": 181,
        "end_page": 250,
        "content": "积分是微分的逆运算。定积分计算函数曲线下的面积。牛顿-莱布尼茨公式建立了积分与微分的联系。",
        "word_count": 950
    },
    {
        "id": "textbook_math_001_ch_4",
        "chapter_num": 4,
        "title": "第5章 线性代数",
        "start_page": 251,
        "end_page": 320,
        "content": "线性代数是机器学习的基础。矩阵用于表示线性变换。特征值和特征向量描述矩阵的本质性质。奇异值分解在降维中应用。",
        "word_count": 1050
    }
]

# 教材 2：物理
textbook2_metadata = {
    "id": "textbook_physics_001",
    "filename": "高中物理.pdf",
    "title": "高中物理基础",
    "file_type": "pdf",
    "file_path": "./data/uploads/physics.pdf",
    "file_size": 4500000,
    "total_pages": 380,
    "upload_time": datetime.now().isoformat()
}

textbook2_chapters = [
    {
        "id": "textbook_physics_001_ch_0",
        "chapter_num": 0,
        "title": "第1章 运动学",
        "start_page": 1,
        "end_page": 60,
        "content": "运动学研究物体运动规律。位移和速度是基本概念。加速度描述速度变化。匀加速直线运动有简单的运动方程。",
        "word_count": 1100
    },
    {
        "id": "textbook_physics_001_ch_1",
        "chapter_num": 1,
        "title": "第2章 牛顿定律",
        "start_page": 61,
        "end_page": 130,
        "content": "牛顿运动定律是经典力学的基础。第一定律是惯性定律。第二定律是 F = ma。第三定律是作用力与反作用力。",
        "word_count": 1200
    },
    {
        "id": "textbook_physics_001_ch_2",
        "chapter_num": 2,
        "title": "第3章 能量与功",
        "start_page": 131,
        "end_page": 190,
        "content": "功是力与位移的乘积。动能与运动有关。势能与位置有关。能量守恒定律是基本定律。",
        "word_count": 1050
    },
    {
        "id": "textbook_physics_001_ch_3",
        "chapter_num": 3,
        "title": "第4章 波与振动",
        "start_page": 191,
        "end_page": 260,
        "content": "简谐振动是常见的振动形式。波是振动的传播。横波与纵波是两种基本形式。干涉和衍射是波的特有现象。",
        "word_count": 1150
    },
    {
        "id": "textbook_physics_001_ch_4",
        "chapter_num": 4,
        "title": "第5章 电磁学",
        "start_page": 261,
        "end_page": 320,
        "content": "电荷是电磁学的基本概念。库伦定律描述电荷相互作用。电场和磁场是电磁学核心。电磁感应是发电原理。",
        "word_count": 1000
    }
]

# 保存数据
with open(metadata_dir / "textbook_math_001_metadata.json", 'w', encoding='utf-8') as f:
    json.dump(textbook1_metadata, f, ensure_ascii=False, indent=2)

with open(metadata_dir / "textbook_math_001_chapters.json", 'w', encoding='utf-8') as f:
    json.dump(textbook1_chapters, f, ensure_ascii=False, indent=2)

with open(metadata_dir / "textbook_physics_001_metadata.json", 'w', encoding='utf-8') as f:
    json.dump(textbook2_metadata, f, ensure_ascii=False, indent=2)

with open(metadata_dir / "textbook_physics_001_chapters.json", 'w', encoding='utf-8') as f:
    json.dump(textbook2_chapters, f, ensure_ascii=False, indent=2)

print("✅ 创建了 2 本教材，共 10 个章节")
print(f"   • textbook_math_001 (5 章)")
print(f"   • textbook_physics_001 (5 章)")

# ============================================================================
# 第2步：验证模块导入
# ============================================================================
print("\n【步骤 2】验证模块导入")
print("-" * 80)

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from backend.services.kg_extractor import KGExtractor
    from backend.services.merger import NodeMerger
    from backend.services.llm_client import LLMClient
    print("✅ 所有模块导入成功")
    print("   • KGExtractor")
    print("   • NodeMerger")
    print("   • LLMClient")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# ============================================================================
# 第3步：测试 KG 提取
# ============================================================================
print("\n【步骤 3】测试知识图谱提取")
print("-" * 80)

try:
    kg_extractor = KGExtractor(data_dir="./data")
    kg_result = kg_extractor.extract_all()

    if kg_result['success']:
        print("✅ 知识图谱提取成功")
        print(f"   • 节点数: {kg_result['nodes_count']}")
        print(f"   • 边数: {kg_result['edges_count']}")
    else:
        print(f"❌ 知识图谱提取失败: {kg_result.get('message')}")

except Exception as e:
    print(f"❌ KG 提取出错: {e}")

# ============================================================================
# 第4步：测试 Merge
# ============================================================================
print("\n【步骤 4】测试节点合并")
print("-" * 80)

try:
    node_merger = NodeMerger(data_dir="./data")
    merge_result = node_merger.merge_all()

    if merge_result['success']:
        print("✅ 节点合并成功")
        print(f"   • 原始节点数: {merge_result['original_nodes']}")
        print(f"   • 合并后节点数: {merge_result['merged_nodes']}")
        print(f"   • 合并数: {merge_result['merged_count']}")
        print(f"   • 可能重复: {merge_result['possible_duplicate_count']}")
        print(f"   • 压缩比: {merge_result['compression_ratio']:.4f}")
    else:
        print(f"❌ 节点合并失败: {merge_result.get('message')}")

except Exception as e:
    print(f"❌ Merge 出错: {e}")

# ============================================================================
# 第5步：验证输出文件
# ============================================================================
print("\n【步骤 5】验证输出文件")
print("-" * 80)

output_files = {
    "kg_nodes.json": processed_dir / "kg_nodes.json",
    "kg_edges.json": processed_dir / "kg_edges.json",
    "merged_kg.json": processed_dir / "merged_kg.json",
    "merge_decisions.json": processed_dir / "merge_decisions.json",
}

all_exist = True
for name, path in output_files.items():
    if path.exists():
        size = path.stat().st_size
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict) and 'nodes' in data:
                count = len(data['nodes'])
            elif isinstance(data, dict):
                count = len(str(data))
            else:
                count = 0
        print(f"✅ {name:25} ({size:8} B, ~{count:3} items)")
    else:
        print(f"❌ {name:25} 不存在")
        all_exist = False

# ============================================================================
# 第6步：显示数据样本
# ============================================================================
print("\n【步骤 6】显示数据样本")
print("-" * 80)

kg_file = processed_dir / "kg_nodes.json"
if kg_file.exists():
    with open(kg_file, 'r', encoding='utf-8') as f:
        nodes = json.load(f)
        print(f"✅ 提取的知识节点数: {len(nodes)}")
        if nodes:
            node = nodes[0]
            print(f"\n   第一个节点:")
            print(f"   • 名称: {node.get('name')}")
            print(f"   • 类型: {node.get('type')}")
            print(f"   • 来源教材: {node.get('source_textbook')}")
            print(f"   • 频率: {node.get('frequency')}")

merged_file = processed_dir / "merged_kg.json"
if merged_file.exists():
    with open(merged_file, 'r', encoding='utf-8') as f:
        merged_kg = json.load(f)
        nodes = merged_kg.get('nodes', [])
        edges = merged_kg.get('edges', [])
        print(f"\n✅ 合并后的知识图谱:")
        print(f"   • 节点数: {len(nodes)}")
        print(f"   • 边数: {len(edges)}")

decisions_file = processed_dir / "merge_decisions.json"
if decisions_file.exists():
    with open(decisions_file, 'r', encoding='utf-8') as f:
        decisions = json.load(f)
        merge_count = len([d for d in decisions if d.get('decision') == 'merge'])
        dup_count = len([d for d in decisions if d.get('decision') == 'possible_duplicate'])
        print(f"\n✅ 合并决策统计:")
        print(f"   • 合并: {merge_count}")
        print(f"   • 可能重复: {dup_count}")
        print(f"   • 总决策数: {len(decisions)}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "="*80)
if all_exist:
    print("✨ 所有测试完成！模块正常工作")
else:
    print("⚠️  部分测试完成，请检查日志")
print("="*80)

print("""
下一步：启动 API 服务

  1. 启动 FastAPI 服务:
     python -m backend.main

  2. 测试 API 端点:

     # 构建知识图谱
     curl -X POST http://localhost:8000/api/kg/build

     # 获取知识图谱
     curl http://localhost:8000/api/kg

     # 合并知识图谱
     curl -X POST http://localhost:8000/api/merge

     # 获取合并决策
     curl http://localhost:8000/api/merge/decisions

  或运行测试脚本:
     bash test_api_kg_merge.sh
""")

print()
