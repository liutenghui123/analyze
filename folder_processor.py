import os
import glob
import pandas as pd
from file_parser import detect_header_format, read_csv_file
from data_cleaner import build_dataframe
from analyzer import compute_sw_bin_by_site, compute_hw_bin_by_site, compute_fail_combos, compute_site_stats

def extract_product_name(lines, first_file_flag):
    """从文件的前几行提取 ProductName（仅在第一个文件执行）"""
    if not first_file_flag:
        return None
    if lines:
        first_line = lines[0].strip()
        import re
        match = re.search(r'ProductName\s*=\s*([^,]+)', first_line)
        if match:
            return match.group(1)
    return None

def process_folder(folder_path: str) -> dict:
    """处理单个文件夹，返回分析结果字典"""
    all_dfs = []
    internal_model_number = None
    file_paths = sorted(glob.glob(os.path.join(folder_path, "*.csv")))
    if not file_paths:
        return {"error": f"文件夹 '{folder_path}' 中没有 CSV 文件"}

    for idx, file_path in enumerate(file_paths):
        try:
            lines = read_csv_file(file_path)   # 行列表

            # 提取 ProductName（仅第一个文件）
            if idx == 0 and internal_model_number is None:
                internal_model_number = extract_product_name(lines, True)

            # 查找表头行
            header_line_idx = None
            format_type = None
            original_columns = None
            for i, line in enumerate(lines):
                if i < 20:   # 只在前20行查找
                    cols, ftype = detect_header_format(line)
                    if cols is not None:
                        header_line_idx = i
                        original_columns = cols
                        format_type = ftype
                        break

            if header_line_idx is None:
                continue

            df = build_dataframe(lines, header_line_idx, original_columns, format_type)
            if not df.empty:
                all_dfs.append(df)
        except Exception:
            # 忽略单个文件的解析错误，继续处理其他文件
            continue

    if not all_dfs:
        return {"error": "没有成功读取任何有效数据"}

    df = pd.concat(all_dfs, ignore_index=True)

    if 'HW_BIN' not in df.columns:
        return {"error": f"无法找到 HW_BIN 列。找到的列: {list(df.columns)}"}

    fail_total = (df['HW_BIN'] != 1).sum()
    fail_df = df[df['HW_BIN'] != 1]

    # 调用分析模块
    from analyzer import (
        compute_sw_bin_summary,
        compute_hw_bin_summary,
        compute_fail_combos,
        compute_site_stats
    )
    sw_bin_by_site = compute_sw_bin_by_site(fail_df)
    hw_bin_by_site = compute_hw_bin_by_site(fail_df)
    sw_bin_summary = compute_sw_bin_summary(fail_df, fail_total)
    hw_bin_summary = compute_hw_bin_summary(fail_df, fail_total)
    fail_combos = compute_fail_combos(fail_df, fail_total)
    site_stats = compute_site_stats(df, fail_df, fail_total)

    return {
        "total_records": int(len(df)),
        "total_failures": int(fail_total),
        "files_processed": len(all_dfs),
        "internal_model_number": str(internal_model_number) if internal_model_number is not None else None,
        "sw_bin_by_site": {str(site): df.to_dict('records') for site, df in sw_bin_by_site.items()},
        "hw_bin_by_site": {str(site): df.to_dict('records') for site, df in hw_bin_by_site.items()},
        "sw_bin_summary": sw_bin_summary.to_dict('records'),
        "hw_bin_summary": hw_bin_summary.to_dict('records'),
        "fail_combo_analysis": fail_combos.to_dict('records'),
        "site_analysis": site_stats.to_dict('records')
    }