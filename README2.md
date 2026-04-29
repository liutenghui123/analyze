# Fenxi8 - 半导体测试数据分析工具

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![License](https://img.shields.io/badge/License-Internal-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**专业的半导体芯片测试数据分析工具，一键生成可视化HTML报告**

[功能特点](#-功能特点) • [快速开始](#-快速开始) • [使用文档](#-使用文档) • [打包部署](#-打包部署)

</div>

---

## 📋 项目简介

Fenxi8 是一款专为半导体行业打造的数据分析工具，用于深度分析首测（FT - First Test）和终测（RT - Retest/Final Test）的测试数据。它能够自动识别多种ATE测试设备的数据格式，执行多维度统计分析，并生成交互式可视化HTML报告，帮助工程师快速定位不良模式、优化生产工艺。

### 🎯 应用场景

- **质量控制**：监控生产良率趋势，及时发现异常
- **工艺优化**：分析不良组合，指导工艺改进
- **问题诊断**：通过站点分布分析，定位设备或工位问题
- **报告生成**：自动生成专业图表，支持质量汇报

---

## ✨ 功能特点

### 核心功能

- 🔍 **多格式兼容**：自动识别4种常见ATE测试设备CSV/Tab分隔格式
- 📊 **批量处理**：支持文件夹级别的CSV文件批处理，一次分析多个文件
- 📈 **深度分析**：HW_BIN/SW_BIN不良统计、站点良率、组合不良帕累托分析
- 🎨 **可视化报告**：基于ECharts生成交互式HTML图表，支持缩放、筛选、悬停查看
- 💻 **双模式运行**：同时支持命令行（CLI）和图形界面（GUI）两种使用方式
- 🔌 **API集成**：可选将分析结果JSON发送到AI分析接口进行智能诊断
- 📦 **独立部署**：可打包为exe文件，无需安装Python环境

### 分析维度

| 分析类型         | 说明                         | 图表类型      |
| ---------------- | ---------------------------- | ------------- |
| 不良组合帕累托图 | Top 15 HW/SW_BIN组合不良分析 | 柱状图+折线图 |
| SW/HW_BIN对比    | 首测vs终测软件/硬件Bin对比   | 分组柱状图    |
| 站点良率分析     | 各测试站点良率统计           | 柱状图        |
| 站点BIN分布      | 按站点分组的SW/HW_BIN分布    | 分组柱状图    |

---

## 🚀 快速开始

### 方式一：使用exe文件（推荐，无需安装）

1. 下载 `Fenxi8.exe` 到任意目录
2. 创建 `FTdata/` 和 `RTdata/` 文件夹，放入CSV数据文件
3. 双击运行 `Fenxi8.exe`
4. 选择输入输出文件夹，点击"开始分析"
5. 打开生成的 `report.html` 查看报告

### 方式二：从源码运行

#### 环境要求

- Python 3.13 或更高版本
- Windows / macOS / Linux 操作系统

#### 安装步骤

```bash
# 1. 克隆或下载项目代码
cd Fenxi8

# 2. 创建虚拟环境（推荐）
python -m venv .venv

# 3. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. 安装依赖
pip install pandas numpy requests
```

#### 准备数据

```
Fenxi8/
├── FTdata/              # 首测数据文件夹
│   ├── test1.csv
│   └── test2.csv
└── RTdata/              # 终测数据文件夹
    └── retest1.csv
```

#### 运行程序

```bash
# GUI模式（推荐）
python ui.py

# CLI模式
python main.py
```

---

## 📖 使用文档

### 图形界面（GUI）使用指南

<div align="center">

| 步骤 | 操作             | 说明                              |
| ---- | ---------------- | --------------------------------- |
| 1️⃣   | 选择FTdata文件夹 | 点击"浏览..."按钮选择首测数据目录 |
| 2️⃣   | 选择RTdata文件夹 | 点击"浏览..."按钮选择终测数据目录 |
| 3️⃣   | 选择输出目录     | 指定报告生成位置（默认当前目录）  |
| 4️⃣   | （可选）AI分析   | 勾选并填写API URL发送JSON结果     |
| 5️⃣   | 开始分析         | 点击按钮，等待处理完成            |
| 6️⃣   | 查看报告         | 用浏览器打开生成的 report.html    |

</div>

### 命令行（CLI）使用指南

```bash
# 基本用法（自动读取FTdata/和RTdata/）
python main.py

# 指定输出目录
python main.py "D:\output"
```

**执行流程**：

1. 扫描 `FTdata/` 文件夹中的所有CSV文件
2. 自动检测格式并解析数据
3. 执行多维度统计分析
4. 同样处理 `RTdata/` 文件夹
5. 计算首测良率和最终良率
6. 生成 `report.html` 交互式报告
7. 在终端输出JSON格式的分析结果

### 输入数据格式

#### 支持的格式

工具自动识别以下4种常见ATE测试设备数据格式：

**Format 1 - 标准CSV格式**

```csv
TestTime#,LotId#,WaferId,XAdr,YAdr,Site#,HBin,SBin,...
2024/01/15 10:30,LOT001,WAF01,10,20,1,1,100,...
```

**Format 2 - 简化CSV格式**

```csv
TestTime,X_POS,Y_POS,SITE,HW_BIN,SW_BIN,...
2024-01-15 10:30:00,10,20,1,1,100,...
```

**Format 3 - 扩展CSV格式**

```csv
TestTime,LotId,WaferId,XAdr,YAdr,Site,HBIN,SBIN,...
01/15/2024 10:30,LOT001,WAF01,10,20,1,1,100,...
```

**Format 4 - Tab分隔格式（.xls文本文件）**

```
Customer:	XH
DEVICE:	CSU18M68-QFN16
LOT_ID:	2604222
...
Time	Test_Count	SITE	H_bin	S_bin	temp_sensor	...
2026-03-17 07:54:21	1	0	1	1	23.88	...
```

> ⚠️ **注意**：Format 4的文件扩展名为`.xls`，但实际是Tab分隔的文本文件，不是Excel二进制格式。

#### 关键列说明

| 标准列名   | 含义      | 说明                              |
| ---------- | --------- | --------------------------------- |
| **HW_BIN** | 硬件Bin码 | 1表示通过，其他值表示硬件失败原因 |
| **SW_BIN** | 软件Bin码 | 配合HW_BIN定位具体失败类型        |
| **SITE**   | 测试站点  | 多工位并行测试的站点编号          |
| TestTime   | 测试时间  | 支持多种日期时间格式              |
| LotId      | 批次号    | 生产批次标识                      |
| WaferId    | 晶圆ID    | 晶圆编号                          |

#### 文件命名建议

```
# FTdata文件夹
GT9916K_FT_RT2_V121C_20240115_103000.csv
[产品型号]_[测试类型]_[版本号]_[日期]_[时间].csv

# RTdata文件夹
GT9916K_RT_V121C_20240116_143000.csv
[产品型号]_[重测类型]_[版本号]_[日期]_[时间].csv
```

---

## 📊 输出报告

### HTML报告内容

生成的 `report.html` 包含以下10个交互式图表：

| #   | 图表名称                | 说明                                        |
| --- | ----------------------- | ------------------------------------------- |
| 1   | 🔵 首测不良组合帕累托图 | Top 15 HW/SW_BIN组合，柱状图+累计百分比折线 |
| 2   | 🟢 终测不良组合帕累托图 | 重测后的不良组合对比                        |
| 3   | 📊 SW_BIN首测vs终测对比 | 软件Bin全局对比柱状图                       |
| 4   | 📊 HW_BIN首测vs终测对比 | 硬件Bin全局对比柱状图                       |
| 5   | 🏭 首测各站点良率       | 多站点良率柱状图                            |
| 6   | 🏭 终测各站点良率       | 重测后站点良率对比                          |
| 7   | 📈 首测各站点SW_BIN分布 | 分组柱状图                                  |
| 8   | 📈 首测各站点HW_BIN分布 | 分组柱状图                                  |
| 9   | 📈 终测各站点SW_BIN分布 | 分组柱状图                                  |
| 10  | 📈 终测各站点HW_BIN分布 | 分组柱状图                                  |

### 报告特点

- ✅ **响应式设计**：最大宽度1400px，适配不同屏幕尺寸
- ✅ **卡片式布局**：阴影效果，视觉层次清晰
- ✅ **交互功能**：鼠标悬停显示详细数据、图例开关、缩放
- ✅ **颜色方案**：首测蓝色(#5470c6)、终测绿色(#91cc75)，易于区分
- ✅ **离线可用**：使用本地ECharts库，无需网络连接
- ✅ **统计数据**：顶部显示首测/终测总数量、失效数量、良率等关键指标

### 报告预览结构

```
┌─────────────────────────────────────────────┐
│         半导体测试数据分析报告                 │
├─────────────────────────────────────────────┤
│  首测良率: 95.5%  │  最终良率: 98.2%        │
├─────────────────────────────────────────────┤
│  首测总数量  │  首测失效  │  终测总数量  │ ... │
├─────────────────────────────────────────────┤
│  🔵 首测 - 不良组合帕累托图 (Top 15)         │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓               │
├─────────────────────────────────────────────┤
│  🟢 终测 - 不良组合帕累托图 (Top 15)         │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                       │
├─────────────────────────────────────────────┤
│  📊 SW_BIN 首测 vs 终测 对比                │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓               │
└─────────────────────────────────────────────┘
```

---

## 🏗️ 项目架构

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
├── assets/                    # ECharts库文件夹
│   └── echarts.min.js        # 本地ECharts核心库
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
├── logger_config.py           # 日志配置模块
│
├── Fenxi8.spec               # PyInstaller配置文件（GUI版）
├── Fenxi8_CLI.spec           # PyInstaller配置文件（CLI版）
├── build.bat                 # 一键打包脚本
├── test_exe.bat              # exe测试脚本
│
├── README.md                  # 项目说明文档
├── 打包说明.md                # 打包详细说明
└── report.html                # 生成的HTML报告（输出文件）
```

### 模块职责

#### 1. file_parser.py - 文件格式检测

| 函数                     | 功能                                      |
| ------------------------ | ----------------------------------------- |
| `detect_header_format()` | 自动识别CSV表头格式（支持format1/2/3/4）  |
| `is_valid_data_row()`    | 过滤无效数据行（空行、单位行等）          |
| `parse_date()`           | 多格式日期时间解析（支持6种常见日期格式） |
| `read_csv_file()`        | UTF-8/GBK双编码读取CSV/XLS文件            |

#### 2. data_cleaner.py - 数据清洗

| 函数                    | 功能                                                     |
| ----------------------- | -------------------------------------------------------- |
| `map_columns()`         | 将不同格式的列名统一映射为标准列（HW_BIN, SW_BIN, SITE） |
| `convert_int_columns()` | 转换为可空整数类型Int64                                  |
| `parse_test_time()`     | 解析测试时间字段                                         |
| `build_dataframe()`     | 构建并清洗DataFrame                                      |

#### 3. analyzer.py - 统计分析

| 函数                       | 功能                                     |
| -------------------------- | ---------------------------------------- |
| `compute_sw_bin_summary()` | SW_BIN（软件Bin）不良统计及占比          |
| `compute_hw_bin_summary()` | HW_BIN（硬件Bin）不良统计及占比          |
| `compute_fail_combos()`    | HW/SW组合不良Top N分析（帕累托图数据源） |
| `compute_site_stats()`     | 站点良率统计                             |
| `compute_sw_bin_by_site()` | 按站点分组的SW_BIN分布                   |
| `compute_hw_bin_by_site()` | 按站点分组的HW_BIN分布                   |

#### 4. folder_processor.py - 文件夹批处理

| 函数                     | 功能                        |
| ------------------------ | --------------------------- |
| `process_folder()`       | 处理单个文件夹的所有CSV文件 |
| `extract_product_name()` | 从文件元数据提取产品型号    |

**处理流程**：

```
扫描CSV文件 → 提取产品型号 → 检测格式 → 解析数据 → 合并DataFrame → 统计分析
```

#### 5. merge_analyzer.py - 合并分析

| 函数                        | 功能                   |
| --------------------------- | ---------------------- |
| `compute_merged_analysis()` | 计算首测良率和最终良率 |

**计算公式**：

- 首测良率 = (1 - FT_failures / FT_total) × 100%
- 最终良率 = (1 - RT_failures / FT_total) × 100%

#### 6. chart_generator.py - 图表生成

| 函数                      | 功能                                     |
| ------------------------- | ---------------------------------------- |
| `generate_pareto_chart()` | 基于ECharts生成HTML交互式报告            |
| `_get_assets_path()`      | 智能获取assets文件夹路径（支持打包环境） |
| `_copy_assets()`          | 复制ECharts库到输出目录                  |

#### 7. ui.py - 图形界面

- 基于tkinter/ttk构建现代化桌面应用
- 支持选择FTdata/RTdata文件夹和输出目录
- 实时进度显示和状态反馈
- 可选发送JSON到API接口进行AI分析
- 内置帮助系统（自动加载README.md）

#### 8. main.py - 命令行入口

- 无GUI模式下直接运行分析
- 完整的日志记录
- 支持命令行参数指定输出目录

---

## 📦 打包部署

### 打包为exe文件

项目支持打包为独立的Windows可执行文件，无需安装Python环境即可运行。

#### 快速打包

**方式一：使用批处理脚本（推荐）**

```bash
# 双击运行
build.bat
```

**方式二：手动执行**

```bash
# 1. 安装PyInstaller
pip install pyinstaller

# 2. 打包GUI版本
pyinstaller --clean Fenxi8.spec

# 3. 打包CLI版本
pyinstaller --clean Fenxi8_CLI.spec
```

#### 生成的文件

打包完成后，在 `dist/` 目录下生成：

| 文件             | 大小  | 说明                          |
| ---------------- | ----- | ----------------------------- |
| `Fenxi8.exe`     | ~69MB | GUI图形界面版本，双击运行     |
| `Fenxi8_CLI.exe` | ~66MB | CLI命令行版本，适合自动化脚本 |

#### 分发使用

**最小分发包**：

```
只需分发 Fenxi8.exe 或 Fenxi8_CLI.exe
```

**完整分发包**：

```
Fenxi8/
├── Fenxi8.exe           # 主程序
├── README.md            # 使用说明
├── FTdata/              # 示例数据（可选）
│   └── example.csv
└── RTdata/
    └── example.csv
```

**用户操作步骤**：

1. 将exe文件复制到任意位置
2. 创建 `FTdata/` 和 `RTdata/` 文件夹并放入CSV文件
3. 运行exe程序进行分析
4. 查看生成的 `report.html` 报告

#### ECharts库说明

✅ **自动管理**：程序会自动将 `assets/echarts.min.js` 复制到输出目录

✅ **离线可用**：HTML报告使用本地ECharts库，无需网络连接

✅ **路径自适应**：

- 开发环境：从源代码目录读取
- 打包后：从exe的临时解压目录读取

⚠️ **重要提示**：不要手动删除输出目录中的 `assets/` 文件夹，否则图表将无法显示。

详细打包说明请查看 [`打包说明.md`](打包说明.md)

---

## ⚙️ 配置说明

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
    "FTdata": {
      "total_records": 10000,
      "total_failures": 450,
      "sw_bin_summary": [...],
      "hw_bin_summary": [...],
      "fail_combo_analysis": [...],
      "site_analysis": [...]
    },
    "RTdata": { ... },
    "merged_analysis": {
      "首测良率(%)": 95.5,
      "最终良率(%)": 98.2
    }
  }
}
```

API应接受POST请求，Content-Type为 `application/json`。

---

## ❓ 常见问题

### Q1: 提示"未找到有效数据"？

**原因**：CSV文件格式不被识别或数据行格式异常

**解决方法**：

1. 检查CSV文件前几行是否包含正确的表头
2. 确认数据行以日期或数字开头
3. 查看控制台输出的错误信息
4. 确保文件编码为UTF-8或GBK

### Q2: 生成的报告中某些图表无数据？

**原因**：对应维度没有失败记录

**解决方法**：

- 这是正常现象，表示该维度良率为100%
- 检查输入数据中是否有HW_BIN != 1的记录
- 如果所有芯片都通过测试，则不会有不良分析数据

### Q3: 中文乱码问题？

**原因**：CSV文件编码不是UTF-8或GBK

**解决方法**：

- 工具已支持UTF-8和GBK自动检测
- 如仍有问题，请用记事本打开CSV文件，另存为UTF-8编码
- 避免使用其他特殊编码格式

### Q4: 如何添加新的CSV格式支持？

**步骤**：

1. 在 `file_parser.py` 的 `detect_header_format()` 中添加新的格式识别规则
2. 在 `data_cleaner.py` 的 `map_columns()` 中添加列映射逻辑
3. 确保新格式包含HW_BIN、SW_BIN、SITE三列（或可映射到这三列）
4. 测试新格式文件的解析和分析功能

### Q5: 大数据量处理速度慢？

**优化建议**：

- 大数据集（>10万行）建议使用pandas的chunksize参数分批读取
- 图表生成时可减少Top N数量（默认15）以提升渲染速度
- 关闭不必要的后台程序，释放内存
- 使用SSD硬盘存储数据和输出文件

### Q6: HTML报告打开后图表不显示？

**检查清单**：

1. ✅ 确认输出目录有 `assets/echarts.min.js` 文件
2. ✅ 用现代浏览器打开（推荐Chrome、Edge、Firefox）
3. ✅ 按F12查看控制台是否有错误信息
4. ✅ 确保没有被安全软件拦截JavaScript执行

### Q7: exe文件运行时提示缺少dll？

**解决方法**：

- 这种情况很少见，因为PyInstaller已打包所有依赖
- 如确实缺少，请安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- 联系技术支持获取帮助

---

## 🏆 架构优势

### 设计原则

| 原则             | 说明                                 |
| ---------------- | ------------------------------------ |
| **单一职责**     | 每个模块只做一类事情，易于理解和测试 |
| **高内聚低耦合** | 模块间通过标准字典接口通信，降低依赖 |
| **可扩展性**     | 新增CSV格式只需修改parser和cleaner   |
| **容错性强**     | 单文件解析失败不影响整体处理         |
| **编码兼容**     | 支持UTF-8和GBK双编码自动检测         |

### 可复用性

- 📦 `file_parser` 和 `analyzer` 模块可在其他项目中直接使用
- 🔄 `folder_processor` 可作为通用批处理框架
- 📊 `chart_generator` 可适配其他数据源的可视化需求
- 🛠️ 所有模块都有完整的docstring，便于二次开发

---

## 👨‍💻 开发者指南

### 代码规范

- ✅ 遵循PEP 8 Python代码风格指南
- ✅ 函数和类必须包含docstring
- ✅ 变量命名采用snake_case
- ✅ 常量使用UPPER_CASE
- ✅ 类型注解（可选但推荐）

### 调试技巧

**启用详细日志**：

```python
# main.py 或 ui.py 中添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

**查看日志文件**：

- 每次运行会在输出目录生成 `fenxi8_YYYYMMDD_HHMMSS.log`
- 日志包含详细的处理步骤和错误信息

### 性能优化建议

| 场景     | 建议                                              |
| -------- | ------------------------------------------------- |
| 大数据集 | 使用pandas的chunksize参数分批读取                 |
| 图表渲染 | 减少Top N数量（默认15）                           |
| 内存占用 | 及时释放不再需要的DataFrame                       |
| 循环操作 | 避免在循环中频繁调用DataFrame操作，使用向量化运算 |

### 添加新功能

1. **新增分析维度**：在 `analyzer.py` 中添加新的分析函数
2. **新增图表类型**：在 `chart_generator.py` 中添加新的图表生成逻辑
3. **新增数据格式**：在 `file_parser.py` 和 `data_cleaner.py` 中添加格式支持
4. **更新UI**：在 `ui.py` 中添加新的界面元素

---

## 📝 技术栈

| 类别         | 技术/库     | 版本  | 用途                    |
| ------------ | ----------- | ----- | ----------------------- |
| **编程语言** | Python      | 3.13+ | 核心开发语言            |
| **数据处理** | pandas      | 2.2+  | DataFrame操作、数据分析 |
| **数值计算** | numpy       | 2.1+  | 数值运算支持            |
| **HTTP请求** | requests    | 2.32+ | API数据发送（可选）     |
| **GUI框架**  | tkinter     | 内置  | 桌面图形界面            |
| **图表库**   | ECharts     | 5.5.0 | HTML交互式图表渲染      |
| **打包工具** | PyInstaller | 6.20+ | 打包为exe文件           |

---

## 📄 许可证

本项目仅供学习和内部使用。

---

## 📞 联系方式

如有问题或建议，请联系：

- **开发者**：信息中心 刘腾辉
- **邮箱**：1604020533@qq.com
- **项目地址**：https://github.com/liutenghui123/Fenxi8

---

## 📅 更新日志

### v1.0 (2026-04-23)

- ✅ 首次发布完整版本
- ✅ 支持4种CSV/Tab分隔格式
- ✅ 实现10种交互式图表
- ✅ 提供GUI和CLI双模式
- ✅ 支持打包为exe文件
- ✅ 自动管理ECharts库
- ✅ 完善的日志系统
- ✅ 详细的文档说明

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给一个Star！**

Made with ❤️ by liutenghui0826@outlook.com

</div>
