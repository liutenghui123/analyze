"""
图表生成模块 - 包含柏拉图、站点良率、站点SW/HW分布（分组柱状图），以及首测vs终测全局SW/HW对比图
"""

import json
import os
import sys
import shutil
import logging


def _prepare_hourly_yield_chart_data(hourly_data):
    """
    将 hourly_site_yield 数据转换为 ECharts 折线图所需格式。
    返回 (time_labels, series)
      - time_labels: X轴时间标签列表（缩短格式 "MM-DD HH:MM"）
      - series: [{'name': 'Site 0', 'data': [90.91, 89.90, ...]}, ...]
    """
    if not hourly_data:
        return [], []

    # 收集去重有序的时间窗口
    time_labels = []
    seen = set()
    for row in hourly_data:
        key = row['time_window_start']
        if key not in seen:
            seen.add(key)
            time_labels.append(key)

    # 收集所有 Site 并排序
    sites = sorted(set(row['site'] for row in hourly_data))

    # 构建 {(time, site): yield_rate} 映射
    data_map = {}
    for row in hourly_data:
        data_map[(row['time_window_start'], row['site'])] = row['yield_rate']

    # 按 Site 生成各系列数据（无数据点用 None 断开折线）
    series = []
    for site in sites:
        values = [data_map.get((t, site), None) for t in time_labels]
        series.append({
            'name': f'Site {site}',
            'data': values
        })

    # 缩短时间标签: "2026-03-14 05:33:58" -> "03-14 05:33"
    short_labels = []
    for t in time_labels:
        parts = t.split(' ')
        if len(parts) == 2:
            date_parts = parts[0].split('-')
            time_parts = parts[1].split(':')
            if len(date_parts) >= 3 and len(time_parts) >= 2:
                short_labels.append(
                    f"{date_parts[1]}-{date_parts[2]} {time_parts[0]}:{time_parts[1]}")
            else:
                short_labels.append(t)
        else:
            short_labels.append(t)

    return short_labels, series


def generate_pareto_chart(data: dict, title: str, output_html: str = "report.html", logger: logging.Logger = None):
    """
    生成HTML图表报告

    参数:
        data: 分析数据
        title: 报告标题
        output_html: 输出HTML文件路径
        logger: 日志记录器（可选）
    """
    if logger:
        logger.info("开始生成HTML图表报告...")

    ft_combo = data.get("FTdata", {}).get("fail_combo_analysis", [])
    rt_combo = data.get("RTdata", {}).get("fail_combo_analysis", [])
    ft_site = data.get("FTdata", {}).get("site_analysis", [])
    rt_site = data.get("RTdata", {}).get("site_analysis", [])

    ft_sw_by_site = data.get("FTdata", {}).get("sw_bin_by_site", {})
    ft_hw_by_site = data.get("FTdata", {}).get("hw_bin_by_site", {})
    rt_sw_by_site = data.get("RTdata", {}).get("sw_bin_by_site", {})
    rt_hw_by_site = data.get("RTdata", {}).get("hw_bin_by_site", {})

    # 全局 SW_BIN 和 HW_BIN 汇总（用于首测vs终测对比）
    ft_sw_summary = data.get("FTdata", {}).get("sw_bin_summary", [])
    ft_hw_summary = data.get("FTdata", {}).get("hw_bin_summary", [])
    rt_sw_summary = data.get("RTdata", {}).get("sw_bin_summary", [])
    rt_hw_summary = data.get("RTdata", {}).get("hw_bin_summary", [])

    # 提取统计数据
    ft_total = data.get("FTdata", {}).get("total_records", 0)
    ft_failures = data.get("FTdata", {}).get("total_failures", 0)
    rt_total = data.get("RTdata", {}).get("total_records", 0)
    rt_failures = data.get("RTdata", {}).get("total_failures", 0)
    ft_yield = data.get("merged_analysis", {}).get("首测良率(%)", "N/A")
    rt_yield = data.get("merged_analysis", {}).get("最终良率(%)", "N/A")
    file_metadata = data.get("merged_analysis", {}).get("file_metadata") or {}

    ft_categories = [item["组合名称"] for item in ft_combo]
    ft_counts = [item["数量"] for item in ft_combo]
    ft_cum_pct = [item["累计百分比"] for item in ft_combo]

    rt_categories = [item["组合名称"] for item in rt_combo]
    rt_counts = [item["数量"] for item in rt_combo]
    rt_cum_pct = [item["累计百分比"] for item in rt_combo]

    # 辅助：将 summary 列表转换为 { bin: count } 字典
    def summary_to_dict(summary_list):
        return {item['SW_BIN'] if 'SW_BIN' in item else item['HW_BIN']: item['数量'] for item in summary_list}

    ft_sw_dict = summary_to_dict(ft_sw_summary)
    rt_sw_dict = summary_to_dict(rt_sw_summary)
    ft_hw_dict = summary_to_dict(ft_hw_summary)
    rt_hw_dict = summary_to_dict(rt_hw_summary)

    # 收集所有出现的 SW_BIN 和 HW_BIN
    all_sw_bins = sorted(set(ft_sw_dict.keys()) | set(rt_sw_dict.keys()))
    all_hw_bins = sorted(set(ft_hw_dict.keys()) | set(rt_hw_dict.keys()))

    # 构建 FT 和 RT 的数据数组
    ft_sw_counts = [ft_sw_dict.get(b, 0) for b in all_sw_bins]
    rt_sw_counts = [rt_sw_dict.get(b, 0) for b in all_sw_bins]
    ft_hw_counts = [ft_hw_dict.get(b, 0) for b in all_hw_bins]
    rt_hw_counts = [rt_hw_dict.get(b, 0) for b in all_hw_bins]

    # 准备分组柱状图数据（SW_BIN 和 HW_BIN 对比）
    sw_compare_series = [
        {'name': '(首测)', 'data': ft_sw_counts},
        {'name': ' (终测)', 'data': rt_sw_counts}
    ]
    sw_recovery = [round((ft - rt) / ft * 100, 2) if ft >
                   0 else None for ft, rt in zip(ft_sw_counts, rt_sw_counts)]
    hw_compare_series = [
        {'name': ' (首测)', 'data': ft_hw_counts},
        {'name': ' (终测)', 'data': rt_hw_counts}
    ]
    hw_recovery = [round((ft - rt) / ft * 100, 2) if ft >
                   0 else None for ft, rt in zip(ft_hw_counts, rt_hw_counts)]

    # 按站点的分组柱状图数据准备（复用之前的函数）
    def prepare_grouped_bar(site_dict, bin_key):
        if not site_dict:
            return [], []
        all_bins = set()
        for site, items in site_dict.items():
            for item in items:
                all_bins.add(item[bin_key])
        categories = sorted(list(all_bins))
        series = []
        for site, items in site_dict.items():
            count_map = {item[bin_key]: item['数量'] for item in items}
            data = [count_map.get(b, 0) for b in categories]
            series.append({'name': f'SITE {site}', 'data': data})
        return categories, series

    ft_sw_cats, ft_sw_series = prepare_grouped_bar(ft_sw_by_site, 'SW_BIN')
    ft_hw_cats, ft_hw_series = prepare_grouped_bar(ft_hw_by_site, 'HW_BIN')
    rt_sw_cats, rt_sw_series = prepare_grouped_bar(rt_sw_by_site, 'SW_BIN')
    rt_hw_cats, rt_hw_series = prepare_grouped_bar(rt_hw_by_site, 'HW_BIN')

    # 按小时 Site 良率折线图数据
    ft_hourly = data.get("FTdata", {}).get("hourly_site_yield", [])
    rt_hourly = data.get("RTdata", {}).get("hourly_site_yield", [])
    ft_hourly_labels, ft_hourly_series = _prepare_hourly_yield_chart_data(
        ft_hourly)
    rt_hourly_labels, rt_hourly_series = _prepare_hourly_yield_chart_data(
        rt_hourly)

    if logger:
        logger.info(
            f"图表数据准备完成: FT组合={len(ft_categories)}, RT组合={len(rt_categories)}, SW_Bins={len(all_sw_bins)}, HW_Bins={len(all_hw_bins)}")

    # 构建文件元数据 HTML
    metadata_html = ''
    if file_metadata:
        m = file_metadata

        def _mc(k, v):
            return f'<div><span style="color:#888;">{k}:</span> <b>{v}</b></div>'
        gs = 'display:grid;grid-template-columns:1fr 1fr 1fr;padding:4px 0;'
        metadata_html = (
            '<div style="background:white;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);padding:14px 24px;margin-bottom:30px;font-size:14px;color:#333;">'
            f'<div style="padding:4px 0;">{_mc("Customer", m.get("Customer", ""))}</div>'
            f'<div style="{gs}">{_mc("DEVICE", m.get("DEVICE", ""))}{_mc("IntDevice", m.get("IntDevice", ""))}{_mc("PO_NO", m.get("PO_NO", ""))}</div>'
            f'<div style="{gs}">{_mc("LOT_ID", m.get("LOT_ID", ""))}{_mc("Program", m.get("Program", ""))}{_mc("ATE_NO", m.get("ATE_NO", ""))}</div>'
            '</div>'
        )

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="assets/echarts.min.js"></script>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background-color: #f5f7fa; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .chart-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; padding: 20px; }}
        .chart-title {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333; border-left: 5px solid #5470c6; padding-left: 15px; }}
        .subtitle {{ color: #666; margin-bottom: 20px; font-size: 14px; }}
        .chart {{ width: 100%; height: 500px; }}
        .flex-row {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .flex-item {{ flex: 1; min-width: 300px; }}
        .stats-row {{ display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }}
        .stat-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 15px 20px; flex: 1; min-width: 200px; text-align: center; }}
        .stat-label {{ color: #666; font-size: 14px; margin-bottom: 8px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .stat-value.blue {{ color: #5470c6; }}
        .stat-value.green {{ color: #91cc75; }}
    </style>
</head>
<body>
<div class="container">
    <h1 style="text-align:center; color:#2c3e50;">异常单测试数据分析报告</h1>
    
    <!-- 良率统计 -->
    <div style="text-align:center; margin-bottom:20px;">
        <span style="background:#5470c6; color:white; padding:8px 20px; border-radius:20px; font-size:16px; margin-right:15px;">首测良率: {ft_yield}%</span>
        <span style="background:#91cc75; color:white; padding:8px 20px; border-radius:20px; font-size:16px;">最终良率: {rt_yield}%</span>
    </div>

    <!-- 详细统计数据 -->
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-label">首测总数量</div>
            <div class="stat-value blue">{ft_total:,}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">首测失效数量</div>
            <div class="stat-value" style="color:#e74c3c;">{ft_failures:,}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">终测总数量</div>
            <div class="stat-value green">{rt_total:,}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">终测失效数量</div>
            <div class="stat-value" style="color:#e74c3c;">{rt_failures:,}</div>
        </div>
    </div>

    {metadata_html}

    <!-- FTdata 柏拉图 -->
    <div class="chart-card">
        <div class="chart-title">🔵 首测 - 不良组合帕累托图 (Top {len(ft_categories)})</div>
        <div class="subtitle">柱状图: 不良数量 &nbsp;|&nbsp; 折线图: 累计百分比 (%)</div>
        <div id="chart-ft" class="chart"></div>
    </div>

    <!-- RTdata 柏拉图 -->
    <div class="chart-card">
        <div class="chart-title">🟢 终测 - 不良组合帕累托图 (Top {len(rt_categories)})</div>
        <div class="subtitle">柱状图: 不良数量 &nbsp;|&nbsp; 折线图: 累计百分比 (%)</div>
        <div id="chart-rt" class="chart"></div>
    </div>

    <!-- 首测 vs 终测 SW_BIN 对比 -->
    <div class="chart-card">
        <div class="chart-title">📊 软件Bin (SW_BIN) 首测 vs 终测 对比</div>
        <div class="subtitle">横轴：软件Bin值；柱状图：不良数量</div>
        <div id="chart-sw-compare" class="chart"></div>
    </div>

    <!-- 首测 vs 终测 HW_BIN 对比 -->
    <div class="chart-card">
        <div class="chart-title">📊 硬件Bin (HW_BIN) 首测 vs 终测 对比</div>
        <div class="subtitle">横轴：硬件Bin值；柱状图：不良数量</div>
        <div id="chart-hw-compare" class="chart"></div>
    </div>

    <!-- 站点良率对比 -->
    <div class="chart-card">
        <div class="chart-title">🏭 各站点良率对比 (FT vs RT)</div>
        <div class="flex-row">
            <div class="flex-item"><div id="chart-site-ft" style="height:400px;"></div></div>
            <div class="flex-item"><div id="chart-site-rt" style="height:400px;"></div></div>
        </div>
    </div>

    <!-- FTdata 按小时 Site 良率趋势 -->
    <div class="chart-card">
        <div class="chart-title">🔵 首测 (FTdata) - 按小时各 Site 良率趋势</div>
        <div class="subtitle">X轴: 时间窗口 (1小时间隔)；Y轴: 良率 (%)；不同 Site 用不同颜色区分</div>
        <div id="chart-ft-hourly-yield" class="chart" style="height:550px;"></div>
    </div>

    <!-- RTdata 按小时 Site 良率趋势 -->
    <div class="chart-card">
        <div class="chart-title">🟢 终测 (RTdata) - 按小时各 Site 良率趋势</div>
        <div class="subtitle">X轴: 时间窗口 (1小时间隔)；Y轴: 良率 (%)；不同 Site 用不同颜色区分</div>
        <div id="chart-rt-hourly-yield" class="chart" style="height:550px;"></div>
    </div>

    <!-- FTdata 各站点 SW_BIN 分布（分组柱状图） -->
    <div class="chart-card">
        <div class="chart-title">🔵 首测  - 各站点 SW_BIN 分布（分组柱状图）</div>
        <div class="subtitle">每个站点在不同软件Bin上的不良数量对比</div>
        <div id="chart-ft-sw" class="chart"></div>
    </div>

    <!-- FTdata 各站点 HW_BIN 分布（分组柱状图） -->
    <div class="chart-card">
        <div class="chart-title">🔵 首测  - 各站点 HW_BIN 分布（分组柱状图）</div>
        <div class="subtitle">每个站点在不同硬件Bin上的不良数量对比</div>
        <div id="chart-ft-hw" class="chart"></div>
    </div>

    <!-- RTdata 各站点 SW_BIN 分布（分组柱状图） -->
    <div class="chart-card">
        <div class="chart-title">🟢 终测 - 各站点 SW_BIN 分布（分组柱状图）</div>
        <div class="subtitle">每个站点在不同软件Bin上的不良数量对比</div>
        <div id="chart-rt-sw" class="chart"></div>
    </div>

    <!-- RTdata 各站点 HW_BIN 分布（分组柱状图） -->
    <div class="chart-card">
        <div class="chart-title">🟢 终测 - 各站点 HW_BIN 分布（分组柱状图）</div>
        <div class="subtitle">每个站点在不同硬件Bin上的不良数量对比</div>
        <div id="chart-rt-hw" class="chart"></div>
    </div>
</div>

<script>
    // 帕累托图
    function drawPareto(domId, categories, counts, cumPct, color) {{
        var chart = echarts.init(document.getElementById(domId));
        chart.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, formatter: function(params) {{
                let res = params[0].axisValue + '<br/>不良数量: ' + params[0].value;
                if (params[1]) res += '<br/>累计百分比: ' + params[1].value + '%';
                return res;
            }} }},
            xAxis: {{ type: 'category', data: categories, axisLabel: {{ rotate: 45, interval: 0 }} }},
            yAxis: [
                {{ type: 'value', name: '不良数量', position: 'left' }},
                {{ type: 'value', name: '累计百分比 (%)', position: 'right', axisLabel: {{ formatter: '{{value}}%' }}, min: 0, max: 100 }}
            ],
            series: [
                {{ name: '不良数量', type: 'bar', data: counts, itemStyle: {{ color: color, borderRadius: [5,5,0,0] }}, barWidth: '60%', yAxisIndex: 0 }},
                {{ name: '累计百分比', type: 'line', data: cumPct, smooth: false, symbol: 'circle', symbolSize: 8, lineStyle: {{ color: '#ee6666', width: 3 }}, yAxisIndex: 1, tooltip: {{ valueFormatter: (value) => value + '%' }} }}
            ],
            grid: {{ containLabel: true, bottom: 80 }}
        }});
        window.addEventListener('resize', () => chart.resize());
    }}

    // 站点良率柱状图
    function drawSiteYield(domId, siteData, title) {{
        if (!siteData || siteData.length === 0) return;
        var sites = siteData.map(item => 'SITE ' + item.SITE);
        var yields = siteData.map(item => item['良率(%)']);
        var totals = siteData.map(item => item['总数']);
        var fails = siteData.map(item => item['不良数量']);
        var chart = echarts.init(document.getElementById(domId));
        chart.setOption({{
            title: {{ text: title, left: 'center', top: 0 }},
            tooltip: {{ trigger: 'axis', formatter: function(params) {{
                var idx = params[0].dataIndex;
                return params[0].name + '<br/>良率: ' + yields[idx] + '%<br/>总数: ' + totals[idx] + '<br/>不良: ' + fails[idx];
            }} }},
            xAxis: {{ type: 'category', data: sites, axisLabel: {{ rotate: 30 }} }},
            yAxis: {{ type: 'value', name: '良率 (%)', min: 0, max: 100, axisLabel: {{ formatter: '{{value}}%' }} }},
            series: [{{
                type: 'bar', data: yields, itemStyle: {{ color: '#91cc75', borderRadius: [5,5,0,0] }},
                label: {{ show: true, position: 'top', formatter: '{{c}}%' }}
            }}, {{
                type: 'bar', data: yields, barGap: '-100%', silent: true,
                itemStyle: {{ color: 'transparent' }},
                label: {{ show: true, position: 'inside', color: '#fff', fontSize: 13, fontWeight: 'bold',
                    formatter: function(params) {{ return totals[params.dataIndex]; }}
                }}
            }}]
        }});
        window.addEventListener('resize', () => chart.resize());
    }}

    // 通用分组柱状图
    function drawGroupedBar(domId, categories, seriesData, recoveryData) {{
        if (!categories.length || !seriesData.length) {{
            document.getElementById(domId).innerHTML = '<div style="text-align:center;padding:50px;">无数据</div>';
            return;
        }}
        var chart = echarts.init(document.getElementById(domId));
        var tooltipFn = function(params) {{
            var res = params[0].axisValue + '<br/>';
            for (var i = 0; i < params.length; i++) {{
                res += params[i].seriesName + ': ' + params[i].value + '<br/>';
            }}
            if (recoveryData) {{
                var v = recoveryData[params[0].dataIndex];
                if (v !== null) res += '<span style="color:' + (v >= 0 ? '#91cc75' : '#ee6666') + '">回收比例: ' + v + '%</span>';
            }}
            return res;
        }};
        var xAxisCfg = [{{ type: 'category', data: categories, axisLabel: {{ rotate: 45, interval: 0 }} }}];
        if (recoveryData) {{
            xAxisCfg.push({{
                type: 'category', position: 'bottom', offset: 36,
                data: recoveryData.map(function(v) {{ return v === null ? '-' : v + '%'; }}),
                axisLine: {{ show: false }}, axisTick: {{ show: false }},
                axisLabel: {{ interval: 0, rotate: 45,
                    color: function(val, idx) {{ var v = recoveryData[idx]; return v !== null && v >= 0 ? '#E8890C' : '#ee6666'; }},
                    fontWeight: 'bold', fontSize: 11
                }}
            }});
        }}
        chart.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, formatter: tooltipFn }},
            legend: {{ data: seriesData.map(s => s.name), top: 0 }},
            grid: {{ containLabel: true, bottom: recoveryData ? 70 : 30, top: 50 }},
            xAxis: xAxisCfg,
            yAxis: {{ type: 'value', name: '不良数量' }},
            series: seriesData.map(s => ({{
                name: s.name, type: 'bar', data: s.data, barGap: 0.1,
                label: {{ show: true, position: 'top' }}
            }}))
        }});
        window.addEventListener('resize', () => chart.resize());
    }}

    // 按小时 Site 良率折线图
    var siteColors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4'];
    function drawHourlyYield(domId, labels, seriesData) {{
        if (!labels.length || !seriesData.length) {{
            document.getElementById(domId).innerHTML = '<div style="text-align:center;padding:50px;">无数据</div>';
            return;
        }}
        var chart = echarts.init(document.getElementById(domId));
        var series = seriesData.map(function(s, idx) {{
            return {{
                name: s.name,
                type: 'line',
                data: s.data,
                smooth: false,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: {{ width: 2, color: siteColors[idx % siteColors.length] }},
                itemStyle: {{ color: siteColors[idx % siteColors.length] }},
                connectNulls: false
            }};
        }});
        chart.setOption({{
            tooltip: {{
                trigger: 'axis',
                formatter: function(params) {{
                    var res = params[0].axisValue + '<br/>';
                    for (var i = 0; i < params.length; i++) {{
                        var val = params[i].value;
                        if (val !== null && val !== undefined) {{
                            res += '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:'
                                + params[i].color + ';margin-right:5px;"></span>'
                                + params[i].seriesName + ': ' + val + '%<br/>';
                        }}
                    }}
                    return res;
                }}
            }},
            legend: {{ data: seriesData.map(s => s.name), top: 0 }},
            grid: {{ left: 60, right: 40, bottom: 80, top: 50 }},
            xAxis: {{
                type: 'category',
                data: labels,
                axisLabel: {{ rotate: 45, interval: 'auto', fontSize: 11 }},
                boundaryGap: false
            }},
            yAxis: {{
                type: 'value',
                name: '良率 (%)',
                min: function(value) {{ return Math.max(0, Math.floor(value.min - 5)); }},
                max: 100,
                axisLabel: {{ formatter: '{{value}}%' }}
            }},
            dataZoom: [
                {{ type: 'inside', start: 0, end: 100 }},
                {{ type: 'slider', start: 0, end: 100, bottom: 10 }}
            ],
            series: series
        }});
        window.addEventListener('resize', () => chart.resize());
    }}

    // 绘制所有图表
    drawPareto('chart-ft', {json.dumps(ft_categories)}, {json.dumps(ft_counts)}, {json.dumps(ft_cum_pct)}, '#5470c6');
    drawPareto('chart-rt', {json.dumps(rt_categories)}, {json.dumps(rt_counts)}, {json.dumps(rt_cum_pct)}, '#91cc75');
    
    drawGroupedBar('chart-sw-compare', {json.dumps(all_sw_bins)}, {json.dumps(sw_compare_series)}, {json.dumps(sw_recovery)});
    drawGroupedBar('chart-hw-compare', {json.dumps(all_hw_bins)}, {json.dumps(hw_compare_series)}, {json.dumps(hw_recovery)});
    
    drawSiteYield('chart-site-ft', {json.dumps(ft_site)}, '首测 各站点良率');
    drawSiteYield('chart-site-rt', {json.dumps(rt_site)}, '终测 各站点良率');

    drawHourlyYield('chart-ft-hourly-yield', {json.dumps(ft_hourly_labels)}, {json.dumps(ft_hourly_series)});
    drawHourlyYield('chart-rt-hourly-yield', {json.dumps(rt_hourly_labels)}, {json.dumps(rt_hourly_series)});

    drawGroupedBar('chart-ft-sw', {json.dumps(ft_sw_cats)}, {json.dumps(ft_sw_series)});
    drawGroupedBar('chart-ft-hw', {json.dumps(ft_hw_cats)}, {json.dumps(ft_hw_series)});
    drawGroupedBar('chart-rt-sw', {json.dumps(rt_sw_cats)}, {json.dumps(rt_sw_series)});
    drawGroupedBar('chart-rt-hw', {json.dumps(rt_hw_cats)}, {json.dumps(rt_hw_series)});
</script>
</body>
</html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)

    if logger:
        logger.info(f"HTML报告已生成: {os.path.abspath(output_html)}")

    # 复制assets文件夹到输出目录（确保ECharts库可用）
    output_dir = os.path.dirname(os.path.abspath(output_html))
    assets_src = _get_assets_path()
    assets_dst = os.path.join(output_dir, 'assets')

    if assets_src and os.path.exists(assets_src):
        _copy_assets(assets_src, assets_dst, logger)
    else:
        if logger:
            logger.warning(f"未找到assets文件夹，HTML中的ECharts可能无法加载")
        print(f"[警告] 未找到assets文件夹，请确保report.html与assets文件夹在同一目录")

    print(f"[OK] 完整图表报告已生成: {os.path.abspath(output_html)}")


def _get_assets_path():
    """
    获取assets文件夹路径（支持多位置查找）
    """
    # 1. 开发环境：脚本同级目录
    assets_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'assets')
    if os.path.exists(assets_path):
        return assets_path

    # 2. PyInstaller打包环境：_MEIPASS目录
    if getattr(sys, 'frozen', False):
        assets_path = os.path.join(sys._MEIPASS, 'assets')
        if os.path.exists(assets_path):
            return assets_path

    return None


def _copy_assets(src, dst, logger=None):
    """
    复制assets文件夹到目标位置
    """
    try:
        # 源路径和目标路径相同时，无需复制
        if os.path.normpath(os.path.abspath(src)) == os.path.normpath(os.path.abspath(dst)):
            if logger:
                logger.info(f"assets源路径与目标路径相同，跳过复制: {src}")
            return

        if os.path.exists(dst):
            # 如果目标已存在，先删除
            shutil.rmtree(dst)

        shutil.copytree(src, dst)

        if logger:
            logger.info(f"已复制assets文件夹: {src} -> {dst}")
        else:
            print(f"[OK] 已复制ECharts库到输出目录")

    except Exception as e:
        if logger:
            logger.error(f"复制assets文件夹失败: {str(e)}")
        else:
            print(f"[错误] 复制文件失败: {str(e)}")
