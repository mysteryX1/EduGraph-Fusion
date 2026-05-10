# EduGraph Fusion API 测试脚本

$BaseURL = "http://localhost:8000"
$Results = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null
    )

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "测试: $Name" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan

    try {
        $Params = @{
            Uri     = "$BaseURL$Endpoint"
            Method  = $Method
            Headers = @{ "Content-Type" = "application/json" }
        }

        if ($Body) {
            $Params["Body"] = ConvertTo-Json $Body
        }

        $Response = Invoke-RestMethod @Params

        Write-Host "✓ 成功" -ForegroundColor Green
        Write-Host "响应:" -ForegroundColor Gray
        Write-Host (ConvertTo-Json $Response -Depth 3) -ForegroundColor White

        $Results += @{
            Name   = $Name
            Status = "✓ 成功"
            Time   = Get-Date
        }
    }
    catch {
        Write-Host "✗ 失败" -ForegroundColor Red
        Write-Host "错误: $($_.Exception.Message)" -ForegroundColor Red

        $Results += @{
            Name   = $Name
            Status = "✗ 失败"
            Error  = $_.Exception.Message
            Time   = Get-Date
        }
    }
}

# 测试序列
Write-Host "开始 EduGraph Fusion API 测试..." -ForegroundColor Green
Write-Host "API 地址: $BaseURL" -ForegroundColor Cyan
Write-Host ""

# 1. 建立 RAG 索引
Test-Endpoint -Name "1. 建立 RAG 索引" -Method "POST" -Endpoint "/api/rag/index"

# 2. 获取 RAG 索引状态
Test-Endpoint -Name "2. 获取 RAG 索引状态" -Method "GET" -Endpoint "/api/rag/status"

# 3. 查询知识库
Test-Endpoint -Name "3. 查询知识库 - 函数概念" -Method "POST" -Endpoint "/api/rag/query" -Body @{
    question = "什么是函数？"
    top_k    = 5
}

# 4. 查询不存在的内容
Test-Endpoint -Name "4. 查询不存在的内容" -Method "POST" -Endpoint "/api/rag/query" -Body @{
    question = "火星上有什么？"
    top_k    = 5
}

# 5. 提交反馈 - 保留
Test-Endpoint -Name "5. 反馈: 保留 函数概念" -Method "POST" -Endpoint "/api/feedback" -Body @{
    instruction = "保留 函数概念"
}

# 6. 提交反馈 - 删除
Test-Endpoint -Name "6. 反馈: 删除 冗余内容" -Method "POST" -Endpoint "/api/feedback" -Body @{
    instruction = "删除 冗余内容"
}

# 7. 提交反馈 - 拆分
Test-Endpoint -Name "7. 反馈: 拆分 函数概念 和 高级函数" -Method "POST" -Endpoint "/api/feedback" -Body @{
    instruction = "拆分 函数概念 和 高级函数"
}

# 8. 提交反馈 - 合并
Test-Endpoint -Name "8. 反馈: 合并 基本函数 和 函数概念" -Method "POST" -Endpoint "/api/feedback" -Body @{
    instruction = "合并 基本函数 和 函数概念"
}

# 9. 获取反馈摘要
Test-Endpoint -Name "9. 获取反馈摘要" -Method "GET" -Endpoint "/api/feedback/summary"

# 10. 生成报告
Test-Endpoint -Name "10. 生成整合报告" -Method "POST" -Endpoint "/api/report/generate"

# 11. 获取最新报告
Test-Endpoint -Name "11. 获取最新报告" -Method "GET" -Endpoint "/api/report/latest"

# 12. 获取报告摘要
Test-Endpoint -Name "12. 获取报告摘要" -Method "GET" -Endpoint "/api/report/summary"

# 输出测试摘要
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "测试摘要" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$SuccessCount = ($Results | Where-Object { $_.Status -eq "✓ 成功" }).Count
$FailureCount = ($Results | Where-Object { $_.Status -eq "✗ 失败" }).Count
$TotalCount = $Results.Count

Write-Host ""
Write-Host "总共: $TotalCount 个测试" -ForegroundColor White
Write-Host "成功: $SuccessCount" -ForegroundColor Green
Write-Host "失败: $FailureCount" -ForegroundColor Red

Write-Host ""
Write-Host "详细结果:" -ForegroundColor Cyan
$Results | Format-Table -Property Name, Status -AutoSize

# 检查报告文件
Write-Host ""
Write-Host "检查生成的文件..." -ForegroundColor Cyan
if (Test-Path ".\report\整合报告.md") {
    Write-Host "✓ 报告文件已生成: .\report\整合报告.md" -ForegroundColor Green
    Write-Host ""
    Write-Host "报告内容 (前 500 字符):" -ForegroundColor Gray
    Get-Content ".\report\整合报告.md" | Select-Object -First 10
}
else {
    Write-Host "✗ 报告文件未找到" -ForegroundColor Red
}

# 检查数据文件
Write-Host ""
Write-Host "检查数据目录..." -ForegroundColor Cyan
Write-Host ""
Write-Host "backend/data/metadata:" -ForegroundColor Cyan
Get-ChildItem ".\backend\data\metadata" -ErrorAction SilentlyContinue | Select-Object Name, Length

Write-Host ""
Write-Host "backend/data/processed:" -ForegroundColor Cyan
Get-ChildItem ".\backend\data\processed" -ErrorAction SilentlyContinue | Select-Object Name, Length

Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green
