# Fenxi8 - 半导体测试数据分析工具

## 项目简介

Fenxi8 是一款专业的半导体芯片测试数据分析工具，用于分析首测（FT - First Test）和终测（RT - Retest/Final Test）的CSV测试数据，自动生成包含多维度统计分析的可视化HTML报告。

### 核心功能

- **多格式兼容**：自动识别3种常见ATE测试设备CSV格式
- **批量处理**：支持文件夹级别的CSV文件批处理
- **深度分析**：HW_BIN/HW_BIN不良统计、站点良率、组合不良帕累托分析
- **可视化报告**：基于ECharts生成交互式HTML图表报告
- **双模式运行**：同时支持命令行（CLI）和图形界面（GUI）两种使用方式
- **API集成**：可选将分析结果JSON发送到AI分析接口

---

## 技术栈

| 类别         | 技术/库  | 版本        | 用途                    |
| ------------ | -------- | ----------- | ----------------------- |
| **编程语言** | Python   | 3.13+       | 核心开发语言            |
| **数据处理** | pandas   | 2.2+        | DataFrame操作、数据分析 |
| **数值计算** | numpy    | 2.1+        | 数值运算支持            |
| **HTTP请求** | requests | 2.32+       | API数据发送（可选）     |
| **GUI框架**  | tkinter  | 内置        | 桌面图形界面            |
| **图表库**   | ECharts  | 5.5.0 (CDN) | HTML交互式图表渲染      |

---

## 安装说明

### 环境要求

- Python 3.13 或更高版本
- Windows / macOS / Linux 操作系统

### 安装步骤

1. **克隆或下载项目代码**

```bash
cd Fenxi8
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv .venv
```

3. **激活虚拟环境**

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

4. **安装依赖**

```bash
pip install pandas numpy requests
```

或使用 `requirements.txt`（如已创建）：

```bash
pip install -r requirements.txt
```

---

## 项目架构

### 目录结构

```
Fenxi8/
├── FTdata/                    # 首测数据文件夹（放置FT CSV文件）
│   ├── GT9916K_EQC_RT_V121C_*.csv
│   └── GT9916K_FT_RT2_V121C_*.csv
│
├── RTdata/                    # 终测数据文件夹（放置RT CSV文件）
│   └── 2.csv
│
├── main.py                    # 命令行入口脚本
├── ui.py                      # GUI图形界面程序
│
├── file_parser.py             # CSV格式检测与解析模块
├── data_cleaner.py            # 数据清洗与列映射模块
├── analyzer.py                # 不良统计分析模块
├── folder_processor.py        # 文件夹批处理核心逻辑
├── merge_analyzer.py          # 首测/终测合并分析模块
├── chart_generator.py         # ECharts图表生成模块
│
├── README.md                  # 项目说明文档
└── report.html                # 生成的HTML报告（输出文件）
```

### 模块职责

#### 1. file_parser.py - 文件格式检测

- **detect_header_format()**: 自动识别CSV表头格式（支持format1/format2/format3）
- **is_valid_data_row()**: 过滤无效数据行（空行、单位行等）
- **parse_date()**: 多格式日期时间解析（支持6种常见日期格式）
- **read_csv_file()**: UTF-8/GBK双编码读取CSV文件

#### 2. data_cleaner.py - 数据清洗

- **map_columns()**: 将不同格式的列名统一映射为标准列（HW_BIN, SW_BIN, SITE）
- **convert_int_columns()**: 转换为可空整数类型Int64
- **parse_test_time()**: 解析测试时间字段
- **build_dataframe()**: 构建并清洗DataFrame

#### 3. analyzer.py - 统计分析

- **compute_sw_bin_summary()**: SW_BIN（软件Bin）不良统计及占比
- **compute_hw_bin_summary()**: HW_BIN（硬件Bin）不良统计及占比
- **compute_fail_combos()**: HW/SW组合不良Top N分析（帕累托图数据源）
- **compute_site_stats()**: 站点良率统计
- **compute_sw_bin_by_site()**: 按站点分组的SW_BIN分布
- **compute_hw_bin_by_site()**: 按站点分组的HW_BIN分布

#### 4. folder_processor.py - 文件夹批处理

- **process_folder()**: 处理单个文件夹的所有CSV文件
  - 扫描所有CSV文件
  - 提取ProductName（内部型号）
  - 自动检测格式并解析
  - 合并所有数据
  - 执行多维度统计分析

#### 5. merge_analyzer.py - 合并分析

- **compute_merged_analysis()**: 计算首测良率和最终良率
  - 首测良率 = (1 - FT_failures / FT_total) × 100%
  - 最终良率 = (1 - RT_failures / FT_total) × 100%

#### 6. chart_generator.py - 图表生成

- **generate_pareto_chart()**: 基于ECharts生成HTML交互式报告
  - 首测/终测不良组合帕累托图（柏拉图）
  - SW_BIN/HW_BIN首测vs终测对比柱状图
  - 各站点良率对比图
  - 各站点SW_BIN/HW_BIN分组柱状图（4个）

#### 7. ui.py - 图形界面

- 基于tkinter/ttk构建现代化桌面应用
- 支持选择FTdata/RTdata文件夹和输出目录
- 实时进度显示和状态反馈
- 可选发送JSON到API接口进行AI分析
- 内置帮助系统（自动加载README.md）

#### 8. main.py - 命令行入口

- 无GUI模式下直接运行分析
- 流程：处理FT → 处理RT → 合并分析 → 生成report.html

---

## 使用方法

### 方法一：命令行模式（CLI）

适用于自动化脚本、定时任务或服务器环境：

```bash
python main.py
```

执行后会：

1. 自动读取 `FTdata/` 和 `RTdata/` 文件夹中的CSV文件
2. 执行完整的数据分析和合并计算
3. 在项目根目录生成 `report.html` 报告文件
4. 在终端输出JSON格式的分析结果

### 方法二：图形界面模式（GUI）

适用于日常交互式使用：

```bash
python ui.py
```

操作步骤：

1. 点击"浏览..."按钮选择FTdata文件夹
2. 点击"浏览..."按钮选择RTdata文件夹
3. 选择输出文件夹（默认为当前目录）
4. （可选）勾选"AI分析"并填写API URL
5. 点击"开始分析"按钮
6. 等待完成后查看生成的 `report.html` 文件

---

## 输入数据格式

### 支持的CSV格式

工具自动识别以下3种常见ATE测试设备CSV格式：

#### Format 1 - 标准格式

```csv
TestTime#,LotId#,WaferId,XAdr,YAdr,Site#,HBin,SBin,...
2024/01/15 10:30,LOT001,WAF01,10,20,1,1,100,...
```

#### Format 2 - 简化格式

```csv
TestTime,X_POS,Y_POS,SITE,HW_BIN,SW_BIN,...
2024-01-15 10:30:00,10,20,1,1,100,...
```

#### Format 3 - 扩展格式

```csv
TestTime,LotId,WaferId,XAdr,YAdr,Site,HBIN,SBIN,...
01/15/2024 10:30,LOT001,WAF01,10,20,1,1,100,...
```

### 关键列说明

| 标准列名 | 含义      | 说明                              |
| -------- | --------- | --------------------------------- |
| HW_BIN   | 硬件Bin码 | 1表示通过，其他值表示硬件失败原因 |
| SW_BIN   | 软件Bin码 | 配合HW_BIN定位具体失败类型        |
| SITE     | 测试站点  | 多工位并行测试的站点编号          |
| TestTime | 测试时间  | 支持多种日期时间格式              |
| LotId    | 批次号    | 生产批次标识                      |
| WaferId  | 晶圆ID    | 晶圆编号                          |

### 数据文件命名建议

**FTdata文件夹**：

```
GT9916K_FT_RT2_V121C_20240115_103000.csv
[产品型号]_[测试类型]_[版本号]_[日期]_[时间].csv
```

**RTdata文件夹**：

```
GT9916K_RT_V121C_20240116_143000.csv
[产品型号]_[重测类型]_[版本号]_[日期]_[时间].csv
```

---

## 输出报告

### HTML报告内容

生成的 `report.html` 包含以下9个交互式图表：

1. **首测不良组合帕累托图** - Top 15 HW/SW_BIN组合不良分析
2. **终测不良组合帕累托图** - 重测后的不良组合对比
3. **SW_BIN首测vs终测对比** - 软件Bin全局对比柱状图
4. **HW_BIN首测vs终测对比** - 硬件Bin全局对比柱状图
5. **首测各站点良率** - 多站点良率柱状图
6. **终测各站点良率** - 重测后站点良率对比
7. **首测各站点SW_BIN分布** - 分组柱状图
8. **首测各站点HW_BIN分布** - 分组柱状图
9. **终测各站点SW_BIN分布** - 分组柱状图
10. **终测各站点HW_BIN分布** - 分组柱状图

### 报告特点

- **响应式设计**：最大宽度1400px，适配不同屏幕
- **卡片式布局**：阴影效果，视觉层次清晰
- **交互功能**：鼠标悬停显示详细数据、图例开关、缩放
- **颜色方案**：首测蓝色(#5470c6)、终测绿色(#91cc75)
- **独立文件**：无需本地依赖，可直接用浏览器打开

---

## 配置说明

### 环境变量（可选）

如需自定义默认路径，可在代码中修改：

```python
# ui.py 第44-46行
self.ft_path = tk.StringVar(value="/path/to/FTdata")
self.rt_path = tk.StringVar(value="/path/to/RTdata")
self.out_dir = tk.StringVar(value="/path/to/output")
```

### API集成配置

在GUI界面中勾选"AI分析"后，填写API URL即可将分析结果以JSON格式发送：

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "FTdata": { ... },
    "RTdata": { ... },
    "merged_analysis": { ... }
  }
}
```

API应接受POST请求，Content-Type为 `application/json`。

---

## 常见问题

### Q1: 提示"未找到有效数据"？

**原因**：CSV文件格式不被识别或数据行格式异常

**解决方法**：

1. 检查CSV文件前几行是否包含正确的表头
2. 确认数据行以日期或数字开头
3. 查看控制台输出的错误信息

### Q2: 生成的报告中某些图表无数据？

**原因**：对应维度没有失败记录

**解决方法**：

- 这是正常现象，表示该维度良率为100%
- 检查输入数据中是否有HW_BIN != 1的记录

### Q3: 中文乱码问题？

**原因**：CSV文件编码不是UTF-8或GBK

**解决方法**：

- 工具已支持UTF-8和GBK自动检测
- 如仍有问题，请用记事本另存为UTF-8编码

### Q4: 如何添加新的CSV格式支持？

**步骤**：

1. 在 `file_parser.py` 的 `detect_header_format()` 中添加新的格式识别规则
2. 在 `data_cleaner.py` 的 `map_columns()` 中添加列映射逻辑
3. 确保新格式包含HW_BIN、SW_BIN、SITE三列（或可映射到这三列）

---

## 架构优势

### 设计原则

1. **单一职责**：每个模块只做一类事情，易于理解和测试
2. **高内聚低耦合**：模块间通过标准字典接口通信
3. **可扩展性**：新增CSV格式只需修改parser和cleaner
4. **容错性强**：单文件解析失败不影响整体处理
5. **编码兼容**：支持UTF-8和GBK双编码自动检测

### 可复用性

- `file_parser` 和 `analyzer` 模块可在其他项目中直接使用
- `folder_processor` 可作为通用批处理框架
- `chart_generator` 可适配其他数据源的可视化需求

---

## 开发者指南

### 代码规范

- 遵循PEP 8 Python代码风格指南
- 函数和类必须包含docstring
- 变量命名采用snake_case
- 常量使用UPPER_CASE

### 调试技巧

在 `main.py` 中启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 性能优化建议

- 大数据集（>10万行）建议使用pandas的chunksize参数分批读取
- 图表生成时可减少Top N数量以提升渲染速度
- 避免在循环中频繁调用DataFrame操作

---

## 许可证

本项目仅供学习和内部使用。

---

## 联系方式

如有问题或建议，请联系项目开发团队。

---

_最后更新时间：2026-04-23_
