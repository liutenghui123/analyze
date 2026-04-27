"""
UI 模块 - 基于 tkinter/ttk 的图形界面，允许用户选择 FTdata/RTdata 文件夹和输出文件夹，
并可选将分析结果 JSON 发送到 Webhook 接口。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
import logging
from datetime import datetime
import sys

# 尝试导入 requests，如果没有则提示安装
try:
    import requests
    # 禁用 SSL 警告（内网 webhook 通常使用自签名证书）
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from folder_processor import process_folder
from merge_analyzer import compute_merged_analysis
from chart_generator import generate_pareto_chart
from logger_config import setup_logger


class AnalysisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("半导体测试数据分析工具")
        self.root.geometry("650x500")
        self.root.resizable(True, True)

        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('微软雅黑', 9))
        style.configure('TButton', font=('微软雅黑', 9))
        style.configure('TEntry', font=('微软雅黑', 9))
        style.configure('TLabelframe.Label', font=('微软雅黑', 10, 'bold'))

        # 变量
        self.ft_path = tk.StringVar()
        self.rt_path = tk.StringVar()
        self.out_dir = tk.StringVar(value=os.getcwd())
        self.api_url = tk.StringVar(value="")  # API 地址（可选）
        self.send_api = tk.BooleanVar(value=False)  # 是否启用发送

        # 默认路径
        if os.path.exists("FTdata"):
            self.ft_path.set(os.path.abspath("FTdata"))
        if os.path.exists("RTdata"):
            self.rt_path.set(os.path.abspath("RTdata"))

        self.create_widgets()

    def create_widgets(self):
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题栏容器（左侧标题 + 右侧帮助按钮）
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = ttk.Label(
            title_frame, text="半导体测试数据分析工具", font=('微软雅黑', 16, 'bold'))
        title_label.pack(side=tk.LEFT)

        help_btn = ttk.Button(title_frame, text="❓ 帮助",
                              width=8, command=self.show_help)
        help_btn.pack(side=tk.RIGHT)

        # 数据源配置框架
        source_frame = ttk.LabelFrame(main_frame, text="数据源配置", padding="10")
        source_frame.pack(fill=tk.X, pady=5)

        # FTdata
        row1 = ttk.Frame(source_frame)
        row1.pack(fill=tk.X, pady=3)
        ttk.Label(row1, text="FTdata 文件夹:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.ft_path, width=45).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(row1, text="浏览...", command=self.select_ft).pack(
            side=tk.LEFT, padx=2)

        # RTdata
        row2 = ttk.Frame(source_frame)
        row2.pack(fill=tk.X, pady=3)
        ttk.Label(row2, text="RTdata 文件夹:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.rt_path, width=45).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(row2, text="浏览...", command=self.select_rt).pack(
            side=tk.LEFT, padx=2)

        # 输出配置框架
        output_frame = ttk.LabelFrame(main_frame, text="输出配置", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        row3 = ttk.Frame(output_frame)
        row3.pack(fill=tk.X, pady=3)
        ttk.Label(row3, text="输出文件夹:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row3, textvariable=self.out_dir, width=45).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(row3, text="浏览...", command=self.select_output_dir).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(output_frame, text="报告将自动保存为 report.html", foreground="gray").pack(
            anchor=tk.W, padx=(65, 0), pady=(0, 5))

        # Webhook 配置框架（可选）
        api_frame = ttk.LabelFrame(
            main_frame, text="Webhook数据推送", padding="10")
        api_frame.pack(fill=tk.X, pady=5)

        # 启用复选框
        cb = ttk.Checkbutton(api_frame, text="勾选后将分析结果推送到Webhook地址", variable=self.send_api,
                             command=self.toggle_api_entry)
        cb.pack(anchor=tk.W, pady=(0, 5))

        # Webhook URL 输入行（默认填入webhook地址）
        row_api = ttk.Frame(api_frame)
        row_api.pack(fill=tk.X, pady=3)
        ttk.Label(row_api, text="Webhook URL:", width=12).pack(side=tk.LEFT)
        self.api_entry = ttk.Entry(
            row_api, textvariable=self.api_url, width=45, state='disabled')
        self.api_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 设置默认webhook地址
        if not self.api_url.get():
            self.api_url.set(
                "http://192.168.58.34/triggers/webhook/qst-2Yjz7Tn43N0IRbvo8ILK")

        # 状态提示
        if not REQUESTS_AVAILABLE:
            ttk.Label(api_frame, text="⚠ 未安装 requests 库，无法发送 Webhook 请求。请运行: pip install requests",
                      foreground="red").pack(anchor=tk.W, padx=(65, 0), pady=5)

        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        self.run_btn = ttk.Button(
            btn_frame, text="开始分析", command=self.run_analysis, width=15)
        self.run_btn.pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="退出", command=self.root.quit,
                   width=8).pack(side=tk.LEFT)

        # 状态栏和进度条
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(
            status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress = ttk.Progressbar(
            status_frame, mode='indeterminate', length=150)
        self.progress.pack(side=tk.RIGHT, padx=5)
        self.progress.pack_forget()

    def show_help(self):
        """显示帮助窗口，内容为 README.md 文件"""
        # 尝试找到 README.md 文件路径
        readme_path = self._find_readme()
        if readme_path is None:
            messagebox.showerror("错误", "未找到 README.md 帮助文件，请确保该文件与程序位于同一目录下。")
            return

        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("错误", f"读取 README.md 失败：{e}")
            return

        # 创建帮助窗口
        help_win = tk.Toplevel(self.root)
        help_win.title("帮助 - 使用说明")
        help_win.geometry("700x500")
        help_win.transient(self.root)  # 设置为父窗口的临时窗口
        help_win.grab_set()            # 模态效果

        # 显示文本区域
        text_area = scrolledtext.ScrolledText(
            help_win, wrap=tk.WORD, font=('微软雅黑', 9))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)  # 只读

        # 关闭按钮
        close_btn = ttk.Button(help_win, text="关闭", command=help_win.destroy)
        close_btn.pack(pady=10)

    def _find_readme(self):
        """查找 README.md 文件（支持开发环境和 PyInstaller 打包环境）"""
        possible_paths = []

        # 1. 当前工作目录
        possible_paths.append(os.path.join(os.getcwd(), "README.md"))
        # 2. 脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(script_dir, "README.md"))
        # 3. 打包后的临时目录（PyInstaller）
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
            possible_paths.append(os.path.join(bundle_dir, "README.md"))

        for path in possible_paths:
            if os.path.isfile(path):
                return path
        return None

    def toggle_api_entry(self):
        """根据复选框状态启用/禁用 API 输入框"""
        if self.send_api.get():
            self.api_entry.config(state='normal')
        else:
            self.api_entry.config(state='disabled')

    def select_ft(self):
        path = filedialog.askdirectory(title="选择 FTdata 文件夹")
        if path:
            self.ft_path.set(path)

    def select_rt(self):
        path = filedialog.askdirectory(title="选择 RTdata 文件夹")
        if path:
            self.rt_path.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory(title="选择输出文件夹")
        if path:
            self.out_dir.set(path)

    def run_analysis(self):
        ft_dir = self.ft_path.get().strip()
        rt_dir = self.rt_path.get().strip()
        out_dir = self.out_dir.get().strip()
        send_api = self.send_api.get()
        api_url = self.api_url.get().strip() if send_api else ""

        # 验证输入
        if not ft_dir or not os.path.isdir(ft_dir):
            messagebox.showerror("错误", "请选择有效的 FTdata 文件夹")
            return
        if not rt_dir or not os.path.isdir(rt_dir):
            messagebox.showerror("错误", "请选择有效的 RTdata 文件夹")
            return
        if not out_dir:
            messagebox.showerror("错误", "请选择输出文件夹")
            return
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出文件夹：{e}")
                return
        if send_api and not api_url:
            messagebox.showerror("错误", "请填写 Webhook URL 或取消勾选推送选项")
            return
        if send_api and not REQUESTS_AVAILABLE:
            messagebox.showerror(
                "错误", "缺少 requests 库，无法发送 Webhook 请求。\n请安装: pip install requests")
            return

        out_file = os.path.join(out_dir, "report.html")

        # 禁用界面
        self.run_btn.config(state=tk.DISABLED)
        self.progress.pack(side=tk.RIGHT, padx=5)
        self.progress.start(10)
        self.status_var.set("正在分析，请稍候...")
        self.root.update()

        # 启动后台线程
        thread = threading.Thread(target=self._analysis_worker, args=(
            ft_dir, rt_dir, out_file, out_dir, send_api, api_url))
        thread.daemon = True
        thread.start()

    def _analysis_worker(self, ft_dir, rt_dir, out_file, out_dir, send_api, api_url):
        # 初始化日志（在输出目录生成日志文件）
        logger, log_file = setup_logger(log_dir=out_dir)
        logger.info("="*60)
        logger.info("Fenxi8 UI - 开始分析")
        logger.info(f"FTdata: {ft_dir}")
        logger.info(f"RTdata: {rt_dir}")
        logger.info(f"输出目录: {out_dir}")
        logger.info("="*60)

        try:
            # 处理数据
            logger.info("开始处理 FTdata...")
            ft_result = process_folder(ft_dir, logger=logger)

            if "error" in ft_result:
                logger.error(f"FTdata 处理失败: {ft_result['error']}")
                self._show_error(f"FTdata 处理失败: {ft_result['error']}")
                return

            logger.info(f"FTdata 处理完成: {ft_result['total_records']} 条记录")

            logger.info("开始处理 RTdata...")
            rt_result = process_folder(rt_dir, logger=logger)

            if "error" in rt_result:
                logger.error(f"RTdata 处理失败: {rt_result['error']}")
                self._show_error(f"RTdata 处理失败: {rt_result['error']}")
                return

            logger.info(f"RTdata 处理完成: {rt_result['total_records']} 条记录")

            merged = compute_merged_analysis(ft_result, rt_result)
            logger.info(
                f"合并分析完成: 首测良率={merged.get('首测良率(%)', 'N/A')}%, 最终良率={merged.get('最终良率(%)', 'N/A')}%")

            full_data = {
                "FTdata": ft_result,
                "RTdata": rt_result,
                "merged_analysis": merged
            }

            # 生成 HTML 报告
            logger.info("开始生成HTML报告...")
            generate_pareto_chart(
                full_data, title="半导体测试数据分析报告", output_html=out_file, logger=logger)

            # 如果需要发送 Webhook
            webhook_success = False
            if send_api and api_url:
                logger.info(f"开始发送数据到Webhook: {api_url}")
                webhook_success = self._send_json_to_api(
                    full_data, api_url, logger)
                if webhook_success:
                    logger.info("✓ Webhook推送成功")
                else:
                    logger.warning("✗ Webhook推送失败（详情请见上方错误信息）")
            else:
                if not send_api:
                    logger.info("Webhook推送未启用（复选框未勾选）")
                elif not api_url:
                    logger.warning("Webhook URL为空，跳过推送")

            logger.info("="*60)
            logger.info("分析完成!")
            logger.info(f"日志文件: {log_file}")
            logger.info(f"报告文件: {out_file}")
            logger.info("="*60)

            if webhook_success:
                self._show_success(
                    f"分析完成！\n报告已保存至: {out_file}\n日志已保存至: {log_file}\nJSON 数据已推送到 Webhook")
            else:
                self._show_success(
                    f"分析完成！\n报告已保存至: {out_file}\n日志已保存至: {log_file}")

        except Exception as e:
            import traceback
            logger.error(f"程序执行出错: {str(e)}")
            logger.error(traceback.format_exc())
            self._show_error(f"发生错误: {str(e)}\n\n详细日志请查看:\n{log_file}")
        finally:
            self.root.after(0, self._reset_ui)

    def _send_json_to_api(self, data, api_url, logger=None):
        """发送 JSON 数据到指定 Webhook，返回是否成功

        数据格式：
        POST {api_url}
        Content-Type: application/json
        Body: {
            "query": "{ ...JSON字符串格式的分析数据... }"
        }

        参数:
            data: 要发送的数据（字典）
            api_url: Webhook URL
            logger: 日志记录器（可选）
        """
        # 如果没有传入logger，使用模块级别的logger
        if logger is None:
            logger = logging.getLogger(__name__)

        try:
            # 构建符合webhook要求的数据格式
            # 注意：query参数必须是JSON字符串，不能是字典对象
            payload = {
                "query": json.dumps(data, ensure_ascii=False)  # 将数据转换为JSON字符串
            }

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Fenxi8/1.0'
            }

            payload_size = len(json.dumps(payload))
            logger.info(f"准备发送数据到Webhook: {api_url}")
            logger.info(
                f"数据包大小: {payload_size:,} bytes ({payload_size/1024:.2f} KB)")
            logger.debug(
                f"Payload结构: query参数类型={type(payload['query']).__name__}")

            # 设置超时 30 秒，禁用SSL验证（内网地址）
            logger.info("正在发送POST请求...")
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=30,
                verify=False  # 内网webhook通常使用自签名证书
            )

            logger.info(f"Webhook响应状态码: {response.status_code}")
            logger.info(f"Webhook响应内容: {response.text[:500]}")

            if response.status_code in (200, 201, 202, 204):
                logger.info("Webhook推送成功")
                return True
            else:
                error_msg = f"Webhook返回非成功状态码: {response.status_code}\n响应: {response.text[:200]}"
                logger.error(error_msg)
                self.root.after(0, lambda: messagebox.showwarning(
                    "Webhook 警告", error_msg))
                return False

        except requests.exceptions.Timeout:
            error_msg = "请求超时 (30秒)，请检查网络连接和Webhook服务状态"
            logger.error(f"Webhook超时: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror(
                "Webhook 超时错误", error_msg))

        except requests.exceptions.ConnectionError as e:
            error_msg = f"无法连接到Webhook服务器\nURL: {api_url}\n错误: {str(e)}"
            logger.error(f"Webhook连接错误: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror(
                "Webhook 连接错误", error_msg))

        except requests.exceptions.InvalidURL as e:
            error_msg = f"无效的Webhook URL: {api_url}\n请检查URL格式是否正确\n错误: {str(e)}"
            logger.error(f"Webhook URL无效: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror(
                "Webhook URL 错误", error_msg))

        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP请求异常: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            self.root.after(0, lambda: messagebox.showerror(
                "Webhook HTTP 错误", error_msg))

        except Exception as e:
            import traceback
            error_msg = f"发送数据到Webhook失败: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            logger.error(f"异常堆栈:\n{traceback.format_exc()}")
            self.root.after(0, lambda: messagebox.showerror(
                "Webhook 错误", error_msg))

        return False

    def _reset_ui(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.run_btn.config(state=tk.NORMAL)
        self.status_var.set("就绪")

    def _show_error(self, msg):
        self.root.after(0, lambda: messagebox.showerror("错误", msg))
        self.root.after(0, lambda: self.status_var.set("错误: " + msg))

    def _show_success(self, msg):
        self.root.after(0, lambda: messagebox.showinfo("完成", msg))
        self.root.after(0, lambda: self.status_var.set("分析完成"))


def main():
    root = tk.Tk()
    app = AnalysisUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
