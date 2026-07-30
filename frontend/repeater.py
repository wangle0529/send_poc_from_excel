import tkinter as tk
from tkinter import filedialog
from backend.http_client import HTTPClient
from backend.request_parser import RequestParser

class Repeater(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="white")

        # --- 主行列权重 ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)  # 统一容器（标签+按钮）
        self.grid_rowconfigure(2, weight=2)  # 输入框：2份
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=3)  # 输出框：3份（更高）

        self.label_width = 12

        # ====== 1. 服务器地址 ======
        server_frame = tk.Frame(self, bg="white")
        server_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        server_frame.grid_columnconfigure(1, weight=1)

        tk.Label(server_frame, text="服务器地址:", width=self.label_width, anchor="w", bg="white").grid(
            row=0, column=0, sticky="w", padx=5)

        self.server_entry = tk.Entry(server_frame)
        self.server_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.server_entry.insert(0, "127.0.0.1:8080")

        # v20251021支持https功能
        self.use_https=tk.IntVar()
        tk.Checkbutton(server_frame, text="HTTPS",  variable=self.use_https).grid(row=0, column=2, padx=5)

        # v20250527自动更新content-length功能
        self.auto_update_content_length=tk.IntVar()
        tk.Checkbutton(server_frame, text="自动更新Content-Length",  variable=self.auto_update_content_length).grid(row=0, column=3, padx=5)

        # ====== 2. 统一容器（标签 + 按钮，保证两按钮右对齐） ======
        control_frame = tk.Frame(self, bg="white")
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        control_frame.grid_columnconfigure(1, weight=1)

        # Row 0: 请求标签 + 发送按钮
        tk.Label(control_frame, text="请求:", anchor="w", bg="white",
                 font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 5), pady=(10, 5))
        tk.Button(control_frame, text="发送", width=10,
                  command=self.on_send_click).grid(
            row=0, column=2, padx=5)

        # Row 1: 从文件获取请求体 + 浏览按钮
        tk.Label(control_frame, text="从文件获取请求体:", bg="white",
                 font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=5)
        self.body_file_entry = tk.Entry(control_frame)
        self.body_file_entry.grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(control_frame, text="浏览", width=10,
                  command=self.browse_body_file).grid(
            row=1, column=2, padx=5)

        # ====== 3. 输入文本框 ======
        input_frame = tk.Frame(self)
        input_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_text = tk.Text(input_frame, wrap="none", undo=False, font=("Consolas", 10), height=4)
        v_scroll1 = tk.Scrollbar(input_frame, orient="vertical", command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=v_scroll1.set)

        self.input_text.grid(row=0, column=0, sticky="nsew")
        v_scroll1.grid(row=0, column=1, sticky="ns")

        # ====== 4. 输出数据标签 ======
        tk.Label(
            self,
            text="响应:",
            anchor="w",
            bg="white",
            font=("Arial", 10, "bold")
        ).grid(row=3, column=0, sticky="w", padx=10, pady=(10, 5))

        # ====== 5. 输出文本框 ======
        output_frame = tk.Frame(self)
        output_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_frame,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
            bg="black",
            fg="lime",
            height=6,
            insertbackground="white"
        )
        v_scroll2 = tk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=v_scroll2.set)

        self.output_text.grid(row=0, column=0, sticky="nsew")
        v_scroll2.grid(row=0, column=1, sticky="ns")

        # 显示欢迎提示
        self.show_welcome_message()

        # 初始化客户端
        self.http_client = HTTPClient()
        self.parser = RequestParser()

    # ==================== 发送按钮点击事件 ====================
    def on_send_click(self):
        # 1. 获取目标地址
        self.dst = self.server_entry.get().strip()
        if not self.dst:
            self.log("错误：服务器地址不能为空！")
            return

        # 2. 获取输入内容
        content = self.input_text.get("1.0", "end-1c").strip()
        if not content:
            self.log("错误：请输入 HTTP 请求内容！")
            return

        # 3. 清空输出框
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")

        # 4. 解析请求
        try:
            request_data = self.parser.parse(content)
        except Exception as e:
            self.log(f"解析失败：{e}")
            return

        # 4.5 从文件获取请求体（覆盖文本框中的 body，按二进制流读取）
        body_file = self.body_file_entry.get().strip()
        if body_file:
            try:
                with open(body_file, 'rb') as f:
                    request_data['body'] = f.read()
            except Exception as e:
                self.log(f"读取请求体文件失败：{e}")
                return

        # 5. 构建 URL
        if self.use_https.get():
            url = f"https://{self.dst}{request_data['path']}"
        else:
            url = f"http://{self.dst}{request_data['path']}"

        # 6. 自动更新 Content-Length
        if self.auto_update_content_length.get():
            body_length = len(request_data['body']) if request_data['body'] else 0
            headers = request_data['headers']
            has_content_length = any(key.lower() == 'content-length' for key in headers)
            if has_content_length:
                keys_to_delete = [key for key in headers if key.lower() == 'content-length']
                for key in keys_to_delete:
                    del headers[key]
            if body_length > 0:
                headers.add('Content-Length', str(body_length))

        # 7. 发送请求
        response = self.http_client.send_request(
            method=request_data['method'],
            url=url,
            headers=request_data['headers'],
            body=request_data['body'],
            http_version=request_data['http_version']
        )

        # 8. 显示结果
        if hasattr(response, 'status_code'):
            result = (
                f"=== 响应状态 ===\n"
                f"Status Code: {response.status_code}\n"
                f"URL: {response.url}\n\n"
                f"=== 响应头 ===\n"
                f"{response.headers}\n\n"
                f"=== 响应体 ===\n"
                f"{response.text}"
            )
            self.output_text.insert("end", result)
        else:
            self.output_text.insert("end", f"发送失败：\n{response}")

        self.output_text.config(state="disabled")

    # ==================== 浏览请求体文件 ====================
    def browse_body_file(self):
        path = filedialog.askopenfilename(title="选择请求体文件")
        if path:
            self.body_file_entry.delete(0, "end")
            self.body_file_entry.insert(0, path)

    # ==================== 日志输出 ====================
    def log(self, message):
        print(message)  # 可改为 GUI 日志面板

    # ==================== 显示欢迎信息 ====================
    def show_welcome_message(self):
        """显示欢迎提示信息"""
        welcome_text = """
============================================================
                        Repeater 工具
============================================================

本功能用于手动发送单个 HTTP 请求，方便测试和调试。

【使用说明】
  1. 在服务器地址输入框中输入目标地址（如：127.0.0.1:8080）
  2. 如需使用 HTTPS，请勾选 HTTPS 选项
  3. 在请求输入框中输入完整的 HTTP 请求报文
  4. 如需发送二进制请求体，可在"从文件获取请求体"处选择文件
  5. 点击"发送"按钮发送请求
  6. 响应结果将显示在下方响应区域

【请求格式示例】
  POST /api/test HTTP/1.1
  Host: 127.0.0.1:8080
  Content-Type: application/json
  Content-Length: 18

  {"key": "value"}

============================================================
"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", welcome_text)
        self.output_text.config(state="disabled")
