import pandas as pd
from file_parser import is_valid_data_row, parse_date

def map_columns(df: pd.DataFrame, format_type: str) -> pd.DataFrame:
    """
    根据格式类型将原始列名映射为标准列名：HW_BIN, SW_BIN, SITE
    若不存在则填充 NA
    """
    if format_type == 'format1':
        if 'HBin' in df.columns:
            df['HW_BIN'] = df['HBin']
        if 'SBin' in df.columns:
            df['SW_BIN'] = df['SBin']
        if 'Site' in df.columns:
            df['SITE'] = df['Site']
    elif format_type == 'format2':
        # format2 已经包含 SITE, HW_BIN 等标准列，无需映射
        pass
    elif format_type == 'format3':
        if 'HBin' in df.columns or 'HBIN' in df.columns:
            col_name = 'HBin' if 'HBin' in df.columns else 'HBIN'
            df['HW_BIN'] = df[col_name]
        if 'SBin' in df.columns or 'SBIN' in df.columns:
            col_name = 'SBin' if 'SBin' in df.columns else 'SBIN'
            df['SW_BIN'] = df[col_name]
        if 'Site' in df.columns or 'SITE' in df.columns:
            col_name = 'Site' if 'Site' in df.columns else 'SITE'
            df['SITE'] = df[col_name]
    # 确保三列都存在
    for col in ['HW_BIN', 'SW_BIN', 'SITE']:
        if col not in df.columns:
            df[col] = pd.NA
    return df

def convert_int_columns(df: pd.DataFrame, cols=['HW_BIN', 'SW_BIN', 'SITE']) -> pd.DataFrame:
    """将指定列转为可空整数类型 Int64"""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    return df

def parse_test_time(df: pd.DataFrame) -> pd.DataFrame:
    """尝试从 'TestTime' 或包含 'time' 的列中解析时间"""
    if 'TestTime' in df.columns:
        df['TestTime'] = df['TestTime'].apply(parse_date)
    else:
        for col in df.columns:
            if 'time' in col.lower():
                df['TestTime'] = df[col].apply(parse_date)
                break
    return df

def build_dataframe(lines: list, header_line_idx: int, original_columns: list, format_type: str) -> pd.DataFrame:
    """根据表头行和数据行构建 DataFrame，并执行基础清洗"""
    # 提取数据行
    data_lines = []
    for line in lines[header_line_idx + 1:]:
        if is_valid_data_row(line, format_type):
            data_lines.append(line.strip())
    if not data_lines:
        return pd.DataFrame()

    rows = []
    for line in data_lines:
        parts = line.split(",")
        if len(parts) < len(original_columns):
            parts.extend([''] * (len(original_columns) - len(parts)))
        elif len(parts) > len(original_columns):
            parts = parts[:len(original_columns)]
        rows.append(parts)

    df = pd.DataFrame(rows, columns=original_columns)
    df = map_columns(df, format_type)
    df = convert_int_columns(df)
    df = parse_test_time(df)
    return df