from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # 创建一个 256x256 的图像，背景为白色
    image = Image.new('RGB', (256, 256), color='white')

    # 创建一个绘图对象
    draw = ImageDraw.Draw(image)

    # 绘制橙色的圆形
    orange_color = (255, 165, 0)
    draw.ellipse((28, 28, 228, 228), fill=orange_color)

    # 绘制纹路
    draw.line((128, 28, 128, 228), fill="white", width=4)
    draw.line((28, 128, 228, 128), fill="white", width=4)
    draw.arc((28, 78, 228, 178), start=30, end=330, fill="white", width=4)
    draw.arc((28, 78, 228, 178), start=150, end=210, fill="white", width=4)

    # 设置字体和大小
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # 在图像上绘制 "DICOM" 文本
    text1 = "DICOM"
    text1_bbox = draw.textbbox((0, 0), text1, font=font)
    text1_width = text1_bbox[2] - text1_bbox[0]
    text1_height = text1_bbox[3] - text1_bbox[1]
    text1_x = (image.width - text1_width) // 2
    text1_y = (image.height - text1_height) // 2 - 30  # 上移一些以留出空间给第二行文本
    draw.text((text1_x, text1_y), text1, fill="black", font=font)

    # 在图像上绘制 "Classifier" 文本
    text2 = "Classifier"
    text2_bbox = draw.textbbox((0, 0), text2, font=font)
    text2_width = text2_bbox[2] - text2_bbox[0]
    text2_height = text2_bbox[3] - text2_bbox[1]
    text2_x = (image.width - text2_width) // 2
    text2_y = text1_y + text1_height + 10  # 放在第一行文本的下方，并留出一些间距
    draw.text((text2_x, text2_y), text2, fill="black", font=font)

    # 保存为 .ico 文件
    image.save("dicom_icon.ico")

if __name__ == "__main__":
    create_icon()