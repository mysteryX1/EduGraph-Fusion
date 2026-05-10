"""
API 集成测试脚本

使用示例:
    python test_api.py

需要先启动 API 服务:
    python -m uvicorn backend.main:app --reload
"""

import requests
import json
from pathlib import Path
import time

BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_root():
    """测试根路由"""
    print("\n=== 测试根路由 ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def create_test_file():
    """创建测试文件"""
    test_file = Path("./test_sample.txt")

    if test_file.exists():
        return str(test_file)

    content = """这是一个测试文档。

第1章 介绍
这是第一章的内容。本章介绍了基本概念和原理。包含了多个段落来展示文本解析功能。
我们使用固定字数（默认1000字）来分割无法识别章节的文本。这是一个重要的功能，可以确保长文本被合理地分割成可管理的章节。

第2章 详细说明
这是第二章的内容。本章详细说明了实现细节和技术要点。
内容较多，用来测试文本分割的正确性。每个章节应该包含足够的文本来演示系统的能力。

第3章 案例分析
这是第三章的内容。本章分析了一些实际案例和应用场景。
通过具体例子来说明文档解析的各个方面和最佳实践。

结论
最后是结论部分。总结了文档的主要内容和关键要点。
这部分用来结束示例文档。
"""

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return str(test_file)


def test_upload_file():
    """测试文件上传"""
    print("\n=== 测试文件上传 ===")

    test_file = create_test_file()

    with open(test_file, 'rb') as f:
        files = {'file': (Path(test_file).name, f)}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)

    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    if response.status_code == 200:
        textbook_id = result['data']['textbook_id']
        return textbook_id
    return None


def test_parse_textbook(textbook_id):
    """测试教材解析"""
    print(f"\n=== 测试教材解析 ({textbook_id}) ===")

    response = requests.post(f"{BASE_URL}/api/parse/{textbook_id}")
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    return response.status_code == 200


def test_list_textbooks():
    """测试获取教材列表"""
    print("\n=== 测试获取教材列表 ===")

    response = requests.get(f"{BASE_URL}/api/textbooks?limit=10&offset=0")
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    return response.status_code == 200


def test_get_textbook(textbook_id):
    """测试获取单个教材"""
    print(f"\n=== 测试获取单个教材 ({textbook_id}) ===")

    response = requests.get(f"{BASE_URL}/api/textbooks/{textbook_id}")
    print(f"状态码: {response.status_code}")
    result = response.json()

    # 只打印部分信息，避免输出过长
    if response.status_code == 200:
        data = result['data']
        summary = {
            'id': data['id'],
            'title': data['title'],
            'file_type': data['file_type'],
            'chapter_count': data['chapter_count'],
            'total_words': data['total_words'],
        }
        print(f"响应摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
        if 'chapters' in data:
            print(f"章节数: {len(data['chapters'])}")
            if data['chapters']:
                print(f"第一章: {data['chapters'][0]['title']}")
    else:
        print(f"错误: {result}")

    return response.status_code == 200


def test_get_stats():
    """测试获取统计信息"""
    print("\n=== 测试获取统计信息 ===")

    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"状态码: {response.status_code}")
    result = response.json()

    if response.status_code == 200:
        data = result['data']
        summary = {
            'total_textbooks': data['summary']['total_textbooks'],
            'total_chapters': data['summary']['total_chapters'],
            'total_words': data['summary']['total_words'],
            'avg_words_per_chapter': data['summary']['avg_words_per_chapter'],
        }
        print(f"响应摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
        if 'file_types' in data:
            print(f"文件类型分布: {data['file_types']}")
    else:
        print(f"错误: {result}")

    return response.status_code == 200


def test_textbook_stats(textbook_id):
    """测试获取单个教材的统计信息"""
    print(f"\n=== 测试获取教材统计 ({textbook_id}) ===")

    response = requests.get(f"{BASE_URL}/api/textbooks/{textbook_id}/stats")
    print(f"状态码: {response.status_code}")
    result = response.json()

    if response.status_code == 200:
        data = result['data']
        summary = {
            'title': data['title'],
            'file_type': data['file_type'],
            'chapter_count': data['chapter_count'],
            'total_words': data['total_words'],
            'avg_words_per_chapter': data['chapter_stats']['avg_words_per_chapter'],
        }
        print(f"响应摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {result}")

    return response.status_code == 200


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始 API 集成测试")
    print("=" * 50)

    try:
        # 测试基础路由
        if not test_health_check():
            print("\n错误：无法连接到 API 服务，请先运行:")
            print("  python -m uvicorn backend.main:app --reload")
            return

        test_root()

        # 测试文件上传和解析
        textbook_id = test_upload_file()
        if textbook_id:
            # 等待文件处理完成
            time.sleep(1)

            # 测试解析
            if test_parse_textbook(textbook_id):
                # 测试获取教材
                test_get_textbook(textbook_id)
                test_textbook_stats(textbook_id)

        # 测试列表和统计
        test_list_textbooks()
        test_get_stats()

        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\n错误：无法连接到 API 服务，请先运行:")
        print("  python -m uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
