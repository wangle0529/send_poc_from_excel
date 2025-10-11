# from tkinter import *
import tkinter as tk
from ExRepeater import ExRepeater
from Repeater import Repeater


class main_window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('WAF工具_v2.0.251011')
        self.geometry('800x600')

        # 设置窗口图标（.ico 文件）
        self.set_window_icon(r"D:\Data\Python\send_poc_from_excel\logo_256x256.ico")

        # 设置窗口最小和最大尺寸
        self.minsize(width=800, height=600)
        self.maxsize(width=1200, height=900)

        # 左右分列，设置行和列的权重
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 左边 Frame：固定宽度
        self.left_frame = tk.Frame(self, width=200, relief="solid", borderwidth=1, bg="light gray")
        self.left_frame.grid(row=0, column=0, sticky="ns")
        self.left_frame.grid_propagate(False)  # 禁止自动调整大小

        # 右边 Frame：可变宽度
        self.right_frame = tk.Frame(self, relief="solid", borderwidth=1, bg="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # 配置 right_frame 权重，让内部 frame 能填满
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # 左边菜单按钮
        self.left_button_texts = ["ExRepeater", "Repeater","others"]
        self.left_buttons = []

        # 设置左边菜单按钮布局
        for i in range(len(self.left_button_texts)):
            self.left_frame.grid_rowconfigure(i, weight=0)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # 创建右侧不同页面的内容
        self.right_content_frames = {}
        self.right_content_frames["ExRepeater"] = ExRepeater(self.right_frame)
        self.right_content_frames["Repeater"] = Repeater(self.right_frame)   #v2.0.250827,增加Repeater模块
        # self.right_content_frames["aaa"] = tk.Frame(self.right_frame, bg="gray")

        # 初始化显示第一个页面
        self.show_frame("Repeater")

        # 生成左边按钮
        for i, text in enumerate(self.left_button_texts):
            btn = tk.Button(self.left_frame, text=text, command=lambda f=text: self.show_frame(f))
            btn.grid(row=i, column=0, sticky="ew", padx=2, pady=2)
            btn.configure(height=2)
            self.left_buttons.append(btn)

    def set_window_icon(self, icon_path):
        try:
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"无法加载图标：{e}")

    def show_frame(self, page_name):
        """ 显示指定的页面 """
        # 先隐藏所有frame
        for frame in self.right_content_frames.values():
            frame.grid_forget()

        # 显示目标frame并填满 right_frame
        self.right_content_frames[page_name].grid(row=0, column=0, sticky="nsew")

if __name__ == '__main__':
    app = main_window()
    app.mainloop()
