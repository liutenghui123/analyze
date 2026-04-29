# merge_analyzer.py
"""
合并分析模块：基于 FTdata 和 RTdata 的分析结果，计算首测良率和最终良率。
"""


def compute_merged_analysis(ft_result: dict, rt_result: dict) -> dict:
    """
    根据 FTdata 和 RTdata 的分析结果，计算良率指标。

    参数:
        ft_result: process_folder("FTdata") 返回的字典
        rt_result: process_folder("RTdata") 返回的字典

    返回:
        包含以下指标的字典：
        - first_pass_yield (%): 首测良率 = (1 - FT_failures / FT_total) * 100
        - final_yield (%):      最终良率 = (1 - RT_failures / FT_total) * 100
    """
    # 检查错误
    if "error" in ft_result:
        return {"error": f"FTdata 分析出错: {ft_result['error']}"}

    ft_total = ft_result.get("total_records", 0)
    ft_fail = ft_result.get("total_failures", 0)

    if ft_total == 0:
        return {"error": "FTdata 总记录数为0，无法计算良率"}

    first_pass_yield = (1 - ft_fail / ft_total) * 100

    result = {
        "首测良率(%)": round(first_pass_yield, 2),
        "file_metadata": ft_result.get("file_metadata"),
    }

    if rt_result and "error" not in rt_result:
        rt_fail = rt_result.get("total_failures", 0)
        final_yield = (1 - rt_fail / ft_total) * 100
        result["最终良率(%)"] = round(final_yield, 2)

    return result
