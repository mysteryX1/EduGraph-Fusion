from fastapi import APIRouter, HTTPException, status
from typing import Dict
import json
from pathlib import Path

from ..services.report_generator import ReportGenerator

router = APIRouter(prefix="/api/report", tags=["Report"])


@router.post("/generate")
async def generate_report() -> Dict:
    """生成整合报告

    根据已解析教材、知识图谱和合并决策生成综合报告

    Returns:
        包含报告路径和摘要的响应
    """
    try:
        generator = ReportGenerator(
            data_dir="./data/processed",
            report_dir="./report"
        )

        result = generator.generate_report()

        if result.get('success'):
            return {
                'status': 'success',
                'message': 'Report generated successfully',
                'data': {
                    'report_file': result.get('report_file'),
                    'report_path': result.get('report_path'),
                    'generated_at': result.get('generated_at'),
                    'summary': result.get('summary')
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to generate report')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/latest")
async def get_latest_report() -> Dict:
    """获取最新的报告

    Returns:
        最新报告的内容和元数据
    """
    try:
        report_file = Path("./report/整合报告.md")

        if not report_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No report found. Call /api/report/generate first"
            )

        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'status': 'success',
            'message': 'Report retrieved successfully',
            'data': {
                'report_file': '整合报告.md',
                'report_path': str(report_file),
                'modified_at': report_file.stat().st_mtime,
                'content': content
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}"
        )


@router.get("/summary")
async def get_report_summary() -> Dict:
    """获取报告摘要

    Returns:
        报告的关键统计和摘要
    """
    try:
        report_file = Path("./report/整合报告.md")

        if not report_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No report found. Call /api/report/generate first"
            )

        generator = ReportGenerator(
            data_dir="./data/processed",
            report_dir="./report"
        )

        textbook_stats = generator._get_textbook_stats()
        kg_stats = generator._get_kg_stats()
        merge_stats = generator._get_merge_stats()

        return {
            'status': 'success',
            'message': 'Report summary retrieved successfully',
            'data': {
                'textbooks': {
                    'total': textbook_stats.get('total_textbooks', 0),
                    'original_words': textbook_stats.get('total_words', 0),
                    'merged_words': textbook_stats.get('merged_words', 0),
                    'compression_ratio': textbook_stats.get('compression_ratio', 0)
                },
                'knowledge_graph': {
                    'nodes': kg_stats.get('nodes_count', 0),
                    'edges': kg_stats.get('edges_count', 0),
                    'node_types': kg_stats.get('node_types', {})
                },
                'decisions': {
                    'keep': merge_stats.get('keep_count', 0),
                    'remove': merge_stats.get('remove_count', 0),
                    'merge': merge_stats.get('merge_count', 0),
                    'split': merge_stats.get('split_count', 0),
                    'total': merge_stats.get('total_decisions', 0)
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )
