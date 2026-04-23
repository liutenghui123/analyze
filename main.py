# main.py 修改后
import json
from folder_processor import process_folder
from merge_analyzer import compute_merged_analysis
from chart_generator import generate_pareto_chart   # 新增导入

def main() -> dict:
    ft_result = process_folder("FTdata")
    rt_result = process_folder("RTdata")
    merged = compute_merged_analysis(ft_result, rt_result)
    result = {
        "FTdata": ft_result,
        "RTdata": rt_result,
        "merged_analysis": merged
    }
    # 生成图表 HTML
    generate_pareto_chart(result, title="测试数据帕累托分析报告", output_html="report.html")
    return result

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))