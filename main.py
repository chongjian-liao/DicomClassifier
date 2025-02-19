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

        # 初始化窗宽窗位
        self.window_width = None
        self.window_level = None
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.zoom_scale = 1.0  # 初始化缩放比例

        self.current_index = 0  # 初始化当前选中的图像索引

    def create_widgets(self):
        # 左侧：未处理文件列表框
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.left_label = tk.Label(self.left_frame, text="待处理文件", font=self.default_font)
        self.left_label.pack()

        # 显示左侧文件夹路径的文本框
        self.left_folder_path = tk.Entry(self.left_frame, font=self.default_font, width=40)
        self.left_folder_path.pack(pady=5)

        # 左侧文件列表和滚动条
        self.left_listbox_frame = tk.Frame(self.left_frame)
        self.left_listbox_frame.pack()

        self.unprocessed_listbox = tk.Listbox(self.left_listbox_frame, height=30, width=40, font=self.default_font)
        self.unprocessed_listbox.pack(side=tk.LEFT)

        self.left_scrollbar = tk.Scrollbar(self.left_listbox_frame, orient=tk.VERTICAL)
        self.left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.unprocessed_listbox.config(yscrollcommand=self.left_scrollbar.set)
        self.left_scrollbar.config(command=self.unprocessed_listbox.yview)

        # 绑定鼠标双击事件
        self.unprocessed_listbox.bind("<Double-Button-1>", self.on_double_click)

        # 显示未分类文件数量的标签
        self.unprocessed_count_label = tk.Label(self.left_frame, text="未分类文件数量: 0", font=self.default_font)
        self.unprocessed_count_label.pack(pady=5)

        # 中间：DICOM 图像显示区域
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.middle_label = tk.Label(self.middle_frame, text="DICOM查看器", font=self.default_font)
        self.middle_label.pack()

        self.canvas = tk.Canvas(self.middle_frame, width=800, height=800, bg="black")
        self.canvas.pack()

        # 显示窗宽窗位的标签
        self.window_info_label = tk.Label(self.middle_frame, text="窗宽: N/A 窗位: N/A", font=self.default_font)
        self.window_info_label.pack(pady=5)

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

        # 右上文件列表和滚动条
        self.top_listbox_frame = tk.Frame(self.right_frame)
        self.top_listbox_frame.pack()

        self.top_folder_listbox = tk.Listbox(self.top_listbox_frame, height=15, width=40, font=self.default_font)
        self.top_folder_listbox.pack(side=tk.LEFT)

        self.top_scrollbar = tk.Scrollbar(self.top_listbox_frame, orient=tk.VERTICAL)
        self.top_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.top_folder_listbox.config(yscrollcommand=self.top_scrollbar.set)
        self.top_scrollbar.config(command=self.top_folder_listbox.yview)

        # 右下：文件夹选择按钮与文件列表
        self.bottom_folder_label = tk.Label(self.right_frame, text="分类文件夹二", font=self.default_font)
        self.bottom_folder_label.pack()

        self.bottom_folder_button = tk.Button(self.right_frame, text="打开文件夹", command=self.open_bottom_folder,
                                              font=self.default_font)
        self.bottom_folder_button.pack()

        # 显示右下文件夹路径的文本框
        self.bottom_folder_path = tk.Entry(self.right_frame, font=self.default_font, width=40)
        self.bottom_folder_path.pack(pady=5)

        # 右下文件列表和滚动条
        self.bottom_listbox_frame = tk.Frame(self.right_frame)
        self.bottom_listbox_frame.pack()

        self.bottom_folder_listbox = tk.Listbox(self.bottom_listbox_frame, height=15, width=40, font=self.default_font)
        self.bottom_folder_listbox.pack(side=tk.LEFT)

        self.bottom_scrollbar = tk.Scrollbar(self.bottom_listbox_frame, orient=tk.VERTICAL)
        self.bottom_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.bottom_folder_listbox.config(yscrollcommand=self.bottom_scrollbar.set)
        self.bottom_scrollbar.config(command=self.bottom_folder_listbox.yview)

        # 中间的操作按钮
        self.button_frame = tk.Frame(self.middle_frame)
        self.button_frame.pack(pady=10)

        self.skip_button = tk.Button(self.button_frame, text="↑ 跳过该图像", command=self.skip_file, font=self.default_font)
        self.skip_button.grid(row=0, column=1, pady=5)

        self.move_left_button = tk.Button(self.button_frame, text="← 移至上方文件夹", command=self.move_to_left_folder,
                                        font=self.default_font)
        self.move_left_button.grid(row=1, column=0, padx=5)

        self.next_button = tk.Button(self.button_frame, text="↓ 下一个图像", command=self.next_image, font=self.default_font)
        self.next_button.grid(row=1, column=1, pady=5)

        self.move_right_button = tk.Button(self.button_frame, text="→ 移至下方文件夹", command=self.move_to_right_folder,
                                        font=self.default_font)
        self.move_right_button.grid(row=1, column=2, padx=5)

        # 菜单栏：文件夹打开选项
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="打开文件夹", command=self.open_folder)

        # 绑定鼠标左键事件
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_image)

        # 绑定鼠标右键事件
        self.canvas.bind("<ButtonPress-3>", self.start_adjust_window)
        self.canvas.bind("<B3-Motion>", self.adjust_window)

        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self.zoom_image)

    def bind_keyboard_events(self):
        """绑定键盘事件"""
        self.root.bind("<Left>", lambda event: self.move_to_left_folder())  # 左箭头
        self.root.bind("<Right>", lambda event: self.move_to_right_folder())  # 右箭头
        self.root.bind("<Up>", lambda event: self.skip_file())  # 上箭头
        self.root.bind("<Down>", lambda event: self.next_image())  # 下箭头

    def next_image(self):
        """显示下一个图像"""
        if self.current_index < len(self.unprocessed_files) - 1:
            self.current_index += 1
            self.window_width = None
            self.window_level = None
            self.display_selected_image(self.current_index)

    def open_folder(self):
        """ 打开文件夹并加载其所有 DICOM 文件 """
        folder_path = filedialog.askdirectory()  # 弹出文件夹选择对话框
        if folder_path:
            self.unprocessed_files = []
            # 递归查找文件夹下的所有 DICOM 文件
            self.load_dicom_files(folder_path)
            self.update_unprocessed_list()  # 更新未处理文件列表

            # 获取上级目录
            parent_folder = os.path.dirname(folder_path)

            # 自动创建 UP、DOWN 和 IGNORE 文件夹
            self.right_top_folder = os.path.join(parent_folder, "UP")
            self.right_bottom_folder = os.path.join(parent_folder, "DOWN")
            self.ignore_folder = os.path.join(parent_folder, "IGNORE")
            os.makedirs(self.right_top_folder, exist_ok=True)
            os.makedirs(self.right_bottom_folder, exist_ok=True)
            os.makedirs(self.ignore_folder, exist_ok=True)

            # 更新文件夹路径显示
            self.left_folder_path.delete(0, tk.END)
            self.left_folder_path.insert(tk.END, folder_path)
            self.top_folder_path.delete(0, tk.END)
            self.top_folder_path.insert(tk.END, self.right_top_folder)
            self.bottom_folder_path.delete(0, tk.END)
            self.bottom_folder_path.insert(tk.END, self.right_bottom_folder)

            # 更新文件夹列表
            self.update_top_folder_list()
            self.update_bottom_folder_list()

            # 显示第一个图像
            if self.unprocessed_files:
                self.current_index = 0
                self.display_selected_image(self.current_index)

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
        for index, file in enumerate(self.unprocessed_files):
            self.unprocessed_listbox.insert(tk.END, os.path.basename(file))  # 插入文件名
        self.unprocessed_count_label.config(text=f"未分类文件数量: {len(self.unprocessed_files)}")  # 更新未分类文件数量

        # 清除所有项目的高亮效果
        for i in range(self.unprocessed_listbox.size()):
            self.unprocessed_listbox.itemconfig(i, {'bg': 'white'})

        # 高亮当前显示的文件
        if self.unprocessed_files:
            self.unprocessed_listbox.itemconfig(self.current_index, {'bg': 'yellow'})

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

    def display_selected_image(self, index):
        """显示选中的 DICOM 图像"""
        if index < len(self.unprocessed_files):
            current_file = self.unprocessed_files[index]
            try:
                ds = pydicom.dcmread(current_file)
                image_data = ds.pixel_array

                # 计算初始窗宽窗位
                if self.window_width is None or self.window_level is None:
                    self.window_width = np.max(image_data) - np.min(image_data)
                    self.window_level = (np.max(image_data) + np.min(image_data)) / 2

                image = self.apply_window_level(image_data, self.window_width, self.window_level)
                image = Image.fromarray(image)  # 转为灰度图

                # 保存原始图像尺寸
                self.original_image = image
                self.original_width, self.original_height = image.size

                # 应用当前缩放比例
                new_width = int(image.width * self.zoom_scale)
                new_height = int(image.height * self.zoom_scale)
                image = image.resize((new_width, new_height), Image.LANCZOS)

                self.pil_image = image  # 保存 PIL 图像对象
                self.photo = ImageTk.PhotoImage(image)
                # 获取当前图像的位置
                current_image = self.canvas.find_withtag("image")
                if current_image:
                    current_coords = self.canvas.coords(current_image)
                else:
                    current_coords = (400, 400)

                # 删除旧图像并显示新图像
                self.canvas.delete("image")
                self.canvas.create_image(current_coords[0], current_coords[1], image=self.photo, tags="image")
                # 更新窗宽窗位标签
                self.window_info_label.config(text=f"窗宽: {self.window_width:.2f} 窗位: {self.window_level:.2f} 缩放比例: {self.zoom_scale * 100:.0f}%")

                # 清除所有项目的高亮效果
                for i in range(self.unprocessed_listbox.size()):
                    self.unprocessed_listbox.itemconfig(i, {'bg': 'white'})

                # 高亮选中的文件名称
                self.unprocessed_listbox.selection_clear(0, tk.END)
                self.unprocessed_listbox.selection_set(index)
                self.unprocessed_listbox.activate(index)
                self.unprocessed_listbox.see(index)
                self.unprocessed_listbox.itemconfig(index, {'bg': 'yellow'})

            except Exception as e:
                messagebox.showerror("错误", f"无法显示图像: {e}")

    def apply_window_level(self, image_data, window_width, window_level):
        """ 应用窗宽窗位调整 """
        min_val = window_level - (window_width / 2)
        max_val = window_level + (window_width / 2)
        image_data = np.clip(image_data, min_val, max_val)
        image_data = ((image_data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        return image_data

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
            current_file = self.unprocessed_files.pop(self.current_index)  # 从未处理文件列表中移除当前文件
            try:
                shutil.move(current_file, destination_folder)  # 移动文件
                self.current_index = min(self.current_index, len(self.unprocessed_files) - 1)  # 更新当前索引
                self.update_unprocessed_list()  # 更新未处理文件列表
                self.update_top_folder_list()  # 更新右上文件夹列表
                self.update_bottom_folder_list()  # 更新右下文件夹列表
            except Exception as e:
                messagebox.showerror("错误", f"文件移动失败: {e}")

    def skip_file(self):
        """ 跳过当前文件 """
        if self.unprocessed_files:
            current_file = self.unprocessed_files.pop(self.current_index)  # 从未处理文件列表中移除当前文件
            try:
                shutil.move(current_file, self.ignore_folder)  # 移动文件到 IGNORE 文件夹
                self.current_index = min(self.current_index, len(self.unprocessed_files) - 1)  # 更新当前索引
                self.update_unprocessed_list()  # 更新未处理文件列表
            except Exception as e:
                messagebox.showerror("错误", f"文件移动失败: {e}")

    def start_adjust_window(self, event):
        """记录鼠标右键按下时的位置"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def adjust_window(self, event):
        """调整窗宽窗位"""
        delta_x = event.x - self.last_mouse_x
        delta_y = event.y - self.last_mouse_y

        self.window_width = max(1, self.window_width + np.int16(delta_x))
        self.window_level = max(0, self.window_level + delta_y)

        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        # 保持图像位置和大小不变
        current_image = self.canvas.find_withtag("image")
        if current_image:
            current_coords = self.canvas.coords(current_image)
            image_width, image_height = self.pil_image.size  # 获取当前图像的原始尺寸
            self.display_selected_image(self.current_index)
            self.canvas.coords(current_image, current_coords)
            self.canvas.scale(current_image, 0, 0, self.zoom_scale, self.zoom_scale)

    def start_drag(self, event):
        """记录鼠标左键按下时的位置"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def drag_image(self, event):
        """拖动图像"""
        delta_x = event.x - self.last_mouse_x
        delta_y = event.y - self.last_mouse_y

        self.canvas.move("image", delta_x, delta_y)

        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def zoom_image(self, event):
        """ 缩放图像 """
        scale = 1.0
        if event.delta > 0:
            scale = 1.1
        elif event.delta < 0:
            scale = 0.9

        self.zoom_scale *= scale  # 更新缩放比例

        # 获取当前图像的位置
        current_image = self.canvas.find_withtag("image")
        if current_image:
            current_coords = self.canvas.coords(current_image)
        else:
            current_coords = (400, 400)  # 默认中心

        # 计算新的图像尺寸
        new_width = int(self.original_width * self.zoom_scale)
        new_height = int(self.original_height * self.zoom_scale)

        # 使用 PIL 对图像进行缩放
        resized_image = self.resize_image(self.pil_image, new_width, new_height)

        # 更新图像对象
        self.photo = resized_image

        # 更新画布上的图像
        self.canvas.itemconfig(current_image, image=self.photo)

        # 重新计算缩放后的图像中心位置，以鼠标位置为中心
        mouse_x, mouse_y = event.x, event.y
        new_x = mouse_x - (mouse_x - current_coords[0]) * scale
        new_y = mouse_y - (mouse_y - current_coords[1]) * scale

        # 移动图像到新的位置
        self.canvas.coords(current_image, new_x, new_y)

        # 更新画布的滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("image"))

        # 更新窗宽窗位标签
        self.window_info_label.config(text=f"窗宽: {self.window_width:.2f} 窗位: {self.window_level:.2f} 缩放比例: {self.zoom_scale * 100:.0f}%")

    def resize_image(self, image, new_width, new_height):
        """ 使用 PIL 对图像进行缩放 """
        pil_image = image.resize((new_width, new_height), Image.LANCZOS)
        return ImageTk.PhotoImage(pil_image)

    def on_double_click(self, event):
        """处理鼠标双击事件以选择图像"""
        selection = self.unprocessed_listbox.curselection()
        if selection:
            self.current_index = selection[0]  # 更新被选择的图像的索引
            self.window_width = None
            self.window_level = None
            self.display_selected_image(self.current_index)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = DicomFileManager(root)
        root.mainloop()
    except Exception as e:
        print(f"程序出错: {e}")