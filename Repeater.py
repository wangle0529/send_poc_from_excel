#v2.0.250827 新增功能

import requests
import re
import tkinter as tk




class Repeater(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="white")

        # --- 主行列权重 ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=2)  # 输入框：2份
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=3)  # 输出框：3份（更高）

        self.label_width = 12

        # ====== 1. 服务器地址 + 发送按钮 ======
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
        tk.Checkbutton(server_frame, text="HTTPS",  variable=self.use_https,command=self.send_https).grid(row=0, column=2, padx=5)
        # print(self.use_https)

        tk.Button(
            server_frame,
            text="发送",
            width=10,
            command=self.on_send_click  # 绑定发送事件
        ).grid(row=0, column=3, padx=5)

        # ====== 2. 输入数据标签 ======
        tk.Label(
            self,
            text="请求:",
            anchor="w",
            bg="white",
            font=("Arial", 10, "bold")
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 5))

        # ====== 3. 输入文本框 ======
        input_frame = tk.Frame(self)
        input_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_text = tk.Text(input_frame, wrap="word", undo=True, font=("Consolas", 10), height=4)
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

        # --- 初始化网络请求变量 ---
        self.headers = {}
        self.body = ""
        self.method = ""
        self.path = ""
        self.http_version = "1.1"

        self.is_use_https=0

    # ==================== 核心方法：解析 HTTP 请求 ====================
    def parse(self, raw_request):
        decoded_request = raw_request.replace('_x000D_', '').replace('\u200b', '')

        if '\r\n\r\n' in decoded_request:
            header_body_split = decoded_request.split('\r\n\r\n', 1)
        else:
            header_body_split = decoded_request.split('\n\n', 1)

        headers_str = header_body_split[0]
        body_str = header_body_split[1] if len(header_body_split) > 1 else ""

        # 修复换行
        body_str = body_str.replace('\n', '\r\n')

        # 提取请求行
        lines = headers_str.strip().splitlines()
        request_line = lines[0]
        match = re.match(r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH|TRACE|CONNECT)\s+([^\s]+)\s+HTTP/([\d.]+)$', request_line)
        if match:
            self.method, self.path, self.http_version = match.groups()
        else:
            raise ValueError("无效的请求行")

        # 解析请求头
        self.headers = {}
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if ': ' in line:
                key, value = line.split(': ', 1)
            elif ':' in line:
                key, value = line.split(':', 1)
                value = value.strip()
            else:
                continue
            self.headers[key] = value

        # 自动添加 User-Agent，防止request自动添加python头触发规则
        if 'User-Agent' not in self.headers and 'user-agent' not in self.headers:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        self.body = body_str

    # v20251021支持https功能
    def send_https(self):
        self.is_use_https=self.use_https.get()
        # return self.is_use_https


    # ==================== 发送单条请求 ====================
    def send_1_poc(self):
        try:
            # v20251021支持https功能
            if self.is_use_https:
                url=f"https://{self.dst}{self.path}"
            else:
                url = f"http://{self.dst}{self.path}"
            response = requests.request(
                method=self.method,      #v1.8.3,选择报文里的请求方法
                url=url,
                headers=self.headers,
                data=self.body,
                allow_redirects=False,
                timeout=10,
                verify=False
            )
            return response
        except requests.exceptions.RequestException as e:
            return f"请求失败: {e}"

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
            self.parse(content)
        except Exception as e:
            self.log(f"解析失败：{e}")
            return

        # 5. 发送请求
        response = self.send_1_poc()

        # 6. 显示结果
        if isinstance(response, requests.Response):
            result = (
                f"=== 响应状态 ===\n"
                f"Status Code: {response.status_code}\n"
                f"URL: {response.url}\n\n"
                f"=== 响应头 ===\n"
                f"{dict(response.headers)}\n\n"
                f"=== 响应体 ===\n"
                f"{response.text}"
            )
            self.output_text.insert("end", result)
        else:
            self.output_text.insert("end", f"发送失败：\n{response}")

        self.output_text.config(state="disabled")

    # ==================== 日志输出 ====================
    def log(self, message):
        print(message)  # 可改为 GUI 日志面板
