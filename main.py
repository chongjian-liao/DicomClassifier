import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import pydicom
from PIL import Image, ImageTk


class DicomFileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM 文件分类器")  # 设置窗口标题

        self.default_font = ("Arial", 12)  # 设置字体

        self.create_widgets()  # 创建用户界面组件

        # 文件列表和文件夹路径的初始化
        self.unprocessed_files = []  # 存储未处理文件的路径
        self.right_top_folder = ""  # 右上文件夹路径
        self.right_bottom_folder = ""  # 右下文件夹路径

        self.bind_keyboard_events()  # 绑定键盘事件

    def create_widgets(self):
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
        """ 打开文件夹并加载其所有 DICOM 文件 """
        folder_path = filedialog.askdirectory()  # 弹出文件夹选择对话框
        if folder_path:
            self.unprocessed_files = []
            # 递归查找文件夹下的所有 DICOM 文件
            self.load_dicom_files(folder_path)
            self.update_unprocessed_list()  # 更新未处理文件列表

    def load_dicom_files(self, folder_path):
        """ 递归遍历文件夹，加载所有 DICOM 文件 """
        for root_dir, dirs, files in os.walk(folder_path):  # 遍历当前文件夹及其子文件夹
            for file in files:
                if file.lower().endswith(".dcm"):  # 判断是否是 DICOM 文件
                    self.unprocessed_files.append(os.path.join(root_dir, file))

    def open_top_folder(self):
        """ 打开右上方文件夹 """
        self.right_top_folder = filedialog.askdirectory()
        if self.right_top_folder:
            self.top_folder_path.delete(0, tk.END)  # 清空文本框
            self.top_folder_path.insert(tk.END, self.right_top_folder)  # 显示文件夹路径
            self.update_top_folder_list()

    def open_bottom_folder(self):
        """ 打开右下方文件夹 """
        self.right_bottom_folder = filedialog.askdirectory()
        if self.right_bottom_folder:
            self.bottom_folder_path.delete(0, tk.END)  # 清空文本框
            self.bottom_folder_path.insert(tk.END, self.right_bottom_folder)  # 显示文件夹路径
            self.update_bottom_folder_list()

    def update_unprocessed_list(self):
        """ 更新未处理文件列表框 """
        self.unprocessed_listbox.delete(0, tk.END)  # 清空列表框内容
        for file in self.unprocessed_files:
            self.unprocessed_listbox.insert(tk.END, os.path.basename(file))  # 插入文件名
        self.display_current_image()  # 显示第一个文件的图像

    def update_top_folder_list(self):
        """ 更新右上文件夹列表 """
        if self.right_top_folder:
            files = os.listdir(self.right_top_folder)
            self.top_folder_listbox.delete(0, tk.END)
            for file in files:
                self.top_folder_listbox.insert(tk.END, file)

    def update_bottom_folder_list(self):
        """ 更新右下文件夹列表 """
        if self.right_bottom_folder:
            files = os.listdir(self.right_bottom_folder)
            self.bottom_folder_listbox.delete(0, tk.END)
            for file in files:
                self.bottom_folder_listbox.insert(tk.END, file)

    def display_current_image(self):
        """ 显示当前 DICOM 图像 """
        if self.unprocessed_files:
            current_file = self.unprocessed_files[0]
            try:
                ds = pydicom.dcmread(current_file)
                image_data = ds.pixel_array
                image = Image.fromarray((image_data / np.max(image_data) * 255).astype(np.uint8))  # 转为灰度图
                image = image.resize((800, 800))  # 调整图像大小
                self.photo = ImageTk.PhotoImage(image)
                self.canvas.create_image(400, 400, image=self.photo)  # 在画布上显示图像
            except Exception as e:
                messagebox.showerror("错误", f"无法显示图像: {e}")

    def move_to_left_folder(self):
        """ 将当前文件移动到上方文件夹 """
        self.move_file(self.right_top_folder)

    def move_to_right_folder(self):
        """ 将当前文件移动到下方文件夹 """
        self.move_file(self.right_bottom_folder)

    def move_file(self, destination_folder):
        """ 将文件移动到指定的文件夹 """
        if not destination_folder:
            messagebox.showwarning("警告", "请先选择目标文件夹!")
            return

        if self.unprocessed_files:
            current_file = self.unprocessed_files.pop(0)  # 从未处理文件列表中移除当前文件
            try:
                shutil.move(current_file, destination_folder)  # 移动文件
                self.update_unprocessed_list()  # 更新未处理文件列表
                self.update_top_folder_list()  # 更新右上文件夹列表
                self.update_bottom_folder_list()  # 更新右下文件夹列表
            except Exception as e:
                messagebox.showerror("错误", f"文件移动失败: {e}")

    def skip_file(self):
        """ 跳过当前文件 """
        if self.unprocessed_files:
            self.unprocessed_files.pop(0)  # 从未处理文件列表中移除当前文件
            self.update_unprocessed_list()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = DicomFileManager(root)
        root.mainloop()
    except Exception as e:
        print(f"程序出错: {e}")
