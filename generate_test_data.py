#!/usr/bin/env python3
"""
生成测试数据的独立脚本
这个脚本不依赖于 backend 模块，只负责生成示例教材数据
"""

import json
from pathlib import Path
from datetime import datetime


def create_test_data():
    """创建测试教材数据"""

    data_dir = Path("./data")
    metadata_dir = data_dir / "metadata"
    processed_dir = data_dir / "processed"

    # 创建必要目录
    metadata_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("📚 生成测试教材数据")
    print("="*80 + "\n")

    # ========================================================================
    # 教材 1：高中数学
    # ========================================================================

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
            "content": "本章介绍集合的基本概念和函数的性质。集合（Set）是数学中的基本概念，由具有某种共同属性的元素组成。函数（Function）是建立两个集合之间对应关系的数学工具。集合的运算包括并集、交集、补集等基本操作。集合的表示方法有列表法、描述法和图形法三种。函数的定义域和值域是函数的重要属性。一次函数、二次函数是最常见的函数类型。",
            "word_count": 1200
        },
        {
            "id": "textbook_math_001_ch_1",
            "chapter_num": 1,
            "title": "第2章 导数与微分",
            "start_page": 51,
            "end_page": 120,
            "content": "导数（Derivative）是微积分中的基本概念，表示函数在某点的变化率。微分（Differential）是导数的应用形式。导数的定义基于极限的概念。常见函数的导数公式包括幂函数、三角函数、指数函数等。导数的应用包括求函数的最值、判断函数的单调性等。梯度下降法（Gradient Descent）在机器学习中广泛应用。反向传播（Backpropagation）算法基于链式求导法则。",
            "word_count": 1350
        },
        {
            "id": "textbook_math_001_ch_2",
            "chapter_num": 2,
            "title": "第3章 三角函数",
            "start_page": 121,
            "end_page": 180,
            "content": "三角函数（Trigonometric Functions）是以角为自变量的函数。主要的三角函数包括正弦（Sine）、余弦（Cosine）、正切（Tangent）等。三角函数在物理中描述周期现象，在工程中应用广泛。三角函数的周期性是其重要特性。傅里叶变换（Fourier Transform）基于三角函数的分解。傅里叶级数（Fourier Series）用三角函数逼近周期函数。",
            "word_count": 1100
        },
        {
            "id": "textbook_math_001_ch_3",
            "chapter_num": 3,
            "title": "第4章 积分学",
            "start_page": 181,
            "end_page": 250,
            "content": "积分（Integration）是微分的逆运算，分为定积分和不定积分。不定积分（Indefinite Integral）求原函数。定积分（Definite Integral）计算函数曲线下的面积。牛顿-莱布尼茨公式（Newton-Leibniz Formula）建立了定积分与不定积分的联系。数值积分方法包括梯形法和辛普森法。",
            "word_count": 950
        },
        {
            "id": "textbook_math_001_ch_4",
            "chapter_num": 4,
            "title": "第5章 线性代数基础",
            "start_page": 251,
            "end_page": 320,
            "content": "线性代数（Linear Algebra）是机器学习的数学基础。矩阵（Matrix）是线性代数的基本工具，用于表示线性变换。向量（Vector）是矩阵的推广。矩阵的秩（Rank）反映其线性独立性。特征值（Eigenvalue）和特征向量（Eigenvector）描述矩阵的本质性质。奇异值分解（SVD）在降维中应用。",
            "word_count": 1050
        }
    ]

    # 保存教材 1
    with open(metadata_dir / "textbook_math_001_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(textbook1_metadata, f, ensure_ascii=False, indent=2)

    with open(metadata_dir / "textbook_math_001_chapters.json", 'w', encoding='utf-8') as f:
        json.dump(textbook1_chapters, f, ensure_ascii=False, indent=2)

    print("✅ 教材 1: 高中数学基础")
    print(f"   • ID: textbook_math_001")
    print(f"   • 章节数: {len(textbook1_chapters)}")
    print(f"   • 总字数: {sum(ch['word_count'] for ch in textbook1_chapters)}")

    # ========================================================================
    # 教材 2：高中物理
    # ========================================================================

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
            "content": "运动学（Kinematics）研究物体的运动规律，不考虑力的作用。位移（Displacement）和速度（Velocity）是基本的运动学概念。加速度（Acceleration）描述速度的变化。匀加速直线运动（Uniformly Accelerated Rectilinear Motion）有简单的运动方程：v = v0 + at, s = v0*t + 0.5*a*t^2。这些概念在物理学和工程中广泛应用。",
            "word_count": 1100
        },
        {
            "id": "textbook_physics_001_ch_1",
            "chapter_num": 1,
            "title": "第2章 牛顿运动定律",
            "start_page": 61,
            "end_page": 130,
            "content": "牛顿运动定律（Newton's Laws of Motion）是经典力学的基础。第一定律（惯性定律）：物体保持静止或匀速直线运动。第二定律：F = ma，力等于质量与加速度的乘积。第三定律：作用力与反作用力大小相等、方向相反。这些定律在物理和工程中有广泛应用。牛顿力学是经典力学的核心。",
            "word_count": 1200
        },
        {
            "id": "textbook_physics_001_ch_2",
            "chapter_num": 2,
            "title": "第3章 能量与功",
            "start_page": 131,
            "end_page": 190,
            "content": "功（Work）是力与位移的乘积。动能（Kinetic Energy）与物体的运动有关。势能（Potential Energy）与物体的位置有关。能量守恒定律（Conservation of Energy）是自然界的基本定律。机械能（Mechanical Energy）是动能与势能的总和。功能关系（Work-Energy Theorem）表明功等于动能的变化。",
            "word_count": 1050
        },
        {
            "id": "textbook_physics_001_ch_3",
            "chapter_num": 3,
            "title": "第4章 波与振动",
            "start_page": 191,
            "end_page": 260,
            "content": "简谐振动（Simple Harmonic Motion）是最常见的振动形式。波（Wave）是振动在空间的传播。横波与纵波是波的两种基本形式。波长（Wavelength）、频率（Frequency）、速度（Wave Speed）的关系：v = f*λ。干涉（Interference）和衍射（Diffraction）是波的特有现象。声波、电磁波都是重要的波类型。",
            "word_count": 1150
        },
        {
            "id": "textbook_physics_001_ch_4",
            "chapter_num": 4,
            "title": "第5章 电磁学基础",
            "start_page": 261,
            "end_page": 320,
            "content": "电荷（Electric Charge）是电磁学的基本概念。库伦定律（Coulomb's Law）描述电荷间的相互作用。电场（Electric Field）和磁场（Magnetic Field）是电磁学的核心。安培力（Ampere Force）是电流在磁场中受到的力。电磁感应（Electromagnetic Induction）是发电的原理。麦克斯韦方程（Maxwell's Equations）统一了电磁学。",
            "word_count": 1000
        }
    ]

    # 保存教材 2
    with open(metadata_dir / "textbook_physics_001_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(textbook2_metadata, f, ensure_ascii=False, indent=2)

    with open(metadata_dir / "textbook_physics_001_chapters.json", 'w', encoding='utf-8') as f:
        json.dump(textbook2_chapters, f, ensure_ascii=False, indent=2)

    print("\n✅ 教材 2: 高中物理基础")
    print(f"   • ID: textbook_physics_001")
    print(f"   • 章节数: {len(textbook2_chapters)}")
    print(f"   • 总字数: {sum(ch['word_count'] for ch in textbook2_chapters)}")

    print("\n" + "="*80)
    print("✨ 测试数据生成完成")
    print("="*80)
    print(f"\n数据位置:")
    print(f"  • 元数据: {metadata_dir}")
    print(f"  • 处理: {processed_dir}")
    print(f"\n数据文件:")
    for f in metadata_dir.glob("*.json"):
        print(f"  • {f.name}")


if __name__ == "__main__":
    create_test_data()
