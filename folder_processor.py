import os
import glob
import logging
import pandas as pd
from file_parser import detect_header_format, read_csv_file
from data_cleaner import build_dataframe
from analyzer import compute_sw_bin_by_site, compute_hw_bin_by_site, compute_fail_combos, compute_site_stats, compute_hourly_site_yield


def extract_product_name(lines, first_file_flag):
    """从文件的前几行提取 ProductName（仅在第一个文件执行）"""
    if not first_file_flag:
        return None
    if lines:
        # 尝试多种格式提取产品名称
        for line in lines[:10]:
            # 格式1: ProductName=xxx
            import re
            match = re.search(r'ProductName\s*=\s*([^,\t]+)', line)
            if match:
                return match.group(1).strip()
            # 格式2: DEVICE: xxx (Tab分隔)
            match = re.search(r'DEVICE:\s*([^\t]+)', line)
            if match:
                return match.group(1).strip()
            # 格式3: IntDevice: xxx
            match = re.search(r'IntDevice:\s*([^\t]+)', line)
            if match:
                return match.group(1).strip()
    return None


def process_folder(folder_path: str, logger: logging.Logger = None, progress_callback=None) -> dict:
    """
    处理单个文件夹，返回分析结果字典

    参数:
        folder_path: 文件夹路径
        logger: 日志记录器（可选）
        progress_callback: 进度回调函数（可选），签名为 callback(current, total, filename)

    返回:
        dict: 分析结果
    """
    all_dfs = []
    internal_model_number = None
    skipped_files = []

    if logger:
        logger.info(f"扫描文件夹: {folder_path}")

    # 支持.csv和.xls（文本格式）文件
    csv_files = sorted(glob.glob(os.path.join(folder_path, "*.csv")))
    xls_files = sorted(glob.glob(os.path.join(folder_path, "*.xls")))
    file_paths = csv_files + xls_files

    if not file_paths:
        error_msg = f"文件夹 '{folder_path}' 中没有 CSV 或 XLS 文件"
        if logger:
            logger.warning(error_msg)
        return {"error": error_msg}

    if logger:
        logger.info(
            f"找到 {len(file_paths)} 个文件: {[os.path.basename(f) for f in file_paths]}")

    for idx, file_path in enumerate(file_paths):
        file_name = os.path.basename(file_path)
        try:
            if logger:
                logger.debug(f"解析文件 [{idx+1}/{len(file_paths)}]: {file_name}")
            if progress_callback:
                progress_callback(idx + 1, len(file_paths), file_name)

            lines = read_csv_file(file_path)   # 行列表

            # 提取 ProductName（仅第一个文件）
            if idx == 0 and internal_model_number is None:
                internal_model_number = extract_product_name(lines, True)
                if logger:
                    logger.info(f"检测到产品型号: {internal_model_number}")

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
                        if logger:
                            logger.debug(
                                f"文件 {file_name}: 在第 {i+1} 行检测到格式 {format_type}")
                        break

            if header_line_idx is None:
                if logger:
                    logger.warning(f"文件 {file_name}: 未识别的格式，跳过")
                skipped_files.append(file_name)
                continue

            df = build_dataframe(lines, header_line_idx,
                                 original_columns, format_type)
            if not df.empty:
                all_dfs.append(df)
                if logger:
                    logger.debug(f"文件 {file_name}: 成功解析 {len(df)} 条记录")
            else:
                if logger:
                    logger.warning(f"文件 {file_name}: 解析后无有效数据")
                skipped_files.append(file_name)

        except Exception as e:
            error_msg = f"文件 {file_name}: 解析失败 - {str(e)}"
            if logger:
                logger.warning(error_msg, exc_info=True)
            skipped_files.append(file_name)
            continue

    if not all_dfs:
        error_msg = "没有成功读取任何有效数据"
        if logger:
            logger.error(error_msg)
        return {"error": error_msg}

    if logger:
        logger.info(f"成功解析 {len(all_dfs)} 个文件，跳过 {len(skipped_files)} 个文件")
        if skipped_files:
            logger.warning(f"跳过的文件: {skipped_files}")

    df = pd.concat(all_dfs, ignore_index=True)

    if 'HW_BIN' not in df.columns:
        error_msg = f"无法找到 HW_BIN 列。找到的列: {list(df.columns)}"
        if logger:
            logger.error(error_msg)
        return {"error": error_msg}

    fail_total = (df['HW_BIN'] != 1).sum()
    fail_df = df[df['HW_BIN'] != 1]

    if logger:
        logger.info(
            f"数据汇总: 总记录={len(df)}, 失败记录={fail_total}, 良率={((len(df)-fail_total)/len(df)*100):.2f}%")

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

    # 按小时统计不同 Site 良品率
    hourly_site_yield = compute_hourly_site_yield(df)
    if logger:
        logger.info(f"按小时良品率统计: {len(hourly_site_yield)} 条记录")

    if logger:
        logger.info(
            f"分析完成: SW_BIN类型={len(sw_bin_summary)}, HW_BIN类型={len(hw_bin_summary)}, 组合Top15={len(fail_combos)}, 站点数={len(site_stats)}")

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
        "site_analysis": site_stats.to_dict('records'),
        "hourly_site_yield": hourly_site_yield,
    }
