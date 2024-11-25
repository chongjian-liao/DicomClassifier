import os
import tkinter as tk
from tkinter import filedialog

from DicomFileHandler import DicomFileHandler


class DicomFileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM 文件分类器")  # 设置窗口标题

        self.default_font = ("Arial", 12)  # 设置字体

        # 创建文件处理类的实例
        self.file_handler = DicomFileHandler()

        self.create_widgets()  # 创建用户界面组件
        self.bind_keyboard_events()  # 绑定键盘事件

    def create_widgets(self):
        """创建用户界面组件"""
        # 左侧：未处理文件列表框
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.left_label = tk.Label(self.left_frame, text="待处理文件", font=self.default_font)
        self.left_label.pack()

        self.unprocessed_listbox = tk.Listbox(self.left_frame, height=30, width=40, font=self.default_font)
        self.unprocessed_listbox.pack()

        # 中间：DICOM 图像显示区域
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.middle_label = tk.Label(self.middle_frame, text="DICOM查看器", font=self.default_font)
        self.middle_label.pack()

        self.canvas = tk.Canvas(self.middle_frame, width=800, height=800, bg="gray")
        self.canvas.pack()

        # 右侧：文件夹选择和文件列表
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # 右上：文件夹选择按钮与文件列表
        self.top_folder_label = tk.Label(self.right_frame, text="分类文件夹一", font=self.default_font)
        self.top_folder_label.pack()

        self.top_folder_button = tk.Button(self.right_frame, text="打开文件夹", command=self.open_top_folder,
                                           font=self.default_font)
        self.top_folder_button.pack()

        # 显示右上文件夹路径的文本框
        self.top_folder_path = tk.Entry(self.right_frame, font=self.default_font, width=40)
        self.top_folder_path.pack(pady=5)

        self.top_folder_listbox = tk.Listbox(self.right_frame, height=15, width=40, font=self.default_font)
        self.top_folder_listbox.pack()

        # 右下：文件夹选择按钮与文件列表
        self.bottom_folder_label = tk.Label(self.right_frame, text="分类文件夹二", font=self.default_font)
        self.bottom_folder_label.pack()

        self.bottom_folder_button = tk.Button(self.right_frame, text="打开文件夹", command=self.open_bottom_folder,
                                              font=self.default_font)
        self.bottom_folder_button.pack()

        # 显示右下文件夹路径的文本框
        self.bottom_folder_path = tk.Entry(self.right_frame, font=self.default_font, width=40)
        self.bottom_folder_path.pack(pady=5)

        self.bottom_folder_listbox = tk.Listbox(self.right_frame, height=15, width=40, font=self.default_font)
        self.bottom_folder_listbox.pack()

        # 中间的操作按钮
        self.move_left_button = tk.Button(self.middle_frame, text="← 移至上方", command=self.move_to_left_folder,
                                          font=self.default_font)
        self.move_left_button.pack(pady=10)

        self.move_right_button = tk.Button(self.middle_frame, text="→ 移至下方", command=self.move_to_right_folder,
                                           font=self.default_font)
        self.move_right_button.pack(pady=10)

        self.skip_button = tk.Button(self.middle_frame, text="↑ 跳过", command=self.skip_file, font=self.default_font)
        self.skip_button.pack(pady=10)

        # 菜单栏：文件夹打开选项
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="打开文件夹", command=self.open_folder)

    def bind_keyboard_events(self):
        """绑定键盘事件"""
        self.root.bind("<Left>", lambda event: self.move_to_left_folder())  # 左箭头
        self.root.bind("<Right>", lambda event: self.move_to_right_folder())  # 右箭头
        self.root.bind("<Up>", lambda event: self.skip_file())  # 上箭头

    def open_folder(self):
        """打开文件夹并加载其所有 DICOM 文件"""
        folder_path = filedialog.askdirectory()  # 弹出文件夹选择对话框
        if folder_path:
            self.file_handler.load_dicom_files(folder_path)  # 使用文件处理类加载文件
            self.update_unprocessed_list()  # 更新未处理文件列表

    def open_top_folder(self):
        """打开右上方文件夹"""
        self.right_top_folder = filedialog.askdirectory()
        if self.right_top_folder:
            self.top_folder_path.delete(0, tk.END)  # 清空文本框
            self.top_folder_path.insert(tk.END, self.right_top_folder)  # 显示文件夹路径
            self.update_top_folder_list()

    def open_bottom_folder(self):
        """打开右下方文件夹"""
        self.right_bottom_folder = filedialog.askdirectory()
        if self.right_bottom_folder:
            self.bottom_folder_path.delete(0, tk.END)  # 清空文本框
            self.bottom_folder_path.insert(tk.END, self.right_bottom_folder)  # 显示文件夹路径
            self.update_bottom_folder_list()

    def update_unprocessed_list(self):
        """更新未处理文件列表框"""
        self.unprocessed_listbox.delete(0, tk.END)  # 清空列表框内容
        for file in self.file_handler.get_unprocessed_files():
            self.unprocessed_listbox.insert(tk.END, os.path.basename(file))  # 插入文件名

    def update_top_folder_list(self):
        """更新右上文件夹列表"""
        if self.right_top_folder:
            files = os.listdir(self.right_top_folder)
            self.top_folder_listbox.delete(0, tk.END)
            for file in files:
                self.top_folder_listbox.insert(tk.END, file)

    def update_bottom_folder_list(self):
        """更新右下文件夹列表"""
        if self.right_bottom_folder:
            files = os.listdir(self.right_bottom_folder)
            self.bottom_folder_listbox.delete(0, tk.END)
            for file in files:
                self.bottom_folder_listbox.insert(tk.END, file)

    def move_to_left_folder(self):
        """移动当前文件到右上文件夹"""
        current_file = self.file_handler.get_current_file()
        if current_file and self.right_top_folder:
            self.file_handler.move_file(current_file, self.right_top_folder)
            self.file_handler.skip_file()
            self.update_unprocessed_list()

    def move_to_right_folder(self):
        """移动当前文件到右下文件夹"""
        current_file = self.file_handler.get_current_file()
        if current_file and self.right_bottom_folder:
            self.file_handler.move_file(current_file, self.right_bottom_folder)
            self.file_handler.skip_file()
            self.update_unprocessed_list()

    def skip_file(self):
        """跳过当前文件"""
        self.file_handler.skip_file()
        self.update_unprocessed_list()
