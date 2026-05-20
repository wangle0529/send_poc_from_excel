import tkinter as tk
from tkinter import filedialog, ttk
from openpyxl.utils import get_column_letter, column_index_from_string
import threading
from utils.format import Formatter

def generate_excel_columns():
    columns = []
    for i in range(0, 26): # A to Z
        columns.append(chr(65 + i)) # chr(65) is 'A'
    for i in range(0, 1):
        for j in range(0, 26): # AA to AZ
            columns.append(chr(65 + i) + chr(65 + j))
    return columns[:26] + columns[26:] # To ensure we only go up to AZ

class FormatterPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="lightgreen")

        # 设置整体列数为1列（每行一个 Frame）
        self.grid_columnconfigure(0, weight=1)

        # 固定 Label 宽度（字符数）
        label_width = 10

        excel_columns = generate_excel_columns()


        # ====== 0. 输入文件选择 ======
        input_file_frame = tk.Frame(self)
        input_file_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # 设置列权重，让 Entry 所在列扩展
        input_file_frame.grid_columnconfigure(1, weight=1)

        # 固定 Label 宽度
        tk.Label(
            input_file_frame,
            text="输入文件:",
            width=label_width,  # 固定宽度
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=0)

        # Entry 自动扩展填充中间区域
        self.input_path = tk.Entry(input_file_frame)
        self.input_path.grid(row=0, column=1, sticky="ew", padx=0)

        # 固定按钮宽度
        tk.Button(
            input_file_frame,
            text="浏览",
            width=label_width,  # 固定按钮宽度
            command=self.browse_input_file
        ).grid(row=0, column=3, padx=0)

        # ====== 1. 起始行 & 输入列 下拉框 ======
        row_col_frame = tk.Frame(self)
        row_col_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        # 设置四列权重
        for i in range(4):
            row_col_frame.grid_columnconfigure(i, weight=1 if i in (1, 3) else 0)

        # 起始行
        tk.Label(row_col_frame, text="起始行:", width=label_width, anchor="w").grid(
            row=0, column=0, sticky="w", padx=0
        )
        self.start_row_combo = ttk.Combobox(row_col_frame, values=[int(i) for i in range(1, 21)], width=10)
        self.start_row_combo.grid(row=0, column=1, sticky="w", padx=0)
        self.start_row_combo.set(2)

        # 输入列
        tk.Label(row_col_frame, text="输入列:", width=12, anchor="w").grid(
            row=0, column=2, sticky="w", padx=0
        )
        self.input_col_combo = ttk.Combobox(row_col_frame, values=excel_columns, width=10)
        self.input_col_combo.grid(row=0, column=3, sticky="w", padx=0)
        self.input_col_combo.set("C")

        # ====== 2. 输出文件选择 ======
        output_file_frame = tk.Frame(self)
        output_file_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        output_file_frame.grid_columnconfigure(1, weight=1)

        tk.Label(output_file_frame, text="输出文件:", width=label_width, anchor="w").grid(
            row=0, column=0, sticky="w", padx=0
        )
        self.output_path = tk.Entry(output_file_frame)
        self.output_path.grid(row=0, column=1, sticky="ew", padx=0)
        tk.Button(output_file_frame, text="新建", command=self.browse_output_file, width=label_width).grid(
            row=0, column=3, padx=0
        )

        # ====== 3. 输出列 + 开始格式化按钮 ======
        output_col_frame = tk.Frame(self)
        output_col_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)

        # 设置列权重：Label 列不扩展，中间列扩展，按钮列不扩展
        output_col_frame.grid_columnconfigure(1, weight=1)

        # 输出列
        tk.Label(output_col_frame, text="输出列:", width=label_width, anchor="w").grid(
            row=0, column=0, sticky="w", padx=0
        )
        self.output_col_combo = ttk.Combobox(output_col_frame, values=excel_columns, width=10)
        self.output_col_combo.grid(row=0, column=1, sticky="w", padx=0)
        self.output_col_combo.set("H")

        # 开始格式化按钮（放在输出列右边）
        tk.Button(output_col_frame, text="开始格式化", width=label_width, command=self.start_format).grid(
            row=0, column=2, padx=0
        )

        # ====== 4. 输出日志窗口 + 滚动条 ======
        output_frame = tk.Frame(self)
        output_frame.grid(row=4, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(4, weight=1)

        self.output_text = tk.Text(output_frame, wrap="word", state="disabled", bg="black", fg="lime")
        scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview)
        self.output_text.config(yscrollcommand=scrollbar.set)

        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 初始化格式化器
        self.formatter = None
        self.formatting = False

        # 显示欢迎提示
        self.show_welcome_message()

    # ==== 功能函数 ====
    def browse_input_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")])
        if path:
            self.input_path.delete(0, "end")
            self.input_path.insert(0, path)

    def browse_output_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")])
        if path:
            self.output_path.delete(0, "end")
            self.output_path.insert(0, path)

    def start_format(self):
        if hasattr(self, 'formatting') and self.formatting:
            self.log("任务已在运行中，请勿重复点击")
            return

        self.formatting = True

        self.log("格式化中，请稍候......")

        try:
            input_file = self.input_path.get()
            row = int(self.start_row_combo.get())
            column = column_index_from_string(self.input_col_combo.get())
            output_file = self.output_path.get()
            output_column = column_index_from_string(self.output_col_combo.get())

            # 创建格式化器
            self.formatter = Formatter()

            # 启动线程
            thread = threading.Thread(target=self.run_format, args=(input_file, row, column, output_file, output_column))
            thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
            thread.start()

        except Exception as e:
            self.log(f"启动任务失败: {e}")
            self.formatting = False

    def run_format(self, input_file, row, column, output_file, output_column):
        try:
            self.formatter.format_excel(input_file, row, column, output_file, output_column, log_func=self.log)
        except Exception as e:
            self.log(f"格式化失败: {e}")
        finally:
            self.formatting = False

    def log(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    def show_welcome_message(self):
        """显示欢迎提示信息"""
        welcome_text = """
============================================================
                    报文格式化工具
============================================================

本功能用于处理报文中的多余空行，让您的报文更加整洁规范。

【使用说明】
  1. 选择输入的Excel文件（包含待处理的报文）
  2. 设置起始行和输入列（指定报文所在位置）
  3. 选择输出文件和输出列（指定格式化后保存位置）
  4. 点击"开始格式化"按钮开始处理

【功能特点】
  • 智能识别并去除连续的多余空行
  • 保留必要的单个空行，保持报文格式
  • 批量处理Excel中的多条报文

============================================================
"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", welcome_text)
        self.output_text.config(state="disabled")
