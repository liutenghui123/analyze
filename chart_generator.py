"""
图表生成模块 - 包含柏拉图、站点良率、站点SW/HW分布（分组柱状图），以及首测vs终测全局SW/HW对比图
"""

import json
import os

def generate_pareto_chart(data: dict, title: str, output_html: str = "report.html"):
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
    hw_compare_series = [
        {'name': ' (首测)', 'data': ft_hw_counts},
        {'name': ' (终测)', 'data': rt_hw_counts}
    ]

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

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background-color: #f5f7fa; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .chart-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; padding: 20px; }}
        .chart-title {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333; border-left: 5px solid #5470c6; padding-left: 15px; }}
        .subtitle {{ color: #666; margin-bottom: 20px; font-size: 14px; }}
        .chart {{ width: 100%; height: 500px; }}
        .flex-row {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .flex-item {{ flex: 1; min-width: 300px; }}
    </style>
</head>
<body>
<div class="container">
    <h1 style="text-align:center; color:#2c3e50;">📊 半导体测试数据分析报告</h1>
    <div style="text-align:center; margin-bottom:30px;">
        <span style="background:#5470c6; color:white; padding:5px 15px; border-radius:20px;">首测良率: {data.get('merged_analysis',{}).get('首测良率(%)', 'N/A')}%</span>
        <span style="background:#91cc75; color:white; padding:5px 15px; border-radius:20px; margin-left:15px;">最终良率: {data.get('merged_analysis',{}).get('最终良率(%)', 'N/A')}%</span>
    </div>

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
        var chart = echarts.init(document.getElementById(domId));
        chart.setOption({{
            title: {{ text: title, left: 'center', top: 0 }},
            tooltip: {{ trigger: 'axis', formatter: '{{b}}<br/>良率: {{c}}%' }},
            xAxis: {{ type: 'category', data: sites, axisLabel: {{ rotate: 30 }} }},
            yAxis: {{ type: 'value', name: '良率 (%)', min: 0, max: 100, axisLabel: {{ formatter: '{{value}}%' }} }},
            series: [{{
                type: 'bar', data: yields, itemStyle: {{ color: '#91cc75', borderRadius: [5,5,0,0] }},
                label: {{ show: true, position: 'top', formatter: '{{c}}%' }}
            }}]
        }});
        window.addEventListener('resize', () => chart.resize());
    }}

    // 通用分组柱状图
    function drawGroupedBar(domId, categories, seriesData) {{
        if (!categories.length || !seriesData.length) {{
            document.getElementById(domId).innerHTML = '<div style="text-align:center;padding:50px;">无数据</div>';
            return;
        }}
        var chart = echarts.init(document.getElementById(domId));
        chart.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, formatter: function(params) {{
                var res = params[0].axisValue + '<br/>';
                for (var i = 0; i < params.length; i++) {{
                    res += params[i].seriesName + ': ' + params[i].value + '<br/>';
                }}
                return res;
            }} }},
            legend: {{ data: seriesData.map(s => s.name), top: 0 }},
            grid: {{ containLabel: true, bottom: 30, top: 50 }},
            xAxis: {{ type: 'category', data: categories, axisLabel: {{ rotate: 45, interval: 0 }} }},
            yAxis: {{ type: 'value', name: '不良数量' }},
            series: seriesData.map(s => ({{
                name: s.name,
                type: 'bar',
                data: s.data,
                barGap: 0.1,
                label: {{ show: true, position: 'top' }}
            }}))
        }});
        window.addEventListener('resize', () => chart.resize());
    }}

    // 绘制所有图表
    drawPareto('chart-ft', {json.dumps(ft_categories)}, {json.dumps(ft_counts)}, {json.dumps(ft_cum_pct)}, '#5470c6');
    drawPareto('chart-rt', {json.dumps(rt_categories)}, {json.dumps(rt_counts)}, {json.dumps(rt_cum_pct)}, '#91cc75');
    
    drawGroupedBar('chart-sw-compare', {json.dumps(all_sw_bins)}, {json.dumps(sw_compare_series)});
    drawGroupedBar('chart-hw-compare', {json.dumps(all_hw_bins)}, {json.dumps(hw_compare_series)});
    
    drawSiteYield('chart-site-ft', {json.dumps(ft_site)}, '首测 各站点良率');
    drawSiteYield('chart-site-rt', {json.dumps(rt_site)}, '终测 各站点良率');

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
    print(f"✅ 完整图表报告已生成: {os.path.abspath(output_html)}")