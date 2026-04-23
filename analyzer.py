import pandas as pd

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
    combos = fail_df.groupby(['HW_BIN', 'SW_BIN']).size().reset_index(name='数量')
    combos = combos.sort_values('数量', ascending=False)
    combos['组合名称'] = combos.apply(lambda x: f"HW{x['HW_BIN']}/SW{x['SW_BIN']}", axis=1)
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
    site_stats['良率(%)'] = ((site_stats['总数'] - site_stats['不良数量']) / site_stats['总数'] * 100).round(2)
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