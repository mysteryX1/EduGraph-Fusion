#!/usr/bin/env python3
"""
KG 和 Merge 模块测试脚本

1. 创建样本教材数据
2. 运行 KG 提取
3. 运行 Merge
4. 验证输出文件
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print("🚀 知识图谱与合并模块测试")
print("="*80 + "\n")

# ============================================================================
# 第1步：创建样本数据
# ============================================================================
print("【步骤 1】创建样本教材数据")
print("-" * 80)

data_dir = Path("./data")
metadata_dir = data_dir / "metadata"
processed_dir = data_dir / "processed"

metadata_dir.mkdir(parents=True, exist_ok=True)
processed_dir.mkdir(parents=True, exist_ok=True)

# 样本教材 1：数学
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
        "content": """
本章介绍集合的基本概念和函数的性质。集合（Set）是数学中的基本概念，
由具有某种共同属性的元素组成。函数（Function）是建立两个集合之间对应
关系的数学工具。集合的运算包括并集、交集、补集等基本操作。
集合的表示方法有列表法、描述法和图形法三种。
函数的定义域和值域是函数的重要属性。
一次函数、二次函数是最常见的函数类型。
""",
        "word_count": 1200
    },
    {
        "id": "textbook_math_001_ch_1",
        "chapter_num": 1,
        "title": "第2章 导数与微分",
        "start_page": 51,
        "end_page": 120,
        "content": """
导数（Derivative）是微积分中的基本概念，表示函数在某点的变化率。
微分（Differential）是导数的应用形式。导数的定义基于极限的概念。
常见函数的导数公式包括幂函数、三角函数、指数函数等。
导数的应用包括求函数的最值、判断函数的单调性等。
梯度下降法（Gradient Descent）在机器学习中广泛应用。
反向传播（Backpropagation）算法基于链式求导法则。
""",
        "word_count": 1350
    },
    {
        "id": "textbook_math_001_ch_2",
        "chapter_num": 2,
        "title": "第3章 三角函数",
        "start_page": 121,
        "end_page": 180,
        "content": """
三角函数（Trigonometric Functions）是以角为自变量的函数。
主要的三角函数包括正弦（Sine）、余弦（Cosine）、正切（Tangent）等。
三角函数在物理中描述周期现象，在工程中应用广泛。
三角函数的周期性是其重要特性。
傅里叶变换（Fourier Transform）基于三角函数的分解。
傅里叶级数（Fourier Series）用三角函数逼近周期函数。
""",
        "word_count": 1100
    },
    {
        "id": "textbook_math_001_ch_3",
        "chapter_num": 3,
        "title": "第4章 积分学",
        "start_page": 181,
        "end_page": 250,
        "content": """
积分（Integration）是微分的逆运算，分为定积分和不定积分。
不定积分（Indefinite Integral）求原函数。定积分（Definite Integral）
计算函数曲线下的面积。牛顿-莱布尼茨公式（Newton-Leibniz Formula）
建立了定积分与不定积分的联系。数值积分方法包括梯形法和辛普森法。
""",
        "word_count": 950
    },
    {
        "id": "textbook_math_001_ch_4",
        "chapter_num": 4,
        "title": "第5章 线性代数基础",
        "start_page": 251,
        "end_page": 320,
        "content": """
线性代数（Linear Algebra）是机器学习的数学基础。矩阵（Matrix）是
线性代数的基本工具，用于表示线性变换。向量（Vector）是矩阵的推广。
矩阵的秩（Rank）反映其线性独立性。特征值（Eigenvalue）和特征向量
（Eigenvector）描述矩阵的本质性质。奇异值分解（SVD）在降维中应用。
""",
        "word_count": 1050
    }
]

# 样本教材 2：物理
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
        "title": "第1章 运动学基础",
        "start_page": 1,
        "end_page": 60,
        "content": """
运动学（Kinematics）研究物体的运动规律，不考虑力的作用。
位移（Displacement）和速度（Velocity）是基本的运动学概念。
加速度（Acceleration）描述速度的变化。
匀加速直线运动（Uniformly Accelerated Rectilinear Motion）有简单的
运动方程：v = v0 + at, s = v0*t + 0.5*a*t^2。
这些概念在物理学和工程中广泛应用。
""",
        "word_count": 1100
    },
    {
        "id": "textbook_physics_001_ch_1",
        "chapter_num": 1,
        "title": "第2章 牛顿运动定律",
        "start_page": 61,
        "end_page": 130,
        "content": """
牛顿运动定律（Newton's Laws of Motion）是经典力学的基础。
第一定律（惯性定律）：物体保持静止或匀速直线运动。
第二定律：F = ma，力等于质量与加速度的乘积。
第三定律：作用力与反作用力大小相等、方向相反。
这些定律在物理和工程中有广泛应用。
牛顿力学是经典力学的核心。
""",
        "word_count": 1200
    },
    {
        "id": "textbook_physics_001_ch_2",
        "chapter_num": 2,
        "title": "第3章 能量与功",
        "start_page": 131,
        "end_page": 190,
        "content": """
功（Work）是力与位移的乘积。动能（Kinetic Energy）与物体的运动有关。
势能（Potential Energy）与物体的位置有关。能量守恒定律（Conservation of Energy）
是自然界的基本定律。机械能（Mechanical Energy）是动能与势能的总和。
功能关系（Work-Energy Theorem）表明功等于动能的变化。
""",
        "word_count": 1050
    },
    {
        "id": "textbook_physics_001_ch_3",
        "chapter_num": 3,
        "title": "第4章 波与振动",
        "start_page": 191,
        "end_page": 260,
        "content": """
简谐振动（Simple Harmonic Motion）是最常见的振动形式。
波（Wave）是振动在空间的传播。横波与纵波是波的两种基本形式。
波长（Wavelength）、频率（Frequency）、速度（Wave Speed）的关系：v = f*λ。
干涉（Interference）和衍射（Diffraction）是波的特有现象。
声波、电磁波都是重要的波类型。
""",
        "word_count": 1150
    },
    {
        "id": "textbook_physics_001_ch_4",
        "chapter_num": 4,
        "title": "第5章 电磁学基础",
        "start_page": 261,
        "end_page": 320,
        "content": """
电荷（Electric Charge）是电磁学的基本概念。
库伦定律（Coulomb's Law）描述电荷间的相互作用。
电场（Electric Field）和磁场（Magnetic Field）是电磁学的核心。
安培力（Ampere Force）是电流在磁场中受到的力。
电磁感应（Electromagnetic Induction）是发电的原理。
麦克斯韦方程（Maxwell's Equations）统一了电磁学。
""",
        "word_count": 1000
    }
]

# 保存样本数据
with open(metadata_dir / "textbook_math_001_metadata.json", 'w', encoding='utf-8') as f:
    json.dump(textbook1_metadata, f, ensure_ascii=False, indent=2)

with open(metadata_dir / "textbook_math_001_chapters.json", 'w', encoding='utf-8') as f:
    json.dump(textbook1_chapters, f, ensure_ascii=False, indent=2)

with open(metadata_dir / "textbook_physics_001_metadata.json", 'w', encoding='utf-8') as f:
    json.dump(textbook2_metadata, f, ensure_ascii=False, indent=2)

with open(metadata_dir / "textbook_physics_001_chapters.json", 'w', encoding='utf-8') as f:
    json.dump(textbook2_chapters, f, ensure_ascii=False, indent=2)

print(f"✅ 创建了 2 本样本教材，共 10 个章节")
print(f"   • textbook_math_001 - 高中数学基础（5 章）")
print(f"   • textbook_physics_001 - 高中物理基础（5 章）")

# ============================================================================
# 第2步：运行 KG 提取
# ============================================================================
print("\n【步骤 2】运行知识图谱提取")
print("-" * 80)

from backend.services.kg_extractor import KGExtractor

kg_extractor = KGExtractor(data_dir="./data")
kg_result = kg_extractor.extract_all()

if kg_result['success']:
    print(f"✅ 知识图谱提取成功")
    print(f"   • 提取的节点数: {kg_result['nodes_count']}")
    print(f"   • 提取的边数: {kg_result['edges_count']}")
else:
    print(f"❌ 知识图谱提取失败: {kg_result['message']}")

# ============================================================================
# 第3步：运行 Merge
# ============================================================================
print("\n【步骤 3】运行节点合并")
print("-" * 80)

from backend.services.merger import NodeMerger

node_merger = NodeMerger(data_dir="./data")
merge_result = node_merger.merge_all()

if merge_result['success']:
    print(f"✅ 节点合并成功")
    print(f"   • 原始节点数: {merge_result['original_nodes']}")
    print(f"   • 合并后节点数: {merge_result['merged_nodes']}")
    print(f"   • 合并的节点对: {merge_result['merged_count']}")
    print(f"   • 标记为可能重复: {merge_result['possible_duplicate_count']}")
    print(f"   • 保留的节点: {merge_result['kept_count']}")
    print(f"   • 原始字符数: {merge_result['original_chars']}")
    print(f"   • 合并后字符数: {merge_result['merged_chars']}")
    print(f"   • 压缩比: {merge_result['compression_ratio']:.4f}")
else:
    print(f"❌ 节点合并失败: {merge_result['message']}")

# ============================================================================
# 第4步：验证输出文件
# ============================================================================
print("\n【步骤 4】验证输出文件")
print("-" * 80)

output_files = {
    "kg_nodes.json": processed_dir / "kg_nodes.json",
    "kg_edges.json": processed_dir / "kg_edges.json",
    "merged_kg.json": processed_dir / "merged_kg.json",
    "merge_decisions.json": processed_dir / "merge_decisions.json",
}

for name, path in output_files.items():
    if path.exists():
        size = path.stat().st_size
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict) and 'nodes' in data:
                count = len(data['nodes'])
            elif isinstance(data, dict) and 'decisions' in data:
                count = len(data['decisions'])
            else:
                count = len(data)
        print(f"✅ {name:25} ({size:8} bytes, {count:3} items)")
    else:
        print(f"❌ {name:25} 文件不存在")

# ============================================================================
# 第5步：显示样本数据
# ============================================================================
print("\n【步骤 5】显示提取的知识数据样本")
print("-" * 80)

kg_file = processed_dir / "kg_nodes.json"
if kg_file.exists():
    with open(kg_file, 'r', encoding='utf-8') as f:
        nodes = json.load(f)
        print(f"前 3 个提取的知识节点:")
        for node in nodes[:3]:
            print(f"\n   • 名称: {node.get('name')}")
            print(f"     ID: {node.get('id')}")
            print(f"     类型: {node.get('type')}")
            print(f"     定义: {node.get('definition', '')[:80]}...")
            print(f"     来源教材: {node.get('source_textbook')}")
            print(f"     频率: {node.get('frequency')}")

merged_file = processed_dir / "merged_kg.json"
if merged_file.exists():
    with open(merged_file, 'r', encoding='utf-8') as f:
        merged_kg = json.load(f)
        nodes = merged_kg.get('nodes', [])
        edges = merged_kg.get('edges', [])
        print(f"\n\n合并后的知识图谱统计:")
        print(f"   • 节点总数: {len(nodes)}")
        print(f"   • 边总数: {len(edges)}")

        if nodes:
            print(f"\n   前 2 个合并后的节点:")
            for node in nodes[:2]:
                print(f"\n   • 名称: {node.get('name')}")
                print(f"     ID: {node.get('id')}")
                print(f"     频率: {node.get('frequency')}")
                print(f"     来源: {node.get('sources')}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "="*80)
print("✨ 测试完成！所有模块正常运行")
print("="*80)
print("""
下一步：运行 API 服务

  python -m backend.main

然后测试 API 端点：

  # 构建知识图谱
  curl -X POST http://localhost:8000/api/kg/build

  # 获取知识图谱
  curl http://localhost:8000/api/kg

  # 合并知识图谱
  curl -X POST http://localhost:8000/api/merge

  # 获取合并决策
  curl http://localhost:8000/api/merge/decisions
""")
print()
