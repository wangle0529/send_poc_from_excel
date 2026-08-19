import tkinter as tk
import os

class ChangelogPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="white")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll_frame = tk.Frame(self)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_rowconfigure(0, weight=1)

        self.text = tk.Text(
            scroll_frame,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
            bg="black",
            fg="lime",
            padx=10,
            pady=10
        )

        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.load_changelog()

    def load_changelog(self):
        changelog_path = os.path.join(os.path.dirname(__file__), "..", "static", "changelog.txt")

        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.text.config(state="normal")
            self.text.insert("end", content)
            self.text.config(state="disabled")
        except Exception as e:
            error_msg = f"无法加载 changelog 文件:\n{e}"
            self.text.config(state="normal")
            self.text.insert("end", error_msg)
            self.text.config(state="disabled")
