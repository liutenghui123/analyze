# main.py
import json
import os
import sys
import traceback
from folder_processor import process_folder
from merge_analyzer import compute_merged_analysis
from chart_generator import generate_pareto_chart
from logger_config import setup_logger


def main(output_dir=None) -> dict:
    """
    主函数 - 命令行模式

    参数:
        output_dir: 输出目录，默认为当前目录

    返回:
        dict: 分析结果
    """
    if output_dir is None:
        output_dir = os.getcwd()

    # 初始化日志
    logger, log_file = setup_logger(log_dir=output_dir)
    logger.info("="*60)
    logger.info("Fenxi8 半导体测试数据分析工具 - 启动")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"输出目录: {output_dir}")
    logger.info("="*60)

    try:
        # 处理FTdata
        logger.info("开始处理 FTdata 文件夹...")
        ft_result = process_folder("FTdata", logger=logger)

        if "error" in ft_result:
            logger.error(f"FTdata 处理失败: {ft_result['error']}")
            return ft_result

        logger.info(
            f"FTdata 处理完成: {ft_result['total_records']} 条记录, {ft_result['total_failures']} 条失败")

        # 处理RTdata
        logger.info("开始处理 RTdata 文件夹...")
        rt_result = process_folder("RTdata", logger=logger)

        if "error" in rt_result:
            logger.error(f"RTdata 处理失败: {rt_result['error']}")
            return rt_result

        logger.info(
            f"RTdata 处理完成: {rt_result['total_records']} 条记录, {rt_result['total_failures']} 条失败")

        # 合并分析
        logger.info("开始合并分析...")
        merged = compute_merged_analysis(ft_result, rt_result)
        logger.info(
            f"合并分析完成: 首测良率={merged.get('首测良率(%)', 'N/A')}%, 最终良率={merged.get('最终良率(%)', 'N/A')}%")

        # 组装结果
        result = {
            "FTdata": ft_result,
            "RTdata": rt_result,
            "merged_analysis": merged
        }

        # 生成图表 HTML
        output_html = os.path.join(output_dir, "report.html")
        logger.info(f"开始生成图表报告: {output_html}")
        generate_pareto_chart(result, title="测试数据帕累托分析报告",
                              output_html=output_html, logger=logger)

        logger.info("="*60)
        logger.info("分析完成!")
        logger.info(f"日志文件: {log_file}")
        logger.info(f"报告文件: {output_html}")
        logger.info("="*60)

        return result

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\n错误: {str(e)}")
        print(f"详细日志请查看: {log_file}")
        sys.exit(1)


if __name__ == "__main__":
    # 支持命令行参数指定输出目录
    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    result = main(output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
