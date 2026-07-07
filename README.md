# 交通事件文本结构化识别系统

## 1. 项目简介

本项目面向交通警情、道路巡查、交通新闻、群众投诉等中文短文本，提供交通事件结构化识别能力。系统输入一段自然语言交通事件描述，输出统一字段的标准 JSON，便于后续接入交通运行监测、事件台账、可视化看板、应急处置流转或数据分析流程。

当前成果版采用“规则词典 + 正则抽取 + 标准化输出”的轻量方案，不依赖深度学习模型，具备部署简单、响应稳定、结果可解释、规则可迭代的特点。项目同时提供命令行程序、FastAPI 服务、前端 Demo、样本评估器和错误分析工具。

## 2. 系统功能

- 单条交通事件文本结构化识别。
- 多条交通事件文本批量识别。
- 事件类型与事件子类型判定。
- 时间、地点、道路名称、涉事车辆、车辆数量、伤亡情况、道路影响、占用车道、拥堵等级、处置措施、事件状态等字段抽取。
- 标准 JSON 输出，保证固定字段顺序与字段完整性。
- Web API 服务，支持前端和外部系统调用。
- 静态前端 Demo，支持输入文本、发起识别、查看 JSON 结果和字段表格。
- Excel 样本评估，输出事件类型准确率、字段抽取准确率、JSON 格式正确率和分字段指标。
- 错误分析报告生成，辅助后续规则优化。

支持的事件类型包括：

| 事件类型 | 编码 |
| --- | --- |
| 交通事故 | `ACCIDENT` |
| 道路拥堵 | `CONGESTION` |
| 道路施工 | `CONSTRUCTION` |
| 交通管制 | `TRAFFIC_CONTROL` |
| 设施故障 | `FACILITY_FAILURE` |
| 恶劣天气影响 | `WEATHER_IMPACT` |
| 违法行为 | `VIOLATION` |
| 其他事件 | `OTHER` |

## 3. 技术路线

系统采用规则驱动的交通事件信息抽取流程：

1. 文本输入：接收命令行、API 或前端 Demo 提交的中文交通事件文本。
2. 事件分类：基于 `rules/event_keywords.json` 中的事件关键词、优先级和子类型词典进行事件类型匹配。
3. 字段抽取：在 `src/extractor.py` 中通过领域词典、正则表达式和特殊规则抽取时间、地点、道路、车辆、伤亡、影响、处置等字段。
4. 输出标准化：由 `src/schema.py` 统一补齐字段、规范空值和事件编码。
5. 服务封装：由 `app.py` 基于 FastAPI 对外提供 REST API。
6. 结果评估：由 `evaluator.py` 读取 Excel 样本，对比标准答案并生成准确率指标。
7. 错误分析：由 `error_analysis.py` 输出字段级错误明细和优化建议。

核心特点：

- 轻量化：纯 Python 规则系统，启动和推理成本低。
- 可解释：每类事件和字段均可追溯到关键词、正则或显式规则。
- 易扩展：新增事件类型、关键词、车辆词典和字段规则不需要重新训练模型。
- 可评估：提供固定样本集和自动化评估脚本，便于量化迭代效果。

## 4. 项目目录结构

```text
.
├── app.py                              # FastAPI 服务入口
├── main.py                             # 命令行识别入口
├── index.html                          # 前端 Demo 页面
├── evaluator.py                        # Excel 样本评估脚本
├── error_analysis.py                   # 错误分析报告脚本
├── test_samples.py                     # 示例样本运行脚本
├── README.md                           # 项目说明文档
├── 产品设计.md                         # 产品设计说明
├── 技术路线.md                         # 技术方案说明
├── 数据规范.md                         # 数据与字段规范
├── 标注规范.md                         # 样本标注规范
├── src/
│   ├── pipeline.py                     # 识别流水线入口
│   ├── extractor.py                    # 字段抽取规则
│   ├── rule_engine.py                  # 关键词规则引擎
│   ├── schema.py                       # 输出字段与标准化逻辑
│   └── __init__.py
├── rules/
│   └── event_keywords.json             # 事件类型、子类型和车辆词典
├── outputs/
│   ├── traffic_samples/                # 基础样本、截图和检查结果
│   └── generalization_test/            # 泛化测试样本和评估报告
├── workbook_build/
│   ├── build_samples.mjs               # 样本工作簿构建脚本
│   └── build_generalization_test.mjs   # 泛化测试工作簿构建脚本
└── traffic_event_structurer/           # 早期/备用结构化模块
```

## 5. 运行方式

### 5.1 环境准备

建议使用 Python 3.10 及以上版本。

安装 API 与评估所需依赖：

```powershell
pip install fastapi uvicorn pydantic openpyxl
```

### 5.2 命令行运行

交互式输入：

```powershell
python main.py
```

直接传入文本：

```powershell
python main.py --text "今天上午8点30分，重庆市南岸区学府大道发生两车追尾事故，造成1人轻伤，占用右侧车道，现场通行缓慢，交警正在疏导。"
```

输出紧凑 JSON：

```powershell
python main.py --text "今天上午8点30分，重庆市南岸区学府大道发生两车追尾事故，造成1人轻伤。" --compact
```

### 5.3 启动 API 服务

```powershell
uvicorn app:app --reload
```

服务启动后访问：

- API 首页：`http://127.0.0.1:8000/`
- 健康检查：`http://127.0.0.1:8000/health`
- 前端 Demo：`http://127.0.0.1:8000/demo`
- FastAPI 文档：`http://127.0.0.1:8000/docs`

### 5.4 运行评估

使用默认样本：

```powershell
python evaluator.py
```

指定样本文件并保存报告：

```powershell
python evaluator.py --samples outputs/generalization_test/samples_v0.2.xlsx --save-report outputs/generalization_test/eval_current.json
```

生成错误分析 Excel：

```powershell
python error_analysis.py --samples outputs/generalization_test/samples_v0.2.xlsx --output error_report.xlsx
```

## 6. API 接口说明

### 6.1 `GET /`

返回系统名称、版本和接口列表。

### 6.2 `GET /health`

健康检查接口。

响应示例：

```json
{
  "status": "ok"
}
```

### 6.3 `GET /demo`

返回前端 Demo 页面。

### 6.4 `GET /index.html`

返回同一份前端 Demo 页面。

### 6.5 `POST /analyze`

单条文本识别接口。

请求体：

```json
{
  "text": "今天上午8点30分，重庆市南岸区学府大道发生两车追尾事故，造成1人轻伤，占用右侧车道，现场通行缓慢，交警正在疏导。"
}
```

响应体：

```json
{
  "source_text": "今天上午8点30分，重庆市南岸区学府大道发生两车追尾事故，造成1人轻伤，占用右侧车道，现场通行缓慢，交警正在疏导。",
  "event_type": "交通事故",
  "event_type_code": "ACCIDENT",
  "event_subtype": "追尾事故",
  "event_time_text": "今天上午8点30分",
  "location": "重庆市南岸区学府大道",
  "road_name": "学府大道",
  "vehicles_involved": [
    "车辆"
  ],
  "vehicle_count": 2,
  "casualties": "1人受伤",
  "injured_count": 1,
  "death_count": 0,
  "road_impact": "占用右侧车道；通行缓慢",
  "occupied_lane": "占用右侧车道",
  "congestion_level": "缓慢",
  "disposal_measure": "交警正在疏导",
  "event_status": "处理中"
}
```

### 6.6 `POST /batch_analyze`

批量文本识别接口。

请求体：

```json
{
  "texts": [
    "今天上午8点30分，重庆市南岸区学府大道发生两车追尾事故，造成1人轻伤，占用右侧车道，现场通行缓慢，交警正在疏导。",
    "今晚20:10，解放碑隧道内信号灯故障，现场交通拥堵，正在抢修，暂无人员伤亡。"
  ]
}
```

响应体为 JSON 数组，每个元素与 `/analyze` 的单条响应结构一致。

### 6.7 标准输出字段

| 字段 | 含义 |
| --- | --- |
| `source_text` | 原始输入文本 |
| `event_type` | 事件类型 |
| `event_type_code` | 事件类型编码 |
| `event_subtype` | 事件子类型 |
| `event_time_text` | 原文中的时间表达 |
| `location` | 事件位置描述 |
| `road_name` | 道路名称 |
| `vehicles_involved` | 涉事车辆列表 |
| `vehicle_count` | 涉事车辆数量 |
| `casualties` | 伤亡描述 |
| `injured_count` | 受伤人数 |
| `death_count` | 死亡人数 |
| `road_impact` | 道路交通影响 |
| `occupied_lane` | 占用车道 |
| `congestion_level` | 拥堵等级 |
| `disposal_measure` | 处置措施 |
| `event_status` | 事件状态 |

未识别出的普通字段返回 `null`，未识别出的车辆列表返回 `[]`。

## 7. 前端 Demo 使用说明

启动 FastAPI 服务后，在浏览器打开：

```text
http://127.0.0.1:8000/demo
```

使用流程：

1. 在左侧文本框输入或粘贴交通事件描述。
2. 点击“开始识别”。
3. 右侧上方查看标准 JSON 结果。
4. 右侧下方查看字段表格，便于快速核对每个字段的抽取结果。

Demo 默认请求地址为：

```javascript
http://127.0.0.1:8000/analyze
```

因此需要先启动本地 API 服务。若服务端口或部署地址发生变化，需要同步修改 `index.html` 中的 `API_URL`。

## 8. 评估结果

当前成果版以 `outputs/generalization_test/samples_v0.2.xlsx` 中的 50 条泛化测试样本为评估集，评估报告位于 `outputs/generalization_test/eval_after_fastapi_rules.json`。

总体指标：

| 指标 | 结果 |
| --- | ---: |
| 样本数量 | 50 |
| 事件类型准确率 | 94.00% |
| 字段抽取总体准确率 | 66.29% |
| JSON 格式正确率 | 100.00% |
| 事件类型正确数 | 47 / 50 |
| 字段正确数 | 464 / 700 |
| JSON 格式正确数 | 50 / 50 |

分字段准确率：

| 字段 | 准确率 |
| --- | ---: |
| `event_subtype` | 52.00% |
| `event_time_text` | 84.00% |
| `location` | 30.00% |
| `road_name` | 68.00% |
| `vehicles_involved` | 74.00% |
| `vehicle_count` | 80.00% |
| `casualties` | 94.00% |
| `injured_count` | 96.00% |
| `death_count` | 96.00% |
| `road_impact` | 20.00% |
| `occupied_lane` | 72.00% |
| `congestion_level` | 56.00% |
| `disposal_measure` | 74.00% |
| `event_status` | 32.00% |

评估结论：

- JSON 输出稳定，字段完整性达到 100%。
- 事件类型识别效果较好，泛化测试中达到 94%。
- 伤亡人数、车辆数量、时间、处置措施等字段已有较高可用性。
- 地点边界、道路影响、事件状态、事件子类型仍是主要优化方向。

## 9. 后续计划

- 优化地点边界识别，提升路口、方向、入口、隧道、桥面、路段组合表达的抽取准确率。
- 细化 `road_impact` 抽取规则，区分占道、封闭、排队、绕行、通行受阻、车辆避让等影响类型。
- 完善事件状态判定，覆盖“发生中、处理中、已恢复、待确认、计划中”等状态。
- 扩展事件子类型词典，增强多车事故、多设施故障、活动管制、多点拥堵等复杂场景识别。
- 引入置信度字段和规则命中证据，方便人工复核和业务系统展示。
- 增加批量文件上传能力，支持 Excel/CSV 输入与结果导出。
- 建立持续评估集，按事件类型和难度分层跟踪每轮优化效果。
- 预留模型增强分支，在规则无法覆盖的复杂表达中引入大模型或序列标注模型进行补充抽取。
