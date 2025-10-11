# ExRepeater.py
import send_poc_from_excel
import tkinter as tk
from tkinter import filedialog, ttk
from send_poc_from_excel import *
from openpyxl.utils import get_column_letter, column_index_from_string
import threading

def generate_excel_columns():
    columns = []
    for i in range(0, 26): # A to Z
        columns.append(chr(65 + i)) # chr(65) is 'A'
    for i in range(0, 1):
        for j in range(0, 26): # AA to AZ
            columns.append(chr(65 + i) + chr(65 + j))
    return columns[:26] + columns[26:] # To ensure we only go up to AZ

class ExRepeater(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="lightblue")

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

        # ====== 3. 输出列 & 发送间隔 ======
        row_col_frame = tk.Frame(self)
        row_col_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)

        # 设置四列权重：Label 列不扩展，Entry/Combobox 列扩展
        for i in range(4):
            row_col_frame.grid_columnconfigure(i, weight=1 if i in (1, 3) else 0)

        # 输出列
        tk.Label(row_col_frame, text="输出列:", width=label_width, anchor="w").grid(
            row=0, column=0, sticky="w", padx=0
        )
        self.output_col_combo = ttk.Combobox(row_col_frame, values=excel_columns, width=10)
        self.output_col_combo.grid(row=0, column=1, sticky="w", padx=0)
        self.output_col_combo.set("H")

        #发送间隔
        tk.Label(row_col_frame, text="发送间隔(ms):", width=12, anchor="w").grid(
            row=0, column=2, sticky="w", padx=0
        )

        self.input_col_interval = ttk.Combobox(row_col_frame, values=[100*int(i) for i in range(1, 21)], width=10,state="readonly")
        self.input_col_interval.grid(row=0, column=3, sticky="w", padx=0)
        self.input_col_interval.set(200)
        # self.input_col_interval.config(state='disabled')

        # ====== 4. 服务器地址 + 发送按钮 ======
        server_frame = tk.Frame(self)
        server_frame.grid(row=4, column=0, sticky="ew", padx=0, pady=0)
        server_frame.grid_columnconfigure(1, weight=1)

        tk.Label(server_frame, text="服务器地址:", width=label_width, anchor="w").grid(
            row=0, column=0, sticky="w", padx=0
        )
        self.server_entry = tk.Entry(server_frame)
        self.server_entry.grid(row=0, column=1, sticky="ew", padx=0)
        self.server_entry.insert(0, "127.0.0.1:8080")

        tk.Button(server_frame, text="发送", width=label_width, command=self.send_to_server).grid(
            row=0, column=2, padx=0
        )
        tk.Button(server_frame, text="停止", width=label_width, command=self.stop_to_send).grid(
            row=0, column=3, padx=0
        )

        # ====== 5. 输出日志窗口 + 滚动条 ======
        output_frame = tk.Frame(self)
        output_frame.grid(row=5, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(5, weight=1)

        self.output_text = tk.Text(output_frame, wrap="word", state="disabled", bg="black", fg="lime")
        scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview)
        self.output_text.config(yscrollcommand=scrollbar.set)

        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ==== 功能函数 ====
    def browse_input_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.input_path.delete(0, "end")
            self.input_path.insert(0, path)

    def browse_output_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            self.output_path.delete(0, "end")
            self.output_path.insert(0, path)

    def send_to_server(self):
        if hasattr(self, 'sending') and self.sending:
            self.log("任务已在运行中，请勿重复点击")
            return

        self.sending = True
        STOP_TO_SEND=0

        self.log("检测中，请稍候......")

        try:
            input_file = self.input_path.get()
            row = int(self.start_row_combo.get())
            column = column_index_from_string(self.input_col_combo.get())
            output_file = self.output_path.get()
            output_column = column_index_from_string(self.output_col_combo.get())
            dst = self.server_entry.get()
            interval = float(self.input_col_interval.get())

            send_poc_from_excel.SEND_INTERVAL=interval/1000
            # print(send_poc_from_excel.SEND_INTERVAL)

            test=excel_sender(input_file,row,column,output_file,output_column,dst,log_func=self.log,finish_callback=self.on_task_complete)
            thread = threading.Thread(target=test.read_excel)
            thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
            thread.start()

        except Exception as e:
            self.log(f"启动任务失败: {e}")



    def on_task_complete(self):
        self.sending = False
        self.log("任务已完成")
        send_poc_from_excel.STOP_TO_SEND=0

    def log(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    # ==== 20251011，新增暂停功能 ====
    def stop_to_send(self):
        send_poc_from_excel.STOP_TO_SEND=1
