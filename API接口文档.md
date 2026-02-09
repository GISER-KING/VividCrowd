# 数字面试官新增API接口文档

## 简历管理API

### 1. 上传简历
```
POST /api/digital-interviewer/resumes/upload
Content-Type: multipart/form-data

参数：
- file: 简历文件（PDF/Word/图片）
- candidate_name: 候选人姓名（可选）
- candidate_id: 候选人ID（可选）

返回：
{
  "message": "简历上传成功",
  "resume_id": 1,
  "resume": {...},
  "quality_score": 85
}
```

### 2. 获取简历列表
```
GET /api/digital-interviewer/resumes?skip=0&limit=20

返回：
{
  "resumes": [...],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

### 3. 简历职位匹配
```
POST /api/digital-interviewer/resumes/{resume_id}/match

参数：
- job_ids: 职位ID列表（可选，不传则匹配所有职位）

返回：
{
  "message": "匹配完成",
  "resume_id": 1,
  "matches": [
    {
      "job_id": 1,
      "match_score": 85,
      "priority": "high",
      "recommendations": [...]
    }
  ]
}
```

## 候选人管理API

### 4. 批量导入候选人
```
POST /api/digital-interviewer/candidates/batch-import
Content-Type: multipart/form-data

参数：
- file: Excel或CSV文件

返回：
{
  "message": "批量导入完成",
  "success_count": 50,
  "failed_count": 2,
  "errors": [...]
}
```

## 数据导出API

### 5. 导出面试结果
```
GET /api/digital-interviewer/interviews/export?start_date=2026-01-01&end_date=2026-12-31

返回：Excel文件流
```

## 评分模板API

### 6. 创建评分模板
```
POST /api/digital-interviewer/scoring-templates
Content-Type: multipart/form-data

参数：
- name: 模板名称
- job_type: 岗位类型
- technical_weight: 技术能力权重（默认25）
- communication_weight: 沟通表达权重（默认15）
- ... (其他6个维度权重)

注意：所有权重总和必须为100

返回：
{
  "message": "评分模板创建成功",
  "template": {...}
}
```

### 7. 获取评分模板列表
```
GET /api/digital-interviewer/scoring-templates?job_type=technical

返回：
{
  "templates": [...]
}
```
