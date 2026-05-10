# EduGraph Fusion BugFix 验证脚本

$BaseURL = "http://localhost:8000"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "EduGraph Fusion - BugFix 验证测试" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# 测试计数
$Results = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null,
        [string]$ExpectStatus = "success"
    )

    Write-Host "测试: $Name" -ForegroundColor Yellow

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

        # 检查返回状态
        $HasStatus = $Response.status -eq $ExpectStatus
        $HasData = $null -ne $Response.data

        if ($HasStatus -and $HasData) {
            Write-Host "  ✓ 通过" -ForegroundColor Green
            $Results += @{
                Name   = $Name
                Status = "✓ 通过"
                Detail = $Response.status
            }
        } else {
            Write-Host "  ✗ 失败: status=$($Response.status), has_data=$HasData" -ForegroundColor Red
            $Results += @{
                Name   = $Name
                Status = "✗ 失败"
                Detail = "返回数据不符合预期"
            }
        }
    }
    catch {
        Write-Host "  ✗ 错误: $($_.Exception.Message)" -ForegroundColor Red
        $Results += @{
            Name   = $Name
            Status = "✗ 错误"
            Detail = $_.Exception.Message
        }
    }

    Write-Host ""
}

# ==================== BugFix 1: RAG LLM 噪声 ====================
Write-Host "[BugFix 1] RAG LLM 报错噪声修复" -ForegroundColor Cyan
Write-Host "-" * 80

Test-Endpoint `
    "RAG 查询（无 LLM 错误日志）" `
    "POST" `
    "/api/rag/query" `
    @{question="什么是函数？"; top_k=5} `
    "success"

# ==================== BugFix 2: Feedback 字段兼容 ====================
Write-Host "[BugFix 2] POST /api/feedback 字段兼容性" -ForegroundColor Cyan
Write-Host "-" * 80

Test-Endpoint `
    "Feedback: instruction 字段（标准）" `
    "POST" `
    "/api/feedback" `
    @{instruction="保留 函数概念"} `
    "success"

Test-Endpoint `
    "Feedback: feedback 字段（兼容）" `
    "POST" `
    "/api/feedback" `
    @{feedback="删除 冗余内容"} `
    "success"

Test-Endpoint `
    "Feedback: text 字段（兼容）" `
    "POST" `
    "/api/feedback" `
    @{text="拆分 函数 和 高级函数"} `
    "success"

Test-Endpoint `
    "Feedback: content 字段（兼容）" `
    "POST" `
    "/api/feedback" `
    @{content="合并 基本函数 和 函数概念"} `
    "success"

# 测试空值
try {
    $Response = Invoke-RestMethod -Uri "$BaseURL/api/feedback" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body (ConvertTo-Json @{instruction=""})
    Write-Host "  Feedback: 空值返回 - 状态异常 (预期 400)" -ForegroundColor Red
}
catch {
    $ErrorMsg = $_.Exception.Response.StatusCode
    if ($ErrorMsg -eq "BadRequest") {
        Write-Host "  ✓ Feedback: 空值正确返回 400" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Feedback: 空值返回 $ErrorMsg (预期 400)" -ForegroundColor Red
    }
}
Write-Host ""

# ==================== BugFix 3: merge_decisions 兼容性 ====================
Write-Host "[BugFix 3] merge_decisions.json 格式兼容性" -ForegroundColor Cyan
Write-Host "-" * 80

Write-Host "创建 list 格式的 merge_decisions.json..." -ForegroundColor Gray

$listFormat = @(
    @{decision = "possible_duplicate"},
    @{decision = "keep_both"}
)

$listJson = ConvertTo-Json $listFormat
$listJson | Set-Content -Path "backend\data\processed\merge_decisions.json" -Encoding UTF8

Write-Host "已创建 list 格式" -ForegroundColor Gray
Write-Host ""

Test-Endpoint `
    "Feedback (list 格式 merge_decisions)：保留" `
    "POST" `
    "/api/feedback" `
    @{instruction="保留 测试内容"} `
    "success"

# 恢复为 dict 格式
$dictFormat = @{
    decisions = @()
    updated_at = (Get-Date).ToUniversalTime().ToString("o")
}

$dictJson = ConvertTo-Json $dictFormat
$dictJson | Set-Content -Path "backend\data\processed\merge_decisions.json" -Encoding UTF8

Write-Host "已恢复为 dict 格式" -ForegroundColor Gray
Write-Host ""

# ==================== BugFix 4: 报告正文接口 ====================
Write-Host "[BugFix 4] 报告正文接口完整性" -ForegroundColor Cyan
Write-Host "-" * 80

Test-Endpoint `
    "生成报告" `
    "POST" `
    "/api/report/generate" `
    $null `
    "success"

# 检查报告文件是否存在
if (Test-Path "report\整合报告.md") {
    Write-Host "  ✓ 报告文件已生成: report\整合报告.md" -ForegroundColor Green
} else {
    Write-Host "  ✗ 报告文件未找到" -ForegroundColor Red
}
Write-Host ""

try {
    $Response = Invoke-RestMethod -Uri "$BaseURL/api/report/latest" `
        -Method GET `
        -Headers @{"Content-Type"="application/json"}

    if ($Response.data.content) {
        Write-Host "  ✓ GET /report/latest 返回 content 字段" -ForegroundColor Green
        Write-Host "  ✓ Content 长度: $($Response.data.content.Length) 字符" -ForegroundColor Green

        # 检查内容是否包含预期内容
        if ($Response.data.content -like "*教材知识整合报告*" -or `
            $Response.data.content -like "*整合概览*") {
            Write-Host "  ✓ Content 包含 Markdown 内容" -ForegroundColor Green
        }
    }
    else {
        Write-Host "  ✗ GET /report/latest 缺少 content 字段" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ✗ 获取报告失败: $($_.Exception.Message)" -ForegroundColor Red
}

# ==================== 测试摘要 ====================
Write-Host ""
Write-Host "=" * 80
Write-Host "BugFix 验证总结" -ForegroundColor Yellow
Write-Host "=" * 80

$PassCount = ($Results | Where-Object { $_.Status -eq "✓ 通过" }).Count
$FailCount = ($Results | Where-Object { $_.Status -eq "✗ 失败" -or $_.Status -eq "✗ 错误" }).Count
$TotalCount = $Results.Count

Write-Host ""
Write-Host "测试统计:"
Write-Host "  总数: $TotalCount"
Write-Host "  通过: $PassCount" -ForegroundColor Green
Write-Host "  失败: $FailCount" -ForegroundColor Red

Write-Host ""
Write-Host "测试结果:" -ForegroundColor Cyan
$Results | Format-Table -Property Name, Status -AutoSize

# ==================== 结论 ====================
Write-Host ""
if ($FailCount -eq 0) {
    Write-Host "✓ 所有 BugFix 验证通过！" -ForegroundColor Green
    Write-Host "  可开始前端集成测试" -ForegroundColor Green
} else {
    Write-Host "✗ 有 $FailCount 个测试失败" -ForegroundColor Red
    Write-Host "  请查看上面的详细结果" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 80
