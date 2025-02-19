# DicomClassifier

## 项目简介

DicomClassifier 是一个用于手动分类 DICOM 文件的工具。该工具提供了一个图形用户界面，用户可以方便地浏览、查看和分类 DICOM 文件。用户可以将 DICOM 文件移动到不同的文件夹中，以便进行进一步的处理和分析。

## 功能特点

- 浏览和查看 DICOM 文件
- 手动分类 DICOM 文件
- 支持图像缩放和窗宽窗位调整
- 支持键盘快捷键操作

## 安装依赖

在使用该项目之前，请确保已安装以下依赖库：

```shell
pip install numpy pydicom pillow
```

## 使用 PyInstaller 打包项目
```shell
pyinstaller --onefile --noconsole --icon=dicom_icon.ico --name=DicomClassifier main.py
```