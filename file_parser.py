import re
import pandas as pd


def detect_header_format(line: str):
    """
    检测 CSV/TSV 表头格式，返回标准化后的列名和格式类型。
    返回 (columns, format_type) 或 (None, None)
    """
    # 检测分隔符类型
    delimiter = '\t' if '\t' in line else ','

    if re.match(r'TestTime#,LotId#,WaferId,XAdr,YAdr,Site#', line):
        columns = [col.strip().replace('#', '') for col in line.split(",")]
        return columns, 'format1'
    if line.startswith("TestTime,X_POS,Y_POS,SITE,HW_BIN"):
        columns = [col.strip() for col in line.split(",")]
        return columns, 'format2'
    if line.startswith("TestTime,LotId,WaferId,XAdr,YAdr,Site"):
        columns = [col.strip() for col in line.split(",")]
        return columns, 'format3'
    # 新增 format4：Time\tTest_Count\tSITE\tH_bin\tS_bin 格式（Tab分隔）
    if delimiter == '\t' and line.startswith('Time'):
        # 验证是Tab分隔且包含关键列
        cols = [col.strip() for col in line.split('\t')]
        if 'H_bin' in cols and 'S_bin' in cols and 'SITE' in cols:
            return cols, 'format4'
    return None, None


def is_valid_data_row(line: str, format_type: str) -> bool:
    """判断一行是否为有效数据行（非空、非单位行、包含日期或数字）"""
    line = line.strip()
    if not line:
        return False

    # 检测分隔符
    delimiter = '\t' if '\t' in line else ','

    # 过滤单位行（如 'V', 'mA'）
    line_no_delim = line.replace(delimiter, '').strip()
    if line_no_delim in ['', 'V', 'mA']:
        return False

    # 日期开头检测
    date_patterns = [
        r'^\d{4}/\d{1,2}/\d{1,2}',
        r'^\d{4}-\d{1,2}-\d{1,2}',
        r'^\d{1,2}/\d{1,2}/\d{4}',
    ]
    for pattern in date_patterns:
        if re.match(pattern, line):
            return True

    # format2 和 format4 可能以数字开头（Test_Count）
    if format_type in ('format2', 'format4') and line and line[0].isdigit():
        return True

    return False


def parse_date(date_str):
    """尝试多种格式将字符串转为 datetime，失败返回 NaT"""
    if pd.isna(date_str) or date_str == '':
        return pd.NaT
    date_str = str(date_str).strip()
    date_formats = [
        '%Y/%m/%d %H:%M',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y %H:%M:%S',
    ]
    for fmt in date_formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    try:
        return pd.to_datetime(date_str, errors='coerce')
    except:
        return pd.NaT


def read_csv_file(file_path: str):
    """
    读取 CSV 文件内容，返回 (content_lines, 文件头前几行用于提取 ProductName)
    这里直接返回整个文件的内容行列表，同时保留原始文本用于后续解析。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()
    return content.splitlines()
