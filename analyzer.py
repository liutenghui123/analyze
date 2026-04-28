import pandas as pd
from datetime import timedelta


def compute_hourly_site_yield(df: pd.DataFrame, gap_threshold_hours: float = 2.0):
    """
    按小时时间窗口统计不同 Site 的良品率（Bin1数量/总数量）。

    逻辑：
    - 以全部数据最早时间为起始，按1小时间隔划分时间窗口
    - 如果相邻记录间出现超过 gap_threshold_hours 的时间空白，
      则以空白后第一条记录的时间作为新段的起始时间重新划分
    - 每个时间窗口内，按 SITE 分别计算良品率

    参数:
        df: 包含 TestTime, HW_BIN, SITE 列的 DataFrame
        gap_threshold_hours: 时间间隔阈值（小时），超过则视为新段

    返回:
        list[dict]: 每条记录包含 segment, time_window_start, time_window_end,
                    site, total, bin1_count, yield_rate
    """
    if 'TestTime' not in df.columns or 'HW_BIN' not in df.columns or 'SITE' not in df.columns:
        return []

    work_df = df.dropna(subset=['TestTime']).copy()
    if work_df.empty:
        return []

    work_df = work_df.sort_values('TestTime').reset_index(drop=True)

    # 检测时间间隔，识别段起始点
    gap_threshold = pd.Timedelta(hours=gap_threshold_hours)
    time_diffs = work_df['TestTime'].diff()
    # 索引0始终是段起始；时间差超阈值的位置也是段起始
    gap_indices = list(time_diffs[time_diffs > gap_threshold].index)
    segment_starts = [0] + gap_indices

    results = []
    for seg_idx, seg_start_idx in enumerate(segment_starts):
        if seg_idx + 1 < len(segment_starts):
            seg_end_idx = segment_starts[seg_idx + 1]
            seg_df = work_df.iloc[seg_start_idx:seg_end_idx]
        else:
            seg_df = work_df.iloc[seg_start_idx:]

        if seg_df.empty:
            continue

        seg_start_time = seg_df['TestTime'].iloc[0]
        seg_end_time = seg_df['TestTime'].iloc[-1]

        # 按1小时间隔划分时间窗口
        current_start = seg_start_time
        while current_start <= seg_end_time:
            current_end = current_start + pd.Timedelta(hours=1)

            mask = (seg_df['TestTime'] >= current_start) & (
                seg_df['TestTime'] < current_end)
            window_df = seg_df[mask]

            if not window_df.empty:
                for site, site_df in window_df.groupby('SITE'):
                    total = len(site_df)
                    bin1_count = int((site_df['HW_BIN'] == 1).sum())
                    yield_rate = round(bin1_count / total *
                                       100, 2) if total > 0 else 0.0

                    results.append({
                        'segment': seg_idx + 1,
                        'time_window_start': current_start.strftime('%Y-%m-%d %H:%M:%S'),
                        'time_window_end': current_end.strftime('%Y-%m-%d %H:%M:%S'),
                        'site': int(site),
                        'total': total,
                        'bin1_count': bin1_count,
                        'yield_rate': yield_rate,
                    })

            current_start = current_end

    return results


def compute_sw_bin_summary(fail_df: pd.DataFrame, fail_total: int):
    """SW_BIN 不良统计"""
    if fail_total == 0 or 'SW_BIN' not in fail_df.columns:
        return pd.DataFrame()
    sw_bin_fail = fail_df['SW_BIN'].value_counts().reset_index()
    sw_bin_fail.columns = ['SW_BIN', '数量']
    sw_bin_fail['占比(%)'] = (sw_bin_fail['数量'] / fail_total * 100).round(2)
    return sw_bin_fail.sort_values('数量', ascending=False)


def compute_hw_bin_summary(fail_df: pd.DataFrame, fail_total: int):
    """HW_BIN 不良统计"""
    if fail_total == 0:
        return pd.DataFrame()
    hw_bin_fail = fail_df['HW_BIN'].value_counts().reset_index()
    hw_bin_fail.columns = ['HW_BIN', '数量']
    hw_bin_fail['占比(%)'] = (hw_bin_fail['数量'] / fail_total * 100).round(2)
    return hw_bin_fail.sort_values('数量', ascending=False)


def compute_fail_combos(fail_df: pd.DataFrame, fail_total: int, top_n=15):
    """HW_BIN 与 SW_BIN 组合不良统计（Top N）"""
    if fail_total == 0 or 'SW_BIN' not in fail_df.columns:
        return pd.DataFrame()
    combos = fail_df.groupby(
        ['HW_BIN', 'SW_BIN']).size().reset_index(name='数量')
    combos = combos.sort_values('数量', ascending=False)
    combos['组合名称'] = combos.apply(
        lambda x: f"HW{x['HW_BIN']}/SW{x['SW_BIN']}", axis=1)
    combos['占比(%)'] = (combos['数量'] / fail_total * 100).round(2)
    combos['累计百分比'] = combos['占比(%)'].cumsum().round(2)
    return combos.head(top_n).copy()


def compute_site_stats(df: pd.DataFrame, fail_df: pd.DataFrame, fail_total: int):
    """站点不良统计及良率"""
    if fail_total == 0 or 'SITE' not in df.columns:
        return pd.DataFrame()
    site_fail = fail_df.groupby('SITE').size().reset_index(name='不良数量')
    site_fail['占比(%)'] = (site_fail['不良数量'] / fail_total * 100).round(2)
    site_total = df.groupby('SITE').size().reset_index(name='总数')
    site_stats = site_fail.merge(site_total, on='SITE', how='left')
    site_stats['良率(%)'] = ((site_stats['总数'] - site_stats['不良数量']
                            ) / site_stats['总数'] * 100).round(2)
    return site_stats.sort_values('不良数量', ascending=False)


# ========== 新增：按 SITE 分组的 SW_BIN 和 HW_BIN 统计 ==========
def compute_sw_bin_by_site(fail_df: pd.DataFrame):
    """
    按站点分组统计 SW_BIN 分布。
    返回字典：{ site: DataFrame(columns=['SW_BIN', '数量', '占比(%)']) }
    占比为该站点内该 SW_BIN 占该站点失败总数的百分比。
    """
    if 'SITE' not in fail_df.columns or 'SW_BIN' not in fail_df.columns:
        return {}

    result = {}
    for site, group in fail_df.groupby('SITE'):
        site_fail_total = len(group)
        if site_fail_total == 0:
            continue
        sw_counts = group['SW_BIN'].value_counts().reset_index()
        sw_counts.columns = ['SW_BIN', '数量']
        sw_counts['占比(%)'] = (sw_counts['数量'] / site_fail_total * 100).round(2)
        sw_counts = sw_counts.sort_values('数量', ascending=False)
        result[site] = sw_counts
    return result


def compute_hw_bin_by_site(fail_df: pd.DataFrame):
    """
    按站点分组统计 HW_BIN 分布。
    返回字典：{ site: DataFrame(columns=['HW_BIN', '数量', '占比(%)']) }
    占比为该站点内该 HW_BIN 占该站点失败总数的百分比。
    """
    if 'SITE' not in fail_df.columns or 'HW_BIN' not in fail_df.columns:
        return {}

    result = {}
    for site, group in fail_df.groupby('SITE'):
        site_fail_total = len(group)
        if site_fail_total == 0:
            continue
        hw_counts = group['HW_BIN'].value_counts().reset_index()
        hw_counts.columns = ['HW_BIN', '数量']
        hw_counts['占比(%)'] = (hw_counts['数量'] / site_fail_total * 100).round(2)
        hw_counts = hw_counts.sort_values('数量', ascending=False)
        result[site] = hw_counts
    return result
