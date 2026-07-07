import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "../outputs/traffic_samples";
await fs.mkdir(outputDir, { recursive: true });

const rawRows = [
  ["001", "事故警情", "报警人称，建设路与民安街交叉口两辆小轿车发生追尾，占用一条直行车道，现场通行缓慢。"],
  ["002", "事故警情", "群众报警反映，东环高架由南向北方向一辆货车与小客车刮碰，无人员受伤，车辆停在右侧车道。"],
  ["003", "事故警情", "110转警，长江路西段一辆电动自行车与轿车发生碰撞，骑车人倒地，需交警和急救到场。"],
  ["004", "事故警情", "报警称，人民大道隧道入口处一辆面包车故障停驶，后方车辆排队明显，存在安全隐患。"],
  ["005", "事故警情", "市民来电称，解放路小学门口有两车轻微剐蹭，双方正在路中协商，影响早高峰车辆通行。"],
  ["006", "事故警情", "接警信息显示，机场快速路出城方向一辆小客车撞上中央护栏，占用最左侧车道，现场无明火。"],
  ["007", "事故警情", "报警人称，新华桥桥面一辆摩托车摔倒，驾驶人受伤，桥面车辆避让导致短时拥堵。"],
  ["008", "事故警情", "群众报警，北二环辅路一辆公交车与出租车发生碰撞，乘客已下车等候，现场需要民警处置。"],
  ["009", "道路巡查记录", "巡查发现，滨河路由东向西方向车流量较大，青年桥至文化路段车辆缓行，未发现事故。"],
  ["010", "道路巡查记录", "巡查至南山路时发现，路面养护施工占用外侧两条车道，现场已设置锥桶和警示标志。"],
  ["011", "道路巡查记录", "巡查人员发现，和平街与春风路路口信号灯不亮，车辆通行秩序混乱，已通知维护单位。"],
  ["012", "道路巡查记录", "巡查记录显示，环城高速K45附近大雾明显，能见度较低，部分车辆开启双闪低速行驶。"],
  ["013", "道路巡查记录", "巡查发现，西湖路非机动车道有多辆机动车违法停放，影响非机动车正常通行。"],
  ["014", "道路巡查记录", "巡查至开发区大道时，发现前方临时交通管制，车辆需从科技路绕行，现场有警力疏导。"],
  ["015", "道路巡查记录", "巡查人员在站前路发现井盖破损，车辆经过时存在颠簸风险，已联系市政部门处理。"],
  ["016", "道路巡查记录", "巡查发现，迎宾大道进城方向因车流集中，收费站出口排队约三百米，通行速度较慢。"],
  ["017", "群众投诉", "市民反映，幸福路菜市场门前长期有车辆占道停车，早晚高峰经常造成公交车无法进站。"],
  ["018", "群众投诉", "群众投诉称，金桂街夜间施工车辆频繁出入，临时占用机动车道，周边车辆通行受影响。"],
  ["019", "群众投诉", "市民来电反映，龙泉路与学府街路口信号灯配时异常，绿灯时间过短，早高峰排队严重。"],
  ["020", "群众投诉", "群众反映，雨后兴业路铁路涵洞积水较深，小型车辆不敢通行，现场未见明显提示牌。"],
  ["021", "群众投诉", "市民投诉，万达广场周边网约车随意上下客，占用右转车道，导致后方车辆连续排队。"],
  ["022", "群众投诉", "群众反映，东风路施工围挡设置过宽，早高峰只剩一条车道通行，车辆拥堵时间较长。"],
  ["023", "群众投诉", "市民称，河西大街部分路段护栏倒伏多日未修复，夜间车辆变道时容易发生危险。"],
  ["024", "交通新闻", "今日上午，市区中山路发生一起三车追尾事故，事故造成该路段短时拥堵，交警已到场处理。"],
  ["025", "交通新闻", "受连续降雨影响，外环东路低洼路段出现积水，交管部门提醒车辆减速慢行，避免涉水通行。"],
  ["026", "交通新闻", "因地铁施工需要，明日起友谊路部分车道将临时封闭，过往车辆可绕行胜利街和青年路。"],
  ["027", "交通新闻", "晚高峰期间，南湖大桥进城方向车流集中，桥面车辆行驶缓慢，交警已加强现场疏导。"],
  ["028", "交通新闻", "城区多处学校周边开展违法停车整治行动，交警对占用斑马线和消防通道车辆依法处罚。"],
  ["029", "交通新闻", "因大型活动安保需要，体育中心周边道路将实施分时段交通管制，公交线路同步调整。"],
  ["030", "交通新闻", "交管部门通报，人民路与广场街路口监控设备故障正在抢修，提醒驾驶人按现场标志通行。"],
];

const classificationRows = [
  ["001", "交通事故", "追尾事故"], ["002", "交通事故", "车辆刮碰"], ["003", "交通事故", "机动车与非机动车碰撞"],
  ["004", "其他事件", "车辆故障"], ["005", "交通事故", "车辆剐蹭"], ["006", "交通事故", "撞护栏事故"],
  ["007", "交通事故", "摩托车摔倒"], ["008", "交通事故", "车辆碰撞"], ["009", "道路拥堵", "车辆缓行"],
  ["010", "道路施工", "养护施工"], ["011", "设施故障", "信号灯故障"], ["012", "恶劣天气影响", "大雾影响"],
  ["013", "违法行为", "违法停车"], ["014", "交通管制", "临时交通管制"], ["015", "设施故障", "井盖破损"],
  ["016", "道路拥堵", "排队缓行"], ["017", "违法行为", "占道停车"], ["018", "道路施工", "临时占道施工"],
  ["019", "设施故障", "信号灯配时异常"], ["020", "恶劣天气影响", "雨后积水"], ["021", "违法行为", "违法上下客"],
  ["022", "道路施工", "施工围挡影响通行"], ["023", "设施故障", "护栏倒伏"], ["024", "交通事故", "追尾事故"],
  ["025", "恶劣天气影响", "降雨积水"], ["026", "交通管制", "施工临时封闭"], ["027", "道路拥堵", "车辆缓行"],
  ["028", "违法行为", "违法停车"], ["029", "交通管制", "活动交通管制"], ["030", "设施故障", "监控设备故障"],
];

const entityRows = [
  ["001", "", "建设路与民安街交叉口", "建设路；民安街", "两辆小轿车", "", "占用一条直行车道", "现场通行缓慢", ""],
  ["002", "", "东环高架由南向北方向", "东环高架", "一辆货车；小客车", "无人员受伤", "车辆停在右侧车道", "", ""],
  ["003", "", "长江路西段", "长江路", "一辆电动自行车；轿车", "骑车人倒地", "", "", "需交警和急救到场"],
  ["004", "", "人民大道隧道入口处", "人民大道", "一辆面包车", "", "故障停驶", "后方车辆排队明显", ""],
  ["005", "早高峰", "解放路小学门口", "解放路", "两车", "", "影响早高峰车辆通行", "", "双方正在路中协商"],
  ["006", "", "机场快速路出城方向；中央护栏", "机场快速路", "一辆小客车", "", "占用最左侧车道", "", "现场无明火"],
  ["007", "", "新华桥桥面", "新华桥", "一辆摩托车", "驾驶人受伤", "桥面车辆避让", "短时拥堵", ""],
  ["008", "", "北二环辅路", "北二环辅路", "一辆公交车；出租车", "", "", "", "乘客已下车等候；现场需要民警处置"],
  ["009", "", "滨河路由东向西方向；青年桥至文化路段", "滨河路；青年桥；文化路", "", "", "车流量较大", "车辆缓行", "未发现事故"],
  ["010", "", "南山路；外侧两条车道", "南山路", "", "", "占用外侧两条车道", "", "现场已设置锥桶和警示标志"],
  ["011", "", "和平街与春风路路口", "和平街；春风路", "", "", "车辆通行秩序混乱", "", "已通知维护单位"],
  ["012", "", "环城高速K45附近", "环城高速", "部分车辆", "", "低速行驶", "", "开启双闪"],
  ["013", "", "西湖路非机动车道", "西湖路", "多辆机动车；非机动车", "", "影响非机动车正常通行", "", ""],
  ["014", "", "开发区大道；科技路", "开发区大道；科技路", "车辆", "", "车辆需从科技路绕行", "", "现场有警力疏导"],
  ["015", "", "站前路", "站前路", "车辆", "", "车辆经过时存在颠簸风险", "", "已联系市政部门处理"],
  ["016", "", "迎宾大道进城方向；收费站出口", "迎宾大道", "", "", "车流集中", "排队约三百米；通行速度较慢", ""],
  ["017", "长期；早晚高峰", "幸福路菜市场门前", "幸福路", "车辆；公交车", "", "占道停车；公交车无法进站", "", ""],
  ["018", "夜间", "金桂街", "金桂街", "施工车辆；车辆", "", "临时占用机动车道；周边车辆通行受影响", "", ""],
  ["019", "早高峰", "龙泉路与学府街路口", "龙泉路；学府街", "", "", "", "排队严重", ""],
  ["020", "雨后", "兴业路铁路涵洞", "兴业路", "小型车辆", "", "小型车辆不敢通行", "", "现场未见明显提示牌"],
  ["021", "", "万达广场周边；右转车道", "", "网约车；车辆", "", "占用右转车道", "后方车辆连续排队", ""],
  ["022", "早高峰", "东风路", "东风路", "车辆", "", "只剩一条车道通行", "车辆拥堵时间较长", ""],
  ["023", "多日；夜间", "河西大街部分路段", "河西大街", "车辆", "", "夜间车辆变道时容易发生危险", "", "未修复"],
  ["024", "今日上午", "市区中山路；该路段", "中山路", "三车", "", "", "短时拥堵", "交警已到场处理"],
  ["025", "连续降雨", "外环东路低洼路段", "外环东路", "车辆", "", "避免涉水通行", "", "交管部门提醒车辆减速慢行"],
  ["026", "明日起", "友谊路；胜利街；青年路", "友谊路；胜利街；青年路", "车辆", "", "部分车道将临时封闭；过往车辆可绕行胜利街和青年路", "", ""],
  ["027", "晚高峰期间", "南湖大桥进城方向；桥面", "南湖大桥", "车辆", "", "车流集中", "车辆行驶缓慢", "交警已加强现场疏导"],
  ["028", "", "城区多处学校周边；斑马线；消防通道", "", "车辆", "", "占用斑马线和消防通道", "", "交警依法处罚"],
  ["029", "", "体育中心周边道路", "", "公交线路", "", "实施分时段交通管制；公交线路同步调整", "", ""],
  ["030", "", "人民路与广场街路口", "人民路；广场街", "驾驶人", "", "按现场标志通行", "", "正在抢修"],
];

const jsonRows = [
  ["交通事故", "追尾事故", null, "建设路与民安街交叉口", "建设路；民安街", 2, null, "占用一条直行车道", "现场通行缓慢"],
  ["交通事故", "车辆刮碰", null, "东环高架由南向北方向", "东环高架", null, "无人员受伤", "车辆停在右侧车道", null],
  ["交通事故", "机动车与非机动车碰撞", null, "长江路西段", "长江路", null, "骑车人倒地", null, null],
  ["其他事件", "车辆故障", null, "人民大道隧道入口处", "人民大道", 1, null, "故障停驶", "后方车辆排队明显"],
  ["交通事故", "车辆剐蹭", "早高峰", "解放路小学门口", "解放路", 2, null, "影响早高峰车辆通行", null],
  ["交通事故", "撞护栏事故", null, "机场快速路出城方向；中央护栏", "机场快速路", 1, null, "占用最左侧车道", null],
  ["交通事故", "摩托车摔倒", null, "新华桥桥面", "新华桥", 1, "驾驶人受伤", "桥面车辆避让", "短时拥堵"],
  ["交通事故", "车辆碰撞", null, "北二环辅路", "北二环辅路", null, null, null, null],
  ["道路拥堵", "车辆缓行", null, "滨河路由东向西方向；青年桥至文化路段", "滨河路；青年桥；文化路", null, null, "车流量较大", "车辆缓行"],
  ["道路施工", "养护施工", null, "南山路；外侧两条车道", "南山路", null, null, "占用外侧两条车道", null],
  ["设施故障", "信号灯故障", null, "和平街与春风路路口", "和平街；春风路", null, null, "车辆通行秩序混乱", null],
  ["恶劣天气影响", "大雾影响", null, "环城高速K45附近", "环城高速", null, null, "低速行驶", null],
  ["违法行为", "违法停车", null, "西湖路非机动车道", "西湖路", null, null, "影响非机动车正常通行", null],
  ["交通管制", "临时交通管制", null, "开发区大道；科技路", "开发区大道；科技路", null, null, "车辆需从科技路绕行", null],
  ["设施故障", "井盖破损", null, "站前路", "站前路", null, null, "车辆经过时存在颠簸风险", null],
  ["道路拥堵", "排队缓行", null, "迎宾大道进城方向；收费站出口", "迎宾大道", null, null, "车流集中", "排队约三百米；通行速度较慢"],
  ["违法行为", "占道停车", "长期；早晚高峰", "幸福路菜市场门前", "幸福路", null, null, "占道停车；公交车无法进站", null],
  ["道路施工", "临时占道施工", "夜间", "金桂街", "金桂街", null, null, "临时占用机动车道；周边车辆通行受影响", null],
  ["设施故障", "信号灯配时异常", "早高峰", "龙泉路与学府街路口", "龙泉路；学府街", null, null, null, "排队严重"],
  ["恶劣天气影响", "雨后积水", "雨后", "兴业路铁路涵洞", "兴业路", null, null, "小型车辆不敢通行", null],
  ["违法行为", "违法上下客", null, "万达广场周边；右转车道", null, null, null, "占用右转车道", "后方车辆连续排队"],
  ["道路施工", "施工围挡影响通行", "早高峰", "东风路", "东风路", null, null, "只剩一条车道通行", "车辆拥堵时间较长"],
  ["设施故障", "护栏倒伏", "多日；夜间", "河西大街部分路段", "河西大街", null, null, "夜间车辆变道时容易发生危险", null],
  ["交通事故", "追尾事故", "今日上午", "市区中山路；该路段", "中山路", 3, null, null, "短时拥堵"],
  ["恶劣天气影响", "降雨积水", "连续降雨", "外环东路低洼路段", "外环东路", null, null, "避免涉水通行", null],
  ["交通管制", "施工临时封闭", "明日起", "友谊路；胜利街；青年路", "友谊路；胜利街；青年路", null, null, "部分车道将临时封闭；过往车辆可绕行胜利街和青年路", null],
  ["道路拥堵", "车辆缓行", "晚高峰期间", "南湖大桥进城方向；桥面", "南湖大桥", null, null, "车流集中", "车辆行驶缓慢"],
  ["违法行为", "违法停车", null, "城区多处学校周边；斑马线；消防通道", null, null, null, "占用斑马线和消防通道", null],
  ["交通管制", "活动交通管制", null, "体育中心周边道路", null, null, null, "实施分时段交通管制；公交线路同步调整", null],
  ["设施故障", "监控设备故障", null, "人民路与广场街路口", "人民路；广场街", null, null, "按现场标志通行", null],
];

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const raw = workbook.worksheets.add("Raw_Texts");
const cls = workbook.worksheets.add("Classification");
const ent = workbook.worksheets.add("Entities");
const std = workbook.worksheets.add("Standard_JSON");

const palette = {
  title: "#1F4E78",
  header: "#D9EAF7",
  subheader: "#E2F0D9",
  border: "#B7C9D6",
  white: "#FFFFFF",
};

function styleSheet(sheet, usedRange, headerRange) {
  sheet.showGridLines = false;
  headerRange.format = {
    fill: palette.title,
    font: { bold: true, color: palette.white },
    wrapText: true,
  };
  usedRange.format.borders = { preset: "all", style: "thin", color: palette.border };
  usedRange.format.wrapText = true;
  usedRange.format.font = { name: "Microsoft YaHei", size: 10 };
  headerRange.format.font = { name: "Microsoft YaHei", size: 10, bold: true, color: palette.white };
  usedRange.format.autofitColumns();
  usedRange.format.autofitRows();
}

raw.getRange("A1:C31").values = [["id", "source_type", "source_text"], ...rawRows];
styleSheet(raw, raw.getRange("A1:C31"), raw.getRange("A1:C1"));
raw.getRange("A:A").format.columnWidth = 8;
raw.getRange("B:B").format.columnWidth = 18;
raw.getRange("C:C").format.columnWidth = 92;
raw.freezePanes.freezeRows(1);
raw.tables.add("A1:C31", true, "RawTextsTable");

cls.getRange("A1:C31").values = [["id", "event_type", "event_subtype"], ...classificationRows];
styleSheet(cls, cls.getRange("A1:C31"), cls.getRange("A1:C1"));
cls.getRange("A:A").format.columnWidth = 8;
cls.getRange("B:C").format.columnWidth = 22;
cls.freezePanes.freezeRows(1);
cls.tables.add("A1:C31", true, "ClassificationTable");

ent.getRange("A1:I31").values = [["id", "TIME", "LOCATION", "ROAD", "VEHICLE", "CASUALTY", "ROAD_IMPACT", "CONGESTION", "DISPOSAL"], ...entityRows];
styleSheet(ent, ent.getRange("A1:I31"), ent.getRange("A1:I1"));
ent.getRange("A:A").format.columnWidth = 8;
ent.getRange("B:B").format.columnWidth = 18;
ent.getRange("C:E").format.columnWidth = 30;
ent.getRange("F:I").format.columnWidth = 32;
ent.freezePanes.freezeRows(1);
ent.tables.add("A1:I31", true, "EntitiesTable");

std.getRange("A1:I31").values = [["event_type", "event_subtype", "event_time", "location", "road_name", "vehicle_count", "casualties", "road_impact", "congestion_level"], ...jsonRows];
styleSheet(std, std.getRange("A1:I31"), std.getRange("A1:I1"));
std.getRange("A:E").format.columnWidth = 24;
std.getRange("F:F").format.columnWidth = 14;
std.getRange("G:I").format.columnWidth = 32;
std.getRange("F2:F31").format.numberFormat = "#,##0";
std.freezePanes.freezeRows(1);
std.tables.add("A1:I31", true, "StandardJsonTable");

summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["交通事件文本训练数据汇总"]];
summary.getRange("A1").format = {
  fill: palette.title,
  font: { bold: true, color: palette.white, size: 16, name: "Microsoft YaHei" },
  horizontalAlignment: "center",
};

summary.getRange("A3:B8").values = [
  ["指标", "数量"],
  ["样本总数", rawRows.length],
  ["来源类型数", new Set(rawRows.map((r) => r[1])).size],
  ["事件类型数", new Set(classificationRows.map((r) => r[1])).size],
  ["有时间信息样本", jsonRows.filter((r) => r[2] !== null).length],
  ["有拥堵描述样本", jsonRows.filter((r) => r[8] !== null).length],
];

const sourceCounts = [...new Map(rawRows.map((r) => [r[1], rawRows.filter((x) => x[1] === r[1]).length])).entries()];
summary.getRange(`D3:E${3 + sourceCounts.length}`).values = [["source_type", "count"], ...sourceCounts];

const eventTypes = [...new Set(classificationRows.map((r) => r[1]))];
const eventCounts = eventTypes.map((type) => [type, classificationRows.filter((r) => r[1] === type).length]);
summary.getRange(`A11:B${11 + eventCounts.length}`).values = [["event_type", "count"], ...eventCounts];

summary.getRange("D11:H11").values = [["工作表", "内容", "行数", "字段数", "备注"]];
summary.getRange("D12:H15").values = [
  ["Raw_Texts", "30条原始交通事件文本", 30, 3, "保留原文"],
  ["Classification", "事件类型与子类型", 30, 3, "审核通过分类"],
  ["Entities", "8类实体抽取结果", 30, 9, "空值保留为空"],
  ["Standard_JSON", "标准Schema字段", 30, 9, "空值为null"],
];

for (const range of ["A3:B8", "D3:E7", "A11:B18", "D11:H15"]) {
  const r = summary.getRange(range);
  r.format.borders = { preset: "all", style: "thin", color: palette.border };
  r.format.font = { name: "Microsoft YaHei", size: 10 };
}
for (const range of ["A3:B3", "D3:E3", "A11:B11", "D11:H11"]) {
  summary.getRange(range).format = {
    fill: palette.header,
    font: { bold: true, color: "#17365D", name: "Microsoft YaHei", size: 10 },
  };
}
summary.getRange("A:A").format.columnWidth = 22;
summary.getRange("B:B").format.columnWidth = 12;
summary.getRange("D:D").format.columnWidth = 20;
summary.getRange("E:E").format.columnWidth = 30;
summary.getRange("F:H").format.columnWidth = 14;

for (const sheetName of ["Summary", "Raw_Texts", "Classification", "Entities", "Standard_JSON"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${outputDir}/${sheetName}.png`, new Uint8Array(await preview.arrayBuffer()));
}

const overview = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 5000,
  tableMaxRows: 4,
  tableMaxCols: 6,
});
console.log(overview.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(`${outputDir}/samples.xlsx`);
