import os
import shutil

class DicomFileHandler:
    """负责所有与文件相关的操作"""
    
    def __init__(self):
        self.unprocessed_files = []  # 存储未处理文件的路径
        self.right_top_folder = ""  # 右上文件夹路径
        self.right_bottom_folder = ""  # 右下文件夹路径

    def load_dicom_files(self, folder_path):
        """递归遍历文件夹，加载所有 DICOM 文件"""
        self.unprocessed_files = []  # 重置未处理文件列表
        for root_dir, dirs, files in os.walk(folder_path):  # 遍历当前文件夹及其子文件夹
            for file in files:
                if file.lower().endswith(".dcm"):  # 判断是否是 DICOM 文件
                    self.unprocessed_files.append(os.path.join(root_dir, file))

    def move_file(self, file, destination_folder):
        """将文件移动到指定的文件夹"""
        if not destination_folder:
            raise ValueError("目标文件夹未选择")
        
        try:
            shutil.move(file, destination_folder)  # 移动文件
        except Exception as e:
            raise RuntimeError(f"文件移动失败: {e}")

    def skip_file(self):
        """跳过当前文件"""
        if self.unprocessed_files:
            self.unprocessed_files.pop(0)  # 从未处理文件列表中移除当前文件

    def get_current_file(self):
        """获取当前需要处理的文件"""
        return self.unprocessed_files[0] if self.unprocessed_files else None

    def get_unprocessed_files(self):
        """获取所有未处理文件"""
        return self.unprocessed_files
